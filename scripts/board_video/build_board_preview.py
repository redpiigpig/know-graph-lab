# -*- coding: utf-8 -*-
"""產出一份可以自己拖拉縮放的「整張黑板」HTML，讓使用者直接看版面並提修改意見。

跟出片用的 board.html 共用同一份 CSS（從那支檔案抽出來），差別是：
  ・所有節點與條目一次全部顯示（不照時間軸浮現）
  ・滑鼠拖曳平移、滾輪縮放、可切三種風格、可顯示鏡頭路徑與節點編號
  ・配圖縮到 700px 內嵌成 data URI，整份單檔可離線開

輸出：<專案>/人魚島黑板_全景.html
"""
import base64
import io
import json
import re
from pathlib import Path

PROJ = Path(r"G:\我的雲端硬碟\創作\影片創作\人魚島解說")
HERE = Path(__file__).parent
OUT = PROJ / "人魚島黑板_全景.html"

PREFIX = {"siren": "賽蓮", "minotaur": "米諾陶洛斯", "yamata": "八岐大蛇",
          "prometheus": "普羅米修斯", "houji": "詩經生民", "happyaku": "八百比丘尼"}
OWN = {"N01": ("劇照", "作者被說毫無人性.jpg"), "N02": ("劇照", "電影劇照.webp"),
       "N20": ("劇照", "電影劇照.webp"), "N73": ("多馬豬", "多馬豬_卡通.png")}


def data_uri(path: Path, max_w=700) -> str | None:
    try:
        from PIL import Image
        im = Image.open(path).convert("RGB")
        if im.width > max_w:
            im = im.resize((max_w, round(im.height * max_w / im.width)))
        buf = io.BytesIO()
        im.save(buf, "JPEG", quality=80)
        return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()
    except Exception as e:
        print(f"  圖片處理失敗 {path.name}: {e}")
        return None


def collect_images(nodes) -> dict:
    imgs = {}
    pd_dir = PROJ / "素材" / "公有領域"
    for n in nodes:
        nid = n["id"]
        if nid in OWN:
            sub, name = OWN[nid]
            p = PROJ / "素材" / sub / name
            if p.exists():
                imgs[nid] = data_uri(p)
                continue
        key = PREFIX.get(n.get("asset") or "")
        if key and pd_dir.exists():
            hit = next((p for p in sorted(pd_dir.glob(f"{key}_*")) if p.is_file()), None)
            if hit:
                imgs[nid] = data_uri(hit)
    return {k: v for k, v in imgs.items() if v}


def main():
    data = json.loads((PROJ / "cues.json").read_text(encoding="utf-8"))
    style = re.search(r"<style>(.*?)</style>", (HERE / "board.html").read_text(encoding="utf-8"),
                      re.S).group(1)
    imgs = collect_images(data["nodes"])

    # 每個節點在哪幾條 cue 被講到（讓使用者看得出黑板順序）
    order, seen = [], set()
    for c in data["cues"]:
        if c["node"] not in seen:
            seen.add(c["node"])
            order.append(dict(node=c["node"], t=c["t"], chapter=c["chapter"]))
    talk = {}
    for c in data["cues"]:
        talk.setdefault(c["node"], []).append(c["text"])

    payload = dict(board=data["board"], nodes=data["nodes"], edges=data["edges"],
                   order=order, images=imgs,
                   talk={k: v[:3] for k, v in talk.items()}, total=data["total"])

    OUT.write_text(TEMPLATE.replace("__STYLE__", style)
                   .replace("__DATA__", json.dumps(payload, ensure_ascii=False)),
                   encoding="utf-8")
    print(f"寫出 {OUT}（{OUT.stat().st_size / 1048576:.1f} MB，{len(imgs)} 張配圖）")


