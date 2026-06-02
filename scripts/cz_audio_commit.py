# -*- coding: utf-8 -*-
"""把清好的錄音口語稿寫進 pong_sermons.content。
若該日已有書面講章在 content → 先搬到 manuscript（保留兩版），再放口語稿。
用法： python scripts/cz_audio_commit.py --date 2005-02-27 --clean-file tmp_sermon/audio/2005-02-27_clean.txt
"""
import os, sys, requests

def env():
    with open(".env", encoding="utf-8") as f:
        for line in f:
            if line.strip() and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1); os.environ[k.strip()] = v.strip()
env()
SB = os.environ["SUPABASE_URL"].rstrip("/") + "/rest/v1"
KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
H = {"apikey": KEY, "Authorization": f"Bearer {KEY}", "Content-Type": "application/json"}

def main():
    a = sys.argv
    date = a[a.index("--date") + 1]
    clean = open(a[a.index("--clean-file") + 1], encoding="utf-8").read().strip()
    if len(clean) < 200:
        print("! clean 太短，中止"); return
    r = requests.get(f"{SB}/pong_sermons?sermon_date=eq.{date}&select=id,content,manuscript,title,preacher", headers=H).json()
    if not r:
        print(f"! 找不到 {date} 的 row"); return
    row = r[0]
    payload = {"content": clean, "has_recording": True}
    # 既有書面講章（content 有實質內容且尚未存過 manuscript）→ 搬到 manuscript
    if (row.get("content") or "").strip() and len((row["content"]).strip()) > 200 and not (row.get("manuscript") or "").strip():
        payload["manuscript"] = row["content"]
        print(f"  保留書面講章 → manuscript（{len(row['content'])}字）")
    rr = requests.patch(f"{SB}/pong_sermons?id=eq.{row['id']}", headers={**H, "Prefer": "return=minimal"}, json=payload)
    print(f"  {'OK' if rr.status_code < 300 else 'FAIL '+rr.text[:120]}  {date}  content={len(clean)}字"
          + ("（雙版）" if "manuscript" in payload else ""))

if __name__ == "__main__":
    main()
