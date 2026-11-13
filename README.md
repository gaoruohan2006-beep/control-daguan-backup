# 控制大观 · 985 高校自动控制原理题库

**[打开刷题网站](https://gaoruohan2006-beep.github.io/control-daguan-backup/)**

默认按专题和考点刷题，亦可在题单菜单中切换到「按院校」。题卡支持收藏、笔记和间隔复习。

已录入的题目来自考研题目及参考答案汇编，保留学校、年份、科目和 PDF 页码。题面和解析使用 LaTeX 数学公式，配图为重绘 SVG。题库持续补录，以网站当前收录为准。

## 本地运行

```powershell
python -m http.server 8765 --bind 127.0.0.1 -d public
```

打开 [本地题库](http://127.0.0.1:8765/)。

审核通过的题卡存于 `data-src/reviewed/`，配图存于 `public/img/reviewed/`。修改后运行 `python tools/build_reviewed_bank.py` 更新网站数据。原版仓库历史保存在 Git 的提交记录中。
