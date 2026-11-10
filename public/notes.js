/* 控制大观 · 题目笔记：Markdown（marked，GFM）+ KaTeX 公式 + DOMPurify 清洗；纯函数 normalize/merge 供同步与测试调用。 */
(() => {
'use strict';
const MAX = 50000; // 单题笔记上限（字符）
const esc = s => String(s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const tex = (src, display) => {
  try { return katex.renderToString(src, { displayMode: display, throwOnError: false, strict: false, trust: false, maxExpand: 500 }); }
  catch { return `<code>${esc(src)}</code>`; }
};
// $$…$$ 独占一行时为块级公式；行内 $…$ 与 $$…$$ 由行内扩展处理。代码块/行内代码里的 $ 不会被当成公式。
const mathBlock = {
  name: 'mathBlock', level: 'block',
  start(src) { const m = /(^|\n)[ \t]{0,3}\$\$/.exec(src); return m ? m.index + m[1].length : undefined; },
  tokenizer(src) { const m = /^[ \t]{0,3}\$\$([\s\S]+?)\$\$[ \t]*(?:\n+|$)/.exec(src); if (m) return { type: 'mathBlock', raw: m[0], text: m[1].trim() }; },
  renderer(t) { return `<div class="math-block">${tex(t.text, true)}</div>\n`; },
};
const mathInline = {
  name: 'mathInline', level: 'inline',
  start(src) { const i = src.indexOf('$'); return i < 0 ? undefined : i; },
  tokenizer(src) {
    let m = /^\$\$([\s\S]+?)\$\$/.exec(src);
    if (m) return { type: 'mathInline', raw: m[0], text: m[1].trim(), display: true };
    m = /^\$(?!\s)((?:\\.|[^\\$\n])+?)(?<!\s)\$(?!\d)/.exec(src);
    if (m) return { type: 'mathInline', raw: m[0], text: m[1], display: false };
  },
  renderer(t) { return tex(t.text, t.display); },
};
const md = new marked.Marked({ gfm: true, breaks: true });
md.use({ extensions: [mathBlock, mathInline], renderer: { html: t => esc(t.text) } }); // 原始 HTML 一律按文本显示
const purify = DOMPurify;
purify.addHook('afterSanitizeAttributes', n => {
  if (n.tagName === 'A' && n.getAttribute('href')) { n.setAttribute('target', '_blank'); n.setAttribute('rel', 'noopener noreferrer nofollow'); }
  if (n.tagName === 'IMG') { n.setAttribute('loading', 'lazy'); n.setAttribute('referrerpolicy', 'no-referrer'); }
});
const SAFE = { USE_PROFILES: { html: true, svg: true, mathMl: true }, ADD_ATTR: ['target'], FORBID_TAGS: ['style', 'form', 'input', 'button', 'textarea', 'select', 'iframe'], FORBID_ATTR: ['id', 'name'] };
/** Markdown → 已清洗的 HTML */
function render(text) {
  if (!text || !text.trim()) return '';
  let html;
  try { html = md.parse(text); } catch { html = `<pre>${esc(text)}</pre>`; }
  return purify.sanitize(html, SAFE);
}
// ---------- 数据 ----------
// notes: { [题号]: { text, at } }；text 为空表示已删除（保留时间戳，让删除也能同步到其他设备）
function normalize(n) {
  const out = {};
  if (!n || typeof n !== 'object') return out;
  for (const [k, v] of Object.entries(n)) {
    if (!/^\d+$/.test(k) || !v || typeof v.text !== 'string') continue;
    const at = +v.at; if (!(at > 0)) continue;
    out[k] = { text: v.text.slice(0, MAX), at };
  }
  return out;
}
/** 逐题取 at 较新的一方；时间相同按内容决出，保证交换律。返回新对象。 */
function merge(a, b) {
  a = normalize(a); b = normalize(b);
  const out = {};
  for (const k of new Set([...Object.keys(a), ...Object.keys(b)])) {
    const x = a[k], y = b[k];
    out[k] = !x ? y : !y ? x : y.at > x.at || (y.at === x.at && y.text > x.text) ? y : x;
  }
  return out;
}
const has = (notes, id) => !!notes?.[id]?.text?.trim();
window.CDGNotes = { render, normalize, merge, has, MAX };
})();
