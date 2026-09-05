# -*- coding: utf-8 -*-
"""由 cues.json 產出 After Effects 專案建置腳本（.jsx）。

跑法：AE 開啟後「檔案 → 指令碼 → 執行指令碼檔案」選這支 .jsx，
它會建兩個合成：
    板面      15200x9400，所有節點、連線、配圖
    主鏡頭    1920x1080，把板面當圖層，用錨點＋縮放做鏡頭運動，另有字幕與幕名
之後所有東西都能在 AE 裡手調（節點位置、字級、緩動、加特效）。

跟 render.mjs 的差別：render.mjs 是全自動直接出片；這支是要進 AE 手工精修時用的。
兩邊吃同一份 cues.json，所以改腳本後兩條路都會同步。
"""
import json
from pathlib import Path

PROJ = Path(r"G:\我的雲端硬碟\創作\影片創作\人魚島解說")
OUT = PROJ / "人魚島黑板_建置.jsx"

KIND_COLOR = {          # 粉筆色，和 board.html 對齊
    "intro": [1.00, 0.93, 0.69], "scene": [0.75, 0.89, 1.00],
    "hub": [1.00, 0.84, 0.84], "role": [1.00, 0.91, 0.79],
    "concept": [0.78, 1.00, 0.84], "myth": [0.89, 0.80, 1.00],
    "outro": [1.00, 0.87, 0.77],
}
PREFIX = {"siren": "賽蓮", "minotaur": "米諾陶洛斯", "yamata": "八岐大蛇",
          "prometheus": "普羅米修斯", "houji": "詩經生民", "happyaku": "八百比丘尼"}

TITLE_SIZE, BULLET_SIZE, LINE_H, PAD = 62, 42, 65, 40


def cam_for(node, h):
    """跟 board.html 的 camFor 同一套算法，確保兩條路徑鏡頭一致。"""
    pad = 250
    w = node["w"] + pad * 2
    hh = h + pad * 2
    s = min(1920 / w, 1080 / hh)
    s = max(0.11, min(0.85, s))
    return node["x"] + node["w"] / 2, node["y"] + h / 2, s


def node_height(node):
    """AE 這邊沒有排版引擎，用字級估高度（跟 HTML 量到的差不多）。"""
    return PAD + TITLE_SIZE + 24 + len(node["bullets"]) * LINE_H + PAD


def build():
    data = json.loads((PROJ / "cues.json").read_text(encoding="utf-8"))
    nodes = {n["id"]: n for n in data["nodes"]}
    heights = {nid: node_height(n) for nid, n in nodes.items()}

    # 節點與條目的出現時間
    first_seen, bullet_time = {}, {}
    for c in data["cues"]:
        first_seen.setdefault(c["node"], c["t"])
        for k in range(c["reveal"]):
            bullet_time.setdefault((c["node"], k), c["t"])

    # 鏡頭關鍵影格：(時間, 錨點x, 錨點y, 縮放%)
    keys, prev = [], None
    for i, c in enumerate(data["cues"]):
        n = nodes[c["node"]]
        cx, cy, s = cam_for(n, heights[c["node"]])
        if prev is None:
            keys.append([round(c["t"], 3), cx, cy, s * 100])
        else:
            travel = prev["node"] != c["node"]
            T = (1.4 if prev["group"] != c["group"] else 0.95) if travel else 0.3
            pn = nodes[prev["node"]]
            pcx, pcy, ps = cam_for(pn, heights[prev["node"]])
            keys.append([round(c["t"], 3), pcx, pcy, ps * 100])
            keys.append([round(c["t"] + T, 3), cx, cy, s * 100])
        keys.append([round(c["t"] + c["dur"], 3), cx, cy, s * 100 * 1.022])
        prev = c

    imgs = {}
    pd_dir = PROJ / "素材" / "公有領域"
    for nid, n in nodes.items():
        key = PREFIX.get(n.get("asset") or "")
        if key and pd_dir.exists():
            hit = next((p for p in sorted(pd_dir.glob(f"{key}_*")) if p.is_file()), None)
            if hit:
                imgs[nid] = str(hit)
    mascot = PROJ / "素材" / "多馬豬" / "多馬豬.png"
    if mascot.exists():
        imgs.setdefault("N01", str(mascot))
        imgs.setdefault("N73", str(mascot))

    payload = dict(
        board=data["board"], total=data["total"],
        nodes=[dict(id=n["id"], kind=n["kind"], x=n["x"], y=n["y"], w=n["w"],
                    h=heights[n["id"]], title=n["title"], bullets=n["bullets"],
                    color=KIND_COLOR.get(n["kind"], [1, 1, 1]),
                    appear=first_seen.get(n["id"]),
                    bulletTimes=[bullet_time.get((n["id"], k)) for k in range(len(n["bullets"]))],
                    img=imgs.get(n["id"], ""))
               for n in data["nodes"] if n["id"] in first_seen],
        edges=[dict(a=e["a"], b=e["b"], label=e["label"],
                    t=max(first_seen.get(e["a"], 1e9), first_seen.get(e["b"], 1e9)) + 0.4)
               for e in data["edges"]
               if e["a"] in first_seen and e["b"] in first_seen],
        cam=keys,
        subs=[dict(t=c["t"], text=c["text"]) for c in data["cues"]],
        chapters=[dict(t=c["t"], text=c["chapter"]) for c in data["cues"] if c["chapter"]],
    )

    OUT.write_text(JSX_TEMPLATE.replace("__DATA__", json.dumps(payload, ensure_ascii=False)),
                   encoding="utf-8")
    print(f"寫出 {OUT}（{len(payload['nodes'])} 節點／{len(keys)} 個鏡頭關鍵影格）")


