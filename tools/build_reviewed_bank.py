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
    "校正", "非线性系统", "状态空间", "选择与填空", "最优控制",
]
# Ordered rules select a single primary path for each question.
TOPIC_GROUPS = {
    "数学基础": (
        ("拉普拉斯变换|微分方程", "连续系统求解 / 拉普拉斯变换"),
        ("差分|Z 变换", "离散系统求解 / Z 变换"),
    ),
    "建模": (
        ("机电|电动机", "物理建模 / 机电系统"),
        ("机械", "物理建模 / 机械系统"),
        ("液位|热", "物理建模 / 液位与热过程"),
        ("方框|信号流|梅森|结构图", "数学模型 / 方框图与信号流图"),
        ("概念", "数学模型 / 基本概念"),
        ("传递函数|微分方程", "数学模型 / 微分方程与传递函数"),
    ),
    "时域分析": (
        ("劳斯|稳定|特征根", "稳定性 / 劳斯判据"),
        ("误差|型别", "稳态误差 / 误差系数"),
        ("由阶跃|反求|确定参数", "动态响应 / 由响应辨识参数"),
        ("主导|降阶", "动态响应 / 主导极点与降阶"),
        ("二阶|性能|超调|调节时间", "动态响应 / 二阶性能指标"),
        ("响应", "动态响应 / 响应计算"),
    ),
    "根轨迹": (
        ("校正", "根轨迹校正"),
        ("稳定|增益|取值", "稳定性与参数"),
        ("参数|圆|零度", "根轨迹绘制 / 参数根轨迹"),
        ("主导|性能|降阶", "稳定性与参数"),
        ("绘制|常规|规则", "根轨迹绘制 / 常规根轨迹"),
    ),
    "频域分析": (
        ("Bode|伯德|对数", "伯德图 / 幅相曲线"),
        ("奈奎斯特|奈氏|幅相", "奈奎斯特分析"),
        ("裕度|交越|截止", "稳定裕度"),
        ("频率指标|带宽|谐振|三频段|频率特性|延迟", "频率特性 / 频域性能指标"),
    ),
    "离散系统": (
        ("采样|保持|脉冲", "采样与保持 / 脉冲传递函数"),
        ("状态方程", "离散模型与响应 / 离散状态方程"),
        ("差分|动态|响应", "离散模型与响应 / 差分方程"),
        ("稳定|朱利|单位圆|Jury", "稳定性 / 单位圆判据"),
        ("误差", "稳态误差"),
        ("最少拍|设计|校正", "控制器设计"),
    ),
    "校正": (
        ("PID|PI|PD", "PID 控制"),
        ("根轨迹", "串联校正 / 根轨迹法"),
        ("超前|滞后|串联|由校正后", "串联校正 / 超前与滞后"),
        ("反馈|复合|前馈", "复合控制 / 反馈与前馈"),
    ),
    "非线性系统": (
        ("自振|谐波", "描述函数法 / 谐波平衡与自振"),
        ("描述", "描述函数法 / 描述函数计算"),
        ("平衡点|奇点", "相平面法 / 平衡点与局部稳定性"),
        ("相平面|相轨迹", "相平面法 / 相轨迹分析"),
        ("反馈线性|校正", "非线性控制 / 反馈线性化"),
        ("环节|等效", "非线性环节 / 特性与等效"),
    ),
    "状态空间": (
        ("观测器|估计", "反馈与观测器 / 状态观测器"),
        ("反馈|配置|解耦|镇定", "反馈与观测器 / 状态反馈"),
        ("能控|能观|可控|可观|对偶|最小实现", "结构性质与实现 / 能控性与能观性"),
        ("标准型|标准形|约旦|对角", "结构性质与实现 / 标准型"),
        ("李雅普诺夫", "稳定性 / 李雅普诺夫方法"),
        ("稳定", "稳定性 / 特征值判据"),
        ("状态转移|响应", "状态转移与响应 / 状态转移矩阵"),
        ("传递函数", "状态空间模型 / 传递函数矩阵"),
        ("状态方程|状态空间|状态变量|建模", "状态空间模型 / 状态方程与结构图"),
    ),
    "选择与填空": (
        ("选择", "选择题"),
        ("填空", "填空题"),
    ),
    "最优控制": (),
}

# These mixed questions are grouped by the task that determines their solution.
PRIMARY_TOPICS = {
    ("北京航空航天大学", 2025, "833", "5"): "状态空间 / 状态观测器",
    ("厦门大学", 2024, "844", "6"): "校正 / 超前",
    ("四川大学", 2025, "871", "2"): "根轨迹 / 绘制",
    ("天津大学", 2023, "812", "1"): "时域分析 / 劳斯",
    ("北京理工大学", 2023, "810", "8"): "最优控制",
    ("南开大学", 2023, "809", "九"): "最优控制",
}


