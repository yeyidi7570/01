import json
from pathlib import Path
import unittest

from catalog import BOOK, HERE, ROOT, Catalog
from server import read_image
from teaching import plan


class PreviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = Catalog()
        cls.samples = json.loads((HERE / "samples.json").read_text(encoding="utf-8"))

    def test_original_json_is_served_verbatim_and_gap_ids_exist(self):
        for sample, (lesson_id, entry) in zip(self.samples, self.catalog.entries.items(), strict=True):
            with self.subTest(lesson=lesson_id):
                raw, _ = self.catalog.content[lesson_id]
                self.assertEqual(raw, (BOOK / sample["path"]).read_bytes())
                self.assertTrue(set(entry["gaps"]) <= self.catalog.index[lesson_id].keys())
        self.assertEqual(sum(len(entry["modules"]) for entry in self.catalog.entries.values()), 5)

    def test_mock_finds_all_five_samples_and_does_not_return_textbook_content(self):
        cases = [
            (1, "请用复合单位讲解时间竖式", "m04", []),
            (1, "用课表讲解怎样计算课间时间", "m05", []),
            (7, "请按第7课第2题讲解多位数笔算借位", "m02", ["note-addition", "note-subtraction"]),
            (10, "请找跨页的体积单位练习", "m03", ["note-volume-units"]),
            (28, "给我有路线图的速度和路程例子，连同教学说明", "m03", ["note-speed"]),
        ]
        for number, request, module, notes in cases:
            with self.subTest(request=request):
                prefix = f"math-2023-grade4-part1:lesson-{number:03}"
                result = plan(self.catalog, request)
                refs = result["references"]
                self.assertEqual([r["object_id"] for r in refs],
                                 [prefix, f"{prefix}:{module}", *(f"{prefix}:{n}" for n in notes)])
                self.assertTrue(all(set(ref) == {"object_id", "lesson_id", "type"} for ref in refs))
                self.assertTrue(all(result["generated"].values()))

    def test_lesson_note_and_no_match(self):
        lesson_id = "math-2023-grade4-part1:lesson-007"
        note_id = f"{lesson_id}:note-subtraction"
        self.assertEqual(plan(self.catalog, "打开第7课")["references"],
                         [{"lesson_id": lesson_id, "object_id": lesson_id, "type": "lesson"}])
        self.assertEqual(plan(self.catalog, f"请展示 {note_id}")["references"],
                         [{"lesson_id": lesson_id, "object_id": note_id, "type": "instructional_note"}])
        for query in ["讲唐诗", "请打开第99课第4题的速度练习", "找第28课第99题"]:
            self.assertEqual(plan(self.catalog, query)["references"], [])

    def test_untrusted_provider_output(self):
        lesson_id = "math-2023-grade4-part1:lesson-001"
        reference = {"lesson_id": lesson_id, "object_id": f"{lesson_id}:m04", "type": "module"}
        generated = {"organization": "教师建议", "explanation": "讲解", "exercise": "练习"}
        result = {"references": [reference], "generated": generated}
        self.assertEqual(plan(self.catalog, "测试", lambda *_: result), result)
        invalid_results = [
            {"references": [{**reference, "object_id": "invented"}], "generated": generated},
            {"references": [{**reference, "type": "lesson"}], "generated": generated},
            {"references": [{**reference, "lesson_id": "math-2023-grade4-part1:lesson-007"}],
             "generated": generated},
            {"references": [{**reference, "text_kk": "replacement"}], "generated": generated},
            {"references": [reference, reference], "generated": generated},
            {**result, "textbook": "replacement"},
            None,
        ]
        for invalid in invalid_results:
            with self.subTest(result=invalid), self.assertRaises(ValueError):
                plan(self.catalog, "测试", lambda *_: invalid)
        for request in [" ", "超" * 501, 12]:
            with self.assertRaises(ValueError):
                plan(self.catalog, request)

    def test_source_images_are_local_and_only_crop_endpoints_return_crops(self):
        from io import BytesIO
        from PIL import Image
        _, data = self.catalog.content["math-2023-grade4-part1:lesson-028"]
        obj = self.catalog.index[data["lesson"]["id"]][f"{data['lesson']['id']}:m03:3А:route"][1]
        crop = data["crop_assets"][obj["crop_asset_id"]]
        page = next(p for p in data["pages"] if p["scan_asset_id"] == crop["scan_asset_id"])
        size = page["width"], page["height"]
        x, y, r, b = crop["bbox"]
        path = page["scan_path"]
        with Image.open(ROOT / Path(path)) as source, Image.open(BytesIO(read_image(path, size, (x, y, r, b)))) as preview:
            self.assertEqual(preview.size, (r - x, b - y))
            self.assertEqual(preview.tobytes(), source.crop((x, y, r, b)).tobytes())
        with self.assertRaises(ValueError):
            read_image(path, size, (0, 0, *size))


if __name__ == "__main__":
    unittest.main()
