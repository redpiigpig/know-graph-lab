# -*- coding: utf-8 -*-
"""產出「115-1 登分簿」artifact 的 HTML。

資料一律由 `course_roster.py` 供給（名單＋評量項目與比例＋與系統已選人數的對帳），
**名單改了就重跑這支再 republish**，不要手改 HTML 裡的學生。

分數不寫在 HTML 裡：頁面用 artifact 的 `db` capability，一門課一個文件
`grades/<課號>`，body 是 `{scores: {學號: {項次: 分數}}}`。所以重新發佈換名單
不會把已經打好的分數洗掉。

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
  --shadow:0 1px 2px rgba(0,0,0,.4), 0 8px 24px -16px rgba(0,0,0,.7);
}

*{box-sizing:border-box}
body{
  margin:0; background:var(--ground); color:var(--ink);
  font-family:"Noto Sans TC","Microsoft JhengHei",system-ui,sans-serif;
  font-size:15px; line-height:1.65;
  -webkit-font-smoothing:antialiased;
}
.wrap{max-width:1180px; margin:0 auto; padding-inline:20px; padding-block:28px 64px}
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
  display:grid; grid-template-columns:repeat(auto-fit,minmax(210px,1fr)); gap:1px;
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
.tab[aria-selected="true"]{
  background:var(--surface); border-color:var(--line); color:var(--ink); font-weight:500;
}
.tab .pill{
  font-size:11px; padding:1px 7px; border-radius:99px; background:var(--sunk);
  color:var(--muted); font-variant-numeric:tabular-nums;
}
.tab[aria-selected="true"] .pill{background:var(--accent-soft); color:var(--accent)}
.tab:focus-visible{outline:2px solid var(--accent); outline-offset:2px}

/* ── 課程面板 ───────────────────────────── */
.panel{background:var(--surface); border:1px solid var(--line); border-radius:0 12px 12px 12px; box-shadow:var(--shadow)}
.panel[hidden]{display:none}
.phead{padding:18px 20px; border-bottom:1px solid var(--line); display:flex; flex-wrap:wrap; gap:8px 20px; align-items:baseline}
.phead h2{font-size:20px}
.phead .meta{color:var(--muted); font-size:13px}
.phead .actions{margin-left:auto; display:flex; gap:8px}
button.act{
  appearance:none; font:inherit; font-size:13px; padding:6px 13px; cursor:pointer;
  border-radius:7px; border:1px solid var(--line-strong); background:var(--surface); color:var(--ink);
}
button.act:hover{background:var(--sunk)}
button.act.primary{background:var(--accent); border-color:var(--accent); color:var(--accent-ink)}
button.act.primary:hover{filter:brightness(1.08)}
button.act:focus-visible{outline:2px solid var(--accent); outline-offset:2px}

.tablewrap{overflow-x:auto}
table{border-collapse:collapse; width:100%; min-width:720px}
thead th{
  position:sticky; top:0; z-index:2; background:var(--surface);
  border-bottom:2px solid var(--line-strong); text-align:left;
  font-size:12px; font-weight:500; color:var(--muted); padding:10px 10px 9px; white-space:nowrap;
}
thead th.score{text-align:center}
thead th .w{display:block; font-size:11px; color:var(--accent); letter-spacing:.04em}
thead th .fillcol{
  display:block; margin:3px auto 0; font:inherit; font-size:10.5px; cursor:pointer;
  border:1px dashed var(--line-strong); background:none; color:var(--muted);
  border-radius:5px; padding:1px 6px;
}
thead th .fillcol:hover{color:var(--accent); border-color:var(--accent)}
tbody td{border-bottom:1px solid var(--line); padding:5px 10px; font-size:14px}
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
input.sc:disabled{background:transparent; border-color:transparent; color:var(--off)}
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

/* ── 課程頁尾統計 ───────────────────────── */
.pfoot{padding:14px 20px 18px; border-top:1px solid var(--line); display:flex; flex-wrap:wrap; gap:14px 30px; align-items:center}
.stat{display:flex; flex-direction:column; gap:1px}
.stat .k{font-size:11px; letter-spacing:.08em; color:var(--muted)}
.stat .v{font-family:"Noto Serif TC",serif; font-size:19px; font-weight:600; font-variant-numeric:tabular-nums}
.bars{display:flex; gap:3px; align-items:flex-end; height:34px; margin-left:auto}
.bars .b{width:26px; background:var(--accent-soft); border-radius:3px 3px 0 0; position:relative}
.bars .b i{position:absolute; bottom:-16px; left:0; right:0; text-align:center; font-style:normal; font-size:10px; color:var(--muted)}
.bars-wrap{display:flex; flex-direction:column; gap:18px; margin-left:auto}
.bars-wrap .k{font-size:11px; letter-spacing:.08em; color:var(--muted); text-align:right}

.foot{margin-top:26px; color:var(--muted); font-size:12.5px; line-height:1.9}
.foot code{background:var(--sunk); padding:1px 5px; border-radius:4px; font-size:12px}

@media (max-width:640px){
  .wrap{padding-block:20px 48px}
  h1{font-size:24px}
  .phead .actions{margin-left:0; width:100%}
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
  var PASS = 60;           // 玄奘及格線
  var WARN = 70;           // 60–69 標為邊緣
  var scores = {};         // code -> sid -> {itemIndex: number}
  var db = null, queue = {}, timers = {}, dirty = {};

  DATA.courses.forEach(function(c){ scores[c.code] = {}; });

  // ── 小工具 ──────────────────────────────
  function el(tag, cls, text){
    var n = document.createElement(tag);
    if (cls) n.className = cls;
    if (text != null) n.textContent = text;
    return n;
  }
  // 名單在產生時就把學籍註記（休學／退學／刪除／保留／W）的人濾掉了，
  // 所以 c.students 全部都是可以登分的人。
  function activeStudents(c){ return c.students; }
  function total(c, sid){
    var g = scores[c.code][sid] || {}, sum = 0, any = false;
    c.assessment.forEach(function(a, i){
      var v = g[i];
      if (typeof v === 'number') { sum += v * a.pct / 100; any = true; }
    });
    return any ? Math.round(sum) : null;
  }
  function complete(c, sid){
    var g = scores[c.code][sid] || {};
    return c.assessment.every(function(_, i){ return typeof g[i] === 'number'; });
  }
  function chipClass(v, done){
    if (v == null) return 'empty';
    if (!done) return '';
    if (v >= WARN) return 'pass';
    if (v >= PASS) return 'warn';
    return 'fail';
  }

  // ── 存檔 ────────────────────────────────
  function setSave(state, text){
    var dot = document.getElementById('dot');
    dot.className = 'dot' + (state ? ' ' + state : '');
    document.getElementById('savetext').textContent = text;
  }
  function flush(code){
    if (!db || !dirty[code]) return;
    if (queue[code]) { timers[code] = setTimeout(function(){ flush(code); }, 400); return; }
    dirty[code] = false;
    queue[code] = true;
    setSave('busy', '儲存中…');
    db.doc('grades/' + code).set({ scores: scores[code], updated: new Date().toISOString() })
      .then(function(){
        queue[code] = false;
        setSave('ok', dirtyAny() ? '儲存中…' : '已儲存 ' + new Date().toLocaleTimeString('zh-TW', {hour:'2-digit', minute:'2-digit'}));
      })
      .catch(function(e){
        queue[code] = false; dirty[code] = true;
        setSave('bad', '存不進去（' + (e && e.code || 'unknown') + '）——先別關掉這頁');
      });
  }
  function dirtyAny(){ return Object.keys(dirty).some(function(k){ return dirty[k]; }); }
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

  // ── 表格 ────────────────────────────────
  function renderCourse(c){
    var panel = el('section', 'panel');
    panel.id = 'panel-' + c.code;
    panel.setAttribute('role', 'tabpanel');
    panel.setAttribute('aria-labelledby', 'tab-' + c.code);

    var head = el('div', 'phead');
    var h = el('div');
    h.appendChild(el('h2', null, c.name));
    h.appendChild(el('div', 'meta', c.klass + '　' + c.time + '　' + c.room));
    head.appendChild(h);
    var acts = el('div', 'actions');
    var csv = el('button', 'act primary', '匯出 CSV');
    csv.type = 'button';
    csv.addEventListener('click', function(){ exportCsv(c); });
    acts.appendChild(csv);
    head.appendChild(acts);
    panel.appendChild(head);

    var wrap = el('div', 'tablewrap');
    var table = el('table');
    var thead = el('thead'), tr = el('tr');
    ['', '學號', '姓名', '班級'].forEach(function(t){ tr.appendChild(el('th', null, t)); });
    c.assessment.forEach(function(a, i){
      var th = el('th', 'score');
      th.appendChild(document.createTextNode(a.item));
      th.appendChild(el('span', 'w', a.pct + '%'));
      var f = el('button', 'fillcol', '整欄填入');
      f.type = 'button';
      f.addEventListener('click', function(){ fillColumn(c, i); });
      th.appendChild(f);
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
        var inp = el('input', 'sc');
        inp.type = 'text';
        inp.inputMode = 'numeric';
        inp.id = 'sc-' + c.code + '-' + s.sid + '-' + i;
        inp.setAttribute('aria-label', s.name + ' ' + a.item);
        inp.addEventListener('input', function(){ onInput(c, s, i, inp); });
        inp.addEventListener('blur', function(){ inp.value = inp.value.trim(); });
        td.appendChild(inp);
        row.appendChild(td);
      });
      var tt = el('td', 'total');
      tt.appendChild(el('span', 'chip empty num', '—'));
      row.appendChild(tt);
      tbody.appendChild(row);
    });
    table.appendChild(tbody);
    wrap.appendChild(table);
    panel.appendChild(wrap);

    var foot = el('div', 'pfoot');
    foot.id = 'foot-' + c.code;
    panel.appendChild(foot);
    return panel;
  }

  function onInput(c, s, i, inp){
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
    activeStudents(c).forEach(function(s){
      var g = scores[c.code][s.sid] || (scores[c.code][s.sid] = {});
      if (typeof g[i] === 'number') return;
      g[i] = v;
      var inp = document.getElementById('sc-' + c.code + '-' + s.sid + '-' + i);
      if (inp) { inp.value = String(v); inp.classList.remove('bad'); }
      refreshRow(c, s.sid);
    });
    refreshFoot(c);
    save(c.code);
  }

  function refreshRow(c, sid){
    var inp = document.getElementById('sc-' + c.code + '-' + sid + '-0');
    if (!inp) return;
    var row = inp.closest('tr');
    var chip = row.querySelector('.chip');
    var v = total(c, sid), done = complete(c, sid);
    chip.textContent = v == null ? '—' : String(v);
    chip.className = 'chip num ' + chipClass(v, done);
    chip.title = v == null ? '' : (done ? '全部項目都打完了' : '尚有項目未登分，這是目前已登項目的加權值');
  }

  function refreshAll(c){
    c.students.forEach(function(s){
      c.assessment.forEach(function(_, i){
        var inp = document.getElementById('sc-' + c.code + '-' + s.sid + '-' + i);
        if (!inp) return;
        var g = scores[c.code][s.sid] || {};
        inp.value = typeof g[i] === 'number' ? String(g[i]) : '';
        inp.classList.remove('bad');
      });
      refreshRow(c, s.sid);
    });
    refreshFoot(c);
    var pill = document.getElementById('pill-' + c.code);
    if (pill) pill.textContent = doneCount(c) + '/' + activeStudents(c).length;
  }

  function doneCount(c){
    return activeStudents(c).filter(function(s){ return complete(c, s.sid); }).length;
  }

  function refreshFoot(c){
    var foot = document.getElementById('foot-' + c.code);
    if (!foot) return;
    var act = activeStudents(c);
    var done = act.filter(function(s){ return complete(c, s.sid); });
    var vals = done.map(function(s){ return total(c, s.sid); });
    var avg = vals.length ? Math.round(vals.reduce(function(a, b){ return a + b; }, 0) / vals.length) : null;
    var passed = vals.filter(function(v){ return v >= PASS; }).length;

    foot.textContent = '';
    function stat(k, v){
      var d = el('div', 'stat');
      d.appendChild(el('span', 'k', k));
      d.appendChild(el('span', 'v num', v));
      foot.appendChild(d);
    }
    stat('已登完', done.length + ' / ' + act.length);
    stat('平均', avg == null ? '—' : String(avg));
    stat('及格', vals.length ? passed + ' / ' + vals.length : '—');
    stat('最低', vals.length ? String(Math.min.apply(null, vals)) : '—');
    stat('最高', vals.length ? String(Math.max.apply(null, vals)) : '—');

    var buckets = [0, 0, 0, 0, 0];
    var labels = ['<60', '60s', '70s', '80s', '90+'];
    vals.forEach(function(v){
      buckets[v < 60 ? 0 : v < 70 ? 1 : v < 80 ? 2 : v < 90 ? 3 : 4]++;
    });
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
  function exportCsv(c){
    var head = ['序', '學號', '姓名', '班級']
      .concat(c.assessment.map(function(a){ return a.item + ' ' + a.pct + '%'; }))
      .concat(['總成績']);
    var lines = [head];
    c.students.forEach(function(s, n){
      var g = scores[c.code][s.sid] || {};
      var v = total(c, s.sid);
      lines.push([n + 1, s.sid, s.name, s.klass]
        .concat(c.assessment.map(function(_, i){ return typeof g[i] === 'number' ? g[i] : ''; }))
        .concat([v == null ? '' : v]));
    });
    var csv = '\uFEFF' + lines.map(function(r){
      return r.map(function(x){
        x = String(x);
        return /[",\n]/.test(x) ? '"' + x.replace(/"/g, '""') + '"' : x;
      }).join(',');
    }).join('\r\n');
    var name = c.code + '_' + c.name + '_成績_' + new Date().toISOString().slice(0, 10) + '.csv';
    claude.use('downloads').then(function(d){
      if (!d) { window.alert('這個檢視不支援下載。'); return; }
      return d.save({ filename: name, data: csv });
    }).catch(function(e){
      if (e && e.code === 'declined') return;
      window.alert('匯出失敗：' + (e && e.message || e));
    });
  }

  // ── 頁籤 ────────────────────────────────
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
      var pill = el('span', 'pill num', '0/' + activeStudents(c).length);
      pill.id = 'pill-' + c.code;
      t.appendChild(pill);
      t.addEventListener('click', function(){ select(c.code); });
      tabs.appendChild(t);

      var p = renderCourse(c);
      p.hidden = idx !== 0;
      panels.appendChild(p);
    });
    DATA.courses.forEach(refreshFoot);

    document.getElementById('foot').innerHTML =
      '及格線 60；60–69 標為邊緣（琥珀），70 以上為綠。分數一改就自動存，' +
      '換裝置打開同一個連結看到的是同一份。<br>' +
      '名單來源與快照日期見上方對帳條——名單要換成最新的，重跑 ' +
      '<code>scripts/course_roster.py</code> 與 <code>scripts/course_grades_site.py</code> 再重新發佈，' +
      '已經打好的分數不會被洗掉（分數存在 <code>grades/&lt;課號&gt;</code>，不在頁面裡）。';
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
  setSave('', '離線——分數不會留下');

  claude.use('db').then(function(d){
    if (!d) { setSave('bad', '這個檢視存不了分數（唯讀或未授權）'); return; }
    db = d;
    setSave('ok', '已連線');
    DATA.courses.forEach(function(c){
      db.doc('grades/' + c.code).onSnapshot(function(snap){
        if (dirty[c.code] || queue[c.code]) return;   // 自己正在寫，別被回音蓋掉
        var body = snap.exists ? snap.data() : null;
        scores[c.code] = (body && body.scores) ? JSON.parse(JSON.stringify(body.scores)) : {};
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

    import course_enrollment as CE
    data = CR.payload(CR.collect(), CE.fetch())
    nstu = sum(c['active'] for c in data['courses'])

    html = (HTML
            .replace('__TEACHER__', data['teacher'])
            .replace('__NSTU__', str(nstu))
            .replace('__DATA__', json.dumps(data, ensure_ascii=False)))
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(html, encoding='utf-8')
    print(f'{a.out}　{len(html):,} 字元　{nstu} 人次')


if __name__ == '__main__':
    main()
