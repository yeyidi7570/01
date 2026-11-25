"""Build the self-contained browser demo from the shared preview sources."""
from base64 import b64encode
from io import BytesIO
import json
import re

from PIL import Image

from catalog import BOOK, HERE, Catalog, index_lesson
from server import read_image
from teaching import plan

OUTPUT = HERE / "textbook-preview-offline.html"


def encode_image(blob, format):
    return f"data:image/{format};base64,{b64encode(blob).decode('ascii')}"


def images_for(lesson):
    scans, crops = {}, {}
    pages = {page["scan_asset_id"]: page for page in lesson["pages"]}
    for asset_id, page in pages.items():
        scan = read_image(page["scan_path"], (page["width"], page["height"]))
        with Image.open(BytesIO(scan)) as image, BytesIO() as output:
            image.convert("RGB").save(output, "WEBP", quality=86)
            scans[asset_id] = encode_image(output.getvalue(), "webp")
    index = index_lesson(lesson["lesson"])
    for kind, obj in index.values():
        if kind != "informative_image" or not obj.get("crop_asset_id"):
            continue
        asset_id = obj["crop_asset_id"]
        asset = lesson["crop_assets"][asset_id]
        page = pages[asset["scan_asset_id"]]
        crop = read_image(page["scan_path"], (page["width"], page["height"]), tuple(asset["bbox"]))
        crops[asset_id] = encode_image(crop, "png")
    return scans, crops


def make_call_example():
    path = BOOK / "02_segmentation_review/lesson_004/revision_1/content.json"
    data = json.loads(path.read_bytes())
    lesson = data["lesson"]
    unit = next(unit for unit in lesson["units"]
                if unit["type"] == "module" and unit["module_number"] == 5)
    module_id = unit["id"]
    lesson_id = lesson["id"]
    pages = {ref["scan_asset_id"] for ref in unit["page_refs"]}
    module = {"id": module_id, "topic": "按数级写数", "number": 5}
    entry = {
        "id": lesson_id, "number": lesson["number"], "title": lesson["title_kk"],
        "version": data["data_version"], "modules": [module], "gaps": {}, "supplement": True,
    }
    lesson = {**lesson, "units": [unit], "content_order": [module_id], "teaching_links": []}
    asset_ids = {obj.get("crop_asset_id") for _, obj in index_lesson(lesson).values()}
    subset = {
        "schema_version": data["schema_version"], "data_version": data["data_version"],
        "book": data["book"], "lesson": lesson,
        "pages": [p for p in data["pages"] if p["scan_asset_id"] in pages],
        "crop_assets": {k: v for k, v in data["crop_assets"].items() if k in asset_ids},
    }
    result = {
        "mode": "mock",
        "references": [{"lesson_id": lesson_id, "object_id": module_id, "type": "module"}],
        "generated": {
            "organization": "请学生依次读三个子题，先确认涉及的数级，再写出对应的数。",
            "explanation": "",
            "exercise": "",
        },
    }
    sample = {**module, "lesson": lesson["number"], "terms": [], "result": result}
    return entry, subset, sample


def build():
    catalog = Catalog()
    entries = catalog.public_entries()
    lessons = {oid: data for oid, (_, data) in catalog.content.items()}
    plans = []
    for entry in entries:
        for module in catalog.entries[entry["id"]]["modules"]:
            number = catalog.index[entry["id"]][module["id"]][1]["module_number"]
            result = plan(catalog, f"展示第{entry['number']}课第{number}题")
            plans.append({
                "id": module["id"], "lesson": entry["number"], "number": number,
                "terms": module["terms"], "result": {"mode": "mock", **result},
            })

    entry, subset, sample = make_call_example()
    entries.append(entry)
    lessons[entry["id"]] = subset
    plans.append(sample)

    scans, crops = {}, {}
    for data in lessons.values():
        new_scans, new_crops = images_for(data)
        scans.update(new_scans)
        crops.update(new_crops)
    payload = {"catalog": entries, "lessons": lessons, "images": {"scan": scans, "crop": crops}, "plans": plans}

    def read(name):
        return (HERE / name).read_text(encoding="utf-8")

    # Shared modules have only named imports and exports. In the single file
    # their top-level declarations share the inline script's private scope.
    code = "\n".join(re.sub(r"^import .*;\n|^export ", "", read(name), flags=re.MULTILINE)
                     for name in ("render.js", "source.js", "app.js"))
    if re.search(r"^\s*(import|export)\b|</script", code, re.MULTILINE | re.IGNORECASE):
        raise ValueError("Unsupported inline script syntax")
    bundle = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).replace("<", r"\u003c")
    html = read("index.html").replace(
        '<link rel="stylesheet" href="/style.css">', f"<style>\n{read('style.css')}</style>"
    ).replace(
        '  <script type="module" src="/app.js"></script>\n', ""
    ).replace(
        'href="/" class="brand"', 'href="?" class="brand"'
    ).replace(
        "</body>", f'<script type="application/json" id="offline-data">{bundle}</script>\n'
        f"<script>\n(() => {{\n{code}\n}})();\n</script>\n</body>"
    )
    OUTPUT.write_text(html, encoding="utf-8")
    print(f"{OUTPUT.name}: {OUTPUT.stat().st_size:,} bytes")


if __name__ == "__main__":
    build()
