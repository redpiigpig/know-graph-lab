# -*- coding: utf-8 -*-
"""使徒統緒批次匯入：讀結構化 JSON → 解析 parent_see_zh → 插入 sees + 主教鏈。

JSON schema（見 skill genealogy-episcopal 的 wiring 規則）：
{
  "sees": [{
    "see_zh": "布加勒斯特", "name_zh": "...", "name_en": "...",
    "church": "羅馬尼亞正教會", "tradition": "希臘正教", "rite": "拜占庭禮",
    "founded_year": 1359, "split_year": 1885,        # split_year 可 null
    "parent_see_zh": "君士坦丁堡",                     # 可寫 "see_zh|church" 消歧
    "location": "...", "current_patriarch_zh": "...", "current_patriarch_en": "...",
    "incumbent_since": 2007, "notes": "...", "sources": "...",
    "founder_apostle_id": null,                        # 使徒立座才填
    "bishops": [
      {"name_zh":"...","name_en":"...","succession_number":1,
       "start_year":1359,"end_year":1372,"status":"正統","notes":"...","sources":"..."}
    ]
  }]
}

用法：
  python -X utf8 scripts/apply_episcopal_batch.py <batch.json>            # 套用
  python -X utf8 scripts/apply_episcopal_batch.py <batch.json> --dry-run  # 只報告
冪等：see_zh+church 已存在則跳過該 see（連同主教）。
"""
import json
import re
import sys
import urllib.request

REF = "vloqgautkahgmqcwgfuo"
API = f"https://api.supabase.com/v1/projects/{REF}/database/query"


def load_token(path=".env"):
    with open(path, encoding="utf-8") as f:
        for line in f:
            if line.startswith("SUPABASE_ACCESS_TOKEN="):
                return line.split("=", 1)[1].strip().strip('"')
    raise RuntimeError("no token")


def q(sql, token):
    req = urllib.request.Request(
        API, data=json.dumps({"query": sql}).encode(),
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json",
                 "User-Agent": "curl/8.4.0"}, method="POST")
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())


def esc(v):
    if v is None:
        return "null"
    if isinstance(v, (int, float)):
        return str(v)
    return "'" + str(v).replace("'", "''") + "'"


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    dry = "--dry-run" in sys.argv
    batch = json.load(open(args[0], encoding="utf-8-sig"))
    token = load_token()

    # 現有 sees 索引：see_zh → [(id, church, tradition)]
    rows = q("select id, see_zh, church, tradition from episcopal_sees", token)
    by_see = {}
    for r in rows:
        by_see.setdefault(r["see_zh"], []).append(r)

    def resolve_parent(ref):
        """ref 可為 'see_zh' 或 'see_zh|church'。回 (id|None, reason)。"""
        name, _, church = ref.partition("|")
        cands = by_see.get(name.strip(), [])
        if church:
            cands = [c for c in cands if c["church"] == church.strip()]
        if len(cands) == 1:
            return cands[0]["id"], "ok"
        if len(cands) == 0:
            return None, "not-found"
        return None, "ambiguous:" + "/".join(c["church"] for c in cands)

    ins_sees = ins_bish = 0
    errors, skipped = [], []
    for s in batch["sees"]:
        see_zh, church = s["see_zh"], s["church"]
        # 冪等：已存在跳過
        exist = [c for c in by_see.get(see_zh, []) if c["church"] == church]
        if exist:
            skipped.append(f"{see_zh}|{church}（已存在）")
            continue
        pid, reason = resolve_parent(s.get("parent_see_zh", ""))
        if pid is None and s.get("founder_apostle_id") is None:
            errors.append(f"{see_zh}: parent「{s.get('parent_see_zh')}」{reason} → 跳過")
            continue
        cols = dict(
            name_zh=s.get("name_zh"), name_en=s.get("name_en"), see_zh=see_zh,
            church=church, tradition=s["tradition"], rite=s.get("rite"),
            founded_year=s.get("founded_year"), split_year=s.get("split_year"),
            parent_see_id=pid, location=s.get("location"),
            current_patriarch_zh=s.get("current_patriarch_zh"),
            current_patriarch_en=s.get("current_patriarch_en"),
            incumbent_since=s.get("incumbent_since"), status=s.get("status", "現存"),
            notes=s.get("notes"), sources=s.get("sources"),
            founder_apostle_id=s.get("founder_apostle_id"),
            patriarchate_start_year=s.get("patriarchate_start_year"),
            patriarchate_end_year=s.get("patriarchate_end_year"))
        cn = ", ".join(cols)
        cv = ", ".join(esc(v) for v in cols.values())
        if dry:
            print(f"  [see] {see_zh}|{church} parent={pid and pid[:8]} bishops={len(s.get('bishops',[]))}")
        else:
            new = q(f"insert into episcopal_sees ({cn}) values ({cv}) returning id", token)
            sid = new[0]["id"]
            by_see.setdefault(see_zh, []).append({"id": sid, "see_zh": see_zh, "church": church, "tradition": s["tradition"]})
        ins_sees += 1
        # 主教鏈：按 succession_number 排序，串 predecessor_id
        prev_id = None
        for b in sorted(s.get("bishops", []), key=lambda x: (x.get("succession_number") or 0)):
            bc = dict(
                name_zh=b.get("name_zh"), name_en=b.get("name_en"), see=see_zh, church=church,
                succession_number=b.get("succession_number"), start_year=b.get("start_year"),
                end_year=b.get("end_year"), status=b.get("status", "正統"),
                end_reason=b.get("end_reason"), appointed_by=b.get("appointed_by"),
                predecessor_id=prev_id, notes=b.get("notes"), sources=b.get("sources"))
            bcn = ", ".join(bc)
            bcv = ", ".join(esc(v) for v in bc.values())
            if not dry:
                nb = q(f"insert into episcopal_succession ({bcn}) values ({bcv}) returning id", token)
                prev_id = nb[0]["id"]
            ins_bish += 1

    print(f"\n{'[DRY] ' if dry else ''}插入 sees={ins_sees} bishops={ins_bish}")
    if skipped:
        print(f"跳過（已存在）{len(skipped)}:", "、".join(skipped[:15]))
    if errors:
        print(f"⚠️ 錯誤 {len(errors)}:")
        for e in errors:
            print("  ", e)


if __name__ == "__main__":
    main()
