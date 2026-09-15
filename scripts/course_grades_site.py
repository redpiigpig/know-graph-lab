# -*- coding: utf-8 -*-
"""產出「115-1 登分簿」artifact 的 HTML。

資料一律由 `course_roster.py` 供給（名單＋評量項目與比例＋點名場次＋與系統已選人數
的對帳），**名單或週次改了就重跑這支再 republish**，不要手改 HTML 裡的學生。

分數不寫在 HTML 裡：頁面用 artifact 的 `db` capability，一門課一個文件
`grades/<課號>`，body 是：

    {scores: {學號: {項次: 分數}},        # 各評量項目 0–100
     attend: {學號: {場次: 1–6}},         # 逐次點名，0／空白＝缺席
     manual: bool}                        # 出席分改手動輸入

所以重新發佈換名單不會把已經打好的分數洗掉。

**出席分預設由點名換算**：`sum ÷ (5 × 已點名場次) × 100`，封頂 100。
分母只算「已經點過的場次」（該場有任何一個人有記號），所以學期中看到的數字才是
有意義的，不會因為後面幾週還沒點就全班很低。

用法：
    python scripts/course_grades_site.py            # 寫到暫存目錄，印出路徑
    python scripts/course_grades_site.py --out X    # 指定輸出檔
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'scripts'))

import course_roster as CR  # noqa: E402

DEFAULT_OUT = Path(r'C:\Users\user\AppData\Local\Temp\claude'
                   r'\c--Users-user-Desktop-know-graph-lab'
                   r'\8608c52b-0cbc-419a-9779-d05fe0c88471\scratchpad'
                   r'\course-grades.html')

HTML = r'''<title>115-1 登分簿</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;500;700&family=Noto+Serif+TC:wght@600;700&display=swap">
<style>
:root{
  --ground:#F4F6F4; --surface:#FFFFFF; --sunk:#EDF1EE;
  --line:#DCE3DE; --line-strong:#C3CEC7;
  --ink:#15201B; --muted:#5F6D65;
  --accent:#1E5A4C; --accent-ink:#FFFFFF; --accent-soft:#E2EFE9;
  --pass:#2F7A55; --warn:#8A6410; --fail:#A33A32; --off:#8B948E;
  --pass-bg:#E6F2EA; --warn-bg:#F7EEDA; --fail-bg:#F7E5E3; --off-bg:#ECEFED;
  --bonus:#5B4A9E; --bonus-bg:#EAE6F5;
  --shadow:0 1px 2px rgba(21,32,27,.06), 0 8px 24px -16px rgba(21,32,27,.28);
}
@media (prefers-color-scheme: dark){
  :root:not([data-theme="light"]){
    --ground:#101413; --surface:#191F1C; --sunk:#141917;
    --line:#2B3430; --line-strong:#3C4742;
    --ink:#E6EDE8; --muted:#94A29A;
    --accent:#6FC2A6; --accent-ink:#0E1A16; --accent-soft:#1D2E28;
    --pass:#66B78B; --warn:#C99A3A; --fail:#E08379; --off:#7A857F;
    --pass-bg:#16281F; --warn-bg:#2A2214; --fail-bg:#2C1B19; --off-bg:#1D2320;
    --bonus:#A99AE0; --bonus-bg:#242040;
    --shadow:0 1px 2px rgba(0,0,0,.4), 0 8px 24px -16px rgba(0,0,0,.7);
  }
}
:root[data-theme="dark"]{
  --ground:#101413; --surface:#191F1C; --sunk:#141917;
  --line:#2B3430; --line-strong:#3C4742;
  --ink:#E6EDE8; --muted:#94A29A;
  --accent:#6FC2A6; --accent-ink:#0E1A16; --accent-soft:#1D2E28;
  --pass:#66B78B; --warn:#C99A3A; --fail:#E08379; --off:#7A857F;
  --pass-bg:#16281F; --warn-bg:#2A2214; --fail-bg:#2C1B19; --off-bg:#1D2320;
  --bonus:#A99AE0; --bonus-bg:#242040;
  --shadow:0 1px 2px rgba(0,0,0,.4), 0 8px 24px -16px rgba(0,0,0,.7);
}

*{box-sizing:border-box}
body{
  margin:0; background:var(--ground); color:var(--ink);
  font-family:"Noto Sans TC","Microsoft JhengHei",system-ui,sans-serif;
  font-size:15px; line-height:1.65;
  -webkit-font-smoothing:antialiased;
}
.wrap{max-width:1240px; margin:0 auto; padding-inline:20px; padding-block:28px 64px}
h1,h2,h3{font-family:"Noto Serif TC",serif; text-wrap:balance; margin:0}
.num{font-variant-numeric:tabular-nums}

/* ── 頁首 ───────────────────────────────── */
header.top{display:flex; flex-wrap:wrap; align-items:flex-end; gap:12px 24px; margin-bottom:22px}
h1{font-size:30px; font-weight:700; letter-spacing:.01em}
.sub{color:var(--muted); font-size:13.5px}
.sub b{color:var(--ink); font-weight:500}
.savebar{margin-left:auto; display:flex; align-items:center; gap:10px; font-size:13px; color:var(--muted)}
.dot{width:8px; height:8px; border-radius:50%; background:var(--off); flex:none}
.dot.ok{background:var(--pass)} .dot.busy{background:var(--warn)} .dot.bad{background:var(--fail)}

/* ── 對帳條 ─────────────────────────────── */
.recon{
  display:grid; grid-template-columns:repeat(auto-fit,minmax(215px,1fr)); gap:1px;
  background:var(--line); border:1px solid var(--line); border-radius:10px;
  overflow:hidden; margin-bottom:26px;
}
.recon div{background:var(--surface); padding:12px 14px}
.recon .rc-name{font-size:13px; color:var(--muted); display:flex; gap:8px; align-items:baseline}
.recon .rc-code{font-size:11px; letter-spacing:.08em; color:var(--off)}
.recon .rc-n{font-family:"Noto Serif TC",serif; font-size:22px; font-weight:600; margin-top:2px}
.recon .rc-n small{font-size:12px; font-weight:400; font-family:"Noto Sans TC",sans-serif; color:var(--muted)}
.recon .rc-note{font-size:12px; color:var(--muted)}
.recon .rc-note.stale{color:var(--warn)}

/* ── 課程頁籤 ───────────────────────────── */
nav.tabs{display:flex; flex-wrap:wrap; gap:6px; margin-bottom:18px; border-bottom:1px solid var(--line)}
.tab{
  appearance:none; border:1px solid transparent; border-bottom:none; background:none;
  color:var(--muted); font:inherit; font-size:14px; padding:9px 15px; cursor:pointer;
  border-radius:8px 8px 0 0; margin-bottom:-1px; display:flex; gap:9px; align-items:center;
}
.tab:hover{color:var(--ink); background:var(--sunk)}
.tab[aria-selected="true"]{background:var(--surface); border-color:var(--line); color:var(--ink); font-weight:500}
.tab .pill{font-size:11px; padding:1px 7px; border-radius:99px; background:var(--sunk); color:var(--muted); font-variant-numeric:tabular-nums}
.tab[aria-selected="true"] .pill{background:var(--accent-soft); color:var(--accent)}
.tab:focus-visible{outline:2px solid var(--accent); outline-offset:2px}

/* ── 課程面板 ───────────────────────────── */
.panel{background:var(--surface); border:1px solid var(--line); border-radius:0 12px 12px 12px; box-shadow:var(--shadow)}
.panel[hidden]{display:none}
.phead{padding:18px 20px; border-bottom:1px solid var(--line); display:flex; flex-wrap:wrap; gap:10px 20px; align-items:center}
.phead h2{font-size:20px}
.phead .meta{color:var(--muted); font-size:13px; flex-basis:100%; margin-top:-6px}
.phead .actions{margin-left:auto; display:flex; gap:8px; align-items:center}

.seg{display:inline-flex; border:1px solid var(--line-strong); border-radius:8px; overflow:hidden}
.seg button{
  appearance:none; font:inherit; font-size:13px; padding:6px 15px; cursor:pointer;
  border:none; background:var(--surface); color:var(--muted);
}
.seg button+button{border-left:1px solid var(--line-strong)}
.seg button[aria-pressed="true"]{background:var(--accent); color:var(--accent-ink); font-weight:500}
.seg button:focus-visible{outline:2px solid var(--accent); outline-offset:-2px}

button.act{
  appearance:none; font:inherit; font-size:13px; padding:6px 13px; cursor:pointer;
  border-radius:7px; border:1px solid var(--line-strong); background:var(--surface); color:var(--ink);
}
button.act:hover{background:var(--sunk)}
button.act.primary{background:var(--accent); border-color:var(--accent); color:var(--accent-ink)}
button.act.primary:hover{filter:brightness(1.08)}
button.act:focus-visible{outline:2px solid var(--accent); outline-offset:2px}

.view[hidden]{display:none}
.tablewrap{overflow-x:auto}
table{border-collapse:separate; border-spacing:0; width:100%}
thead th{
  position:sticky; top:0; z-index:3; background:var(--surface);
  border-bottom:2px solid var(--line-strong); text-align:left;
  font-size:12px; font-weight:500; color:var(--muted); padding:9px 10px 8px; white-space:nowrap;
}
thead th.score{text-align:center}
thead th .w{display:block; font-size:11px; color:var(--accent); letter-spacing:.04em}
thead th .tool{
  display:block; margin:3px auto 0; font:inherit; font-size:10.5px; cursor:pointer;
  border:1px dashed var(--line-strong); background:none; color:var(--muted);
  border-radius:5px; padding:1px 6px;
}
thead th .tool:hover{color:var(--accent); border-color:var(--accent)}
thead th .tool[aria-pressed="true"]{border-style:solid; color:var(--accent); border-color:var(--accent); background:var(--accent-soft)}
tbody td{border-bottom:1px solid var(--line); padding:5px 10px; font-size:14px; background:var(--surface)}
tbody tr:hover td{background:var(--sunk)}
td.idx{color:var(--off); font-size:12px; width:34px}
td.sid{font-variant-numeric:tabular-nums; letter-spacing:.02em; width:104px; color:var(--muted)}
td.sname{font-weight:500; white-space:nowrap}
td.klass{color:var(--muted); font-size:12.5px; white-space:nowrap}
td.score{text-align:center; padding:4px 6px}
input.sc{
  width:56px; text-align:center; font:inherit; font-size:14px; font-variant-numeric:tabular-nums;
  padding:5px 2px; border:1px solid var(--line); border-radius:6px;
  background:var(--ground); color:var(--ink);
}
input.sc:hover{border-color:var(--line-strong)}
input.sc:focus{outline:none; border-color:var(--accent); box-shadow:0 0 0 3px var(--accent-soft); background:var(--surface)}
input.sc.bad{border-color:var(--fail); box-shadow:0 0 0 3px var(--fail-bg)}
td.total{text-align:center; width:96px}
.chip{
  display:inline-block; min-width:46px; padding:2px 9px; border-radius:99px;
  font-variant-numeric:tabular-nums; font-weight:500; font-size:13.5px;
  background:var(--off-bg); color:var(--off);
}
.chip.pass{background:var(--pass-bg); color:var(--pass)}
.chip.warn{background:var(--warn-bg); color:var(--warn)}
.chip.fail{background:var(--fail-bg); color:var(--fail)}
.chip.empty{background:transparent; color:var(--off)}
.chip.derived{background:var(--accent-soft); color:var(--accent); min-width:40px; font-size:13px}

/* ── 點名表 ─────────────────────────────── */
.att table{min-width:max-content}
.att th.stick, .att td.stick{position:sticky; z-index:2; background:var(--surface)}
.att tbody tr:hover td.stick{background:var(--sunk)}
.att th.stick{z-index:4}
.att .c-idx{left:0; width:34px}
.att .c-name{left:34px; width:108px; box-shadow:1px 0 0 var(--line)}
.att th.wk{text-align:center; padding:6px 3px; min-width:38px; line-height:1.3}
.att th.wk b{display:block; font-weight:500; color:var(--ink); font-size:12px}
.att th.wk span{display:block; font-size:10.5px; color:var(--off); font-variant-numeric:tabular-nums}
.att th.wk .tool{margin-top:2px}
.att th.wk.exam b{color:var(--fail)}
.att td.wk{text-align:center; padding:3px 3px}
.att td.sum{text-align:center; white-space:nowrap}
input.at{
  width:30px; text-align:center; font:inherit; font-size:14px; font-variant-numeric:tabular-nums;
  padding:4px 0; border:1px solid var(--line); border-radius:5px;
  background:var(--ground); color:var(--ink);
}
input.at:hover{border-color:var(--line-strong)}
input.at:focus{outline:none; border-color:var(--accent); box-shadow:0 0 0 3px var(--accent-soft); background:var(--surface)}
input.at.absent{color:var(--fail); border-color:var(--fail-bg); background:var(--fail-bg)}
input.at.bonus{color:var(--bonus); border-color:var(--bonus); background:var(--bonus-bg); font-weight:700}
input.at.bad{border-color:var(--fail); box-shadow:0 0 0 3px var(--fail-bg)}
.att tfoot td{border-top:2px solid var(--line-strong); padding:7px 3px; text-align:center;
  font-size:11.5px; color:var(--muted); font-variant-numeric:tabular-nums; background:var(--surface)}
.att tfoot td.stick{text-align:left; padding-left:10px}
.legend{padding:10px 20px 0; font-size:12px; color:var(--muted); display:flex; flex-wrap:wrap; gap:6px 18px}
.legend b{font-weight:500; color:var(--ink)}
.legend .sw{display:inline-block; width:10px; height:10px; border-radius:3px; vertical-align:-1px; margin-right:5px}

/* ── 課程頁尾統計 ───────────────────────── */
.pfoot{padding:14px 20px 18px; border-top:1px solid var(--line); display:flex; flex-wrap:wrap; gap:14px 30px; align-items:center}
.stat{display:flex; flex-direction:column; gap:1px}
.stat .k{font-size:11px; letter-spacing:.08em; color:var(--muted)}
.stat .v{font-family:"Noto Serif TC",serif; font-size:19px; font-weight:600; font-variant-numeric:tabular-nums}
.bars{display:flex; gap:3px; align-items:flex-end; height:34px}
.bars .b{width:26px; background:var(--accent-soft); border-radius:3px 3px 0 0; position:relative}
.bars .b i{position:absolute; bottom:-16px; left:0; right:0; text-align:center; font-style:normal; font-size:10px; color:var(--muted)}
.bars-wrap{display:flex; flex-direction:column; gap:18px; margin-left:auto}
.bars-wrap .k{font-size:11px; letter-spacing:.08em; color:var(--muted); text-align:right}

.foot{margin-top:26px; color:var(--muted); font-size:12.5px; line-height:1.9}
.foot code{background:var(--sunk); padding:1px 5px; border-radius:4px; font-size:12px}

@media (max-width:640px){
  .wrap{padding-block:20px 48px}
  h1{font-size:24px}
  .phead .actions{margin-left:0; width:100%; flex-wrap:wrap}
  .bars-wrap{margin-left:0; width:100%}
}
@media (prefers-reduced-motion:reduce){*{transition:none!important; animation:none!important}}
</style>

<div class="wrap">
  <header class="top">
    <div>
      <h1>115-1 登分簿</h1>
      <div class="sub">玄奘大學宗教與文化學系　授課教師 <b>__TEACHER__</b>　四門課 <b>__NSTU__</b> 人次</div>
    </div>
    <div class="savebar"><span class="dot" id="dot"></span><span id="savetext">連線中…</span></div>
  </header>

  <section class="recon" id="recon" aria-label="名單與系統已選人數對帳"></section>

  <nav class="tabs" id="tabs" role="tablist"></nav>
  <div id="panels"></div>

  <p class="foot" id="foot"></p>
</div>

<script type="application/json" id="seed">__DATA__</script>
<script>
(function(){
  "use strict";
  var DATA = JSON.parse(document.getElementById('seed').textContent);
  var PASS = 60, WARN = 70;      // 及格線 60；60–69 標邊緣
  var FULL = 5;                  // 課程單一次滿分 5，6 是加分
  var scores = {}, attend = {}, manual = {};
  var db = null, queue = {}, timers = {}, dirty = {}, view = {};

  DATA.courses.forEach(function(c){
    scores[c.code] = {}; attend[c.code] = {}; manual[c.code] = false;
    view[c.code] = 'grade';
    c.attIdx = -1;
    c.assessment.forEach(function(a, i){ if (a.item === '出席') c.attIdx = i; });
  });

  function el(tag, cls, text){
    var n = document.createElement(tag);
    if (cls) n.className = cls;
    if (text != null) n.textContent = text;
    return n;
  }

  // ── 出席分由點名換算 ────────────────────
  // 分母只算「已經點過的場次」（該場有任何一個人有記號），
  // 否則學期中還沒點的那幾週會把全班拖低。
  function recordedSessions(c){
    var out = [];
    c.sessions.forEach(function(_, j){
      var any = c.students.some(function(s){
        var a = attend[c.code][s.sid];
        return a && typeof a[j] === 'number';
      });
      if (any) out.push(j);
    });
    return out;
  }
  function attendRaw(c, sid){
    var rec = recordedSessions(c);
    if (!rec.length) return null;
    var a = attend[c.code][sid] || {}, sum = 0;
    rec.forEach(function(j){ sum += (typeof a[j] === 'number' ? a[j] : 0); });
    return { sum: sum, of: rec.length, pct: sum / (FULL * rec.length) * 100 };
  }
  function attendScore(c, sid){
    var r = attendRaw(c, sid);
    return r == null ? null : Math.min(100, Math.round(r.pct));
  }

  function itemScore(c, sid, i){
    if (i === c.attIdx && !manual[c.code]) return attendScore(c, sid);
    var g = scores[c.code][sid];
    var v = g && g[i];
    return typeof v === 'number' ? v : null;
  }
  function total(c, sid){
    var sum = 0, any = false;
    c.assessment.forEach(function(a, i){
      var v = itemScore(c, sid, i);
      if (v != null) { sum += v * a.pct / 100; any = true; }
    });
    return any ? Math.round(sum) : null;
  }
  function complete(c, sid){
    return c.assessment.every(function(_, i){ return itemScore(c, sid, i) != null; });
  }
  function chipClass(v, done){
    if (v == null) return 'empty';
    if (!done) return '';
    return v >= WARN ? 'pass' : v >= PASS ? 'warn' : 'fail';
  }

  // ── 存檔 ────────────────────────────────
  function setSave(state, text){
    var dot = document.getElementById('dot');
    dot.className = 'dot' + (state ? ' ' + state : '');
    document.getElementById('savetext').textContent = text;
  }
  function dirtyAny(){ return Object.keys(dirty).some(function(k){ return dirty[k]; }); }
  function flush(code){
    if (!db || !dirty[code]) return;
    if (queue[code]) { timers[code] = setTimeout(function(){ flush(code); }, 400); return; }
    dirty[code] = false; queue[code] = true;
    setSave('busy', '儲存中…');
    db.doc('grades/' + code).set({
      scores: scores[code], attend: attend[code], manual: manual[code],
      updated: new Date().toISOString()
    }).then(function(){
      queue[code] = false;
      setSave('ok', dirtyAny() ? '儲存中…'
        : '已儲存 ' + new Date().toLocaleTimeString('zh-TW', {hour:'2-digit', minute:'2-digit'}));
    }).catch(function(e){
      queue[code] = false; dirty[code] = true;
      setSave('bad', '存不進去（' + (e && e.code || 'unknown') + '）——先別關掉這頁');
    });
  }
  function save(code){
    dirty[code] = true;
    clearTimeout(timers[code]);
    timers[code] = setTimeout(function(){ flush(code); }, 700);
  }

  // ── 對帳條 ──────────────────────────────
  function renderRecon(){
    var box = document.getElementById('recon');
    box.textContent = '';
    DATA.courses.forEach(function(c){
      var d = el('div');
      var nm = el('div', 'rc-name');
      nm.appendChild(el('span', null, c.name));
      nm.appendChild(el('span', 'rc-code', c.code));
      d.appendChild(nm);
      var n = el('div', 'rc-n num');
      n.appendChild(document.createTextNode(String(c.active)));
      var small = el('small', null, c.excluded.length
        ? '　人可登分　已剔除學籍註記 ' + c.excluded.length + ' 人'
        : '　人可登分');
      if (c.excluded.length) {
        small.title = c.excluded.map(function(s){ return s.name + '（' + s.mark + '）'; }).join('、');
      }
      n.appendChild(small);
      d.appendChild(n);
      var stale = c.system != null && c.system !== c.active;
      var note = el('div', 'rc-note' + (stale ? ' stale' : ''));
      note.textContent = stale
        ? '⚠ 系統現在是 ' + c.system + ' 人，這份名單是 ' + c.snapshot + ' 的快照'
        : '系統已選 ' + (c.system == null ? '—' : c.system) + ' 人，與名單一致（' + c.snapshot + '）';
      d.appendChild(note);
      box.appendChild(d);
    });
  }

  // ── 成績表 ──────────────────────────────
  function gradeView(c){
    var v = el('div', 'view');
    v.id = 'grade-' + c.code;
    var wrap = el('div', 'tablewrap');
    var table = el('table');
    var thead = el('thead'), tr = el('tr');
    ['', '學號', '姓名', '班級'].forEach(function(t){ tr.appendChild(el('th', null, t)); });
    c.assessment.forEach(function(a, i){
      var th = el('th', 'score');
      th.appendChild(document.createTextNode(a.item));
      th.appendChild(el('span', 'w', a.pct + '%'));
      if (i === c.attIdx) {
        var m = el('button', 'tool', '手動輸入');
        m.type = 'button';
        m.id = 'manual-' + c.code;
        m.setAttribute('aria-pressed', 'false');
        m.title = '預設由點名換算；按下改成自己填';
        m.addEventListener('click', function(){ toggleManual(c); });
        th.appendChild(m);
      } else {
        var f = el('button', 'tool', '整欄填入');
        f.type = 'button';
        f.addEventListener('click', function(){ fillColumn(c, i); });
        th.appendChild(f);
      }
      tr.appendChild(th);
    });
    var tht = el('th', 'score');
    tht.appendChild(document.createTextNode('總成績'));
    tht.appendChild(el('span', 'w', '100%'));
    tr.appendChild(tht);
    thead.appendChild(tr);
    table.appendChild(thead);

    var tbody = el('tbody');
    c.students.forEach(function(s, n){
      var row = el('tr');
      row.appendChild(el('td', 'idx num', String(n + 1)));
      row.appendChild(el('td', 'sid', s.sid));
      row.appendChild(el('td', 'sname', s.name));
      row.appendChild(el('td', 'klass', s.klass));
      c.assessment.forEach(function(a, i){
        var td = el('td', 'score');
        td.id = 'cell-' + c.code + '-' + s.sid + '-' + i;
        row.appendChild(td);
      });
      var tt = el('td', 'total');
      tt.appendChild(el('span', 'chip empty num', '—'));
      row.appendChild(tt);
      tbody.appendChild(row);
    });
    table.appendChild(tbody);
    wrap.appendChild(table);
    v.appendChild(wrap);
    return v;
  }

  /** 出席欄在自動模式下是唯讀徽章，其餘欄位都是輸入格。 */
  function paintCell(c, s, i){
    var td = document.getElementById('cell-' + c.code + '-' + s.sid + '-' + i);
    if (!td) return;
    var auto = (i === c.attIdx && !manual[c.code]);
    if (auto) {
      var r = attendRaw(c, s.sid), v = attendScore(c, s.sid);
      td.textContent = '';
      var chip = el('span', 'chip derived num', v == null ? '—' : String(v));
      chip.title = r == null ? '這門課還沒點過名'
        : '課程單 ' + r.sum + ' 分 ÷（' + FULL + ' × 已點 ' + r.of + ' 次）＝ '
          + (Math.round(r.pct * 10) / 10) + '％'
          + (r.pct > 100 ? '（加分後超過 100，登記 100）' : '');
      td.appendChild(chip);
      return;
    }
    var inp = td.querySelector('input');
    if (!inp) {
      td.textContent = '';
      inp = el('input', 'sc');
      inp.type = 'text';
      inp.inputMode = 'numeric';
      inp.id = 'sc-' + c.code + '-' + s.sid + '-' + i;
      inp.setAttribute('aria-label', s.name + ' ' + c.assessment[i].item);
      inp.addEventListener('input', function(){ onScore(c, s, i, inp); });
      inp.addEventListener('blur', function(){ inp.value = inp.value.trim(); });
      td.appendChild(inp);
    }
    var g = scores[c.code][s.sid] || {};
    inp.value = typeof g[i] === 'number' ? String(g[i]) : '';
    inp.classList.remove('bad');
  }

  function onScore(c, s, i, inp){
    var raw = inp.value.trim();
    var g = scores[c.code][s.sid] || (scores[c.code][s.sid] = {});
    if (raw === '') {
      delete g[i];
      inp.classList.remove('bad');
    } else {
      var v = Number(raw);
      var ok = /^\d{1,3}(\.\d)?$/.test(raw) && v >= 0 && v <= 100;
      inp.classList.toggle('bad', !ok);
      if (!ok) return;
      g[i] = v;
    }
    if (!Object.keys(g).length) delete scores[c.code][s.sid];
    refreshRow(c, s.sid);
    refreshFoot(c);
    save(c.code);
  }

  function fillColumn(c, i){
    var a = c.assessment[i];
    var raw = window.prompt('把「' + a.item + '」整欄填成幾分？（只填空白的格子；留空取消）', '');
    if (raw == null) return;
    raw = raw.trim();
    if (raw === '') return;
    var v = Number(raw);
    if (!/^\d{1,3}(\.\d)?$/.test(raw) || v < 0 || v > 100) { window.alert('請輸入 0–100 的分數。'); return; }
    c.students.forEach(function(s){
      var g = scores[c.code][s.sid] || (scores[c.code][s.sid] = {});
      if (typeof g[i] === 'number') return;
      g[i] = v;
      paintCell(c, s, i);
      refreshRow(c, s.sid);
    });
    refreshFoot(c);
    save(c.code);
  }

  function toggleManual(c){
    manual[c.code] = !manual[c.code];
    var btn = document.getElementById('manual-' + c.code);
    btn.setAttribute('aria-pressed', manual[c.code] ? 'true' : 'false');
    btn.textContent = manual[c.code] ? '改回自動' : '手動輸入';
    // 從自動切到手動時，把換算出來的分數先寫進去當起點。
    if (manual[c.code]) {
      c.students.forEach(function(s){
        var v = attendScore(c, s.sid);
        if (v == null) return;
        var g = scores[c.code][s.sid] || (scores[c.code][s.sid] = {});
        if (typeof g[c.attIdx] !== 'number') g[c.attIdx] = v;
      });
    }
    refreshAll(c);
    save(c.code);
  }

  // ── 點名表 ──────────────────────────────
  function attView(c){
    var v = el('div', 'view att');
    v.id = 'att-' + c.code;
    v.hidden = true;

    var lg = el('div', 'legend');
    lg.appendChild(el('b', null, '課程單：1–5 分，加分記 6；缺席記 0 或留空。'));
    var a1 = el('span'); a1.innerHTML = '<span class="sw" style="background:var(--fail-bg);border:1px solid var(--fail)"></span>0＝缺席';
    var a2 = el('span'); a2.innerHTML = '<span class="sw" style="background:var(--bonus-bg);border:1px solid var(--bonus)"></span>6＝加分';
    lg.appendChild(a1); lg.appendChild(a2);
    lg.appendChild(el('span', null, '打完一格自動跳到同一欄的下一位——照著課程單那疊一路往下打。'));
    v.appendChild(lg);

    var wrap = el('div', 'tablewrap');
    var table = el('table');
    var thead = el('thead'), tr = el('tr');
    var h0 = el('th', 'stick c-idx', ''); tr.appendChild(h0);
    var h1 = el('th', 'stick c-name', '姓名'); tr.appendChild(h1);
    c.sessions.forEach(function(ss, j){
      var th = el('th', 'wk' + (/期末考/.test(ss.title) ? ' exam' : ''));
      th.appendChild(el('b', null, ss.label.replace(/第\s*/, '').replace(/\s/g, '')));
      th.appendChild(el('span', null, ss.date.replace(/（.）/, '')));
      th.title = ss.label + '　' + ss.date + '　' + ss.title;
      var f = el('button', 'tool', '全 5');
      f.type = 'button';
      f.title = '把這一次還沒填的人全部記 5 分';
      f.addEventListener('click', function(){ fillSession(c, j); });
      th.appendChild(f);
      tr.appendChild(th);
    });
    tr.appendChild(el('th', 'score', '出席分'));
    thead.appendChild(tr);
    table.appendChild(thead);

    var tbody = el('tbody');
    c.students.forEach(function(s, n){
      var row = el('tr');
      row.appendChild(el('td', 'idx num stick c-idx', String(n + 1)));
      row.appendChild(el('td', 'sname stick c-name', s.name));
      c.sessions.forEach(function(_, j){
        var td = el('td', 'wk');
        var inp = el('input', 'at');
        inp.type = 'text';
        inp.inputMode = 'numeric';
        inp.maxLength = 1;
        inp.id = 'at-' + c.code + '-' + s.sid + '-' + j;
        inp.dataset.row = String(n);
        inp.setAttribute('aria-label', s.name + ' ' + c.sessions[j].label);
        inp.addEventListener('input', function(){ onAttend(c, s, j, inp, true); });
        inp.addEventListener('focus', function(){ inp.select(); });
        td.appendChild(inp);
        row.appendChild(td);
      });
      var sum = el('td', 'sum');
      sum.id = 'atsum-' + c.code + '-' + s.sid;
      sum.appendChild(el('span', 'chip derived num', '—'));
      row.appendChild(sum);
      tbody.appendChild(row);
    });
    table.appendChild(tbody);

    var tfoot = el('tfoot'), ftr = el('tr');
    var f0 = el('td', 'stick c-idx', ''); ftr.appendChild(f0);
    var f1 = el('td', 'stick c-name', '到課／平均'); ftr.appendChild(f1);
    c.sessions.forEach(function(_, j){
      var td = el('td');
      td.id = 'atcol-' + c.code + '-' + j;
      td.textContent = '—';
      ftr.appendChild(td);
    });
    ftr.appendChild(el('td', null, ''));
    tfoot.appendChild(ftr);
    table.appendChild(tfoot);

    wrap.appendChild(table);
    v.appendChild(wrap);
    return v;
  }

  function onAttend(c, s, j, inp, advance){
    var raw = inp.value.trim();
    var a = attend[c.code][s.sid] || (attend[c.code][s.sid] = {});
    if (raw === '') {
      delete a[j];
      inp.classList.remove('bad');
    } else {
      var v = Number(raw);
      var ok = /^[0-6]$/.test(raw);
      inp.classList.toggle('bad', !ok);
      if (!ok) return;
      a[j] = v;
      if (advance) {
        // 老師是拿著一疊課程單一路往下打，所以跳到同一欄的下一位，不是右邊那格。
        var nx = c.students[Number(inp.dataset.row) + 1];
        if (nx) {
          var e = document.getElementById('at-' + c.code + '-' + nx.sid + '-' + j);
          if (e) e.focus();
        }
      }
    }
    if (!Object.keys(a).length) delete attend[c.code][s.sid];
    paintAttend(c, s, j);
    refreshAttend(c);
    save(c.code);
  }

  function fillSession(c, j){
    c.students.forEach(function(s){
      var a = attend[c.code][s.sid] || (attend[c.code][s.sid] = {});
      if (typeof a[j] === 'number') return;
      a[j] = FULL;
      paintAttend(c, s, j);
    });
    refreshAttend(c);
    save(c.code);
  }

  function paintAttend(c, s, j){
    var inp = document.getElementById('at-' + c.code + '-' + s.sid + '-' + j);
    if (!inp) return;
    var a = attend[c.code][s.sid] || {};
    var v = a[j];
    inp.value = typeof v === 'number' ? String(v) : '';
    inp.classList.toggle('absent', v === 0);
    inp.classList.toggle('bonus', v > FULL);
    inp.classList.remove('bad');
  }

  /** 點名表的小計、欄底統計，以及成績表裡跟著動的出席欄與總成績。 */
  function refreshAttend(c){
    var rec = recordedSessions(c);
    c.students.forEach(function(s){
      var cell = document.getElementById('atsum-' + c.code + '-' + s.sid);
      if (cell) {
        var r = attendRaw(c, s.sid), v = attendScore(c, s.sid);
        var chip = cell.querySelector('.chip');
        chip.textContent = v == null ? '—' : String(v);
        chip.title = r == null ? '' : r.sum + ' / ' + (FULL * r.of);
      }
      if (!manual[c.code]) paintCell(c, s, c.attIdx);
      refreshRow(c, s.sid);
    });
    c.sessions.forEach(function(_, j){
      var td = document.getElementById('atcol-' + c.code + '-' + j);
      if (!td) return;
      if (rec.indexOf(j) < 0) { td.textContent = '—'; return; }
      var marks = c.students.map(function(s){
        var a = attend[c.code][s.sid] || {};
        return typeof a[j] === 'number' ? a[j] : 0;
      });
      var here = marks.filter(function(m){ return m > 0; }).length;
      var avg = marks.reduce(function(x, y){ return x + y; }, 0) / marks.length;
      td.textContent = here + '／' + marks.length + '　' + (Math.round(avg * 10) / 10);
    });
    refreshFoot(c);
  }

  // ── 共用刷新 ────────────────────────────
  function refreshRow(c, sid){
    var td = document.getElementById('cell-' + c.code + '-' + sid + '-0');
    if (!td) return;
    var chip = td.closest('tr').querySelector('td.total .chip');
    var v = total(c, sid), done = complete(c, sid);
    chip.textContent = v == null ? '—' : String(v);
    chip.className = 'chip num ' + chipClass(v, done);
    chip.title = v == null ? '' : (done ? '全部項目都齊了' : '還有項目沒登，這是已登項目的加權值');
  }

  function refreshAll(c){
    c.students.forEach(function(s){
      c.assessment.forEach(function(_, i){ paintCell(c, s, i); });
      c.sessions.forEach(function(_, j){ paintAttend(c, s, j); });
    });
    var btn = document.getElementById('manual-' + c.code);
    if (btn) {
      btn.setAttribute('aria-pressed', manual[c.code] ? 'true' : 'false');
      btn.textContent = manual[c.code] ? '改回自動' : '手動輸入';
    }
    refreshAttend(c);
  }

  function refreshFoot(c){
    var foot = document.getElementById('foot-' + c.code);
    if (!foot) return;
    var act = c.students;
    var done = act.filter(function(s){ return complete(c, s.sid); });
    var vals = done.map(function(s){ return total(c, s.sid); });
    var avg = vals.length ? Math.round(vals.reduce(function(a, b){ return a + b; }, 0) / vals.length) : null;
    var passed = vals.filter(function(v){ return v >= PASS; }).length;
    var rec = recordedSessions(c).length;

    foot.textContent = '';
    function stat(k, v){
      var d = el('div', 'stat');
      d.appendChild(el('span', 'k', k));
      d.appendChild(el('span', 'v num', v));
      foot.appendChild(d);
    }
    stat('已點名', rec + ' / ' + c.sessions.length + ' 次');
    stat('成績齊', done.length + ' / ' + act.length);
    stat('平均', avg == null ? '—' : String(avg));
    stat('及格', vals.length ? passed + ' / ' + vals.length : '—');
    stat('最低', vals.length ? String(Math.min.apply(null, vals)) : '—');
    stat('最高', vals.length ? String(Math.max.apply(null, vals)) : '—');

    var buckets = [0, 0, 0, 0, 0];
    var labels = ['<60', '60s', '70s', '80s', '90+'];
    vals.forEach(function(v){ buckets[v < 60 ? 0 : v < 70 ? 1 : v < 80 ? 2 : v < 90 ? 3 : 4]++; });
    var max = Math.max.apply(null, buckets) || 1;
    var bw = el('div', 'bars-wrap');
    bw.appendChild(el('div', 'k', '總成績分布'));
    var bars = el('div', 'bars');
    buckets.forEach(function(n, i){
      var b = el('div', 'b');
      b.style.height = Math.max(3, Math.round(n / max * 34)) + 'px';
      if (n) b.style.background = 'var(--accent)';
      b.title = labels[i] + '：' + n + ' 人';
      b.appendChild(el('i', null, labels[i]));
      bars.appendChild(b);
    });
    bw.appendChild(bars);
    foot.appendChild(bw);

    var pill = document.getElementById('pill-' + c.code);
    if (pill) pill.textContent = done.length + '/' + act.length;
  }

  // ── 匯出 ────────────────────────────────
  function csvText(rows){
    return '\uFEFF' + rows.map(function(r){
      return r.map(function(x){
        x = String(x);
        return /[",\n]/.test(x) ? '"' + x.replace(/"/g, '""') + '"' : x;
      }).join(',');
    }).join('\r\n');
  }
  function offer(name, text){
    claude.use('downloads').then(function(d){
      if (!d) { window.alert('這個檢視不支援下載。'); return; }
      return d.save({ filename: name, data: text });
    }).catch(function(e){
      if (e && e.code === 'declined') return;
      window.alert('匯出失敗：' + (e && e.message || e));
    });
  }
  function today(){ return new Date().toISOString().slice(0, 10); }

  function exportGrades(c){
    var rows = [['序', '學號', '姓名', '班級']
      .concat(c.assessment.map(function(a){ return a.item + ' ' + a.pct + '%'; }))
      .concat(['總成績'])];
    c.students.forEach(function(s, n){
      var v = total(c, s.sid);
      rows.push([n + 1, s.sid, s.name, s.klass]
        .concat(c.assessment.map(function(_, i){
          var x = itemScore(c, s.sid, i);
          return x == null ? '' : x;
        }))
        .concat([v == null ? '' : v]));
    });
    offer(c.code + '_' + c.name + '_成績_' + today() + '.csv', csvText(rows));
  }

  function exportAttend(c){
    var rows = [['序', '學號', '姓名', '班級']
      .concat(c.sessions.map(function(ss){ return ss.label.replace(/\s/g, '') + ' ' + ss.date; }))
      .concat(['課程單合計', '已點次數', '出席分'])];
    var rec = recordedSessions(c);
    c.students.forEach(function(s, n){
      var a = attend[c.code][s.sid] || {};
      var r = attendRaw(c, s.sid);
      rows.push([n + 1, s.sid, s.name, s.klass]
        .concat(c.sessions.map(function(_, j){ return typeof a[j] === 'number' ? a[j] : ''; }))
        .concat([r ? r.sum : '', rec.length, attendScore(c, s.sid) == null ? '' : attendScore(c, s.sid)]));
    });
    offer(c.code + '_' + c.name + '_點名_' + today() + '.csv', csvText(rows));
  }

  // ── 面板與頁籤 ──────────────────────────
  function renderCourse(c){
    var panel = el('section', 'panel');
    panel.id = 'panel-' + c.code;
    panel.setAttribute('role', 'tabpanel');
    panel.setAttribute('aria-labelledby', 'tab-' + c.code);

    var head = el('div', 'phead');
    head.appendChild(el('h2', null, c.name));

    var seg = el('div', 'seg');
    var bg = el('button', null, '成績'), ba = el('button', null, '點名　' + c.sessions.length + ' 次');
    bg.type = ba.type = 'button';
    bg.setAttribute('aria-pressed', 'true');
    ba.setAttribute('aria-pressed', 'false');
    bg.addEventListener('click', function(){ setView(c, 'grade'); });
    ba.addEventListener('click', function(){ setView(c, 'att'); });
    bg.id = 'v-grade-' + c.code; ba.id = 'v-att-' + c.code;
    seg.appendChild(bg); seg.appendChild(ba);
    head.appendChild(seg);

    var acts = el('div', 'actions');
    var e1 = el('button', 'act primary', '匯出成績');
    e1.type = 'button';
    e1.addEventListener('click', function(){ exportGrades(c); });
    var e2 = el('button', 'act', '匯出點名');
    e2.type = 'button';
    e2.addEventListener('click', function(){ exportAttend(c); });
    acts.appendChild(e1); acts.appendChild(e2);
    head.appendChild(acts);
    head.appendChild(el('div', 'meta', c.klass + '　' + c.time + '　' + c.room));
    panel.appendChild(head);

    panel.appendChild(gradeView(c));
    panel.appendChild(attView(c));

    var foot = el('div', 'pfoot');
    foot.id = 'foot-' + c.code;
    panel.appendChild(foot);
    return panel;
  }

  function setView(c, which){
    view[c.code] = which;
    document.getElementById('grade-' + c.code).hidden = which !== 'grade';
    document.getElementById('att-' + c.code).hidden = which !== 'att';
    document.getElementById('v-grade-' + c.code).setAttribute('aria-pressed', which === 'grade' ? 'true' : 'false');
    document.getElementById('v-att-' + c.code).setAttribute('aria-pressed', which === 'att' ? 'true' : 'false');
  }

  function build(){
    var tabs = document.getElementById('tabs');
    var panels = document.getElementById('panels');
    DATA.courses.forEach(function(c, idx){
      var t = el('button', 'tab');
      t.type = 'button';
      t.id = 'tab-' + c.code;
      t.setAttribute('role', 'tab');
      t.setAttribute('aria-controls', 'panel-' + c.code);
      t.setAttribute('aria-selected', idx === 0 ? 'true' : 'false');
      t.appendChild(document.createTextNode(c.name + '　' + c.code));
      var pill = el('span', 'pill num', '0/' + c.students.length);
      pill.id = 'pill-' + c.code;
      t.appendChild(pill);
      t.addEventListener('click', function(){ select(c.code); });
      tabs.appendChild(t);

      var p = renderCourse(c);
      p.hidden = idx !== 0;
      panels.appendChild(p);
    });
    DATA.courses.forEach(refreshAll);

    document.getElementById('foot').innerHTML =
      '<b>出席分預設由點名換算</b>：課程單總分 ÷（5 × 已點名次數）× 100，封頂 100；' +
      '加分的 6 分會把分數往上推，但登記不超過 100。分母只算已經點過的場次，' +
      '所以學期中看到的數字就是當下的實況。要自己填就按出席欄的「手動輸入」。<br>' +
      '及格線 60；60–69 標琥珀、70 以上綠。改任何一格都自動存，換裝置開同一個連結是同一份。<br>' +
      '名單與週次都由 <code>scripts/course_roster.py</code> 供給——換名單重跑它與 ' +
      '<code>scripts/course_grades_site.py</code> 再重新發佈，已打好的分數與點名不會被洗掉' +
      '（存在 <code>grades/&lt;課號&gt;</code>，不在頁面裡）。';
  }

  function select(code){
    DATA.courses.forEach(function(c){
      var on = c.code === code;
      document.getElementById('tab-' + c.code).setAttribute('aria-selected', on ? 'true' : 'false');
      document.getElementById('panel-' + c.code).hidden = !on;
    });
  }

  // ── 啟動 ────────────────────────────────
  renderRecon();
  build();
  setSave('', '離線——改了不會留下');

  claude.use('db').then(function(d){
    if (!d) { setSave('bad', '這個檢視存不了（唯讀或未授權）'); return; }
    db = d;
    setSave('ok', '已連線');
    DATA.courses.forEach(function(c){
      db.doc('grades/' + c.code).onSnapshot(function(snap){
        if (dirty[c.code] || queue[c.code]) return;   // 自己正在寫，別被回音蓋掉
        var body = snap.exists ? snap.data() : null;
        var clone = function(x){ return x ? JSON.parse(JSON.stringify(x)) : {}; };
        scores[c.code] = clone(body && body.scores);
        attend[c.code] = clone(body && body.attend);
        manual[c.code] = !!(body && body.manual);
        refreshAll(c);
      }, function(e){
        setSave('bad', '同步斷了（' + e.code + '）——重新整理這頁');
      });
    });
  });
})();
</script>
'''


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', type=Path, default=DEFAULT_OUT)
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding='utf-8')

    data = CR.payload(CR.collect(), CR.live_counts())
    nstu = sum(c['active'] for c in data['courses'])

    html = (HTML
            .replace('__TEACHER__', data['teacher'])
            .replace('__NSTU__', str(nstu))
            .replace('__DATA__', json.dumps(data, ensure_ascii=False)))
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(html, encoding='utf-8')
    print(f'{a.out}　{len(html):,} 字元　{nstu} 人次　'
          + '／'.join(f'{c["code"]} {len(c["sessions"])} 次' for c in data['courses']))


if __name__ == '__main__':
    main()
