"""Provider boundary. The local mock only handles the pilot's vocabulary."""
import re

REFERENCE_TYPES = {"lesson", "module", "instructional_note"}
GENERATED_FIELDS = {"organization", "explanation", "exercise"}


def plan(catalog, request, provider=None):
    if not isinstance(request, str) or not request.strip() or len(request) > 500:
        raise ValueError("请输入 1–500 字的教学请求。")
    provider = provider or mock_provider
    result = provider(catalog, request.strip())
    if not isinstance(result, dict) or set(result) != {"references", "generated"}:
        raise ValueError("教学接口返回了额外字段或缺少必填字段。")
    references = result["references"]
    if not isinstance(references, list):
        raise ValueError("教材引用必须是数组。")
    seen = set()
    for ref in references:
        if not isinstance(ref, dict) or set(ref) != {"lesson_id", "object_id", "type"} or not all(
            isinstance(v, str) for v in ref.values()
        ):
            raise ValueError("无效的教材引用。")
        lesson_id, object_id, kind = ref["lesson_id"], ref["object_id"], ref["type"]
        target = catalog.index.get(lesson_id, {}).get(object_id)
        if kind not in REFERENCE_TYPES or not target or target[0] != kind or object_id in seen:
            raise ValueError(f"无效或重复的教材引用 {object_id}。")
        seen.add(object_id)
    generated = result["generated"]
    if not isinstance(generated, dict) or set(generated) != GENERATED_FIELDS or not all(
        isinstance(value, str) for value in generated.values()
    ):
        raise ValueError("生成内容必须按组织建议、讲解和练习分别返回。")
    return result


def mock_provider(catalog, request):
    candidates = []
    needle = request.casefold()
    lesson_pattern = re.search(r"第\s*0*(\d+)\s*课|lesson[ _-]0*(\d+)", needle)
    module_pattern = re.search(r"第\s*0*(\d+)\s*题|module\s*0*(\d+)", needle)
    lesson_number = int(next(n for n in lesson_pattern.groups() if n)) if lesson_pattern else None
    module_number = int(next(n for n in module_pattern.groups() if n)) if module_pattern else None
    lesson_results = []
    for lesson_id, entry in catalog.entries.items():
        if lesson_number is not None and lesson_number != entry["number"]:
            continue
        index = catalog.index[lesson_id]
        lesson = catalog.content[lesson_id][1]["lesson"]
        explicit = [(kind, oid) for oid, (kind, _) in index.items()
                    if re.search(rf"(?<![\w:-]){re.escape(oid.casefold())}(?![\w:-])", needle)
                    and kind in REFERENCE_TYPES]
        for kind, oid in explicit:
            lesson_results.append((3, lesson_id, oid, kind))
        if lesson_number == entry["number"] or entry["title"].casefold() in needle:
            lesson_results.append((1, lesson_id, lesson_id, "lesson"))
        for module in entry["modules"]:
            obj = index[module["id"]][1]
            if module_number is not None and module_number != obj["module_number"]:
                continue
            score = sum(term.casefold() in needle for term in module["terms"])
            if obj["id"].casefold() in needle:
                score += 100
            if module_number is not None and lesson_number is not None:
                score += 100
            if score:
                candidates.append((score, module, lesson))
    candidates.sort(key=lambda candidate: candidate[0], reverse=True)
    generated = dict.fromkeys(sorted(GENERATED_FIELDS), "")
    references = []

    def add(lesson_id, oid, kind):
        ref = {"lesson_id": lesson_id, "object_id": oid, "type": kind}
        if ref not in references:
            references.append(ref)

    explicit_note = next((r for r in lesson_results if r[0] == 3 and r[3] == "instructional_note"), None)
    if explicit_note:
        _, lesson_id, oid, kind = explicit_note
        add(lesson_id, oid, kind)
        generated["organization"] = "先阅读教材说明，再根据其中的例子组织讨论。"
    elif candidates and (len(candidates) == 1 or candidates[0][0] > candidates[1][0]):
        _, module, lesson = candidates[0]
        lesson_id, oid = lesson["id"], module["id"]
        index = catalog.index[lesson_id]
        add(lesson_id, lesson_id, "lesson")
        add(lesson_id, oid, "module")
        for link in lesson["teaching_links"]:
            if link["relationship"] == "uses_as_material":
                task, note = link["from_id"], link["to_id"]
            elif link["relationship"] == "supports":
                task, note = link["to_id"], link["from_id"]
            else:
                continue
            if (task == oid or task.startswith(f"{oid}:")) and index.get(note, ("",))[0] == "instructional_note":
                add(lesson_id, note, "instructional_note")
        generated.update({k: module[k] for k in GENERATED_FIELDS})
    elif (lesson_results and not candidates and module_number is None
          and len({x[1] for x in lesson_results}) == 1):
        _, lesson_id, oid, kind = max(lesson_results)
        add(lesson_id, oid, kind)
        generated["organization"] = "从课次标题和教学说明开始，再选一道原书任务。"
    return {"references": references, "generated": generated}
