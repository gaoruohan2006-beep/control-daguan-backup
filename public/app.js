/* 控制大观 · 静态版 */
(() => {
'use strict';
const $ = (s, r = document) => r.querySelector(s);
const STORE = 'control-daguan:v1';
const MARKS = { shaky: '不熟练', unknown: '不会', mastered: '掌握' };
const FONT = [85, 100, 115, 130];
const IC = {
  eye: '<svg viewBox="0 0 24 24" class="ic"><path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7S2 12 2 12z"/><circle cx="12" cy="12" r="3"/></svg>',
  book: '<svg viewBox="0 0 24 24" class="ic"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20V3H6.5A2.5 2.5 0 0 0 4 5.5v14z"/><path d="M8 7h8"/></svg>',
  star: '<svg viewBox="0 0 24 24" class="ic"><path d="m12 2 3.1 6.3 6.9 1-5 4.9 1.2 6.8L12 17.8 5.8 21l1.2-6.8-5-4.9 6.9-1z"/></svg>',
  gauge: '<svg viewBox="0 0 24 24" class="ic"><circle cx="12" cy="12" r="9"/><path d="m12 12 4-4"/></svg>',
  x: '<svg viewBox="0 0 24 24" class="ic"><circle cx="12" cy="12" r="9"/><path d="m9 9 6 6m0-6-6 6"/></svg>',
  ok: '<svg viewBox="0 0 24 24" class="ic"><circle cx="12" cy="12" r="9"/><path d="m8 12 3 3 5-6"/></svg>',
  chev: '<svg viewBox="0 0 24 24" class="ic"><path d="m9 6 6 6-6 6"/></svg>',
  check: '<svg viewBox="0 0 24 24" class="ic" style="width:12px;height:12px"><path d="m5 12 5 5 9-10"/></svg>',
};
const MARK_IC = { shaky: IC.gauge, unknown: IC.x, mastered: IC.ok };

// ---------- 存储 ----------
function loadRec() {
  try { const r = JSON.parse(localStorage.getItem(STORE) || 'null'); if (r && typeof r === 'object') return normRec(r); } catch {}
  return normRec({});
}
function normRec(r) {
  return { favorites: Array.isArray(r.favorites) ? r.favorites.map(Number) : [], marks: r.marks && typeof r.marks === 'object' ? r.marks : {},
    history: Array.isArray(r.history) ? r.history : [], mode: r.mode === 'multiple' ? 'multiple' : 'single',
    fontScale: FONT.includes(r.fontScale) ? r.fontScale : 100, collapsed: !!r.collapsed, open: r.open && typeof r.open === 'object' ? r.open : {} };
}
let rec = loadRec();
const save = () => { try { localStorage.setItem(STORE, JSON.stringify(rec)); } catch { toast('浏览器未能保存进度，本次更改未保存，请重试。'); } };
window.addEventListener('storage', e => { if (e.key === STORE) { rec = loadRec(); render(); } });

// ---------- 状态 ----------
let lib, byId = new Map(), details = new Map();
const st = { tab: 'bank', listId: 'complete', node: null, qid: null, q: '', page: 0, show: {} };

// ---------- 渲染工具 ----------
const esc = s => s.replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
function tex(src, display) {
  try { return katex.renderToString(src, { displayMode: display, throwOnError: false, strict: false }); }
  catch { return esc(src); }
}
function inline(s, hl) {
  const out = []; let i = 0;
  const re = /\$\$([\s\S]+?)\$\$|\$([^$]+?)\$|!\[([^\]]*)\]\(([^)]+)\)|\*\*(.+?)\*\*/g; let m;
  const txt = t => { let h = esc(t); if (hl) h = h.replace(new RegExp(hl.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'gi'), x => `<mark>${x}</mark>`); return h; };
  while ((m = re.exec(s))) {
    out.push(txt(s.slice(i, m.index)));
    if (m[1] != null) out.push(tex(m[1], true));
    else if (m[2] != null) out.push(tex(m[2], false));
    else if (m[4] != null) { const [alt, w] = m[3].split('|'); out.push(`<span class="fig"><img src="${esc(m[4])}" alt="${esc(alt)}" ${w ? `style="width:${+w}px"` : ''} loading="lazy" data-zoom title="单击放大图片"></span>`); }
    else out.push(`<strong>${txt(m[5])}</strong>`);
    i = re.lastIndex;
  }
  out.push(txt(s.slice(i)));
  return out.join('');
}
const md = (s, hl) => s.split(/\n\s*\n/).map(p => p.trim()).filter(Boolean).map(p => {
  const h = inline(p.replace(/\n/g, ' '), hl);
  return /^<span class="fig">[^]*<\/span>$/.test(h) ? `<div class="fig">${h.replace(/^<span class="fig">|<\/span>$/g, '')}</div>` : `<p>${h}</p>`;
}).join('');

