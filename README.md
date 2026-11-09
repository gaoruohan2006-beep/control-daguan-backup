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

| 年份 | 题数 | 含图题 | 有答案/解析 |
| ---- | ---- | ------ | ----------- |
| 2025 | 8 | 4 | 8 |
| 2024 | 8 | 6 | 8 |
| 2023 | 8 | 4 | 8 |

专题：建模、时域分析、根轨迹、频域分析、校正、离散系统、非线性系统、状态空间。

## 目录结构

```
public/                 # 静态站点根目录（直接部署）
  index.html app.js app.css
  vendor/katex/         # 本地 KaTeX，离线可用
  data/library.json     # 题单、分类、题干
  data/questions/<id>.json   # 答案、文字解析、原图解析列表
  img/                  # 题图与原图解析（已去除水印和页眉页脚）
tools/
  questions_2023_2025.py    # 题目数据（Markdown + LaTeX）
  crops.py / crops.json     # 从 PDF 页面裁剪题图与解析图
  build_data.py             # 生成 public/data
  verify.py                 # Playwright 全控件点击验收
.github/workflows/pages.yml # 推送 main 后自动部署到 GitHub Pages
```

## 本地运行

```bash
python3 -m http.server 8765 -d public
# 打开 http://localhost:8765/
python3 tools/verify.py http://localhost:8765/   # 可选：自动验收
```

## 追加年份

1. 仿照 `tools/questions_2023_2025.py` 新建题目文件（题号 `id = 年份*100 + 题号`）。
2. 在 `tools/crops.py` 中登记该年题图的裁剪框和答案页的起止位置，运行生成图片与 `crops.json`。
3. 在 `tools/build_data.py` 的 `SOURCES` 中登记新文件，运行 `python3 tools/build_data.py`。

题单、目录和年份列表都会根据数据自动生成。
