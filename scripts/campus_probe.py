#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""到玄奘校內時，實測哪些訂閱資料庫真的驗得過。

**這支腳本回答一個只有在校內才問得到的問題。** 館方清單上列了五十幾個庫
（見 `data/research-data/hcu-eresources.json`），但「清單上有」不等於「還在訂」，
更不等於「這台機器驗得過」。在校外怎麼看都是一片 unknown；一連上校網跑一次，
就能把 `hcu-harvest-plan.json` 裡的 `access` 欄從 unknown 變成實測結果，
之後要替哪個庫寫抓取程式才有依據。

🚨 **這支只做探測，不下載任何東西。** 訂閱庫的大量下載會被當成異常流量，而處置是
停**整個機構**的權限（華藝那條管線已經記過這件事）。探測就是每個庫抓一次首頁，
看回應裡有沒有「已認出機構」的跡象，兩秒一個。

🚨 **先驗機構身分再探測。** 不先驗的話，離開校網之後每個庫都會回「沒訂」，
而那是假的——庫還在，只是不認得這台機器。判準沿用華藝那一套：它的首頁在認得
機構時會寫「您好！玄奘大學 IP:…」，認不得就換成「透過您的圖書館登入」。

用法：
  python scripts/campus_probe.py --check     # 只問「現在在不在校網」
  python scripts/campus_probe.py             # 在校網才探測，並回寫計畫檔
  python scripts/campus_probe.py --force     # 不在校網也硬跑（只為了看錯誤長相）
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from datetime import datetime
from pathlib import Path

import requests

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
PLAN = ROOT / "data" / "research-data" / "hcu-harvest-plan.json"
STATE = ROOT / "scripts" / "state" / "campus_probe.json"

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
      "Accept-Language": "zh-TW,zh;q=0.9,en;q=0.8"}
DELAY = 2.0

# 每個要探測的庫：key 對應 hcu-harvest-plan.json 的 targets[].key
PROBES = {
    "proquest-research": "https://www.proquest.com/results/",
    "proquest-arts": "https://www.proquest.com/artshumanities/",
    "pqdt": "https://www.proquest.com/pqdt/",
    "project-muse": "https://muse.jhu.edu/",
    "degruyter": "https://www.degruyterbrill.com/",
    "oxford-scholarship": "https://academic.oup.com/",
    "cambridge-companions": "https://www.cambridge.org/core/what-we-publish/cambridge-companions",
    "springerlink": "https://link.springer.com/",
    "wiley": "https://onlinelibrary.wiley.com/",
    "ebsco-omnifile": "https://search.ebscohost.com/login.aspx?profile=wilson",
    "ebsco-ebooks": "https://search.ebscohost.com/login.aspx?profile=ehost",
    "gale-vrl": "https://go.gale.com/ps/start.do?p=GVRL",
    "wanfang": "http://www.wanfangdata.com.cn/index.html",
    "huso": "https://huso.stpi.narl.org.tw/",
    "taiwan-people": "https://tbmc.ncl.edu.tw/",
}

# 認出機構身分的跡象。⚠️ 各平台寫法不同，這裡只能抓共通的幾種。
GRANTED = re.compile(
    r"玄奘|Hsuan\s*Chuang|HSUAN[- ]CHUANG|Access provided by|Institutional access|"
    r"Brought to you by|已訂購|機構帳號", re.I)
DENIED = re.compile(
    r"透過您的圖書館登入|Sign in via|Get access|Purchase|Log in to|"
    r"You do not have access|no access", re.I)

AIRITI = "https://www.airitilibrary.com"
_ORG_RE = re.compile(r'unitEntranceName[^>]*>\s*(?:您好！\s*)?([^<]{2,30}?)\s*</')
_IP_RE = re.compile(r"IP\s*[:：]\s*([\d.]+)")


