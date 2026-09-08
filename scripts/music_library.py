# -*- coding: utf-8 -*-
"""建一個「可商用、可改作、純器樂」的配樂庫，並標好每一首的資料。

起因：人魚島那批 27 首配樂裡，18 首帶 NC（非商業性）、9 首帶 ND（禁止改作）或 SA，
真正能用在營利頻道的只有 2 首——當初抓素材時沒有設授權過濾。這支腳本把這件事做對。

主來源：incompetech（Kevin MacLeod）的完整目錄 `pieces.json`，1,442 首，
**全部 CC BY 4.0、全部純器樂**，每首附 feel／genre／樂器／BPM／長度／描述。
官方 FAQ 明文：YouTube 可營利，唯一要求是標示。標示格式原文：

    Title Kevin MacLeod (incompetech.com)
    Licensed under Creative Commons: By Attribution 4.0
    https://creativecommons.org/licenses/by/4.0/

用法：
    python music_library.py --plan            # 看分類與數量，不下載
    python music_library.py --run             # 下載（可續跑）
    python music_library.py --run --mood 黑暗懸疑
    python music_library.py --index           # 重出索引網頁與授權標示
    python music_library.py --loudness        # 量響度（慢，可分次跑）
"""
import argparse
import csv
import html
import json
import re
import subprocess
import time
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

CATALOG = "https://incompetech.com/music/royalty-free/pieces.json"
MP3 = "https://incompetech.com/music/royalty-free/mp3-royaltyfree/"
ROOT = Path(r"G:\我的雲端硬碟\創作\影片創作\_素材庫\配樂庫")
UA = {"User-Agent": "know-graph-lab/1.0 (personal video project)"}

# 情緒桶 → incompetech 的 feel 標籤。順序就是優先序：一首只進第一個中的桶，
# 這樣資料夾之間不會重複，挑的時候才不會同一首看三遍。
MOODS = [
    ("神話史詩", ["Epic", "Action", "Intense", "Aggressive"]),
    ("黑暗懸疑", ["Eerie", "Unnerving", "Suspenseful", "Dark", "Mysterious"]),
    ("莊嚴沉思", ["Somber", "Mystical"]),
    ("思辨鋼琴", ["Calm", "Calming"]),
    ("溫暖收束", ["Uplifting", "Relaxed"]),
    ("開場輕快", ["Bright", "Bouncy", "Humorous"]),
    ("敘事鋪底", ["Grooving", "Driving"]),
]
OTHER = "其他"
VOCAL_HINT = re.compile(r"choir|vocal|voice|chant|sing", re.I)
BAD = re.compile(r'[\\/:*?"<>|\r\n\t]')


def fetch(url, tries=3, timeout=90):
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout) as r:
                return r.read()
        except Exception:
            if i == tries - 1:
                raise
            time.sleep(2 * (i + 1))


def secs(hhmmss):
    try:
        p = [int(x) for x in (hhmmss or "").split(":")]
        return p[0] * 3600 + p[1] * 60 + p[2] if len(p) == 3 else 0
    except Exception:
        return 0


def bucket(piece):
    feels = [f.strip() for f in (piece.get("feel") or "").split(",") if f.strip()]
    for name, tags in MOODS:
        if any(t in feels for t in tags):
            return name
    return OTHER


def catalog():
    cache = ROOT / "_metadata" / "incompetech_pieces.json"
    cache.parent.mkdir(parents=True, exist_ok=True)
    if not cache.exists():
        cache.write_bytes(fetch(CATALOG))
    pieces = json.loads(cache.read_text(encoding="utf-8"))
    out = []
    for p in pieces:
        fn = p.get("filename") or ""
        if not fn.lower().endswith(".mp3"):
            continue
        mood = bucket(p)
        out.append({
            "title": p.get("title") or Path(fn).stem,
            "filename": fn,
            "mood": mood,
            "feel": p.get("feel") or "",
            "instruments": p.get("instruments") or "",
            "bpm": p.get("bpm") or "",
            "length": p.get("length") or "",
            "seconds": secs(p.get("length")),
            "description": (p.get("description") or "").strip(),
            "vocal_hint": bool(VOCAL_HINT.search(p.get("instruments") or "")),
            "url": MP3 + urllib.parse.quote(fn),
            "path": str(Path(mood) / BAD.sub("", fn)),
            "license": "CC BY 4.0",
            "creator": "Kevin MacLeod",
            "source": "https://incompetech.com/music/royalty-free/music.html",
        })
    return out


