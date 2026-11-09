# 控制大观

自动控制原理（重庆大学 844）初试真题的静态刷题网站，界面与交互仿照「数学大观」：题单、章节目录、单题/多题阅读、答案与解析折叠、收藏、不熟练/不会/掌握标记、复测、搜索、字号调节，以及学习记录的导出与导入。

在线访问：<https://mintonight.github.io/control-daguan/>

> ## 版权与使用声明
>
> - 本站题目、答案及解析图片**来源于网络**公开流传的真题资料（含考生回忆版），经整理后仅供个人**学习与交流**使用。
> - **严禁用于任何商业用途**，包括但不限于出售、付费分发和商业培训。
> - 相关内容的**版权归原作者及原出版方所有**。如有侵权，请权利人通过 GitHub Issues 联系，我们核实后会**立即删除**相关内容。
> - 题目与答案可能存在错漏，请以官方资料为准。

## 收录范围

| 年份 | 题数 | 含图题 | 答案/解析形式 |
| ---- | ---- | ------ | ------------- |
| 2025 | 8 | 4 | 文字 LaTeX + 原图 |
| 2024 | 8 | 6 | 文字 LaTeX + 原图 |
| 2023 | 8 | 4 | 文字 LaTeX + 原图 |
| 2022 | 8 | 5 | 原图解析 |
| 2021 | 8 | 5 | 原图解析 |
| 2020 | 7 | 4 | 原图解析 |
| 2019 | 9 | 3 | 原图解析 |
| 2018 | 8 | 5 | 原图解析 |
| 2017 | 8 | 5 | 原图解析 |
| 2016 | 8 | 5 | 原图解析 |
| 合计 | 80 | 46 | |

2016–2022 的题干为文字 + LaTeX，答案与解析为原书解析页截图（已去水印、页眉页脚和标签）；录入时发现的原文笔误写在每题的「勘误/说明」里。

专题：建模、时域分析、根轨迹、频域分析、校正、离散系统、非线性系统、状态空间。

## 间隔复习（FSRS）

复习调度用 [ts-fsrs](https://github.com/open-spaced-repetition/ts-fsrs)（`public/vendor/ts-fsrs/`），全部在浏览器本地计算，没有服务器。

- 三个标记就是评分：**不会 = Again**，**不熟练 = Hard**，**掌握 = Good**（不提供 Easy）。标记仍作为标签显示，下次复习时间由 FSRS 决定。
- 按钮上显示各评分对应的间隔预览（如「不会 1天 / 不熟练 2天 / 掌握 3天」），题目右上角显示下次复习日期。
- 「复测」页默认是**今日待复习**：列出今天到期（含已过期）的题，按到期时间排序；标签上的红色角标是到期题数。另有「不熟练 · 不会」视图，按标签筛题。
- 设置里可调**目标记忆率**（默认 0.90，范围 0.80–0.95；越高间隔越短），也可**重置复习进度**（需确认，标记和收藏保留）。
- 每题的卡片状态和复习日志与标记一起保存在本地，并包含在导出 JSON（version 2）和记录码里。导入时按题取最近一次复习的卡片，日志按 id 去重合并；旧版（version 1）记录照常导入。

## 目录结构

```
public/                 # 静态站点根目录（直接部署）
  index.html app.js app.css
  vendor/katex/         # 本地 KaTeX，离线可用
  data/library.json     # 题单、分类、题干
  data/questions/<id>.json   # 答案、文字解析、原图解析列表
  img/                  # 题图与原图解析（已去除水印和页眉页脚）
data-src/<年份>/          # 2016–2022：questions.json + img/（规范见 incoming/SPEC.md）
incoming/                 # 协作录入区与规范、裁图工具 incoming/tools/cdg_crop.py
tools/
  questions_2023_2025.py    # 2023–2025 题目数据（Markdown + LaTeX）
  make_2019_2022.py         # 生成 data-src/2019–2022
  validate_incoming.mjs     # 校验 questions.json（结构、图片、KaTeX）
  crops.py / crops.json     # 从 PDF 页面裁剪题图与解析图
  build_data.py             # 生成 public/data
  verify.py                 # Playwright 全控件点击验收
  verify_fsrs.py            # FSRS 验收（模拟时间到期、导入导出往返）
.github/workflows/pages.yml # 推送 main 后自动部署到 GitHub Pages
```

## 本地运行

```bash
python3 -m http.server 8765 -d public
# 打开 http://localhost:8765/
python3 tools/verify.py http://localhost:8765/        # 可选：全控件验收
python3 tools/verify_fsrs.py http://localhost:8765/   # 可选：FSRS 验收
```

## 追加年份

推荐方式：按 `incoming/SPEC.md` 产出 `data-src/<年份>/questions.json` 与 `img/`，运行 `node tools/validate_incoming.mjs data-src/<年份>` 校验后，执行 `python3 tools/build_data.py`。

也可以用 Python 源文件的方式：

1. 仿照 `tools/questions_2023_2025.py` 新建题目文件（题号 `id = 年份*100 + 题号`）。
2. 在 `tools/crops.py` 中登记该年题图的裁剪框和答案页的起止位置，运行生成图片与 `crops.json`。
3. 在 `tools/build_data.py` 的 `SOURCES` 中登记新文件，运行 `python3 tools/build_data.py`。

题单、目录和年份列表都会根据数据自动生成。
