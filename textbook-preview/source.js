async function json(url, options) {
  const response = await fetch(url, options);
  const body = await response.json();
  if (!response.ok) throw Error(body.error ?? `请求失败 (${response.status})`);
  return body;
}

function apiAsset(kind, lesson, id = "") {
  return `/api/${kind}?${new URLSearchParams({lesson, id})}`;
}

function ordinal(text) {
  if (/^\d+$/.test(text)) return Number(text);
  const digits = "零一二三四五六七八九";
  if (text === "两") return 2;
  if (text.length === 1 && text !== "十") return digits.indexOf(text);
  const [tens, units] = text.split("十");
  return (tens ? digits.indexOf(tens) : 1) * 10 + (units ? digits.indexOf(units) : 0);
}

function offlinePlan(data, request) {
  const text = request.trim().normalize("NFKC").toLowerCase();
  if (!text || text.length > 500) throw Error("请输入 1–500 字的教学请求。");
  const number = "[0-9零一二两三四五六七八九十]+";
  const lesson = text.match(new RegExp(`第\\s*(${number})\\s*课`));
  const question = text.match(new RegExp(`第\\s*(${number})\\s*题`));
  const candidates = data.plans.map(sample => {
    if (lesson && sample.lesson !== ordinal(lesson[1])) return {...sample, score: 0};
    if (question && sample.number !== ordinal(question[1])) return {...sample, score: 0};
    const explicit = (lesson && question) || text.includes(sample.id);
    const score = explicit ? 100 : sample.terms.filter(term => text.includes(term.toLowerCase())).length;
    return {...sample, score};
  }).filter(item => item.score > 0).sort((a, b) => b.score - a.score);
  const [first, second] = candidates;
  return first && first.score !== second?.score ? first.result : {mode: "mock", references: []};
}

export function previewSource(data) {
  if (data) return {
    offline: true,
    catalog: () => data.catalog,
    lesson: id => data.lessons[id],
    image: (kind, lesson, id) => data.images[kind][id],
    plan: request => offlinePlan(data, request),
  };
  return {
    offline: false,
    catalog: () => json("/api/catalog"),
    lesson: id => json(apiAsset("lesson", id)),
    image: apiAsset,
    plan: request => json("/api/teaching-plan", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({request}),
    }),
  };
}
