#!/usr/bin/env python3
"""控制大观 裁图工具（共享给所有贡献者）。坐标一律用 PDF 点(pt)，页面 595×842，原点左上。

  python3 cdg_crop.py grid <页码>                     # 输出带 50pt 坐标网格的页面图，方便量框
  python3 cdg_crop.py fig <页码> <x0> <y0> <x1> <y1> <输出.png>   # 裁题图，自动去白边
  python3 cdg_crop.py ans <年份> <输出目录>            # 按“【万人教育解析/解题】”标记自动切分该年答案，输出 ans-<题号>-<k>.png 并打印 JSON

依赖：pdftoppm/pdftotext(poppler)、Pillow、numpy。去水印版 PDF：/workspace/cdg/clean.pdf（水印图层已透明）。
"""
import tempfile, sys, os, re, json, subprocess
from PIL import Image, ImageDraw
import numpy as np
SRC = '/workspace/cdg/book.pdf'      # 原 PDF（取文字坐标）
CLEAN = '/workspace/cdg/clean.pdf'   # 去水印 PDF（取图像）
CACHE = '/workspace/cdg/pages'; os.makedirs(CACHE, exist_ok=True)
DPI = 200; S = DPI / 72
TOP, BOT = 57, 764                   # 页眉线以下 / 页脚以上（pt）
ANS_START = {2011:58,2012:68,2013:77,2014:87,2015:96,2016:105,2017:115,2018:123,2019:132,2020:141,
             2021:150,2022:162,2023:170,2024:181,2025:192,2026:203}
def render(p):
    f = f'{CACHE}/p-{p:03d}.png'
    if not os.path.exists(f):
        # 每次渲染用独立临时目录 + 原子 rename，避免并发渲染互相覆盖（曾导致缓存页串页）
        with tempfile.TemporaryDirectory(dir=CACHE, prefix='.render-') as td:
            subprocess.run(['pdftoppm','-r',str(DPI),'-png','-singlefile','-f',str(p),'-l',str(p),CLEAN,f'{td}/page'],check=True)
            os.replace(f'{td}/page.png', f)
    return Image.open(f).convert('RGB')
def words(p):
    out = subprocess.run(['pdftotext','-bbox','-f',str(p),'-l',str(p),SRC,'-'],capture_output=True,text=True).stdout
    return [(float(a),float(b),float(c),float(d),t) for a,b,c,d,t in re.findall(r'<word xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">([^<]*)</word>',out)]
def trim(im, pad=12, thr=235):
    a = np.asarray(im.convert('L')) < thr
    ys = np.where(a.any(1))[0]; xs = np.where(a.any(0))[0]
    if not len(ys): return None
    return im.crop((max(0,xs[0]-pad),max(0,ys[0]-pad),min(im.width,xs[-1]+pad),min(im.height,ys[-1]+pad)))
def fig(p, x0, y0, x1, y1, out):
    im = trim(render(p).crop(tuple(int(v*S) for v in (x0,y0,x1,y1))))
    im.save(out, optimize=True); print(out, im.size)
def grid(p):
    im = render(p); d = ImageDraw.Draw(im)
    for v in range(0, 850, 50):
        d.line([(v*S,0),(v*S,im.height)], fill=(255,120,120), width=1); d.line([(0,v*S),(im.width,v*S)], fill=(255,120,120), width=1)
        d.text((v*S+2,2), str(v), fill='red'); d.text((2,v*S+2), str(v), fill='red')
    out = f'{CACHE}/grid-{p:03d}.png'; im.resize((im.width//2, im.height//2)).save(out); print(out)
def markers(p):
    ws = words(p); res = []
    for i,(x0,y0,x1,y1,t) in enumerate(ws):
        if '【' in t and '万人教育' in ''.join(w[4] for w in ws[i:i+9]).replace(' ',''):
            res.append(y0)
    title = [w[1] for i,w in enumerate(ws) if '答案' in w[4] and '试题' in ''.join(x[4] for x in ws[max(0,i-3):i+1])]
    return sorted(set(round(y,1) for y in res)), (title[0] if title else None)
def whiteout(im, p):
    dr = ImageDraw.Draw(im); ws = words(p); i = 0
    while i < len(ws):
        if '【' in ws[i][4]:
            j = i
            while j < len(ws) and '】' not in ws[j][4] and j - i < 12: j += 1
            for a,b,c,d,t in ws[i:j+1]:
                n = len(t); s = max(t.find('【'),0); e = t.find('】'); e = n-1 if e < 0 else e
                cw = d - b   # 全角字符宽 ≈ 字号（词框高度），不按词宽平均（词内含半角时会偏小）
                dr.rectangle([(a+cw*s)*S-2,b*S-2,(max(c, a+cw*n) if e == n-1 else a+cw*(e+1))*S+2,d*S+3], fill='white')
            i = j + 1
        else: i += 1
    return im
def safe_cut(p, y_pt, minband=25):
    """从标记顶端向上找最近的 ≥minband px 空白带，在其中点切分（避免把上一题末行切进下一题）"""
    g = np.asarray(render(p).convert('L'))[:, 150:1654-150] < 235
    blank = ~g.any(1); y = int(y_pt*S) - 2; run = 0
    while y > TOP*S:
        if blank[y]:
            run += 1
            if run >= minband: return (y + run//2) / S
        else: run = 0
        y -= 1
    return TOP
def ans(year, outdir):
    os.makedirs(outdir, exist_ok=True)
    p0, pend = ANS_START[year], ANS_START[year+1]
    bounds = []
    for p in range(p0, pend + 1):
        ms, title = markers(p)
        if p == pend:  # 下一年的首页：只取标题位置作为终点
            bounds.append((p, safe_cut(p, title) if title else 0)); break
        bounds += [(p, safe_cut(p, y)) for y in ms]
    res = {}
    for q in range(len(bounds) - 1):
        (pa, ya), (pb, yb) = bounds[q], bounds[q+1]; segs = []
        for p in range(pa, pb + 1):
            top = max(TOP, ya) if p == pa else TOP
            bot = yb if p == pb else BOT
            if p == pb and yb == 0: continue
            if bot - top < 8: continue
            im = whiteout(render(p), p).crop((150, int(top*S), 1654-150, int(bot*S)))
            t = trim(im, pad=10)
            if t is None or t.height < 30: continue
            name = f'ans-{q+1}-{len(segs)+1}.png'; t.save(os.path.join(outdir, name), optimize=True); segs.append(name)
        res[str(q+1)] = segs
    print(json.dumps(res, ensure_ascii=False)); return res
if __name__ == '__main__':
    c = sys.argv[1]
    if c == 'grid': grid(int(sys.argv[2]))
    elif c == 'fig': fig(int(sys.argv[2]), *map(float, sys.argv[3:7]), sys.argv[7])
    elif c == 'ans': ans(int(sys.argv[2]), sys.argv[3])
