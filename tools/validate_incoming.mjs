// 校验 incoming/<年份>/questions.json（或 data-src/<年份>）：结构、图片、KaTeX
// 用法: node tools/validate_incoming.mjs incoming/2017
import fs from 'node:fs'; import path from 'node:path'; import katex from 'katex';
const TOPICS = ['建模','时域分析','根轨迹','频域分析','校正','离散系统','非线性系统','状态空间'];
const dir = process.argv[2]; const errs = [], warns = [];
let j; try { j = JSON.parse(fs.readFileSync(path.join(dir, 'questions.json'), 'utf8')); } catch (e) { console.log('FATAL', e.message); process.exit(2); }
if (!Number.isInteger(j.year)) errs.push('year 缺失');
const nos = j.questions.map(q => q.no);
nos.forEach((n, i) => { if (n !== i + 1) errs.push(`题号不连续: 第 ${i + 1} 个是 ${n}`); });
const mathOf = s => [...s.matchAll(/\$\$([\s\S]+?)\$\$|\$([^$]+?)\$/g)].map(m => [m[1] ?? m[2], !!m[1]]);
for (const q of j.questions) {
  const tag = `${j.year}-${q.no}`;
  for (const k of ['no','cats','stem','figures','answerImages']) if (!(k in q)) errs.push(`${tag} 缺字段 ${k}`);
  (q.cats || []).forEach(c => { if (!TOPICS.includes(c.split(' / ')[0])) errs.push(`${tag} 专题非法: ${c}`); if (c.startsWith('历年真题')) errs.push(`${tag} cats 不应含 历年真题`); });
  if (!q.cats?.length) errs.push(`${tag} cats 为空`);
  const ph = [...(q.stem || '').matchAll(/\[\[fig:(\d+)\]\]/g)].map(m => +m[1]);
  if (ph.length !== (q.figures || []).length) errs.push(`${tag} 占位符 ${ph.length} ≠ figures ${q.figures?.length}`);
  for (const f of [...(q.figures || []), ...(q.answerImages || [])]) if (!fs.existsSync(path.join(dir, f))) errs.push(`${tag} 图片不存在 ${f}`);
  if (!q.answerImages?.length) errs.push(`${tag} 没有答案图`);
  for (const [src, disp] of mathOf((q.stem || '') + '\n' + (q.answer || '') + '\n' + (q.explanation || ''))) {
    try { katex.renderToString(src, { displayMode: disp, throwOnError: true, strict: false }); } catch (e) { errs.push(`${tag} KaTeX: ${e.message.slice(0, 90)}`); }
  }
  const stripped = (q.stem || '').replace(/\$\$[\s\S]+?\$\$|\$[^$]+?\$/g, '');
  if (/[\u{1D400}-\u{1D7FF}]|ω|ζ|σ|∞|→/u.test(stripped)) warns.push(`${tag} 公式外有数学符号（可能是 pdftotext 原样粘贴）: ${stripped.match(/.{0,8}([\u{1D400}-\u{1D7FF}]|ω|ζ|σ|∞|→).{0,8}/u)?.[0]}`);
  if (/万人教育|小白学长|公众号|QQ|kongzhiwyz/.test(q.stem)) errs.push(`${tag} 题干含广告`);
}
console.log(JSON.stringify({ dir, year: j.year, questions: j.questions.length, errors: errs, warnings: warns }, null, 1));
process.exit(errs.length ? 1 : 0);