TEMPLATE = r"""<!doctype html>
<meta charset="utf-8">
<title>人魚島解說・整張黑板</title>
<style>
__STYLE__
/* ── 預覽專用 ── */
html, body { width: 100%; height: 100%; overflow: hidden; }
#viewport { width: 100vw; height: 100vh; cursor: grab; }
#viewport.drag { cursor: grabbing; }
#bar { position: fixed; left: 0; right: 0; top: 0; z-index: 9; display: flex; gap: 10px;
  align-items: center; padding: 10px 16px; background: rgba(20,24,22,.86); color: #eee;
  font: 14px/1.5 "Microsoft JhengHei", sans-serif; flex-wrap: wrap; }
#bar button { font: 13px "Microsoft JhengHei", sans-serif; padding: 5px 12px; cursor: pointer;
  border: 1px solid #667; background: #2b3330; color: #eee; border-radius: 6px; }
#bar button.on { background: #d8c48a; color: #222; border-color: #d8c48a; }
#bar .sp { opacity: .65; margin-left: 6px; }
#tip { position: fixed; right: 14px; bottom: 14px; z-index: 9; max-width: 420px;
  background: rgba(20,24,22,.9); color: #eee; padding: 12px 14px; border-radius: 10px;
  font: 13px/1.7 "Microsoft JhengHei", sans-serif; display: none; }
#tip b { color: #ffd98a; }
.node { cursor: pointer; }
.node.hl { outline: 4px solid #ffcf5c; outline-offset: 6px; }
#pathsvg { position: absolute; left: 0; top: 0; pointer-events: none; display: none; }
#pathsvg path { fill: none; stroke: rgba(255,180,80,.75); stroke-width: 6; stroke-dasharray: 20 16; }
#pathsvg circle { fill: rgba(255,180,80,.9); }
#pathsvg text { fill: #fff; font: bold 40px sans-serif; text-anchor: middle; }
.badge { position: absolute; z-index: 3; background: #ffcf5c; color: #23281f; border-radius: 999px;
  width: 74px; height: 74px; line-height: 74px; text-align: center; font: bold 34px sans-serif;
  display: none; }
body.showorder .badge { display: block; }
</style>
<div id="bar">
  <b>整張黑板</b>
  <span class="sp">拖曳平移・滾輪縮放・點節點看該格講什麼</span>
  <button id="fit">整板</button>
  <button data-th="paper" class="on">米色手帳</button>
  <button data-th="chalk">綠黑板</button>
  <button data-th="neon">知識圖譜</button>
  <button id="ord">顯示講述順序</button>
  <button id="pth">顯示鏡頭路徑</button>
  <span class="sp" id="info"></span>
</div>
<div id="viewport">
  <div id="board"><svg id="edges"></svg><svg id="pathsvg"></svg></div>
</div>
<div id="tip"></div>
<script>
const D = __DATA__;
const board = document.getElementById('board'), vp = document.getElementById('viewport');
const svg = document.getElementById('edges'), psvg = document.getElementById('pathsvg');
const nodeById = {};
board.style.width = D.board.w + 'px'; board.style.height = D.board.h + 'px';
svg.setAttribute('width', D.board.w); svg.setAttribute('height', D.board.h);
psvg.setAttribute('width', D.board.w); psvg.setAttribute('height', D.board.h);
document.body.className = 'theme-paper';

const orderIdx = {};
D.order.forEach((o, i) => orderIdx[o.node] = i + 1);

D.nodes.forEach(n => {
  nodeById[n.id] = n;
  const d = document.createElement('div');
  d.className = 'node k-' + n.kind + (D.images[n.id] ? '' : ' noimg');
  d.style.cssText += `left:${n.x}px;top:${n.y}px;max-width:${n.w}px;opacity:1;` +
    `transform:rotate(${(n.id.charCodeAt(2) % 5 - 2) * 0.22}deg)`;
  d.innerHTML = `<div class="txt"><div class="ttl">${n.title}</div><ul>` +
    n.bullets.map(b => `<li style="opacity:1">${b}</li>`).join('') + '</ul></div>' +
    (D.images[n.id] ? `<img src="${D.images[n.id]}">` : '');
  d.onclick = () => showTip(n);
  board.appendChild(d);
  n._el = d;
  const b = document.createElement('div');
  b.className = 'badge';
  b.textContent = orderIdx[n.id] || '';
  b.style.left = (n.x - 30) + 'px'; b.style.top = (n.y - 30) + 'px';
  board.appendChild(b);
});
// 量到真實高度後才畫連線與路徑，跟出片端同一套邏輯
D.nodes.forEach(n => n._h = n._el.offsetHeight);

D.edges.forEach(e => {
  const a = nodeById[e.a], b = nodeById[e.b];
  if (!a || !b) return;
  const ax = a.x + a.w / 2, ay = a.y + a._h / 2, bx = b.x + b.w / 2, by = b.y + b._h / 2;
  const mx = (ax + bx) / 2 + (by - ay) * .07, my = (ay + by) / 2 + (ax - bx) * .07;
  const p = document.createElementNS('http://www.w3.org/2000/svg', 'path');
  p.setAttribute('d', `M ${ax} ${ay} Q ${mx} ${my} ${bx} ${by}`);
  svg.appendChild(p);
  if (e.label) {
    const t = document.createElementNS('http://www.w3.org/2000/svg', 'text');
    t.setAttribute('x', mx); t.setAttribute('y', my); t.setAttribute('text-anchor', 'middle');
    t.style.opacity = .8; t.textContent = e.label;
    svg.appendChild(t);
  }
});

// 鏡頭走位：把講述順序連成一條線
let dpath = '';
D.order.forEach((o, i) => {
  const n = nodeById[o.node];
  const x = n.x + n.w / 2, y = n.y + n._h / 2;
  dpath += (i ? ' L ' : 'M ') + x + ' ' + y;
  const c = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
  c.setAttribute('cx', x); c.setAttribute('cy', y); c.setAttribute('r', 16);
  psvg.appendChild(c);
});
const pp = document.createElementNS('http://www.w3.org/2000/svg', 'path');
pp.setAttribute('d', dpath); psvg.insertBefore(pp, psvg.firstChild);

let s = 0.1, ox = 0, oy = 0;
function apply() {
  board.style.transform = `translate(${ox}px,${oy}px) scale(${s})`;
  document.getElementById('info').textContent =
    `縮放 ${(s * 100).toFixed(0)}%　板面 ${D.board.w}×${D.board.h}　節點 ${D.nodes.length}　全片估 ${Math.floor(D.total / 60)} 分 ${Math.round(D.total % 60)} 秒`;
}
function fit() {
  s = Math.min(innerWidth / D.board.w, (innerHeight - 60) / D.board.h) * 0.96;
  ox = (innerWidth - D.board.w * s) / 2; oy = 60 + (innerHeight - 60 - D.board.h * s) / 2;
  apply();
}
document.getElementById('fit').onclick = fit;
vp.addEventListener('wheel', ev => {
  ev.preventDefault();
  const k = ev.deltaY < 0 ? 1.12 : 1 / 1.12;
  const mx = ev.clientX, my = ev.clientY;
  ox = mx - (mx - ox) * k; oy = my - (my - oy) * k;
  s *= k; apply();
}, { passive: false });
let drag = null;
vp.addEventListener('pointerdown', ev => { drag = [ev.clientX - ox, ev.clientY - oy]; vp.classList.add('drag'); });
addEventListener('pointerup', () => { drag = null; vp.classList.remove('drag'); });
addEventListener('pointermove', ev => { if (drag) { ox = ev.clientX - drag[0]; oy = ev.clientY - drag[1]; apply(); } });

document.querySelectorAll('#bar button[data-th]').forEach(b => b.onclick = () => {
  document.body.className = 'theme-' + b.dataset.th +
    (document.body.classList.contains('showorder') ? ' showorder' : '');
  document.querySelectorAll('#bar button[data-th]').forEach(x => x.classList.toggle('on', x === b));
});
document.getElementById('ord').onclick = function () {
  document.body.classList.toggle('showorder');
  this.classList.toggle('on', document.body.classList.contains('showorder'));
};
document.getElementById('pth').onclick = function () {
  const on = psvg.style.display !== 'block';
  psvg.style.display = on ? 'block' : 'none';
  this.classList.toggle('on', on);
};

function showTip(n) {
  document.querySelectorAll('.node').forEach(e => e.classList.remove('hl'));
  n._el.classList.add('hl');
  const tip = document.getElementById('tip');
  const idx = orderIdx[n.id], o = D.order[idx - 1];
  const mm = o ? `${String(Math.floor(o.t / 60)).padStart(2, '0')}:${String(Math.round(o.t % 60)).padStart(2, '0')}` : '—';
  tip.innerHTML = `<b>${n.title}</b>（${n.id}・第 ${idx} 站・約 ${mm} 講到）<br>` +
    (D.talk[n.id] || []).map(t => '「' + t + '」').join('<br>');
  tip.style.display = 'block';
}
fit();
</script>
"""

if __name__ == "__main__":
    main()