def download(t):
    dest = ROOT / t["path"]
    if dest.exists() and dest.stat().st_size > 10240:
        return "skip"
    dest.parent.mkdir(parents=True, exist_ok=True)
    try:
        data = fetch(t["url"], timeout=180)
        tmp = dest.with_suffix(".part")
        tmp.write_bytes(data)
        tmp.replace(dest)
        return "ok"
    except Exception as e:
        print(f"\n  失敗 {t['filename']}：{str(e)[:80]}")
        return "fail"


def loudness(path: Path):
    """量整合響度（只看前 90 秒，全曲太慢）。"""
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-t", "90", "-i", str(path),
                        "-af", "ebur128=framelog=quiet", "-f", "null", "-"],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    m = re.search(r"I:\s*(-?\d+\.?\d*)\s*LUFS", r.stderr or "")
    return float(m.group(1)) if m else None


def write_index(tracks, loud):
    """一頁可以直接試聽的索引（本機開，audio 指向同資料夾的檔案）。"""
    rows = []
    for t in sorted(tracks, key=lambda x: (x["mood"], x["title"])):
        if not (ROOT / t["path"]).exists():
            continue
        lu = loud.get(t["path"])
        rows.append((t, lu))
    by_mood = {}
    for t, lu in rows:
        by_mood.setdefault(t["mood"], []).append((t, lu))

    parts = ["""<!doctype html><meta charset="utf-8"><title>配樂庫</title>
<style>
body{font-family:"Noto Sans TC","Microsoft JhengHei",system-ui,sans-serif;margin:0;
 background:#f4f6f6;color:#161c1e;line-height:1.6}
.wrap{max-width:1180px;margin:0 auto;padding:28px 20px 80px}
h1{font-size:28px;margin:0 0 4px}
.sub{color:#5b696d;margin:0 0 20px}
h2{font-size:20px;margin:34px 0 10px;padding-bottom:6px;border-bottom:2px solid #0d6f78;color:#0d6f78}
table{border-collapse:collapse;width:100%;background:#fff;font-size:14px;
 border:1px solid #d5dedf;border-radius:4px;overflow:hidden}
th{background:#eaf0f0;text-align:left;padding:8px 10px;font-size:12px;color:#5b696d;white-space:nowrap}
td{padding:7px 10px;border-top:1px solid #edf1f2;vertical-align:top}
td.n{font-variant-numeric:tabular-nums;white-space:nowrap;color:#3d4a4e}
audio{height:32px;width:210px}
.warn{background:#fdf0d5;color:#8a5a00;padding:1px 6px;border-radius:3px;font-size:12px}
.note{background:#fff;border-left:3px solid #0d6f78;padding:12px 16px;margin:0 0 18px;font-size:14px}
</style>
<div class="wrap"><h1>配樂庫</h1>
<p class="sub">Kevin MacLeod／incompetech ── 全部 CC BY 4.0、全部純器樂、YouTube 可營利。
標示格式見同資料夾的 <code>授權標示.txt</code>。</p>
<div class="note"><b>怎麼挑</b>：直接在這頁試聽，看中哪首就把它的<b>檔名</b>填進
<code>素材/音樂/配置.json</code> 對應那一幕的「曲目」欄，再跑一次
<code>mix_audio.py</code>，不必重渲影片。<br>
<b>響度</b>欄是整合響度（LUFS），數字越小越安靜；混音時會自動拉齊，這欄只是給你參考。
<b>人聲</b>欄是看樂器欄有沒有 choir／vocal，標了的請先試聽。</div>"""]
    for mood, items in by_mood.items():
        parts.append(f"<h2>{html.escape(mood)}（{len(items)} 首）</h2><table>"
                     "<tr><th>試聽</th><th>曲名</th><th>長度</th><th>BPM</th>"
                     "<th>響度</th><th>樂器</th><th>感覺</th><th>描述</th></tr>")
        for t, lu in items:
            rel = urllib.parse.quote(t["path"].replace("\\", "/"))
            warn = ' <span class="warn">可能有人聲</span>' if t["vocal_hint"] else ""
            parts.append(
                f'<tr><td><audio controls preload="none" src="{rel}"></audio></td>'
                f'<td><b>{html.escape(t["title"])}</b>{warn}<br>'
                f'<span style="color:#6b7a80;font-size:12px">{html.escape(t["filename"])}</span></td>'
                f'<td class="n">{t["length"]}</td><td class="n">{t["bpm"]}</td>'
                f'<td class="n">{f"{lu:.1f}" if lu is not None else "—"}</td>'
                f'<td>{html.escape(t["instruments"])}</td>'
                f'<td>{html.escape(t["feel"])}</td>'
                f'<td>{html.escape(t["description"])}</td></tr>')
        parts.append("</table>")
    parts.append("</div>")
    (ROOT / "配樂庫.html").write_text("\n".join(parts), encoding="utf-8")

    with open(ROOT / "配樂庫.csv", "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["情緒", "曲名", "檔名", "長度", "秒", "BPM", "響度LUFS", "樂器",
                    "感覺", "可能有人聲", "描述", "授權", "作者"])
        for t, lu in rows:
            w.writerow([t["mood"], t["title"], t["filename"], t["length"], t["seconds"],
                        t["bpm"], f"{lu:.1f}" if lu is not None else "", t["instruments"],
                        t["feel"], "是" if t["vocal_hint"] else "", t["description"],
                        t["license"], t["creator"]])

    (ROOT / "授權標示.txt").write_text(
        "配樂庫　授權標示\n"
        "══════════════════════════════════════\n\n"
        "全部曲目：Kevin MacLeod（incompetech.com），CC BY 4.0。\n"
        "官方 FAQ 明文允許 YouTube 營利使用，唯一要求是標示。\n\n"
        "每用一首，說明欄放這三行（Title 換成該曲實際曲名）：\n\n"
        "    Title Kevin MacLeod (incompetech.com)\n"
        "    Licensed under Creative Commons: By Attribution 4.0\n"
        "    https://creativecommons.org/licenses/by/4.0/\n\n"
        "標示要放在「想知道音樂哪來的人不必費力就找得到」的位置。\n"
        "若某支片不能標示（例如電視廣告），要另外買 Standard License。\n\n"
        f"本庫共 {len(rows)} 首，索引見 配樂庫.html／配樂庫.csv。\n",
        encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", action="store_true")
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--index", action="store_true")
    ap.add_argument("--loudness", action="store_true")
    ap.add_argument("--mood")
    ap.add_argument("--limit", type=int)
    ap.add_argument("--workers", type=int, default=8)
    args = ap.parse_args()

    ROOT.mkdir(parents=True, exist_ok=True)
    tracks = catalog()
    if args.mood:
        tracks = [t for t in tracks if t["mood"] == args.mood]
    counts = {}
    for t in tracks:
        counts[t["mood"]] = counts.get(t["mood"], 0) + 1
    print(f"目錄共 {len(tracks):,} 首（全部 CC BY 4.0 純器樂）")
    for m, n in sorted(counts.items(), key=lambda x: -x[1]):
        print(f"  {m:8} {n:4} 首")
    print(f"  其中樂器欄有 choir／vocal 的：{sum(1 for t in tracks if t['vocal_hint'])} 首")
    (ROOT / "_metadata" / "tracks.json").write_text(
        json.dumps(tracks, ensure_ascii=False, indent=1), encoding="utf-8")

    loud_path = ROOT / "_metadata" / "loudness.json"
    loud = json.loads(loud_path.read_text(encoding="utf-8")) if loud_path.exists() else {}

    if args.run:
        todo = [t for t in tracks if not (ROOT / t["path"]).exists()]
        if args.limit:
            todo = todo[:args.limit]
        print(f"\n待下載 {len(todo):,} 首")
        done = {"ok": 0, "skip": 0, "fail": 0}
        t0 = time.time()
        with ThreadPoolExecutor(max_workers=args.workers) as ex:
            for i, res in enumerate(ex.map(download, todo), 1):
                done[res] += 1
                if i % 20 == 0 or i == len(todo):
                    el = time.time() - t0
                    print(f"\r  {i}/{len(todo)}  成功 {done['ok']}  失敗 {done['fail']}"
                          f"  剩約 {el / i * (len(todo) - i) / 60:.0f} 分   ", end="", flush=True)
        print()

    if args.loudness:
        todo = [t for t in tracks if (ROOT / t["path"]).exists() and t["path"] not in loud]
        if args.limit:
            todo = todo[:args.limit]
        print(f"\n量響度 {len(todo)} 首")
        for i, t in enumerate(todo, 1):
            lu = loudness(ROOT / t["path"])
            if lu is not None:
                loud[t["path"]] = lu
            if i % 10 == 0 or i == len(todo):
                print(f"\r  {i}/{len(todo)}", end="", flush=True)
                loud_path.write_text(json.dumps(loud, ensure_ascii=False), encoding="utf-8")
        loud_path.write_text(json.dumps(loud, ensure_ascii=False), encoding="utf-8")
        print()

    if args.run or args.index or args.loudness:
        write_index(tracks, loud)
        print(f"\n索引 → {ROOT / '配樂庫.html'}\n授權 → {ROOT / '授權標示.txt'}")


if __name__ == "__main__":
    main()
