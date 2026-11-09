/* 控制大观 · 本地存储（IndexedDB）与 GitHub Gist 同步。纯函数部分（merge）供测试直接调用。 */
(() => {
'use strict';
// ---------- IndexedDB ----------
const idb = window.idbKeyval;
const kv = idb.createStore('control-daguan', 'kv');
const CDGStore = {
  get: k => idb.get(k, kv), set: (k, v) => idb.set(k, v, kv), del: k => idb.del(k, kv), keys: () => idb.keys(kv),
};

// ---------- 合并 ----------
// 每题的「最后更新时间」：rec.updated[id]；旧数据没有时用标记时间/最近复习时间推算
const ts = (r, id) => Math.max(+(r.updated?.[id]) || 0, +(r.marks?.[id]?.at) || 0, Date.parse(r.srs?.[id]?.card?.last_review || '') || 0);
const sortObj = v => Array.isArray(v) ? v.map(sortObj) : v && typeof v === 'object' ? Object.fromEntries(Object.keys(v).sort().map(k => [k, sortObj(v[k])])) : v;
const canon = v => JSON.stringify(sortObj(v));
const unionLogs = (...lists) => {
  const m = new Map(); lists.flat().forEach(l => { if (l && l.id && !m.has(l.id)) m.set(l.id, l); });
  return [...m.values()].sort((x, y) => Date.parse(x.review) - Date.parse(y.review) || (x.id < y.id ? -1 : 1));
};
/** 合并本地与远端记录：逐题取最后更新的一方（收藏、标记、FSRS 卡片），复习日志按 id 取并集；
 *  胜出方已删除复习卡片（重置）时结果也不含卡片。返回新对象，不修改入参。界面偏好（模式、字号等）沿用 local。 */
function merge(local, remote) {
  const a = local || {}, b = remote || {};
  const ids = new Set();
  for (const r of [a, b]) {
    Object.keys(r.updated || {}).forEach(k => ids.add(String(k))); Object.keys(r.marks || {}).forEach(k => ids.add(String(k)));
    Object.keys(r.srs || {}).forEach(k => ids.add(String(k))); (r.favorites || []).forEach(k => ids.add(String(k)));
  }
  const out = { ...a, favorites: [], marks: {}, srs: {}, updated: {} };
  for (const id of [...ids].sort()) {
    const ta = ts(a, id), tb = ts(b, id), w = tb > ta ? b : a;
    if ((w.favorites || []).map(String).includes(id)) out.favorites.push(Number(id));
    if (w.marks?.[id]) out.marks[id] = w.marks[id];
    if (w.srs?.[id]) out.srs[id] = { card: w.srs[id].card, logs: unionLogs(a.srs?.[id]?.logs || [], b.srs?.[id]?.logs || []) };
    const t = Math.max(ta, tb); if (t) out.updated[id] = t;
  }
  const hk = h => `${h.id}:${h.at}:${h.state}`; const hm = new Map();
  [...(a.history || []), ...(b.history || [])].forEach(h => { if (h && !hm.has(hk(h))) hm.set(hk(h), h); });
  out.history = [...hm.values()].sort((x, y) => x.at - y.at);
  const ra = +a.retentionAt || 0, rb = +b.retentionAt || 0;
  out.retention = rb > ra ? b.retention : (a.retention ?? b.retention); out.retentionAt = Math.max(ra, rb);
  return out;
}
const SYNC_KEYS = ['favorites', 'marks', 'srs', 'history', 'updated', 'retention', 'retentionAt'];
const syncPart = r => Object.fromEntries(SYNC_KEYS.map(k => [k, r[k]]));

// ---------- GitHub Gist ----------
const FILE = 'control-daguan-progress.json', API = 'https://api.github.com';
class SyncError extends Error { constructor(msg, kind) { super(msg); this.kind = kind; } }
class GistSync {
  /** opts: getLocal() → rec；applyMerged(rec)；onStatus(cfg)；fetch（测试可替换） */
  constructor(opts) { Object.assign(this, { fetch: (...a) => fetch(...a) }, opts); this.cfg = null; this.busy = null; this.timer = null; this.pending = false; }
  async init() { this.cfg = (await CDGStore.get('gist')) || null; this.emit(); return this.cfg; }
  get connected() { return !!this.cfg?.token; }
  async saveCfg(p) { this.cfg = { ...(this.cfg || {}), ...p }; await CDGStore.set('gist', this.cfg); this.emit(); }
  emit() { this.onStatus?.(this.cfg, this.busy != null, this.pending); }
  async api(path, init = {}) {
    let r;
    try {
      r = await this.fetch(API + path, { ...init, headers: { Accept: 'application/vnd.github+json', 'X-GitHub-Api-Version': '2022-11-28', Authorization: `Bearer ${this.cfg.token}`, ...(init.body ? { 'Content-Type': 'application/json' } : {}) } });
    } catch { throw new SyncError('网络连接失败，稍后会自动重试。', 'offline'); }
    if (r.status === 401) throw new SyncError('令牌无效或已过期，请重新粘贴 gist 令牌。', 'auth');
    if (r.status === 403 || r.status === 429) {
      const left = r.headers.get('x-ratelimit-remaining');
      throw new SyncError(left === '0' ? 'GitHub API 调用次数已用完，请稍后再同步。' : '令牌没有 gist 权限（需要 gist 读写）。', left === '0' ? 'rate' : 'auth');
    }
    if (r.status === 404) throw new SyncError('找不到同步用的 Gist。', 'notfound');
    if (!r.ok) throw new SyncError(`GitHub 返回错误 ${r.status}，请稍后重试。`, 'http');
    const scopes = r.headers.get('x-oauth-scopes');
    if (scopes != null && this.cfg) this.cfg.scopes = scopes;
    return r.status === 204 ? null : r.json();
  }
  async findOrCreate() {
    for (let page = 1; page <= 10; page++) {
      const list = await this.api(`/gists?per_page=100&page=${page}`);
      const g = list.find(x => x.files && x.files[FILE]);
      if (g) return g.id;
      if (list.length < 100) break;
    }
    const g = await this.api('/gists', { method: 'POST', body: JSON.stringify({ description: '控制大观 学习进度同步（自动生成，请勿公开）', public: false, files: { [FILE]: { content: JSON.stringify(this.payload(this.getLocal()), null, 1) } } }) });
    return g.id;
  }
  payload(rec) { return { app: 'control-daguan', kind: 'progress', version: 3, savedAt: new Date().toISOString(), ...syncPart(rec) }; }
  async readRemote() {
    const g = await this.api(`/gists/${this.cfg.gistId}`);
    const f = g.files?.[FILE]; if (!f) throw new SyncError('Gist 中没有进度文件。', 'notfound');
    let text = f.content;
    if (f.truncated && f.raw_url) { const r = await this.fetch(f.raw_url); text = await r.text(); }
    try { const d = JSON.parse(text || '{}'); return d && d.app === 'control-daguan' ? d : {}; } catch { return {}; }
  }
  /** 连接：保存令牌 → 查找或创建私密 Gist → 立即同步 */
  async connect(token) {
    token = (token || '').trim();
    if (!/^(gh[pousr]_|github_pat_)[A-Za-z0-9_]{20,}$/.test(token)) throw new SyncError('这不像 GitHub 令牌（应以 ghp_ 或 github_pat_ 开头）。', 'input');
    await this.saveCfg({ token, gistId: null, lastSync: null, lastError: null });
    try { return await this.sync(); } catch (e) { if (e.kind === 'auth') await this.disconnect(); throw e; }
  }
  async disconnect() { clearTimeout(this.timer); this.cfg = null; this.pending = false; await CDGStore.del('gist'); this.emit(); }
  schedule(ms = 3000) {
    if (!this.connected) return;
    this.pending = true; clearTimeout(this.timer); this.timer = setTimeout(() => this.sync().catch(() => {}), ms); this.emit();
  }
  sync() {
    if (!this.connected) return Promise.resolve(null);
    if (this.busy) { this.again = true; return this.busy; }
    this.busy = this._sync().finally(() => { this.busy = null; this.emit(); if (this.again) { this.again = false; this.schedule(500); } });
    this.emit(); return this.busy;
  }
  async _sync() {
    clearTimeout(this.timer);
    if (navigator.onLine === false) { this.pending = true; await this.saveCfg({ lastError: '当前离线，联网后自动同步。', errorKind: 'offline' }); throw new SyncError('当前离线，联网后自动同步。', 'offline'); }
    try {
      if (!this.cfg.gistId) await this.saveCfg({ gistId: await this.findOrCreate() });
      let remote;
      try { remote = await this.readRemote(); }
      catch (e) { if (e.kind !== 'notfound') throw e; await this.saveCfg({ gistId: await this.findOrCreate() }); remote = await this.readRemote(); }
      const local = this.getLocal(), merged = merge(local, remote);
      const localChanged = canon(syncPart(merged)) !== canon(syncPart(local));
      const remoteChanged = canon(syncPart(merged)) !== canon(syncPart(merge({}, remote)));
      if (localChanged) await this.applyMerged(merged);
      if (remoteChanged) await this.api(`/gists/${this.cfg.gistId}`, { method: 'PATCH', body: JSON.stringify({ files: { [FILE]: { content: JSON.stringify(this.payload(merged), null, 1) } } }) });
      this.pending = false;
      await this.saveCfg({ lastSync: Date.now(), lastError: null, errorKind: null, lastResult: { pulled: localChanged, pushed: remoteChanged } });
      return { pulled: localChanged, pushed: remoteChanged };
    } catch (e) {
      if (e.kind === 'offline') this.pending = true;
      await this.saveCfg({ lastError: e.message || String(e), errorKind: e.kind || 'unknown' });
      throw e;
    }
  }
}
window.CDGStore = CDGStore;
window.CDGSync = { merge, canon, syncPart, GistSync, SyncError, FILE };
})();
