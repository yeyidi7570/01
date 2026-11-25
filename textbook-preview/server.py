"""Serve the independent preview and the local teaching API."""
import argparse
from functools import lru_cache
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from io import BytesIO
import json
from urllib.parse import parse_qs, urlsplit

from PIL import Image

from catalog import HERE, ROOT, Catalog
from teaching import plan

STATIC = {
    "/": ("index.html", "text/html; charset=utf-8"),
    "/app.js": ("app.js", "text/javascript; charset=utf-8"),
    "/render.js": ("render.js", "text/javascript; charset=utf-8"),
    "/source.js": ("source.js", "text/javascript; charset=utf-8"),
    "/style.css": ("style.css", "text/css; charset=utf-8"),
}


@lru_cache(maxsize=128)
def read_image(scan_path, expected_size, box=None):
    path = (ROOT / scan_path).resolve()
    if not path.is_relative_to(ROOT / "wiki-data") or path.suffix.lower() != ".png":
        raise ValueError("扫描图路径无效。")
    with Image.open(path) as source:
        if source.size != expected_size:
            raise ValueError("扫描尺寸与教材记录不一致。")
        if box is None:
            return path.read_bytes()
        x, y, r, b = box
        if not (0 <= x < r <= source.width and 0 <= y < b <= source.height):
            raise ValueError("裁图边界无效。")
        if box == (0, 0, *expected_size):
            raise ValueError("整页扫描仅供原书对照。")
        output = BytesIO()
        source.crop(box).save(output, format="PNG")
        return output.getvalue()


class Handler(BaseHTTPRequestHandler):
    def send_data(self, data, media_type, status=HTTPStatus.OK):
        self.send_response(status)
        self.send_header("Content-Type", media_type)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(data)

    def send_json(self, obj, status=HTTPStatus.OK):
        self.send_data(json.dumps(obj, ensure_ascii=False).encode(), "application/json; charset=utf-8", status)

    def do_GET(self):
        url = urlsplit(self.path)
        if url.path in STATIC:
            name, media_type = STATIC[url.path]
            self.send_data((HERE / name).read_bytes(), media_type)
            return
        if url.path == "/api/catalog":
            self.send_json(self.server.catalog.public_entries())
            return
        if url.path not in {"/api/lesson", "/api/crop", "/api/scan"}:
            self.send_json({"error": "未找到该入口。"}, HTTPStatus.NOT_FOUND)
            return
        params = parse_qs(url.query)
        try:
            raw, data = self.server.catalog.content[params["lesson"][0]]
            if url.path == "/api/lesson":
                self.send_data(raw, "application/json; charset=utf-8")
                return
            pages = {p["scan_asset_id"]: p for p in data["pages"]}
            asset_id = params["id"][0]
            crop = data["crop_assets"][asset_id] if url.path == "/api/crop" else None
            page = pages[crop["scan_asset_id"] if crop else asset_id]
            box = tuple(crop["bbox"]) if crop else None
            blob = read_image(page["scan_path"], (page["width"], page["height"]), box)
            self.send_data(blob, "image/png")
        except (KeyError, OSError, ValueError):
            self.send_json({"error": "未找到教材或扫描资源，或资源无效。"}, HTTPStatus.NOT_FOUND)

    def do_POST(self):
        if self.path != "/api/teaching-plan":
            self.send_json({"error": "未找到该入口。"}, HTTPStatus.NOT_FOUND)
            return
        try:
            size = int(self.headers.get("Content-Length", "0"))
            if not 0 < size <= 8192:
                raise ValueError("请求长度无效。")
            payload = json.loads(self.rfile.read(size))
            if not isinstance(payload, dict) or set(payload) != {"request"}:
                raise ValueError("请求应包含 request 字段。")
            result = plan(self.server.catalog, payload["request"])
        except ValueError as error:
            self.send_json({"error": str(error)}, HTTPStatus.BAD_REQUEST)
            return
        self.send_json({"mode": "mock", **result})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    with ThreadingHTTPServer((args.host, args.port), Handler) as server:
        server.catalog = Catalog()
        print(f"Textbook Preview · http://{args.host}:{server.server_port}", flush=True)
        server.serve_forever()


if __name__ == "__main__":
    main()