// ---------- 题目集合 ----------
const curList = () => lib.lists.find(l => l.id === st.listId) || lib.lists[0];
function scopeIds() {
  const L = curList(); let ids = L.questionIds;
  if (st.tab === 'fav') ids = ids.filter(id => rec.favorites.includes(id));
  if (st.tab === 'retest') ids = ids.filter(id => ['shaky', 'unknown'].includes(rec.marks[id]?.state));
  if (st.q) { const k = st.q.toLowerCase(); ids = ids.filter(id => (byId.get(id).search + ' ' + (L.categoryByQuestion[id] || []).join(' ')).toLowerCase().includes(k)); }
  return ids;
}
function buildTree(ids) {
  const L = curList(), root = { kids: new Map(), ids: [] };
  for (const id of ids) for (const path of L.categoryByQuestion[id] || []) {
    let n = root; const parts = path.split(' / ');
    parts.forEach((p, i) => {
      if (!n.kids.has(p)) n.kids.set(p, { name: p, path: parts.slice(0, i + 1).join(' / '), kids: new Map(), ids: [] });
      n = n.kids.get(p); if (!n.ids.includes(id)) n.ids.push(id);
    });
  }
  const ord = lib.topicOrder;
  const sortKids = n => { n.list = [...n.kids.values()].sort((a, b) => {
    const ia = ord.indexOf(a.name), ib = ord.indexOf(b.name);
    if (ia >= 0 || ib >= 0) return (ia < 0 ? 99 : ia) - (ib < 0 ? 99 : ib);
    if (/^\d{4}$/.test(a.name) && /^\d{4}$/.test(b.name)) return b.name - a.name;
    return 0; }); n.list.forEach(sortKids); };
  sortKids(root);
  return root;
}
function flatNodes(root) { const out = []; const walk = n => n.list.forEach(k => { out.push(k); walk(k); }); walk(root); return out; }
function sectionIds(tree) {
  if (!st.node) return [];
  const n = flatNodes(tree).find(x => x.path === st.node);
  return n ? n.ids : [];
}
function topSections(tree) { return tree.list.map(n => n.path); }

// ---------- 主渲染 ----------
let tree;
function ensureSelection() {
  const ids = scopeIds(); tree = buildTree(ids);
  const all = flatNodes(tree).map(n => n.path);
  if (!st.node || !all.includes(st.node)) {
    // 优先选择包含当前题目的顶层分类
    const top = tree.list.find(n => n.ids.includes(st.qid)) || tree.list[0];
    st.node = top ? top.path : null;
  }
  const sec = sectionIds(tree);
  if (!sec.includes(st.qid)) st.qid = sec[0] ?? null;
  return sec;
}
function render() {
  document.documentElement.style.setProperty('--fs', rec.fontScale / 100);
  const sec = ensureSelection();
  // tabs
  document.querySelectorAll('#tabs button').forEach(b => b.setAttribute('aria-selected', b.dataset.tab === st.tab));
  $('#app').classList.toggle('app-collapsed', rec.collapsed && !isMobile());
  $('#tocBtn').setAttribute('aria-expanded', isMobile() ? $('#app').classList.contains('drawer-open') : !rec.collapsed);
  $('#listBtn').parentElement.hidden = st.tab !== 'bank';
  const L = curList();
  $('#listName').textContent = `${L.name} · ${L.questionIds.length} 题`;
  const node = st.node ? flatNodes(tree).find(n => n.path === st.node) : null;
  $('#sectionLabel').textContent = node ? `${st.q ? '搜索 · ' : ''}${st.tab === 'retest' ? '复测 · ' : ''}${node.name}  ${sec.length} 题` : (st.q ? `搜索「${st.q}」 0 题` : '');
  renderTree(); renderCards(sec); renderPager(sec); syncURL();
  document.querySelectorAll('#modeSeg button').forEach(b => b.classList.toggle('on', b.dataset.mode === rec.mode));
  document.querySelectorAll('#fontSeg button').forEach(b => b.classList.toggle('on', +b.dataset.font === rec.fontScale));
}
const isMobile = () => matchMedia('(max-width:900px)').matches;