def primary_topic(card):
    identity = card["school"], card["year"], card["variant"], str(card["number"])
    topic = PRIMARY_TOPICS.get(identity, card["topics"][0])
    chapter, _, point = topic.partition(" / ")
    assert chapter in TOPIC_GROUPS, (identity, topic)
    for pattern, group in TOPIC_GROUPS[chapter]:
        if re.search(pattern, point):
            return f"{chapter} / {group}"
    assert not point, (identity, topic)
    return chapter


def validate_topic_tree(questions):
    children = {}
    for question in questions:
        path, = question["categories"]
        levels = path.split(" / ")
        assert len(levels) <= 3, path
        for level in range(1, len(levels)):
            siblings = children.setdefault(tuple(levels[:level]), set())
            siblings.add(levels[level])
            assert len(siblings) <= 5, (levels[:level], siblings)


FIGURE = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")
SOURCE_FIELDS = ("school", "year", "variant", "number")


def write_json(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def question_id(parts):
    identity = json.dumps(parts, ensure_ascii=False)
    return int.from_bytes(hashlib.blake2s(identity.encode(), digest_size=5).digest(), "big") + 1_000_000


def source_id(source):
    school, year, variant, number = (source[k] for k in SOURCE_FIELDS)
    return question_id([school, year, variant, str(number)])


def source_entry(source):
    return {key: source[key] for key in SOURCE_FIELDS}


PRACTICE_TITLE = "起点精选1000题"
PRACTICE_CHAPTERS = {
    1: "自动控制基本概念",
    2: "控制系统数学模型",
    3: "线性系统时域分析",
    4: "线性系统的根轨迹法",
}
PRACTICE_KINDS = ("选择题", "填空题", "判断题", "简答题", "分析题")


def load_practice(ids, aliases, detail_rows, merged_references):
    rows = []
    source = ROOT / "data-src" / "practice"
    for file in sorted(source.glob("qd1000-*.json")):
        for card in json.loads(file.read_text(encoding="utf-8-sig")):
            volume = card["volume"]
            chapter = card["chapter"]
            kind = card["kind"]
            number = card["number"]
            origin = card["origin"]
            identity = (volume, chapter, kind, number)
            assert volume in {"A", "B"} and chapter > 0 and kind in PRACTICE_KINDS and number > 0, identity
            identifier = question_id([PRACTICE_TITLE, *identity])
            assert identifier not in ids and identifier not in aliases, identity
            if target := card.get("sameAs"):
                assert target != identifier, identity
                aliases[identifier] = target
                school, year = re.fullmatch(r"(.+?)(?:\s*(\d{4}))?", origin.strip()).groups()
                merged_references.append((target, dict(
                    volume=volume, chapter=chapter, kind=kind, number=number, origin=origin,
                    school=re.sub(r"（(?:学硕|专硕|\d{3})）$", "", school), year=int(year) if year else None,
                    questionPages=card["questionPages"], answerPages=card["answerPages"],
                )))
                continue
            ids.add(identifier)
            stem, answer, explanation = [card[k].strip() for k in ("stem", "answer", "explanation")]
            assert all((stem, answer, explanation, origin, card["questionPages"], card["answerPages"])), identity
            for location in FIGURE.findall("\n".join((stem, answer, explanation))):
                assert location.startswith("img/reviewed/") and location.endswith(".svg")
                assert (PUBLIC / location).is_file(), (identity, location)
            topic_paths = [primary_topic({**card, "school": origin, "year": None, "variant": volume})]
            tags = [topic_paths[0].split(" / ")[0]]
            number_label = f"{volume}册 · 第{chapter}章 · {kind}{number}"
            chapter_label = f"{volume}册 第{chapter}章 {PRACTICE_CHAPTERS.get(chapter, '')}".strip()
            school, year = re.fullmatch(r"(.+?)(?:\s*(\d{4}))?", origin.strip()).groups()
            school = re.sub(r"（(?:学硕|专硕|\d{3})）$", "", school)
            rows.append(dict(
                id=identifier, number=number_label, source=f"{PRACTICE_TITLE} · {origin}", sourceType="practice",
                school=school, year=int(year) if year else None,
                categories=topic_paths, tags=tags, hasFigure=bool(FIGURE.search(stem)), stem=stem,
                pdfPage=card["questionPages"], search=" ".join((PRACTICE_TITLE, origin, number_label, chapter_label, *topic_paths, stem)),
            ))
            detail_rows[identifier] = dict(
                answer=answer, explanation=explanation, originalImages=[], answerPdfPages=card["answerPages"],
                referenceNote=card.get("notes", ""), sourceType="practice",
            )
    return rows


def school_paths(question):
    entries = [question, *question.get("alsoAppearedIn", []), *question.get("practiceReferences", [])]
    paths = (f'{q["school"]} / {q["year"]}' if q["year"] else q["school"] for q in entries)
    return list(dict.fromkeys(paths))


def build():
    source = ROOT / "data-src" / "reviewed"
    questions = []
    detail_dir = PUBLIC / "data" / "questions"
    detail_dir.mkdir(parents=True, exist_ok=True)
    ids = set()
    aliases = {}
    detail_rows = {}
    stems = {}
    for path in sorted(source.glob("*.json")):
        for card in json.loads(path.read_text(encoding="utf-8-sig")):
            school, year, variant, number = identity = tuple(card[k] for k in SOURCE_FIELDS)
            tier = card.get("tier", "985")
            assert tier in {"985", "211", "双非"}, identity
            identifier = source_id(card)
            assert identifier not in ids, identity
            ids.add(identifier)
            topic_paths = [primary_topic(card)]
            tags = [topic_paths[0].split(" / ")[0]]
            for field in ("stem", "answer", "explanation", "questionPages", "answerPages"):
                assert str(card[field]).strip(), (identity, field)
            stem, answer, explanation = [card[k].strip() for k in ("stem", "answer", "explanation")]
            normalized_stem = re.sub(r"\s+", "", stem)
            assert normalized_stem not in stems, (identity, stems.get(normalized_stem))
            stems[normalized_stem] = identity
            for location in FIGURE.findall("\n".join((stem, answer, explanation))):
                assert location.startswith("img/reviewed/") and location.endswith(".svg")
                assert (PUBLIC / location).is_file(), (identity, location)
            label = f"{school} · {year}" + (f" · {variant}" if variant else "")
            other_sources = card.get("alsoAppearedIn", [])
            for entry in other_sources:
                alias = source_id(entry)
                assert alias != identifier and alias not in aliases, (identity, entry)
                aliases[alias] = identifier
            source_search = " ".join(" ".join(str(entry[key]) for key in SOURCE_FIELDS) for entry in other_sources)
            questions.append(dict(
                id=identifier, school=school, year=year, number=number, source=label, sourceType="reviewed",
                categories=topic_paths, tags=tags, hasFigure=bool(FIGURE.search(stem)),
                stem=stem, pdfPage=str(card["questionPages"]),
                **({"alsoAppearedIn": [source_entry(entry) for entry in other_sources]} if other_sources else {}),
                search=" ".join(filter(None, [school, tier, str(year), str(variant), str(number), source_search,
                                               *topic_paths, *card["topics"], stem])),
            ))
            detail_rows[identifier] = dict(
                answer=answer, explanation=explanation, originalImages=[], answerPdfPages=str(card["answerPages"]),
                referenceNote=card.get("notes", ""), sourceType="reviewed",
            )

    merged_references = []
    practice = load_practice(ids, aliases, detail_rows, merged_references)
    assert not ids.intersection(aliases), "A merged question is still present as its own card"
    assert set(aliases.values()) <= ids, "A merged question's retained card is missing"
    retained = {q["id"]: q for q in [*questions, *practice]}
    for target, reference in merged_references:
        question = retained[target]
        question.setdefault("practiceReferences", []).append(reference)
        reference_label = f'{reference["volume"]}册 第{reference["chapter"]}章 {reference["kind"]}{reference["number"]}'
        question["search"] += f' {PRACTICE_TITLE} {reference_label} {reference["origin"]}'
        if PRACTICE_TITLE not in question["source"]:
            question["source"] += f' · {PRACTICE_TITLE}'
    for identifier, detail in detail_rows.items():
        write_json(detail_dir / f"{identifier}.json", detail)
    for path in detail_dir.glob("*.json"):
        if path.stem.isdigit() and int(path.stem) not in ids:
            path.unlink()

    def question_list(key, name, rows, paths):
        return dict(id=key, name=name, questionIds=[q["id"] for q in rows],
                    categoryByQuestion={str(q["id"]): paths(q) for q in rows})

    questions.sort(key=lambda q: (q["school"], -q["year"], q["source"], str(q["number"]).zfill(4)))
    all_questions = questions + practice
    validate_topic_tree(all_questions)
    by_school = sorted(all_questions, key=lambda q: (q["school"], -(q["year"] or 0)))
    lists = [
        question_list("complete", "按专题", all_questions, lambda q: q["categories"]),
        question_list("by-school", "按院校", by_school, school_paths),
    ]
    write_json(PUBLIC / "data" / "library.json", dict(
        subject="自动控制原理", source="院校初试题库与起点精选1000题", topicOrder=TOPICS,
        years=sorted({entry["year"] for q in all_questions for entry in [q, *q.get("alsoAppearedIn", [])]
                      if entry["year"] is not None}, reverse=True),
        questionAliases=aliases, lists=lists, questions=all_questions,
    ))
    print(f"{len(questions)} 道重排核对题，{len({q['school'] for q in questions})} 所院校")
    print(f"{len(practice)} 道起点精选练习")
    print(dict(Counter(tag for q in questions for tag in q["tags"])))


if __name__ == "__main__":
    build()
