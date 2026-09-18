"""修 gthom：把 574 節裡不屬於《多馬福音》的 361 節搬出去。

🚨 為什麼**不**直接拆成各書的 slug：那 361 節的 OCR 是壞的（訛誤 53.7／萬字，
   「耶蕻」75 次、「約慈」33 次、「耶蘇」48 次）。把壞資料分到正確的桶裡，
   仍然是壞資料，而且會讓每一本都變成「有全文但不能引」。
   ch.11–12 的多馬福音本體反而是乾淨的（訛誤 0），所以留下。

🚨 也**不**刪除：其中有些作品站上沒有別的來源，刪掉就是真的沒了。
   改成搬到一個明確標示「整冊舊 OCR、待重做」的 slug，可逆、可查、可排程。

做法：
  · gthom 只留 chapter 11–12（213 節，訛誤 0）＝真正的《多馬福音》
  · 其餘 361 節搬到 cct-gospels-unsplit，並在 documents 建一列說明它是什麼
  · 兩邊的 sections 計數同步回譜系資料層
"""
import argparse
import json
from collections import Counter
from pathlib import Path
import requests

ROOT = Path(r"C:\Users\user\Desktop\know-graph-lab")
env = dict(l.strip().split("=", 1)
           for l in (ROOT / ".env").read_text(encoding="utf-8-sig").splitlines()
           if "=" in l and not l.startswith("#"))
URL = env["SUPABASE_URL"].rstrip("/")
H = {"apikey": env["SUPABASE_SERVICE_ROLE_KEY"],
     "Authorization": "Bearer " + env["SUPABASE_SERVICE_ROLE_KEY"],
     "Content-Type": "application/json"}

KEEP_CH = {11, 12}
NEW_SLUG = "cct-gospels-unsplit"

ap = argparse.ArgumentParser()
ap.add_argument("--write", action="store_true")
ap.add_argument("--dry-run", action="store_true")
a = ap.parse_args()
if not (a.write or a.dry_run):
    ap.error("要 --dry-run 或 --write")


def get(path, params):
    params.setdefault("limit", "2000")
    r = requests.get(f"{URL}/rest/v1/{path}", headers=H, params=params, timeout=120)
    if r.status_code >= 400:
        raise SystemExit(f"{r.status_code} {r.text[:200]}")
    j = r.json()
    if not isinstance(j, list):
        raise SystemExit("不是 list")
    return j


g = get("apocrypha_sections",
        {"select": "id,chapter,section_label,order_index,text",
         "doc_slug": "eq.gthom", "order": "order_index.asc"})
keep = [s for s in g if s["chapter"] in KEEP_CH]
move = [s for s in g if s["chapter"] not in KEEP_CH]
print(f"gthom 現有 {len(g)} 節")
print(f"  留下（多馬福音本體 ch.11–12）：{len(keep)} 節")
print(f"  搬走（整冊其餘作品）：        {len(move)} 節")
assert len(keep) + len(move) == len(g)
assert len(keep) == 213, f"預期留下 213 節，實得 {len(keep)}"

print("\n  搬走的章節分佈：")
for ch, n in sorted(Counter(s["chapter"] for s in move).items()):
    first = next(s for s in move if s["chapter"] == ch)
    print(f"    ch{ch:>3} {n:>4} 節 │ {(first['text'] or '')[:46]}")

if a.dry_run:
    print("\n（dry-run：沒有寫入）")
    raise SystemExit(0)

# ① 先建 documents 那一列
doc = {
  "slug": NEW_SLUG,
  "title_zh": "《基督教典外文獻・典外福音書》整冊（未拆分，舊 OCR）",
  "title_zh_short": "典外福音書整冊（待重做）",
  "title_en": "Christian Apocrypha, Gospels volume (unsplit, legacy OCR)",
  "category": "nt_apocrypha",
  "testament": "nt",
  "composition_low": 100, "composition_high": 400,
  "language_orig": "zh",
  "summary_zh": (
    "🚨 這不是一部文獻，是整冊書被倒進單一 slug 的殘留。"
    "原本掛在 gthom（多馬福音）名下共 574 節，其中只有 213 節（ch.11–12）"
    "真的是《多馬福音》，其餘 361 節橫跨雅各原始福音、嬰孩多馬、"
    "拉丁語嬰孩福音、彼拉多文獻、十二使徒福音、腓力福音、摩尼派殘片等。"
    "而且這 361 節的文字層是壞的：實測字形訛誤 53.7／萬字"
    "（「耶蕻」75 次、「耶蘇」48 次、「約慈」33 次、「撤迦利亞」12 次），"
    "所以正確的修法是重 OCR 後逐書入庫，不是把壞資料分到正確的桶裡。"
    "在重做之前先搬到這裡：不刪除（有些作品站上沒有別的來源），"
    "但也不再灌水到「站上有全文」的統計裡。"),
  "intro_zh": None,
  "display_order": 9999,
}
r = requests.post(f"{URL}/rest/v1/apocrypha_documents", headers=H,
                  data=json.dumps([doc], ensure_ascii=False).encode("utf-8"), timeout=60)
if r.status_code >= 400 and "duplicate" not in r.text.lower():
    raise SystemExit(f"建 document 失敗：{r.status_code} {r.text[:300]}")
print(f"\n① documents 建列 {NEW_SLUG}（{r.status_code}）")

# ② 逐筆搬 sections
ok = 0
for s in move:
    r = requests.patch(f"{URL}/rest/v1/apocrypha_sections", headers=H,
                       params={"id": f"eq.{s['id']}"},
                       data=json.dumps({"doc_slug": NEW_SLUG}).encode("utf-8"),
                       timeout=60)
    if r.status_code >= 400:
        print(f"   ⛔ {s['id']} 失敗 {r.status_code} {r.text[:120]}")
        break
    ok += 1
print(f"② sections 搬走 {ok} / {len(move)} 節")

# ③ 讀回來驗
after_g = get("apocrypha_sections", {"select": "id", "doc_slug": "eq.gthom"})
after_n = get("apocrypha_sections", {"select": "id", "doc_slug": f"eq.{NEW_SLUG}"})
print(f"③ 讀回：gthom {len(after_g)} 節　{NEW_SLUG} {len(after_n)} 節")
assert len(after_g) == 213, f"🚨 gthom 應為 213，實得 {len(after_g)}"
assert len(after_n) == len(move), f"🚨 新 slug 應為 {len(move)}，實得 {len(after_n)}"
print("   ✓ 兩邊都對得上")