def on_campus(s: requests.Session) -> tuple[str, str]:
    """回傳（機構名, 對方看到的 IP）。認不得就機構名為空字串。"""
    try:
        html = s.get(f"{AIRITI}/", headers=UA, timeout=60).text
    except requests.RequestException as e:
        print(f"  連不上華藝：{type(e).__name__}", file=sys.stderr)
        return "", ""
    m = _ORG_RE.search(html)
    who = m.group(1).strip() if m else ""
    # 認不得時同一個 span 寫的是「透過您的圖書館登入」——那是提示不是機構名，
    # 直接回傳會讓這道閘永遠為真，等於沒有閘。
    who = "" if (not who or "登入" in who) else who
    ip = (_IP_RE.search(html) or [None, ""])[1] if _IP_RE.search(html) else ""
    return who, ip


def probe(s: requests.Session, key: str, url: str) -> dict:
    try:
        r = s.get(url, headers=UA, timeout=45, allow_redirects=True)
    except requests.RequestException as e:
        return {"access": "error", "detail": type(e).__name__}
    body = r.text[:200000]
    granted = bool(GRANTED.search(body))
    denied = bool(DENIED.search(body))
    if r.status_code >= 400:
        access = "error"
    elif granted and not denied:
        access = "granted"
    elif granted and denied:
        access = "partial"          # 首頁同時有兩種字樣，多半是部分館藏有訂
    elif denied:
        access = "denied"
    else:
        access = "unclear"          # 平台沒在首頁表態，要進到文章頁才看得出來
    return {"access": access, "http": r.status_code,
            "final_url": r.url[:160],
            "detail": (GRANTED.search(body) or DENIED.search(body) or [""])[0]
                      if (granted or denied) else ""}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="只問在不在校網")
    ap.add_argument("--force", action="store_true", help="不在校網也硬跑")
    args = ap.parse_args()

    s = requests.Session()
    who, ip = on_campus(s)
    now = datetime.now().isoformat(timespec="seconds")
    STATE.parent.mkdir(parents=True, exist_ok=True)

    if who:
        print(f"✅ 對方認出的機構：{who}" + (f"（IP {ip}）" if ip else ""))
    else:
        print(f"✗ 不在校網（華藝認不出機構身分）" + (f"，對方看到的 IP {ip}" if ip else ""))

    if args.check:
        STATE.write_text(json.dumps({"checked_at": now, "institution": who, "ip": ip},
                                    ensure_ascii=False, indent=1), encoding="utf-8")
        return 0 if who else 1

    if not who and not args.force:
        print("  探測略過。到校內再跑，或用 --force 看錯誤長相。")
        STATE.write_text(json.dumps({"checked_at": now, "institution": "", "ip": ip,
                                     "skipped": True}, ensure_ascii=False, indent=1),
                         encoding="utf-8")
        return 1

    plan = json.loads(PLAN.read_text(encoding="utf-8"))
    by_key = {t["key"]: t for t in plan["targets"]}
    results = {}
    for i, (key, url) in enumerate(PROBES.items(), 1):
        r = probe(s, key, url)
        results[key] = r
        t = by_key.get(key)
        if t is not None:
            t["access"] = r["access"]
            t["access_checked_at"] = now
            t["access_detail"] = r.get("detail") or ""
        name = (t or {}).get("name", key)
        print(f"  [{i}/{len(PROBES)}] {r['access']:<8} {name[:44]}")
        time.sleep(DELAY)

    plan["access_probed_at"] = now
    plan["access_probed_from"] = who or "(強制執行，非校網)"
    PLAN.write_text(json.dumps(plan, ensure_ascii=False, indent=1), encoding="utf-8")
    STATE.write_text(json.dumps({"checked_at": now, "institution": who, "ip": ip,
                                 "results": results}, ensure_ascii=False, indent=1),
                     encoding="utf-8")

    tally: dict[str, int] = {}
    for r in results.values():
        tally[r["access"]] = tally.get(r["access"], 0) + 1
    print("\n" + "、".join(f"{k} {v}" for k, v in sorted(tally.items())))
    print(f"→ {PLAN}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
