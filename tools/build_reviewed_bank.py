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
# Ordered rules select a single primary path for each question.
TOPIC_GROUPS = {
    "数学基础": (
        ("拉普拉斯变换|微分方程", "变换与响应 / 连续系统"),
        ("差分|Z 变换", "变换与响应 / 离散系统"),
    ),
    "建模": (
        ("电路|运放|运算放大器", "物理建模 / 电路系统"),
        ("机电|电动机", "物理建模 / 机电系统"),
        ("机械", "物理建模 / 机械系统"),
        ("液位|热", "物理建模 / 过程系统"),
        ("方框|信号流|梅森|结构图", "模型化简 / 方框图与信号流图"),
        ("概念", "模型化简 / 基本概念"),
        ("传递函数|微分方程", "模型化简 / 方程与传递函数"),
    ),
    "时域分析": (
        ("劳斯|稳定|特征根", "稳定性"),
        ("误差|型别", "稳态误差"),
        ("由阶跃|反求|确定参数", "动态性能 / 响应反求参数"),
        ("主导|降阶", "动态性能 / 主导极点与降阶"),
        ("二阶|性能|超调|调节时间", "动态性能 / 二阶系统"),
        ("响应", "动态性能 / 响应求解"),
    ),
    "根轨迹": (
        ("校正", "根轨迹校正"),
        ("稳定|增益|取值", "稳定性与参数"),
        ("参数|圆|零度", "绘制 / 特殊根轨迹"),
        ("主导|性能|降阶", "稳定性与参数"),
        ("绘制|常规|规则", "绘制 / 常规根轨迹"),
    ),
    "频域分析": (
        ("Bode|伯德|对数", "伯德图 / 绘制与识读"),
        ("奈奎斯特|奈氏|幅相", "奈奎斯特图"),
        ("裕度|交越|截止", "稳定裕度"),
        ("频率指标|带宽|谐振|三频段|频率特性|延迟", "频率特性与指标"),
    ),
    "离散系统": (
        ("采样|保持|脉冲", "采样与脉冲模型"),
        ("差分|状态方程|动态|响应", "差分方程与响应"),
        ("稳定|朱利", "稳定性"),
        ("误差", "稳态误差"),
        ("最少拍|设计|校正", "控制器设计"),
    ),
    "校正": (
        ("PID|PI|PD", "PID 控制"),
        ("根轨迹", "频域与根轨迹设计 / 根轨迹校正"),
        ("超前|滞后|串联|由校正后", "频域与根轨迹设计 / 串联校正"),
        ("反馈|复合|前馈", "反馈与前馈补偿"),
    ),
    "非线性系统": (
        ("描述|自振|谐波", "描述函数法"),
        ("相平面|平衡点|奇点|相轨迹", "相平面法"),
        ("反馈线性|校正", "非线性控制设计"),
        ("环节|等效", "非线性环节"),
    ),
    "状态空间": (
        ("观测器|估计", "反馈与观测器 / 状态观测器"),
        ("反馈|配置|解耦|镇定", "反馈与观测器 / 状态反馈"),
        ("能控|能观|可控|可观|对偶|最小实现", "能控能观与实现 / 能控性与能观性"),
        ("标准型|标准形|约旦|对角", "能控能观与实现 / 标准型"),
        ("李雅普诺夫|稳定", "稳定性"),
        ("状态转移|响应", "状态转移与响应"),
        ("状态方程|状态空间|状态变量|传递函数|建模", "状态建模与传递函数"),
    ),
    "选择与填空": (
        ("选择", "选择题"),
        ("填空", "填空题"),
    ),
    "专业综合": (),
}

# These mixed questions are grouped by the task that determines their solution.
PRIMARY_TOPICS = {
    ("厦门大学", 2024, "844", "6"): "校正 / 超前",
    ("四川大学", 2025, "871", "2"): "根轨迹 / 绘制",
    ("天津大学", 2023, "812", "1"): "专业综合",
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
            topic_paths = [primary_topic(card)]
            tags = [topic_paths[0].split(" / ")[0]]
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
                search=" ".join([school, "985", str(year), str(variant), str(number), *topic_paths, *card["topics"], stem]),
            ))
            write_json(detail_dir / f"{identifier}.json", dict(
                answer=answer, explanation=explanation, originalImages=[], answerPdfPages=str(card["answerPages"]),
                referenceNote=card.get("notes", ""), sourceType="reviewed",
            ))

    def question_list(key, name, rows, paths):
        return dict(id=key, name=name, questionIds=[q["id"] for q in rows],
                    categoryByQuestion={str(q["id"]): paths(q) for q in rows})

    questions.sort(key=lambda q: (q["school"], -q["year"], q["source"], str(q["number"]).zfill(4)))
    validate_topic_tree(questions)
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
