# -*- coding: utf-8 -*-
"""一貫道國家檔案：離線搜尋工具（單一 HTML 檔，資料加密內嵌）。

    python -X utf8 scripts/yiguandao_search_html.py

給老師們的是一個資料夾：雙擊 HTML 用瀏覽器開、輸入密碼即可查，不用安裝、不連網路。
資料（件層總表＋全文逐頁＋人名）先 gzip 再用 AES-256-GCM 加密後內嵌；
金鑰由密碼經 PBKDF2-SHA256（310,000 次）導出，瀏覽器以 WebCrypto 解開，只留在記憶體。

來源：
  public/content/research-data/yiguandao/catalog/{cases,items,people}.json（gitignore）
  全文：各卷宗的謄打本 PDF 文字層，按 PDF 頁切（與總表「PDF頁」欄對得上）
🚨 密碼用 .env 的 YIGUANDAO_DOCX_PASSWORD；程式碼進 git，資料與產出的 HTML 不進。
"""
import base64
import gzip
import json
import os
import re
from pathlib import Path

import fitz
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

ROOT = Path(__file__).resolve().parents[1]
CAT = ROOT / "public/content/research-data/yiguandao/catalog"
SRC = Path(r"G:/我的雲端硬碟/玄奘/博一上/工作/中研院助理/05_檔案全文")
OUT_DIR = Path(r"G:/我的雲端硬碟/玄奘/博一上/工作/中研院助理/09_一貫道檔案搜尋")
# 卷宗代號 → 謄打本 PDF；reverse＝直排公文文字層的欄序是由右至左，顯示前要倒回來
FULLTEXT = {
    "BS": {"pdf": "[勿外傳] 國史館 捕鼠案.pdf", "reverse": False},
    "DW": {"pdf": "[勿外傳] 國史館 敵偽.pdf", "reverse": True},
}
ITER = 310_000


def page_text(raw, reverse):
    """PDF 文字層 → 可讀的一頁。一字一行的欄（直排）接回一串，欄與欄之間以「／」分。"""
    segs, cur = [], []
    for ln in raw.split("\n"):
        s = ln.strip()
        if not s:
            if cur:
                segs.append(cur)
                cur = []
            continue
        cur.append(s)
    if cur:
        segs.append(cur)
    cols = ["".join(s) if all(len(x) <= 2 for x in s) else " ".join(s) for s in segs]
    if reverse:
        cols.reverse()
    return "／".join(c for c in cols if c)


def load_pages():
    pages = []
    for code, cfg in FULLTEXT.items():
        p = SRC / cfg["pdf"]
        if not p.exists():
            print(f"  ⚠ 找不到全文 {p.name}，{code} 只有件層資料")
            continue
        for i, pg in enumerate(fitz.open(p), 1):
            pages.append({"c": code, "p": i, "t": page_text(pg.get_text(), cfg["reverse"])})
    return pages


def password():
    pw = os.environ.get("YIGUANDAO_DOCX_PASSWORD")
    if not pw:
        for line in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
            if line.startswith("YIGUANDAO_DOCX_PASSWORD="):
                pw = line.split("=", 1)[1].strip()
    if not pw:
        raise SystemExit("缺 YIGUANDAO_DOCX_PASSWORD")
    return pw


def encrypt(obj, pw):
    raw = gzip.compress(json.dumps(obj, ensure_ascii=False).encode("utf-8"))
    salt, iv = os.urandom(16), os.urandom(12)
    key = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=ITER).derive(pw.encode())
    ct = AESGCM(key).encrypt(iv, raw, None)
    b = lambda x: base64.b64encode(x).decode()  # noqa: E731
    return {"salt": b(salt), "iv": b(iv), "iter": ITER, "ct": b(ct)}


def main():
    cases = json.loads((CAT / "cases.json").read_text(encoding="utf-8"))
    items = json.loads((CAT / "items.json").read_text(encoding="utf-8"))
    people = json.loads((CAT / "people.json").read_text(encoding="utf-8")) if (CAT / "people.json").exists() else {}
    pages = load_pages()
    data = {"cases": cases, "columns": items["columns"], "items": items["items"],
            "people": people, "pages": pages}
    blob = encrypt(data, password())
    html = TEMPLATE.replace("__BLOB__", json.dumps(blob))
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "一貫道檔案搜尋.html").write_text(html, encoding="utf-8")
    (OUT_DIR / "使用說明.txt").write_text(README, encoding="utf-8")
    print(f"{len(cases)} 卷宗、{len(items['items'])} 件、{len(pages)} 頁全文 → {OUT_DIR}")