function renderTree() {
  const el = $('#tree');
  const markedCount = ids => ids.filter(id => rec.marks[id]).length;
  const nodeHTML = (n, depth) => {
    const open = rec.open[n.path] ?? (n.path === st.node || (st.node || '').startsWith(n.path + ' / '));
    const hasKids = n.list.length > 0;
    const cnt = st.tab === 'bank' ? `已标记 ${markedCount(n.ids)} / ${n.ids.length}` : `${n.ids.length} 题`;
    const selMark = n.path === st.node ? IC.check : '';
    return `<div class="node ${depth === 0 ? 'top' : ''} ${open && hasKids ? 'open' : ''} ${n.path === st.node ? 'sel' : ''}" data-path="${esc(n.path)}">
      <button type="button" class="tw ${hasKids ? '' : 'leaf'}" aria-label="${open ? '收起' : '展开'}${esc(n.name)}" data-act="toggle">${IC.chev}</button>
      <button type="button" class="nm" data-act="select"><span class="t" title="${esc(n.name)}">${esc(n.name)}</span><span class="c">${selMark}${cnt}</span></button></div>
      ${hasKids && open ? `<div class="kids">${n.list.map(k => nodeHTML(k, depth + 1)).join('')}</div>` : ''}`;
  };
  el.innerHTML = tree.list.length ? tree.list.map(n => nodeHTML(n, 0)).join('') : `<div class="empty" style="padding:30px 0">${st.q ? '没有匹配的题目' : st.tab === 'fav' ? '暂无收藏题目' : st.tab === 'retest' ? '暂无复测题目' : '暂无章节'}</div>`;
}

