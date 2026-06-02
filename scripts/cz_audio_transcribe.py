# -*- coding: utf-8 -*-
"""城中本機錄音批次轉錄 → raw 逐字稿草稿。
只轉「週報證道=龐」且日期可信的錄音（對照 bulletin 確認日期＋講員）。
Whisper(faster_whisper) 直接吃本機 wav；raw 存 tmp_sermon/audio/<date>_raw.txt（可續跑）。
用法： python scripts/cz_audio_transcribe.py --list     (只列清單不轉)
       python scripts/cz_audio_transcribe.py --test     (只轉第一個)
       python scripts/cz_audio_transcribe.py            (整批，可續跑)
"""
import os, re, sys, json, glob, datetime
from pathlib import Path
sys.path.insert(0, os.path.abspath("scripts/pong-archive"))

BASE = "pong-archive/stores/城中週報/錄音"
OUT = Path("tmp_sermon/audio"); OUT.mkdir(parents=True, exist_ok=True)
NONSERMON = ("查經", "訓練", "集訓", "沙龍", "關懷怖道", "關懷佈道", "衛斯理", "傳道書",
             "耶利米哀歌", "進入世界", "以馬忤斯", "釘十字架", "part2", ".doc")

def prov_date(rel, fn):
    relp = "/" + rel.replace("\\", "/")
    ym = re.search(r"/(20\d{2})/", relp); yr = int(ym.group(1)) if ym else None
    if "95年" in rel: yr = 2006
    stem = re.sub(r"\.(wav|WAV|mp3)$", "", fn)
    m = re.match(r"(\d{6})", stem)
    if m:
        s = m.group(1); y = int("20" + s[:2])
        if 2003 <= y <= 2009 and 1 <= int(s[2:4]) <= 12:
            return f"{y}-{s[2:4]}-{s[4:6]}"
        y = 1911 + int(s[:2])
        if 2003 <= y <= 2009:
            return f"{y}-{int(s[2:4]):02d}-{int(s[4:6]):02d}"
    m = re.match(r"(\d{4})(?:錄音)?$", stem)
    if m and yr:
        return f"{yr}-{m.group(1)[:2]}-{m.group(1)[2:]}"
    return None

def build_list():
    idx = json.load(open("public/content/chengzhong-bulletins/index.json", encoding="utf-8"))["items"]
    pre = {}
    for b in idx:
        d = b["date"]
        if d not in pre or b["service"] == "主日崇拜":
            pre[d] = b.get("preacher")
    out = []
    for f in glob.glob(BASE + "/**/*", recursive=True):
        if not os.path.isfile(f): continue
        fn = os.path.basename(f); rel = os.path.relpath(f, BASE)
        if not fn.lower().endswith((".wav", ".mp3")): continue
        if os.path.getsize(f) < 3 * 1048576: continue
        if any(k in rel for k in NONSERMON): continue
        if re.match(r"REC\d+", fn, re.I) or fn.lower().startswith("voice"): continue
        d = prov_date(rel, fn)
        if not d: continue
        p = pre.get(d)
        if p and "龐" in p:
            out.append((d, f, p))
    # dedupe by date (keep largest)
    best = {}
    for d, f, p in out:
        if d not in best or os.path.getsize(f) > os.path.getsize(best[d][1]):
            best[d] = (d, f, p)
    return sorted(best.values())

def build_undated():
    """Undated/VOICE recordings (no reliable filename date), deduped by (size, head-hash)."""
    import hashlib
    dated_files = {os.path.abspath(f) for _, f, _ in build_list()}
    seen = {}; out = []
    for f in sorted(glob.glob(BASE + "/**/*", recursive=True)):
        if not os.path.isfile(f): continue
        fn = os.path.basename(f); rel = os.path.relpath(f, BASE)
        if not fn.lower().endswith((".wav", ".mp3")): continue
        sz = os.path.getsize(f)
        if sz < 3 * 1048576: continue
        if any(k in rel for k in NONSERMON): continue
        if os.path.abspath(f) in dated_files: continue
        if prov_date(rel, fn): continue   # has a reliable date -> not "undated"
        with open(f, "rb") as fh:
            h = hashlib.md5(fh.read(2 * 1048576)).hexdigest()
        key = (sz, h)
        if key in seen: continue          # duplicate content (VOICE舊 mirrors)
        seen[key] = rel
        out.append((rel, f, sz))
    return out

