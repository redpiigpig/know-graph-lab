# -*- coding: utf-8 -*-
"""biblical_people 資料一致性稽核＋分級修復（走 Management API，鎖站期間可用）。

檢查四類問題（族譜圖視覺斷裂/斷鏈的資料層根因）：
  1. 懸空引用：spouse/children 引用的名字找不到 row
  2. 變體引用：去括號後可唯一對到 row（寫法不一，如 流便/呂便 改名殘留）
  3. wife.children 不在「所有丈夫 children 聯集」→ 子嗣 drop 從 husband 直落、視覺斷裂
  4. spouse 不互指：A.spouse 有 B、B.spouse 卻沒 A

用法：
  python -X utf8 scripts/genealogy_data_audit.py                        # 稽核 biblical_people
  python -X utf8 scripts/genealogy_data_audit.py --table islamic_people # 稽核伊斯蘭族譜（同構 schema）
  python -X utf8 scripts/genealogy_data_audit.py --fix                  # 套 Tier-1 機械修復：
      (a) 變體引用改寫成 row 的正確全名（唯一對應才改）
      (b) spouse 互指補回
      (c) 單一丈夫的 wife.children 缺漏 → 補進 husband.children（既有 row 才補）
  無法機械判定者（懸空引用、多夫歸屬、多候選變體）永遠只報告不動。
"""
import json
import os
import re
import sys
import urllib.request

REF = "vloqgautkahgmqcwgfuo"
API = f"https://api.supabase.com/v1/projects/{REF}/database/query"

# 以下三組人工判斷名單只適用 biblical_people（--table 其他表時自動清空）
# 同名不同人：base-name 對到的 row 其實是別人，引用本身是對的（缺 row），絕不可改寫
FALSE_FRIENDS = {
    ("米迦（米非波設之子）", "亞哈斯（米迦之子）"),   # 代上8:35 便雅憫支派，≠ 猶大王亞哈斯（約坦之子）
    ("馬利安美一世", "阿里斯托布魯（大希律之子）"),   # Aristobulus IV，≠ 哈基斯王希律之子
}
# 多候選但經文可確解的引用
RESOLVE_OVERRIDES = {
    ("密迦", "children", "烏斯"): "烏斯（拿鶴之子）",          # 創22:21 烏斯是拿鶴由密迦所生長子
    ("拉麥（該隱後裔）", "spouse", "亞大"): "亞大（拉麥之妻）",  # 創4:19 拉麥娶亞大、洗拉
    ("阿何利巴瑪", "children", "可拉"): "可拉（以掃之子）",      # 創36:14 阿何利巴瑪為以掃生可拉
}
# spouse 互指不可補的例外：原始資料本身有誤（親子誤植為配偶），留人工修
SPOUSE_SKIP = {
    ("撒母耳", "哈拿"),  # 哈拿是撒母耳之母；撒母耳.spouse 欄有誤，須人工清掉
}
# wife.children 對齊不可補的例外：BiblicalSpineTree 對羅得亂倫群組有特殊佈局
#（摩押/便亞米刻意只掛在女兒的 wife-marriage 中點下），補進羅得.children 會重複繪製
KID_SKIP = {
    ("羅得長女", "羅得"),
    ("羅得次女", "羅得"),
    # 拉比傳統：俄珥巴（＝哈拉法）四子（歌利亞等，梳妲 42b）非丈夫基連所出，不可補進基連.children
    ("俄珥巴", "基連"),
}

# islamic_people 專屬名單
ISLAMIC_FALSE_FRIENDS = {
    # 宰娜卜之子阿里（夭折的外孫）≠ 阿里·伊本·艾比·塔利卜
    ("宰娜卜（穆聖之女）", "阿里（艾布·阿斯之子）"),
}
ISLAMIC_KID_SKIP = {
    # 爾撒（耶穌）在伊斯蘭神學無父，只掛麥爾彥；優素福不得列為父
    ("麥爾彥", "優素福（馬利亞之夫）"),
}


def load_env(path=".env"):
    env = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                env[k] = v.strip().strip('"')
    return env