JSX_TEMPLATE = r"""// 人魚島解說 — 無限黑板 AE 專案建置腳本（由 build_ae_jsx.py 產生，勿手改此檔頂端資料）
// AE：檔案 → 指令碼 → 執行指令碼檔案
(function () {
  var D = __DATA__;
  var FONT = "DFKaiShu-SB-Estd-BF";     // 標楷體；AE 找不到時會自動退回預設字體
  var FPS = 30;

  app.beginUndoGroup("建立無限黑板");
  var proj = app.project || app.newProject();

  var board = proj.items.addComp("板面", D.board.w, D.board.h, 1, D.total + 3, FPS);
  var bg = board.layers.addSolid([0.055, 0.086, 0.071], "黑板底", D.board.w, D.board.h, 1);
  bg.locked = true;

  function textLayer(comp, str, size, color, x, y) {
    var L = comp.layers.addText(str);
    var doc = L.property("Source Text").value;
    doc.resetCharStyle();
    doc.fontSize = size;
    doc.fillColor = color;
    doc.applyFill = true;
    doc.applyStroke = false;
    doc.justification = ParagraphJustification.LEFT_JUSTIFY;
    try { doc.font = FONT; } catch (e) {}
    L.property("Source Text").setValue(doc);
    L.property("Transform").property("Position").setValue([x, y]);
    return L;
  }

  function fadeIn(layer, t, dur) {
    var op = layer.property("Transform").property("Opacity");
    op.setValueAtTime(0, 0);
    op.setValueAtTime(Math.max(t - 0.001, 0.001), 0);
    op.setValueAtTime(t + (dur || 0.3), 100);
  }

  // ── 節點 ────────────────────────────────────────────────
  for (var i = 0; i < D.nodes.length; i++) {
    var n = D.nodes[i];
    var box = board.layers.addShape();
    box.name = n.id + " 框";
    var grp = box.property("Contents").addProperty("ADBE Vector Group");
    var rect = grp.property("Contents").addProperty("ADBE Vector Shape - Rect");
    rect.property("Size").setValue([n.w, n.h]);
    rect.property("Roundness").setValue(26);
    var stroke = grp.property("Contents").addProperty("ADBE Vector Graphic - Stroke");
    stroke.property("Color").setValue(n.color);
    stroke.property("Stroke Width").setValue(3);
    stroke.property("Opacity").setValue(55);
    box.property("Transform").property("Position").setValue([n.x + n.w / 2, n.y + n.h / 2]);
    fadeIn(box, n.appear);

    var t = textLayer(board, n.title, __TITLE__, n.color, n.x + 40, n.y + 40 + __TITLE__);
    t.name = n.id + " 標題";
    fadeIn(t, n.appear);

    for (var k = 0; k < n.bullets.length; k++) {
      var by = n.y + 40 + __TITLE__ + 24 + (k + 1) * __LINE__;
      var b = textLayer(board, "・" + n.bullets[k], __BULLET__, [0.93, 0.95, 0.91], n.x + 62, by);
      b.name = n.id + " 點" + (k + 1);
      fadeIn(b, n.bulletTimes[k] === null ? n.appear : n.bulletTimes[k], 0.25);
    }

    if (n.img) {
      var f = new File(n.img);
      if (f.exists) {
        var io = new ImportOptions(f);
        var item = proj.importFile(io);
        var L = board.layers.add(item);
        L.name = n.id + " 配圖";
        var sc = Math.min(320 / item.height, (n.w * 0.42) / item.width) * 100;
        L.property("Transform").property("Scale").setValue([sc, sc]);
        L.property("Transform").property("Position").setValue(
          [n.x + n.w - 34 - item.width * sc / 200, n.y + n.h - 30 - item.height * sc / 200]);
        fadeIn(L, n.appear + 0.4);
      }
    }
  }

  // ── 連線 ────────────────────────────────────────────────
  var byId = {};
  for (var i2 = 0; i2 < D.nodes.length; i2++) byId[D.nodes[i2].id] = D.nodes[i2];
  for (var e = 0; e < D.edges.length; e++) {
    var ed = D.edges[e], A = byId[ed.a], B = byId[ed.b];
    if (!A || !B) continue;
    var line = board.layers.addShape();
    line.name = ed.a + "→" + ed.b;
    var g2 = line.property("Contents").addProperty("ADBE Vector Group");
    var path = g2.property("Contents").addProperty("ADBE Vector Shape - Group");
    var sh = new Shape();
    sh.vertices = [[A.x + A.w / 2, A.y + A.h / 2], [B.x + B.w / 2, B.y + B.h / 2]];
    sh.closed = false;
    path.property("Path").setValue(sh);
    var st = g2.property("Contents").addProperty("ADBE Vector Graphic - Stroke");
    st.property("Color").setValue([0.93, 0.95, 0.91]);
    st.property("Stroke Width").setValue(5);
    st.property("Opacity").setValue(42);
    var trim = g2.property("Contents").addProperty("ADBE Vector Filter - Trim");
    var end = trim.property("End");
    end.setValueAtTime(ed.t, 0);
    end.setValueAtTime(ed.t + 0.8, 100);
    line.moveToEnd();
  }

  // ── 主鏡頭 ──────────────────────────────────────────────
  var main = proj.items.addComp("主鏡頭", 1920, 1080, 1, D.total + 3, FPS);
  var boardLayer = main.layers.add(board);
  boardLayer.name = "板面（鏡頭）";
  var anchor = boardLayer.property("Transform").property("Anchor Point");
  var scale = boardLayer.property("Transform").property("Scale");
  boardLayer.property("Transform").property("Position").setValue([960, 540]);
  for (var c = 0; c < D.cam.length; c++) {
    var kf = D.cam[c];
    anchor.setValueAtTime(kf[0], [kf[1], kf[2]]);
    scale.setValueAtTime(kf[0], [kf[3], kf[3]]);
  }
  // 緩動：全部設成 easy ease，鏡頭才不會硬邦邦
  for (var q = 1; q <= anchor.numKeys; q++) {
    try { anchor.setInterpolationTypeAtKey(q, KeyframeInterpolationType.BEZIER, KeyframeInterpolationType.BEZIER); } catch (e2) {}
  }
  for (var q2 = 1; q2 <= scale.numKeys; q2++) {
    try { scale.setInterpolationTypeAtKey(q2, KeyframeInterpolationType.BEZIER, KeyframeInterpolationType.BEZIER); } catch (e3) {}
  }

  // 字幕（配音對稿用；正式版把這層關掉即可）
  var sub = main.layers.addText("");
  var sdoc = sub.property("Source Text").value;
  sdoc.resetCharStyle(); sdoc.fontSize = 46; sdoc.fillColor = [0.95, 0.96, 0.93];
  sdoc.applyFill = true; sdoc.justification = ParagraphJustification.CENTER_JUSTIFY;
  try { sdoc.font = "MicrosoftJhengHeiRegular"; } catch (e4) {}
  sub.property("Source Text").setValue(sdoc);
  sub.property("Transform").property("Position").setValue([960, 1000]);
  sub.name = "字幕";
  var srcT = sub.property("Source Text");
  for (var s2 = 0; s2 < D.subs.length; s2++) srcT.setValueAtTime(D.subs[s2].t, D.subs[s2].text);

  // 幕名
  var chap = main.layers.addText("");
  var cdoc = chap.property("Source Text").value;
  cdoc.resetCharStyle(); cdoc.fontSize = 52; cdoc.fillColor = [1, 0.96, 0.85];
  cdoc.applyFill = true;
  try { cdoc.font = FONT; } catch (e5) {}
  chap.property("Source Text").setValue(cdoc);
  chap.property("Transform").property("Position").setValue([120, 110]);
  chap.name = "幕名";
  var cSrc = chap.property("Source Text");
  var cOp = chap.property("Transform").property("Opacity");
  for (var s3 = 0; s3 < D.chapters.length; s3++) {
    var ct = D.chapters[s3].t;
    cSrc.setValueAtTime(ct, D.chapters[s3].text);
    cOp.setValueAtTime(ct, 0); cOp.setValueAtTime(ct + 0.5, 100);
    cOp.setValueAtTime(ct + 2.3, 100); cOp.setValueAtTime(ct + 2.8, 0);
  }

  main.openInViewer();
  app.endUndoGroup();
  alert("建好了：板面 " + D.board.w + "x" + D.board.h + "，主鏡頭 " + Math.round(D.total) + " 秒。\n配音錄好後重跑 make_cues.py 再產一次即可對齊。");
})();
"""

JSX_TEMPLATE = (JSX_TEMPLATE.replace("__TITLE__", str(TITLE_SIZE))
                .replace("__BULLET__", str(BULLET_SIZE))
                .replace("__LINE__", str(LINE_H)))

if __name__ == "__main__":
    build()