UOUT = Path("tmp_sermon/audio_undated"); UOUT.mkdir(parents=True, exist_ok=True)

def main():
    if "--undated" in sys.argv:
        items = build_undated()
        print(f"去重後 undated 錄音: {len(items)}")
        if "--list" in sys.argv:
            for rel, f, sz in items: print(f"  {sz//1048576:4}MB  {rel}")
            return
        import subprocess
        from pong_sermon_pipeline import transcribe
        todo = [(rel, f) for rel, f, _ in items]
        if "--test" in sys.argv: todo = todo[:1]
        for i, (rel, f) in enumerate(todo, 1):
            safe = re.sub(r"[\\/]", "_", os.path.splitext(rel)[0])
            if (UOUT / f"{safe}.txt").exists(): continue
            print(f"\n[{i}/{len(todo)}] {rel}", flush=True)
            conv = UOUT / f"{safe}.conv.mp3"
            try:
                r = subprocess.run(["ffmpeg", "-y", "-i", os.path.abspath(f), "-ac", "1",
                                    "-ar", "16000", "-b:a", "64k", str(conv)], capture_output=True)
                if r.returncode != 0 or not conv.exists():
                    print("  ! ffmpeg fail", flush=True); continue
                txt = transcribe(Path(str(conv)), "zh")
                (UOUT / f"{safe}.txt").write_text(txt, encoding="utf-8")
                print(f"  -> {safe}.txt  {len(txt)}字", flush=True)
            except Exception as e:
                print(f"  ! ERROR {rel}: {e}", flush=True)
            finally:
                for c in UOUT.glob(f"{safe}.conv*"):
                    try: c.unlink()
                    except: pass
                for c in glob.glob(os.path.join(os.path.dirname(os.path.abspath(f)), "chunk_*.mp3")):
                    try: os.remove(c)
                    except: pass
        print("DONE")
        return
    items = build_list()
    print(f"龐-confirmed 可轉錄錄音: {len(items)}")
    if "--list" in sys.argv:
        for d, f, p in items:
            done = "✓" if (OUT / f"{d}_raw.txt").exists() else " "
            print(f"  [{done}] {d}  {os.path.getsize(f)//1048576:3}MB  {os.path.relpath(f, BASE)}")
        return
    import subprocess
    from pong_sermon_pipeline import transcribe
    todo = [(d, f, p) for d, f, p in items if not (OUT / f"{d}_raw.txt").exists()]
    if "--test" in sys.argv: todo = todo[:1]
    print(f"待轉: {len(todo)}")
    for i, (d, f, p) in enumerate(todo, 1):
        t0 = datetime.datetime.now()
        print(f"\n[{i}/{len(todo)}] {d}  {os.path.relpath(f, BASE)}", flush=True)
        conv = OUT / f"{d}.conv.mp3"
        try:
            # 先轉 16k mono mp3（Whisper 原生取樣率；舊 wav 無法 -c copy 切段）
            r = subprocess.run(["ffmpeg", "-y", "-i", os.path.abspath(f), "-ac", "1",
                                "-ar", "16000", "-b:a", "64k", str(conv)],
                               capture_output=True)
            if r.returncode != 0 or not conv.exists():
                print(f"  ! ffmpeg 轉檔失敗: {r.stderr.decode('utf-8','ignore')[-200:]}", flush=True); continue
            txt = transcribe(Path(str(conv)), "zh")
            (OUT / f"{d}_raw.txt").write_text(txt, encoding="utf-8")
            print(f"  -> {d}_raw.txt  {len(txt)}字  耗時 {(datetime.datetime.now()-t0).seconds}s", flush=True)
        except Exception as e:
            print(f"  ! ERROR {d}: {e}", flush=True)
        finally:
            for c in OUT.glob(f"{d}.conv*"):
                try: c.unlink()
                except: pass
            for c in glob.glob(os.path.join(os.path.dirname(os.path.abspath(f)), "chunk_*.mp3")):
                try: os.remove(c)
                except: pass
    print("DONE")

if __name__ == "__main__":
    main()
