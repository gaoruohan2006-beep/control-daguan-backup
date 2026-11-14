# 控制大观 · 985 与 211 高校自动控制原理题库

**[打开刷题网站](https://gaoruohan2006-beep.github.io/control-daguan-backup/)**

默认按专题和考点刷题，亦可在题单菜单中切换到「按院校」。题卡支持收藏、笔记和间隔复习。现代控制理论中的状态空间方法和最优控制分别设有专题。

已从汇编中 24 所 985 高校的 79 份试卷选录题目。211 专篇所列的 29 所院校、91 份 2023–2025 年试卷均已有题目入库。可通过「按院校」或搜索「211」查看新增题目。题面和解析使用 LaTeX。框图、工程示意图及函数曲线以 SVG 显示，可点击放大。同一道题只显示一张卡片。

## 本地运行

```powershell
python -m http.server 8765 --bind 127.0.0.1 -d public
```

打开 [本地题库](http://127.0.0.1:8765/)。

审核通过的题卡存于 `data-src/reviewed/`，配图存于 `public/img/reviewed/`。修改后运行 `python tools/build_reviewed_bank.py` 更新网站数据。原版仓库历史保存在 Git 的提交记录中。