function cardHTML(id, idx) {
  const q = byId.get(id), L = curList(), d = details.get(id);
  const paths = (L.categoryByQuestion[id] || q.categories);
  const leaf = (paths.find(p => !p.startsWith('历年真题')) || paths[0]).split(' / ').pop();
  const sh = st.show[id] || {}; const mk = rec.marks[id]?.state; const fav = rec.favorites.includes(id);
  const hl = st.q && st.q.length > 0 ? st.q : null;
  let ans = '';
  const origHTML = d && d.originalImages.length ? `<div class="orig"><div class="lab">原图解析（源文件顺序，PDF 第 ${d.answerPdfPages} 页）</div>${d.originalImages.map(o => `<img src="${o.src}" style="width:${o.w}px" alt="原图解析" loading="lazy" data-zoom title="单击放大图片">`).join('')}</div>` : '';
  const noteHTML = d && d.notes ? `<p class="note">勘误/说明：${inline(d.notes)}</p>` : '';
  if (sh.answer) {
    let body = '加载中';
    if (d) body = d.answer ? md(d.answer) : (sh.exp ? '<p class="muted">本题答案见下方「解析」中的原图。</p>' : origHTML);
    ans += `<section class="box"><h4>答案</h4><div class="body">${body}${d && !sh.exp ? noteHTML : ''}</div></section>`;
  }
  if (sh.exp) ans += `<section class="box"><h4>解析</h4><div class="body">${d ? (d.explanation ? md(d.explanation) : '') + origHTML + noteHTML : '加载中'}</div></section>`;
  const hist = rec.history.filter(h => h.id === id);
  return `<article class="card" data-id="${id}">
    <div class="meta"><span class="qno">第 ${idx + 1} 题</span><span class="src">${esc(q.source)}</span>
      <span class="pop-wrap"><button type="button" class="cat-btn" data-act="cats" aria-expanded="false" aria-label="查看完整分类路径，共 ${paths.length} 处">${esc(leaf)}</button>
      <div class="popover catpop" hidden><b>分类路径</b>${paths.map(p => `<button type="button" data-act="gocat" data-path="${esc(p)}" title="查看本分类全部题目">${esc(p)}</button>`).join('')}</div></span></div>
    <div class="stem">${md(q.stem, hl)}</div>
    <div class="actions">
      <button type="button" class="tog" data-act="answer" aria-pressed="${!!sh.answer}" aria-label="答案">${IC.eye}答案</button>
      <button type="button" class="tog" data-act="exp" aria-pressed="${!!sh.exp}" aria-label="解析">${IC.book}解析</button>
      <div class="marks">
        <button type="button" class="mk fav" data-act="fav" aria-pressed="${fav}" aria-label="${fav ? '取消收藏' : '收藏'}">${IC.star}${fav ? '已收藏' : '收藏'}</button>
        ${Object.entries(MARKS).map(([k, v]) => `<button type="button" class="mk" data-act="mark" data-mark="${k}" aria-pressed="${mk === k}" title="标记为${v}" aria-label="标记为${v}">${MARK_IC[k]}${v}</button>`).join('')}
      </div></div>
    ${mk ? `<button type="button" class="unmark" data-act="unmark">取消标记</button>` : ''}
    ${st.tab === 'retest' && hist.length ? `<details class="history"><summary>查看复测历史（${hist.length}）</summary><ul>${hist.slice().reverse().map(h => `<li>${new Date(h.at).toLocaleString('zh-CN')} · ${h.state ? MARKS[h.state] : '取消标记'}</li>`).join('')}</ul></details>` : ''}
    ${ans}</article>`;
}
function renderCards(sec) {
  const el = $('#cards');
  if (!sec.length) { el.innerHTML = `<div class="empty">${st.q ? '没有匹配的题目' : st.tab === 'fav' ? '暂无收藏题目。点题目下方的「收藏」即可加入。' : st.tab === 'retest' ? '暂无复测题目。把题目标记为「不熟练」或「不会」后会出现在这里。' : '暂无题目'}</div>`; return; }
  const ids = rec.mode === 'multiple' ? sec : [st.qid];
  ids.forEach(id => { if ((st.show[id]?.answer || st.show[id]?.exp) && !details.has(id)) loadDetail(id); });
  el.innerHTML = ids.map(id => cardHTML(id, sec.indexOf(id))).join('');
}
function renderPager(sec) {
  const prev = $('#prevBtn'), next = $('#nextBtn');
  const tops = sectionsAtDepth();
  const si = tops.indexOf(st.node);
  if (rec.mode === 'multiple') {
    $('#pos').textContent = sec.length ? `第 ${si + 1} / ${tops.length} 节 · ${sec.length} 题` : '0 / 0';
    prev.querySelector('span').textContent = '上一小节'; next.querySelector('span').textContent = '下一小节';
    prev.disabled = si <= 0; next.disabled = si < 0 || si >= tops.length - 1; return;
  }
  const i = sec.indexOf(st.qid);
  $('#pos').textContent = sec.length ? `${i + 1} / ${sec.length}` : '0 / 0';
  const atStart = i <= 0, atEnd = i >= sec.length - 1;
  prev.querySelector('span').textContent = atStart && si > 0 ? '上一小节' : '上一题';
  next.querySelector('span').textContent = atEnd && si >= 0 && si < tops.length - 1 ? '下一小节' : '下一题';
  prev.disabled = !sec.length || (atStart && si <= 0);
  next.disabled = !sec.length || (atEnd && (si < 0 || si >= tops.length - 1));
}
// 小节 = 与当前所选分类同一层级的分类（按目录顺序）
function sectionsAtDepth() {
  const depth = (st.node || '').split(' / ').length;
  return flatNodes(tree).filter(n => n.ids.length && n.path.split(' / ').length === depth).map(n => n.path);
}
function step(dir) {
  const sec = sectionIds(tree);
  const tops = sectionsAtDepth();
  const si = tops.indexOf(st.node);
  if (rec.mode === 'multiple') { const t = tops[si + dir]; if (t) { st.node = t; st.qid = null; render(); $('#main').scrollTo(0, 0); } return; }
  const i = sec.indexOf(st.qid);
  if (sec[i + dir] != null) st.qid = sec[i + dir];
  else { const t = tops[si + dir]; if (!t) return; st.node = t; const n = flatNodes(tree).find(x => x.path === t); st.qid = dir > 0 ? n.ids[0] : n.ids[n.ids.length - 1]; }
  render(); $('#main').scrollTo(0, 0);
}

