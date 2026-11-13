"""Build the static library from reviewed, typeset questions."""
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
TOPICS = [
    "数学基础", "建模", "时域分析", "根轨迹", "频域分析", "离散系统",
    "校正", "非线性系统", "状态空间", "选择与填空", "专业综合",
]
TOPIC_ALIASES = {
    "时域分析 / 稳定性": "时域分析 / 稳定性与劳斯判据",
    "时域分析 / 稳定性判别": "时域分析 / 稳定性与劳斯判据",
    "时域分析 / 劳斯判据与稳定性": "时域分析 / 稳定性与劳斯判据",
    "时域分析 / 二阶系统性能指标": "时域分析 / 动态性能 / 二阶系统性能指标",
    "时域分析 / 主导极点与性能估算": "时域分析 / 动态性能 / 主导极点与性能估算",
    "频域分析 / Bode 图": "频域分析 / 伯德图",
    "频域分析 / Bode 图绘制": "频域分析 / 伯德图 / 绘制",
    "频域分析 / 奈氏判据": "频域分析 / 奈奎斯特图 / 稳定判据",
    "校正 / 超前校正": "校正 / 超前",
    "校正 / 滞后校正": "校正 / 滞后",
}
FIGURE = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")


def write_json(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def build():
    source = ROOT / "data-src" / "reviewed"
    questions = []
    detail_dir = PUBLIC / "data" / "questions"
    detail_dir.mkdir(parents=True, exist_ok=True)
    ids = set()
    for path in sorted(source.glob("*.json")):
        for card in json.loads(path.read_text(encoding="utf-8-sig")):
            school, year, variant, number = (card[k] for k in ("school", "year", "variant", "number"))
            identity = json.dumps([school, year, variant, str(number)], ensure_ascii=False)
            identifier = int.from_bytes(hashlib.blake2s(identity.encode(), digest_size=5).digest(), "big") + 1_000_000
            assert identifier not in ids, identity
            ids.add(identifier)
            topic_paths = list(dict.fromkeys(TOPIC_ALIASES.get(p, p) for p in card["topics"]))
            tags = list(dict.fromkeys(p.split(" / ")[0] for p in topic_paths))
            assert tags and set(tags) <= set(TOPICS), (identity, tags)
            for field in ("stem", "answer", "explanation", "questionPages", "answerPages"):
                assert str(card[field]).strip(), (identity, field)
            stem, answer, explanation = [card[k].strip() for k in ("stem", "answer", "explanation")]
            for location in FIGURE.findall("\n".join((stem, answer, explanation))):
                assert location.startswith("img/reviewed/") and location.endswith(".svg")
                assert (PUBLIC / location).is_file(), (identity, location)
            label = f"{school} · {year}" + (f" · {variant}" if variant else "")
            questions.append(dict(
                id=identifier, school=school, year=year, number=number, source=label, sourceType="reviewed",
                categories=topic_paths, tags=tags, hasFigure=bool(FIGURE.search(stem)),
                stem=stem, pdfPage=str(card["questionPages"]),
                search=" ".join([school, "985", str(year), str(variant), str(number), *topic_paths, stem]),
            ))
            write_json(detail_dir / f"{identifier}.json", dict(
                answer=answer, explanation=explanation, originalImages=[], answerPdfPages=str(card["answerPages"]),
                referenceNote=card.get("notes", ""), sourceType="reviewed",
            ))

    def question_list(key, name, rows, paths):
        return dict(id=key, name=name, questionIds=[q["id"] for q in rows],
                    categoryByQuestion={str(q["id"]): paths(q) for q in rows})

    questions.sort(key=lambda q: (q["school"], -q["year"], q["source"], str(q["number"]).zfill(4)))
    lists = [
        question_list("complete", "专题分类", questions, lambda q: q["categories"]),
        question_list("by-school", "按院校", questions, lambda q: [f'{q["school"]} / {q["year"]}']),
    ]
    write_json(PUBLIC / "data" / "library.json", dict(
        subject="自动控制原理", source="985 高校初试题库", topicOrder=TOPICS,
        years=sorted({q["year"] for q in questions}, reverse=True), lists=lists, questions=questions,
    ))
    print(f"{len(questions)} 道重排核对题，{len({q['school'] for q in questions})} 所 985 院校")
    print(dict(Counter(tag for q in questions for tag in q["tags"])))


if __name__ == "__main__":
    build()
