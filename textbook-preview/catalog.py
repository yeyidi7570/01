"""Read the selected version of each lesson directly from the repository."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
BOOK = ROOT / "structured_textbooks" / "数学2023_哈语学生_哈语教材（4-1）_АЛМАТЫКІТАП"


def index_lesson(lesson):
    index = {}

    def visit(obj, kind):
        object_id = obj["id"]
        if object_id in index:
            raise ValueError(f"Duplicate object ID: {object_id}")
        index[object_id] = (kind, obj)
        for child in obj.get("units", obj.get("elements", [])):
            visit(child, child["type"])
        for cell in obj.get("cells", []):
            visit(cell, "table_cell")

    visit(lesson, "lesson")
    for link in lesson.get("teaching_links", []):
        visit(link, "teaching_link")
    return index


class Catalog:
    def __init__(self):
        self.entries = {}
        self.content = {}
        self.index = {}
        for sample in json.loads((HERE / "samples.json").read_text(encoding="utf-8")):
            raw = (BOOK / sample["path"]).read_bytes()
            data = json.loads(raw)
            lesson = data["lesson"]
            lesson_id = lesson["id"]
            if data["schema_version"] != "textbook-lesson/4.0" or lesson["number"] != sample["lesson"]:
                raise ValueError(f"Unexpected lesson: {sample['path']}")
            index = index_lesson(lesson)
            modules = [{**m, "id": f"{lesson_id}:{m['key']}"} for m in sample["modules"]]
            if any(index[m["id"]][0] != "module" for m in modules):
                raise ValueError(f"Invalid pilot modules: {lesson_id}")
            self.entries[lesson_id] = {
                "id": lesson_id, "title": lesson["title_kk"], "number": lesson["number"],
                "version": data["data_version"], "modules": modules,
                "gaps": {f"{lesson_id}:{key}": reason for key, reason in sample["gaps"].items()},
            }
            self.content[lesson_id] = raw, data
            self.index[lesson_id] = index

    def public_entries(self):
        return [{**entry, "modules": [
            {"id": m["id"], "topic": m["topic"], "number": self.index[entry["id"]][m["id"]][1]["module_number"]}
            for m in entry["modules"]
        ]} for entry in self.entries.values()]