// ---------- 详情（答案/解析） ----------
async function loadDetail(id) {
  if (details.has(id)) return;
  try { const r = await fetch(`data/questions/${id}.json`); if (!r.ok) throw 0; details.set(id, await r.json()); render(); }
  catch { toast('静态文件读取失败，请重试。'); }
}

// ---------- URL ----------
function syncURL() {
  const u = new URL(location.href); const p = u.searchParams;
  p.set('list', st.listId); st.qid != null ? p.set('question', st.qid) : p.delete('question');
  st.tab !== 'bank' ? p.set('tab', st.tab) : p.delete('tab');
  st.q ? p.set('q', st.q) : p.delete('q');
  st.node ? p.set('section', st.node) : p.delete('section');
  if (u.href !== location.href) history.replaceState(null, '', u);
}
function readURL() {
  const p = new URLSearchParams(location.search);
  st.listId = lib.lists.some(l => l.id === p.get('list')) ? p.get('list') : 'complete';
  st.tab = ['bank', 'fav', 'retest'].includes(p.get('tab')) ? p.get('tab') : 'bank';
  st.qid = p.get('question') ? Number(p.get('question')) : null;
  st.q = p.get('q') || ''; $('#search').value = st.q;
  st.node = p.get('section') || null;
  if (st.qid != null && !st.node) {
    const paths = curList().categoryByQuestion[st.qid]; if (paths) st.node = paths[0].split(' / ')[0];
  }
}