README = """一貫道國家檔案搜尋（本機版）

使用方式
1. 用 Chrome、Edge 或 Firefox 打開「一貫道檔案搜尋.html」（雙擊即可）。
2. 輸入密碼（另行告知）。資料只在瀏覽器記憶體中解開，不會寫到硬碟、不會連網。
3. 關閉分頁即清除；下次開啟須再輸入密碼。

可以做的事
・全文關鍵字：同時比對公文摘要與逐頁全文；多個詞以空格分開，須全部符合。
・篩選：卷宗、時期、機關類型、行動、定性框架。
・點選一件，可看完整欄位與該件各頁的全文，並可跳至相鄰各件。
・人名分頁：列出人名、身分與出現的件。

注意
・全文為謄打本 PDF 的文字層，直排公文的欄序已盡量還原，閱讀請以 Word 謄打本為準。
・本檔含第三人姓名，限計畫內部使用，請勿轉寄；密碼請與檔案分開傳送。
"""

TEMPLATE = r"""<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>一貫道檔案搜尋</title>
<style>
:root{--bg:#f7f6f2;--card:#fff;--ink:#1f2328;--muted:#6b6f76;--line:#dcd9d0;--accent:#8a3b12;--hl:#ffe58a;--chip:#efece4}
@media (prefers-color-scheme:dark){:root{--bg:#17181a;--card:#212326;--ink:#e8e6e1;--muted:#a0a3a8;--line:#3a3c40;--accent:#e2915f;--hl:#6b5a12;--chip:#2c2e32}}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.6 "Noto Sans TC","Microsoft JhengHei","PingFang TC",sans-serif}
header{padding:14px 20px;border-bottom:1px solid var(--line);display:flex;gap:16px;align-items:baseline;flex-wrap:wrap}
header h1{margin:0;font-size:18px}
header .stat{color:var(--muted);font-size:13px}
#gate{max-width:360px;margin:18vh auto;background:var(--card);border:1px solid var(--line);border-radius:10px;padding:24px}
#gate h2{margin:0 0 12px;font-size:17px}
input,select,button{font:inherit;color:inherit}
input[type=password],input[type=search]{width:100%;padding:9px 11px;border:1px solid var(--line);border-radius:7px;background:var(--bg)}
button{padding:8px 14px;border:1px solid var(--accent);background:var(--accent);color:#fff;border-radius:7px;cursor:pointer}
button.ghost{background:transparent;color:var(--accent)}
#err{color:#c0392b;font-size:13px;min-height:1.2em;margin-top:8px}
#app{display:none;grid-template-columns:260px 1fr;min-height:calc(100vh - 56px)}
aside{border-right:1px solid var(--line);padding:16px;overflow:auto}
aside label{display:block;font-size:12px;color:var(--muted);margin:12px 0 4px}
aside select{width:100%;padding:6px;border:1px solid var(--line);border-radius:6px;background:var(--card)}
main{padding:16px 20px;overflow:auto;min-width:0}
.tabs{display:flex;gap:6px;margin:12px 0}
.tabs button{background:transparent;color:var(--ink);border-color:var(--line)}
.tabs button.on{background:var(--accent);color:#fff;border-color:var(--accent)}
.res{background:var(--card);border:1px solid var(--line);border-radius:9px;padding:11px 14px;margin:8px 0;cursor:pointer}
.res:hover{border-color:var(--accent)}
.meta{color:var(--muted);font-size:12.5px;display:flex;gap:10px;flex-wrap:wrap}
.chip{background:var(--chip);border-radius:5px;padding:0 6px;font-size:12px}
.sum{margin-top:4px;overflow-wrap:anywhere}
mark{background:var(--hl);color:inherit;border-radius:2px}
#detail{display:none}
#detail table{border-collapse:collapse;width:100%;background:var(--card);margin:10px 0}
#detail td{border:1px solid var(--line);padding:6px 9px;vertical-align:top;overflow-wrap:anywhere}
#detail td:first-child{width:110px;color:var(--muted);white-space:nowrap}
.page{background:var(--card);border:1px solid var(--line);border-radius:9px;padding:12px 14px;margin:10px 0;white-space:pre-wrap;overflow-wrap:anywhere}
.page h4{margin:0 0 6px;font-size:13px;color:var(--muted)}
.nav{display:flex;gap:8px;flex-wrap:wrap;margin:8px 0}
.empty{color:var(--muted);padding:20px 0}
@media (max-width:760px){#app{grid-template-columns:1fr}aside{border-right:0;border-bottom:1px solid var(--line)}}
</style>
</head>
<body>
<header><h1>一貫道國家檔案搜尋</h1><span class="stat" id="stat">本機版・資料加密</span></header>
<div id="gate">
  <h2>請輸入密碼</h2>
  <form id="gf"><input type="password" id="pw" autocomplete="off" autofocus>
  <div style="margin-top:12px"><button type="submit">開啟</button></div></form>
  <div id="err"></div>
</div>
<div id="app">
  <aside>
    <label>關鍵字（空格分開＝全部符合）</label>
    <input type="search" id="q" placeholder="例：中華道德慈善會 社會部">
    <label>卷宗</label><select id="f-case"></select>
    <label>時期</label><select id="f-時期"></select>
    <label>機關類型</label><select id="f-機關類型"></select>
    <label>行動</label><select id="f-行動"></select>
    <label>定性框架</label><select id="f-定性框架"></select>
    <label>排序</label><select id="sort"><option value="file">卷宗內順序</option><option value="date">日期</option></select>
    <div style="margin-top:14px"><button class="ghost" id="reset" type="button">清除條件</button></div>
  </aside>
  <main>
    <div class="tabs"><button data-t="items" class="on">公文（件）</button><button data-t="pages">全文（頁）</button><button data-t="people">人名</button><button data-t="cases">卷宗</button></div>
    <div id="list"></div>
    <div id="detail"></div>
  </main>
</div>
<script>
const BLOB=__BLOB__;
const b64=s=>Uint8Array.from(atob(s),c=>c.charCodeAt(0));
let D=null, tab='items';
const norm=s=>(s||'').replace(/\s+/g,'').replace(/臺/g,'台');
const esc=s=>(s||'').replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
async function unlock(pw){
  const km=await crypto.subtle.importKey('raw',new TextEncoder().encode(pw),'PBKDF2',false,['deriveKey']);
  const key=await crypto.subtle.deriveKey({name:'PBKDF2',salt:b64(BLOB.salt),iterations:BLOB.iter,hash:'SHA-256'},km,{name:'AES-GCM',length:256},false,['decrypt']);
  const gz=await crypto.subtle.decrypt({name:'AES-GCM',iv:b64(BLOB.iv)},key,b64(BLOB.ct));
  const txt=await new Response(new Blob([gz]).stream().pipeThrough(new DecompressionStream('gzip'))).text();
  return JSON.parse(txt);
}
document.getElementById('gf').addEventListener('submit',async e=>{
  e.preventDefault(); const err=document.getElementById('err'); err.textContent='解密中…';
  try{ D=await unlock(document.getElementById('pw').value); document.getElementById('pw').value=''; init(); }
  catch(x){ err.textContent='密碼錯誤，或瀏覽器版本過舊（請用新版 Chrome／Edge／Firefox）。'; }
});
function pagesOf(it){ // "4–6" → [4,5,6]；非數字（未謄打）→ []
  const m=(it['PDF頁']||'').match(/^(\d+)(?:[–-](\d+))?$/); if(!m) return [];
  const a=+m[1], b=+(m[2]||m[1]); const r=[]; for(let i=a;i<=b;i++) r.push(i); return r;
}
function init(){
  document.getElementById('gate').style.display='none';
  document.getElementById('app').style.display='grid';
  D.caseName={}; D.cases.forEach(c=>D.caseName[c['卷宗代號']]=c['案名']);
  D.pageIdx={}; D.pages.forEach(p=>{D.pageIdx[p.c+'-'+p.p]=p; p.n=norm(p.t);});
  D.items.forEach((it,i)=>{it._i=i; it._pages=pagesOf(it); it._n=norm(Object.values(it).filter(v=>typeof v==='string').join('|'));});
  D.pageItem={}; D.items.forEach(it=>it._pages.forEach(p=>D.pageItem[it['卷宗代號']+'-'+p]=it));
  document.getElementById('stat').textContent=`${D.cases.length} 卷宗・${D.items.length} 件・${D.pages.length} 頁全文`;
  fill('f-case',D.cases.map(c=>[c['卷宗代號'],c['卷宗代號']+' '+c['案名']]));
  ['時期','機關類型','行動','定性框架'].forEach(k=>{
    const vals=new Set(); D.items.forEach(it=>(it[k]||'').split('；').forEach(v=>{v=v.trim(); if(v) vals.add(v);}));
    fill('f-'+k,[...vals].sort().map(v=>[v,v]));
  });
  document.querySelectorAll('aside select, #q').forEach(el=>el.addEventListener('input',render));
  document.getElementById('reset').onclick=()=>{document.querySelectorAll('aside select').forEach(s=>s.selectedIndex=0);document.getElementById('q').value='';render();};
  document.querySelectorAll('.tabs button').forEach(b=>b.onclick=()=>{tab=b.dataset.t;document.querySelectorAll('.tabs button').forEach(x=>x.classList.toggle('on',x===b));render();});
  render();
}
function fill(id,opts){const s=document.getElementById(id); s.innerHTML='<option value="">（全部）</option>'+opts.map(([v,l])=>`<option value="${esc(v)}">${esc(l)}</option>`).join('');}
function terms(){return document.getElementById('q').value.split(/\s+/).map(norm).filter(Boolean);}
function hl(text,ts){ if(!ts.length) return esc(text);
  // 以去空白後的比對找原文位置：逐字對應
  const chars=[...text]; const map=[]; let flat='';
  chars.forEach((c,i)=>{ if(!/\s/.test(c)){ map.push(i); flat+=(c==='臺'?'台':c);} });
  const on=new Array(chars.length).fill(false);
  ts.forEach(t=>{let k=flat.indexOf(t); while(k>=0){for(let j=k;j<k+t.length;j++) on[map[j]]=true; k=flat.indexOf(t,k+t.length);}});
  let out='',open=false; chars.forEach((c,i)=>{ if(on[i]&&!open){out+='<mark>';open=true;} if(!on[i]&&open){out+='</mark>';open=false;} out+=esc(c); });
  return out+(open?'</mark>':'');
}
function snippet(text,ts,len=90){ const n=norm(text); let k=ts.length?n.indexOf(ts[0]):0; if(k<0)k=0;
  // 近似：用原文字元位置切
  const chars=[...text]; let cnt=0, start=0; for(let i=0;i<chars.length;i++){ if(!/\s/.test(chars[i])){ if(cnt===Math.max(0,k-30)){start=i;break;} cnt++; } }
  return (start>0?'…':'')+chars.slice(start,start+len).join('')+(start+len<chars.length?'…':'');
}
function filters(){ const f={case:document.getElementById('f-case').value};
  ['時期','機關類型','行動','定性框架'].forEach(k=>f[k]=document.getElementById('f-'+k).value); return f; }
function itemOK(it,f,ts){
  if(f.case&&it['卷宗代號']!==f.case) return false;
  for(const k of ['時期','機關類型','行動','定性框架']) if(f[k]&&!(it[k]||'').split('；').map(s=>s.trim()).includes(f[k])) return false;
  if(!ts.length) return true;
  const pageText=it._pages.map(p=>(D.pageIdx[it['卷宗代號']+'-'+p]||{}).n||'').join('');
  return ts.every(t=>it._n.includes(t)||pageText.includes(t));
}
function render(){
  document.getElementById('detail').style.display='none'; const L=document.getElementById('list'); L.style.display='block';
  const ts=terms(), f=filters();
  if(tab==='items'){
    let rows=D.items.filter(it=>itemOK(it,f,ts));
    if(document.getElementById('sort').value==='date') rows=[...rows].sort((a,b)=>(a['日期（國曆）']||'9').localeCompare(b['日期（國曆）']||'9'));
    L.innerHTML=`<div class="meta">${rows.length} 件</div>`+rows.map(it=>`<div class="res" data-i="${it._i}">
      <div class="meta"><span class="chip">${esc(it['卷宗代號'])}-${esc(String(it['件序']))}</span><span>${esc(it['日期（國曆）']||it['日期原文']||'日期不詳')}</span><span>${esc(it['文種'])}</span><span>頁 ${esc(it['PDF頁'])}</span></div>
      <div><b>${hl(it['發文者']||'',ts)}</b>${it['受文者']?' → '+hl(it['受文者'],ts):''}</div>
      <div class="sum">${hl(it['事由摘要']||'',ts)}</div></div>`).join('')||'<div class="empty">沒有符合的件。</div>';
    L.querySelectorAll('.res').forEach(r=>r.onclick=()=>show(D.items[+r.dataset.i],ts));
  } else if(tab==='pages'){
    if(!ts.length){L.innerHTML='<div class="empty">請輸入關鍵字，搜尋逐頁全文。</div>';return;}
    const rows=D.pages.filter(p=>(!f.case||p.c===f.case)&&ts.every(t=>p.n.includes(t)));
    L.innerHTML=`<div class="meta">${rows.length} 頁</div>`+rows.map(p=>{const it=D.pageItem[p.c+'-'+p.p];
      return `<div class="res" data-k="${p.c}-${p.p}"><div class="meta"><span class="chip">${esc(p.c)} 頁 ${p.p}</span><span>${it?'屬 '+esc(p.c)+'-'+it['件序']+'：'+esc((it['事由摘要']||'').slice(0,40)):''}</span></div>
      <div class="sum">${hl(snippet(p.t,ts),ts)}</div></div>`;}).join('')||'<div class="empty">全文中沒有找到。</div>';
    L.querySelectorAll('.res').forEach(r=>r.onclick=()=>{const it=D.pageItem[r.dataset.k]; if(it) show(it,ts); else showPage(r.dataset.k,ts);});
  } else if(tab==='people'){
    const cnt={}; D.items.forEach(it=>(it['人名']||'').split('；').forEach(n=>{n=n.trim(); if(n){(cnt[n]=cnt[n]||[]).push(it);}}));
    let names=Object.keys(cnt).sort((a,b)=>cnt[b].length-cnt[a].length);
    if(ts.length) names=names.filter(n=>ts.every(t=>norm(n+JSON.stringify(D.people[n]||{})).includes(t)));
    L.innerHTML=`<div class="meta">${names.length} 人</div>`+names.map(n=>{const p=D.people[n]||{};
      return `<div class="res" data-n="${esc(n)}"><div><b>${hl(n,ts)}</b> <span class="meta">${cnt[n].length} 件</span></div>
      <div class="sum">${esc([p['身分'],p['派系'],p['去向']].filter(Boolean).join('・'))}</div></div>`;}).join('');
    L.querySelectorAll('.res').forEach(r=>r.onclick=()=>{document.getElementById('q').value=r.dataset.n;tab='items';document.querySelectorAll('.tabs button').forEach(x=>x.classList.toggle('on',x.dataset.t==='items'));render();});
  } else {
    L.innerHTML=D.cases.map(c=>`<div class="res" data-c="${esc(c['卷宗代號'])}"><div class="meta"><span class="chip">${esc(c['卷宗代號'])}</span><span>${esc(c['檔號'])}</span><span>${esc(c['典藏機關'])}</span></div>
      <div><b>${esc(c['案名'])}</b>　${esc(c['起訖'])}</div><div class="sum">${esc(c['摘要'])}</div><div class="meta">${esc(c['謄打範圍'])}・${esc(c['公開狀態'])}</div></div>`).join('');
    L.querySelectorAll('.res').forEach(r=>r.onclick=()=>{document.getElementById('f-case').value=r.dataset.c;tab='items';document.querySelectorAll('.tabs button').forEach(x=>x.classList.toggle('on',x.dataset.t==='items'));render();});
  }
}
function show(it,ts){
  document.getElementById('list').style.display='none'; const d=document.getElementById('detail'); d.style.display='block';
  const same=D.items.filter(x=>x['卷宗代號']===it['卷宗代號']); const k=same.indexOf(it);
  const prev=same[k-1], next=same[k+1];
  d.innerHTML=`<div class="nav"><button class="ghost" id="back">← 回結果</button>${prev?'<button class="ghost" id="prev">上一件</button>':''}${next?'<button class="ghost" id="next">下一件</button>':''}</div>
    <h3 style="margin:6px 0">${esc(D.caseName[it['卷宗代號']]||'')}　第 ${esc(String(it['件序']))} 件</h3>
    <table>${D.columns.map(c=>`<tr><td>${esc(c)}</td><td>${hl(String(it[c]||''),ts)}</td></tr>`).join('')}</table>
    ${it._pages.map(p=>{const pg=D.pageIdx[it['卷宗代號']+'-'+p]; return pg?`<div class="page"><h4>全文　PDF 頁 ${p}</h4>${hl(pg.t,ts)}</div>`:'';}).join('')||'<div class="empty">此件沒有對應的全文頁。</div>'}`;
  document.getElementById('back').onclick=render;
  if(prev) document.getElementById('prev').onclick=()=>show(prev,ts);
  if(next) document.getElementById('next').onclick=()=>show(next,ts);
  window.scrollTo(0,0);
}
function showPage(key,ts){ const pg=D.pageIdx[key]; const d=document.getElementById('detail');
  document.getElementById('list').style.display='none'; d.style.display='block';
  d.innerHTML=`<div class="nav"><button class="ghost" id="back">← 回結果</button></div><div class="page"><h4>${esc(key)}</h4>${hl(pg.t,ts)}</div>`;
  document.getElementById('back').onclick=render; }
</script>
</body>
</html>
"""

if __name__ == "__main__":
    main()