def query(sql, token):
    req = urllib.request.Request(
        API,
        data=json.dumps({"query": sql}).encode(),
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": "curl/8.4.0",  # api.supabase.com 的 Cloudflare 擋 Python-urllib 預設 UA
        },
        method="POST",
    )
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read().decode())


def split_names(s):
    """頓號/逗號分隔，但括號內的分隔符不切（如「無名祭司一世（亞倫線，以利亞撒之曾孫）」）。"""
    if not s:
        return []
    parts, buf, depth = [], "", 0
    for ch in s:
        if ch in "（(":
            depth += 1
        elif ch in "）)":
            depth = max(0, depth - 1)
        if depth == 0 and ch in "、,，;；":
            if buf.strip():
                parts.append(buf.strip())
            buf = ""
        else:
            buf += ch
    if buf.strip():
        parts.append(buf.strip())
    return parts


def join_names(names):
    return "、".join(names)


def base(name):
    return re.sub(r"（[^）]*）$", "", name).strip()


def main():
    global FALSE_FRIENDS, RESOLVE_OVERRIDES, SPOUSE_SKIP, KID_SKIP
    apply_fix = "--fix" in sys.argv
    table = sys.argv[sys.argv.index("--table") + 1] if "--table" in sys.argv else "biblical_people"
    if table == "islamic_people":
        FALSE_FRIENDS, RESOLVE_OVERRIDES = ISLAMIC_FALSE_FRIENDS, {}
        SPOUSE_SKIP, KID_SKIP = set(), ISLAMIC_KID_SKIP
    elif table != "biblical_people":
        FALSE_FRIENDS, RESOLVE_OVERRIDES, SPOUSE_SKIP, KID_SKIP = set(), {}, set(), set()
    token = load_env()["SUPABASE_ACCESS_TOKEN"]
    rows = query(
        f"select id, name_zh, gender, spouse, children from {table} order by name_zh",
        token,
    )
    by_name = {r["name_zh"]: r for r in rows}
    by_base = {}
    for r in rows:
        by_base.setdefault(base(r["name_zh"]), []).append(r)

    def resolve(ref, ctx=None):
        """ctx=(who, field) 供 RESOLVE_OVERRIDES / FALSE_FRIENDS 判斷。"""
        if ctx and (ctx[0], ctx[1], ref) in RESOLVE_OVERRIDES:
            return by_name[RESOLVE_OVERRIDES[(ctx[0], ctx[1], ref)]], "override"
        if ref in by_name:
            return by_name[ref], "exact"
        # FALSE_FRIENDS 只擋 base-name 誤配；正主 row 建好後精確命中優先
        if ctx and (ctx[0], ref) in FALSE_FRIENDS:
            return None, "false_friend"
        cands = by_base.get(base(ref), [])
        if len(cands) == 1:
            return cands[0], "base"
        return None, None

    dangling, variants_fix, variants_ambig = [], [], []
    kid_fix, kid_report, spouse_fix = [], [], []

    # 1+2. 引用解析
    for r in rows:
        for field in ("spouse", "children"):
            for ref in split_names(r[field]):
                row, how = resolve(ref, (r["name_zh"], field))
                if how == "false_friend":
                    dangling.append((r["name_zh"], field, ref + "（同名不同人，缺 row）"))
                elif row is None:
                    cands = [c["name_zh"] for c in by_base.get(base(ref), [])]
                    if cands:
                        variants_ambig.append((r["name_zh"], field, ref, cands))
                    else:
                        dangling.append((r["name_zh"], field, ref))
                elif how in ("base", "override") and ref != row["name_zh"]:
                    variants_fix.append((r["name_zh"], field, ref, row["name_zh"]))

    # 3. wife.children vs 所有丈夫 children 聯集
    for r in rows:
        if r["gender"] != "女":
            continue
        kids = split_names(r["children"])
        husbands = [h for h in (resolve(s, (r["name_zh"], "spouse"))[0]
                                for s in split_names(r["spouse"])) if h]
        if not kids or not husbands:
            continue
        union = set()
        for h in husbands:
            for k in split_names(h["children"]):
                kr, _ = resolve(k, (h["name_zh"], "children"))
                union.add(kr["name_zh"] if kr else k)
        missing = []
        for k in kids:
            kr, _ = resolve(k, (r["name_zh"], "children"))
            key = kr["name_zh"] if kr else k
            if key not in union:
                missing.append((k, kr))
        if not missing:
            continue
        if any((r["name_zh"], h["name_zh"]) in KID_SKIP for h in husbands):
            continue
        if len(husbands) == 1 and all(kr is not None for _, kr in missing):
            kid_fix.append((r, husbands[0], [kr["name_zh"] for _, kr in missing]))
        else:
            kid_report.append((r["name_zh"], [h["name_zh"] for h in husbands],
                               [k for k, _ in missing]))

    # 4. spouse 互指
    for r in rows:
        for sp_ref in split_names(r["spouse"]):
            s, _ = resolve(sp_ref, (r["name_zh"], "spouse"))
            if s is None or (r["name_zh"], s["name_zh"]) in SPOUSE_SKIP:
                continue
            back = {(resolve(b, (s["name_zh"], "spouse"))[0] or {"name_zh": b})["name_zh"]
                    for b in split_names(s["spouse"])}
            if r["name_zh"] not in back:
                spouse_fix.append((r["name_zh"], s))

    # ---- 報告 ----
    print(f"總人數 {len(rows)}")
    print(f"\n== 懸空引用（缺 row，需人工/查經補建）: {len(dangling)} ==")
    for who, f, ref in dangling:
        print(f"  {who} .{f} → 「{ref}」")
    print(f"\n== 變體引用・多候選（需人工定奪）: {len(variants_ambig)} ==")
    for who, f, ref, cands in variants_ambig:
        print(f"  {who} .{f} → 「{ref}」 候選 {cands}")
    print(f"\n== 變體引用・唯一對應（Tier-1 可修）: {len(variants_fix)} ==")
    for who, f, ref, canonical in variants_fix:
        print(f"  {who} .{f} 「{ref}」 → 「{canonical}」")
    print(f"\n== wife.children 缺於夫方・單夫可修（Tier-1）: {len(kid_fix)} ==")
    for w, h, missing in kid_fix:
        print(f"  {w['name_zh']} ⚭ {h['name_zh']} 補進夫方: {missing}")
    print(f"\n== wife.children 缺於夫方・多夫/缺row（需人工歸屬）: {len(kid_report)} ==")
    for w, hs, missing in kid_report:
        print(f"  {w} ⚭ {hs} 缺: {missing}")
    print(f"\n== spouse 互指補回（Tier-1 可修）: {len(spouse_fix)} ==")
    for a, s in spouse_fix:
        print(f"  {s['name_zh']}.spouse += 「{a}」")

    if not apply_fix:
        print("\n（dry-run，加 --fix 套用 Tier-1）")
        return

    # ---- Tier-1 套用 ----
    updates = {}  # id -> {field: new_value}

    def stage(row, field, new_val):
        updates.setdefault(row["id"], {"name": row["name_zh"]})[field] = new_val

    # (a) 變體引用正名
    for who, field, ref, canonical in variants_fix:
        r = by_name[who]
        cur = updates.get(r["id"], {}).get(field, r[field])
        names = [canonical if n == ref else n for n in split_names(cur)]
        stage(r, field, join_names(names))
    # (b) spouse 互指
    for a, s in spouse_fix:
        cur = updates.get(s["id"], {}).get("spouse", s["spouse"]) or ""
        names = split_names(cur)
        if a not in names:
            names.append(a)
        stage(s, "spouse", join_names(names))
    # (c) 單夫 children 補齊
    for w, h, missing in kid_fix:
        cur = updates.get(h["id"], {}).get("children", h["children"]) or ""
        names = split_names(cur)
        for m in missing:
            if m not in names:
                names.append(m)
        stage(h, "children", join_names(names))

    print(f"\n---- 套用 {len(updates)} 列 UPDATE ----")
    for pid, fields in updates.items():
        name = fields.pop("name")
        sets = ", ".join(
            f"{col} = '" + val.replace("'", "''") + "'" for col, val in fields.items()
        )
        sql = f"update {table} set {sets}, updated_at = now() where id = '{pid}'"
        query(sql, token)
        print(f"  ✅ {name}: {list(fields.keys())}")
    print("完成。建議重跑本腳本確認歸零。")


if __name__ == "__main__":
    main()