// ---------- 记录导入导出 ----------
function setMsg(t, err) { const m = $('#setMsg'); m.textContent = t; m.classList.toggle('err', !!err); }
function exportJSON() {
  const data = { app: 'control-daguan', version: 1, exportedAt: new Date().toISOString(), favorites: rec.favorites, marks: rec.marks, history: rec.history };
  const a = document.createElement('a'); a.href = URL.createObjectURL(new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' }));
  a.download = `control-daguan-records-${data.exportedAt.slice(0, 10)}.json`; $('#settings').appendChild(a); a.click(); a.remove();
  setMsg('已导出学习记录 JSON。');
}
function applyImport(d) {
  if (!d || d.app !== 'control-daguan' || !Array.isArray(d.favorites) || typeof d.marks !== 'object') throw new Error('不是有效的控制大观记录文件，请重新导出 JSON。');
  const known = id => byId.has(Number(id));
  rec.favorites = [...new Set([...rec.favorites, ...d.favorites.map(Number).filter(known)])];
  for (const [k, v] of Object.entries(d.marks)) if (known(k) && v && MARKS[v.state] && (!rec.marks[k] || (v.at || 0) >= (rec.marks[k].at || 0))) rec.marks[k] = v;
  if (Array.isArray(d.history)) { const seen = new Set(rec.history.map(h => h.id + ':' + h.at)); d.history.forEach(h => { if (known(h.id) && !seen.has(h.id + ':' + h.at)) rec.history.push(h); }); rec.history.sort((a, b) => a.at - b.at); }
  save(); render();
}
// 记录码：CG1-<分段序号>/<总段数>-<base64url>-<校验>，校验为 FNV-1a 32 位
const fnv = s => { let h = 0x811c9dc5; for (let i = 0; i < s.length; i++) { h ^= s.charCodeAt(i); h = Math.imul(h, 0x01000193) >>> 0; } return h.toString(36); };
const b64 = s => btoa(unescape(encodeURIComponent(s))).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
const unb64 = s => decodeURIComponent(escape(atob(s.replace(/-/g, '+').replace(/_/g, '/'))));
function genCode() {
  const payload = b64(JSON.stringify({ app: 'control-daguan', version: 1, favorites: rec.favorites, marks: rec.marks, history: rec.history.slice(-200) }));
  const batch = Date.now().toString(36), size = 400, parts = [];
  for (let i = 0; i < payload.length; i += size) parts.push(payload.slice(i, i + size));
  const code = parts.map((p, i) => `CG1-${batch}-${i + 1}/${parts.length}-${p}-${fnv(batch + i + p)}`).join('\n');
  $('#codeInput').value = code; $('#importCodeBtn').disabled = false;
  navigator.clipboard?.writeText(code).then(() => setMsg(`已生成 ${parts.length} 段记录码并复制到剪贴板。`), () => setMsg(`已生成 ${parts.length} 段记录码，请手动复制。`));
}
function importCode() {
  const segs = [...$('#codeInput').value.matchAll(/CG1-([0-9a-z]+)-(\d+)\/(\d+)-([A-Za-z0-9_-]+)-([0-9a-z]+)/g)];
  try {
    if (!segs.length) throw new Error('没有找到记录码，请粘贴以 CG1 开头的全部分段。');
    const batch = segs[0][1], total = +segs[0][3];
    if (segs.some(s => s[1] !== batch)) throw new Error('混入了不同批次的记录码，请使用同一组的全部分段。');
    const parts = []; segs.forEach(s => { if (fnv(batch + (s[2] - 1) + s[4]) !== s[5]) throw new Error(`第 ${s[2]} 段校验失败，请重新复制。`); parts[s[2] - 1] = s[4]; });
    if (parts.filter(Boolean).length !== total) throw new Error(`记录码不完整：需要 ${total} 段，只找到 ${parts.filter(Boolean).length} 段。`);
    applyImport(JSON.parse(unb64(parts.join('')))); setMsg('记录码校验通过，已导入。'); $('#codeInput').value = ''; $('#importCodeBtn').disabled = true;
  } catch (e) { setMsg(e.message || '记录码无效。', true); }
}

// ---------- 交互 ----------
let toastT; function toast(t) { const el = $('#toast'); el.textContent = t; el.hidden = false; clearTimeout(toastT); toastT = setTimeout(() => el.hidden = true, 2200); }
function closePops(except) { document.querySelectorAll('.popover').forEach(p => { if (p !== except && !p.contains(except)) { p.hidden = true; const b = p.previousElementSibling; if (b?.hasAttribute('aria-expanded')) b.setAttribute('aria-expanded', 'false'); } }); }
function setMark(id, state) {
  const prev = rec.marks[id]?.state;
  if (state) rec.marks[id] = { state, at: Date.now() }; else delete rec.marks[id];
  rec.history.push({ id, state: state || null, at: Date.now() }); save();
  if (st.tab === 'retest' && !['shaky', 'unknown'].includes(state) && prev) {
    const sec = sectionIds(tree); const i = sec.indexOf(id); const nxt = sec[i + 1] ?? sec[i - 1] ?? null;
    st.qid = nxt; toast(state === 'mastered' ? '已掌握，已移出复测' : '已取消标记，已移出复测');
  }
  render();
}
function bind() {
  $('#tabs').addEventListener('click', e => { const b = e.target.closest('button'); if (!b) return; st.tab = b.dataset.tab; st.node = null; render(); });
  $('#brand').addEventListener('click', e => { e.preventDefault(); Object.assign(st, { tab: 'bank', listId: 'complete', node: null, qid: null, q: '' }); $('#search').value = ''; render(); $('#main').scrollTo(0, 0); });
  $('#tocBtn').addEventListener('click', () => { if (isMobile()) $('#app').classList.toggle('drawer-open'); else { rec.collapsed = !rec.collapsed; save(); } render(); });
  $('#scrim').addEventListener('click', () => { $('#app').classList.remove('drawer-open'); render(); });
  $('#gearBtn').addEventListener('click', e => { e.stopPropagation(); const p = $('#settings'); const open = p.hidden; closePops(); p.hidden = !open; $('#gearBtn').setAttribute('aria-expanded', open); setMsg(''); });
  $('#listBtn').addEventListener('click', e => {
    e.stopPropagation(); const p = $('#listPop'); const open = p.hidden; closePops(); p.hidden = !open; $('#listBtn').setAttribute('aria-expanded', open);
    p.innerHTML = lib.lists.map(l => `<button type="button" role="option" data-list="${l.id}" aria-selected="${l.id === st.listId}"><span>${esc(l.name)} · ${l.questionIds.length} 题</span>${l.id === st.listId ? IC.check : ''}</button>`).join('');
  });
  $('#listPop').addEventListener('click', e => { const b = e.target.closest('button[data-list]'); if (!b) return; st.listId = b.dataset.list; st.node = null; st.qid = null; closePops(); render(); $('#main').scrollTo(0, 0); });
  $('#settings').addEventListener('click', e => {
    e.stopPropagation(); const b = e.target.closest('button'); if (!b) return;
    if (b.dataset.mode) { rec.mode = b.dataset.mode; save(); render(); }
    if (b.dataset.font) { rec.fontScale = +b.dataset.font; save(); render(); }
  });
  $('#exportBtn').addEventListener('click', exportJSON);
  $('#genCodeBtn').addEventListener('click', genCode);
  $('#codeInput').addEventListener('input', e => $('#importCodeBtn').disabled = !e.target.value.trim());
  $('#importCodeBtn').addEventListener('click', importCode);
  $('#importJsonBtn').addEventListener('click', () => $('#importFile').click());
  $('#importFile').addEventListener('change', async e => {
    const f = e.target.files[0]; e.target.value = ''; if (!f) return;
    if (f.size > 10 * 1024 * 1024) return setMsg('记录文件超过 10 MB，请选择导出的学习记录 JSON。', true);
    try { applyImport(JSON.parse(await f.text())); setMsg('已导入学习记录 JSON。'); } catch (err) { setMsg(err instanceof SyntaxError ? '无法读取 JSON，请重新选择完整的学习记录文件。' : err.message, true); }
  });
  let sT; $('#search').addEventListener('input', e => { clearTimeout(sT); sT = setTimeout(() => { st.q = e.target.value.trim(); st.node = null; render(); }, 150); });
  $('#tree').addEventListener('click', e => {
    const b = e.target.closest('button[data-act]'); if (!b) return; const path = b.closest('.node').dataset.path;
    if (b.dataset.act === 'toggle') { const n = b.closest('.node'); rec.open[path] = !n.classList.contains('open'); save(); renderTree(); return; }
    st.node = path; st.qid = null; rec.open[path] = true; save(); if (isMobile()) $('#app').classList.remove('drawer-open'); render(); $('#main').scrollTo(0, 0);
  });
  $('#cards').addEventListener('click', e => {
    const img = e.target.closest('img[data-zoom]'); if (img) { $('#lbImg').src = img.src; $('#lightbox').hidden = false; return; }
    const b = e.target.closest('button[data-act]'); if (!b) return; const id = Number(b.closest('.card').dataset.id);
    const sh = st.show[id] = st.show[id] || {};
    switch (b.dataset.act) {
      case 'answer': sh.answer = !sh.answer; break;
      case 'exp': sh.exp = !sh.exp; break;
      case 'fav': { const i = rec.favorites.indexOf(id); i >= 0 ? rec.favorites.splice(i, 1) : rec.favorites.push(id); save(); toast(i >= 0 ? '已取消收藏' : '已收藏'); if (st.tab === 'fav' && i >= 0) { const sec = sectionIds(tree); const k = sec.indexOf(id); st.qid = sec[k + 1] ?? sec[k - 1] ?? null; } break; }
      case 'mark': return setMark(id, rec.marks[id]?.state === b.dataset.mark ? rec.marks[id].state : b.dataset.mark);
      case 'unmark': return setMark(id, null);
      case 'cats': { e.stopPropagation(); const p = b.nextElementSibling; const open = p.hidden; closePops(); p.hidden = !open; b.setAttribute('aria-expanded', open); return; }
      case 'gocat': st.tab = 'bank'; st.node = b.dataset.path; st.qid = id; rec.open[b.dataset.path.split(' / ')[0]] = true; save(); closePops(); break;
    }
    render();
  });
  $('#prevBtn').addEventListener('click', () => step(-1));
  $('#nextBtn').addEventListener('click', () => step(1));
  $('#lightbox').addEventListener('click', () => $('#lightbox').hidden = true);
  document.addEventListener('click', e => { if (!e.target.closest('.popover')) closePops(); });
  document.addEventListener('keydown', e => {
    if (e.key === 'Escape') { $('#lightbox').hidden = true; closePops(); return; }
    if (e.target.matches('input,textarea')) return;
    if (e.key === 'ArrowRight') step(1); if (e.key === 'ArrowLeft') step(-1);
  });
  addEventListener('resize', () => render());
  addEventListener('popstate', () => { readURL(); render(); });
}

// ---------- 启动 ----------
fetch('data/library.json').then(r => { if (!r.ok) throw 0; return r.json(); }).then(d => {
  lib = d; d.questions.forEach(q => byId.set(q.id, q));
  readURL(); bind(); render();
}).catch(() => { $('#cards').innerHTML = '<div class="empty">静态文件读取失败，请刷新重试。</div>'; });
})();
