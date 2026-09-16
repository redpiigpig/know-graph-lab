"""把國小英語一千字重排，讓每課的「字母難易」平順遞增。

2026-09-16 使用者回報：第二課就要背 thumbs up／shake hands，第四十二課反而在背
go／up／down；L20 整課 20 個字有 13 個是多字片語（pearl milk tea…）。原本的分課
只按語意順序切 20 個一課，完全沒有考慮拼字難度。

作法（使用者定案「主題內重排＋搬走極端值」）：
  1. 二十個主題的**順序不動**，主題歸屬也不動——語意分組是課文寫得出來的前提。
  2. 成套的序列（one..ten、Monday..Sunday、方位介系詞…）整塊搬，不可以拆散。
  3. 主題是 50 字、課是 20 字，所以每個主題橫跨 2～3 課。把該主題的字分派到
     它所佔的那幾課，使每課難度貼近一條由易到難的目標曲線。

🚨 不要改成「主題內由易到難排序」——試過，每 2.5 課就重置一次，鋸齒反而從
   57.8 惡化到 103.2。要平順必須跨主題一起算（難的主題把難字丟給它所佔的
   最後一課，而那一課同時收下一個主題最簡單的字，就攤平了）。

用法：
    python scripts/reorder_english_vocab.py          # 只看重排後的難度曲線
    python scripts/reorder_english_vocab.py --write  # 真的寫回詞表
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
VOCAB = REPO / "data" / "originalReaders" / "vocabulary" / "english-1000.json"

# 成套的序列整塊搬。拆散了學生會在不同課遇到 one 跟 three，
# 課文也寫不出「數到十」這種情境。以主題內的 en 原字串指定。
PROTECTED_BLOCKS: list[tuple[str, ...]] = [
    ("what", "who", "how", "where", "when", "why", "which", "whose"),
    ("good morning", "good afternoon", "good evening", "good night"),
    ("one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten"),
    ("eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen",
     "seventeen", "eighteen", "nineteen", "twenty"),
    ("thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety",
     "hundred", "thousand", "million"),
    ("first", "second", "third", "fourth", "fifth", "sixth", "seventh",
     "eighth", "ninth", "tenth"),
    ("plus", "minus", "add", "equal"),
    ("red", "blue", "yellow", "green", "orange(s)", "purple", "pink",
     "brown", "black", "white", "gray", "gold"),
    ("circle", "line", "round", "square", "triangle", "diamond",
     "rectangle", "star", "arrow", "heart shape", "oval", "cube"),
    ("big", "large", "medium", "small"),
    ("breakfast", "lunch", "dinner"),
    ("elementary school", "junior high school", "senior high school"),
    ("in", "on", "under", "near", "behind", "beside", "above", "below",
     "here", "there"),
    ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"),
    ("January", "February", "March", "April", "May", "June", "July",
     "August", "September", "October", "November", "December"),
    ("morning", "noon", "afternoon", "evening", "night"),
    ("a.m.", "p.m."),
    ("spring", "summer", "autumn/fall", "winter"),
    ("up", "down", "left", "right", "into", "over", "out", "back", "front"),
    ("east", "west", "north"),
    ("Taipei", "New Taipei", "Beitou", "Taoyuan", "Taichung", "Tainan",
     "Kaohsiung", "Hualien"),
    ("Japan", "Korea", "Singapore", "Hong Kong", "Vietnam", "Thailand",
     "the Philippines", "Malaysia", "Canada", "Australia", "England",
     "France", "Germany", "India"),
    ("Chinese New Year", "red envelope", "Dragon Boat Festival",
     "Moon Festival", "moon cake", "Halloween", "pumpkin", "Christmas",
     "Santa Claus"),
]


def core(en: str) -> str:
    """取拼字主體：斜線取前者、去掉括號複數。

    詞表把複數寫成 apple(s)、mango(es)，也把同義寫成 father/dad。
    量難度只看學生真正要拼的那一個形式。
    """
    return re.sub(r"\(.*?\)", "", en.split("/")[0]).strip()


def score(en: str) -> float:
    """拼字難度：字母數 + 每多一個單字加 3 分。

    多字片語（pearl milk tea）對國小生遠比同長度的單字難記，所以另外加權；
    不然 L20 那種整課片語的又會排到前面去。
    """
    c = core(en)
    letters = len(c.replace(" ", "").replace(".", "").replace("-", ""))
    return letters + 3 * (c.count(" ") + c.count("-"))


def group_themes(entries: list[dict]) -> list[tuple[str, list[dict]]]:
    out: list[tuple[str, list[dict]]] = []
    for e in entries:
        if not out or out[-1][0] != e["theme"]:
            out.append((e["theme"], []))
        out[-1][1].append(e)
    return out


def build_units(words: list[dict]) -> list[list[dict]]:
    """把一個主題的字切成「單位」：成套序列是一個單位，其餘一字一個。"""
    index = {w["en"]: i for i, w in enumerate(words)}
    taken: set[int] = set()
    units: list[tuple[int, list[dict]]] = []
    for block in PROTECTED_BLOCKS:
        hits = [index[w] for w in block if w in index]
        if len(hits) < 2:
            continue
        if any(i in taken for i in hits):
            continue
        taken.update(hits)
        # 照 PROTECTED_BLOCKS 宣告的順序，不是詞表裡的順序——原詞表把 May 排在
        # December 後面（主題切分的副作用），照原順序搬會把五月印在十二月之後。
        units.append((min(hits), [words[index[w]] for w in block if w in index]))
    for i, w in enumerate(words):
        if i not in taken:
            units.append((i, [w]))
    units.sort(key=lambda u: u[0])          # 先回到原本的語意順序
    return [u[1] for u in units]


PASSES = 6


def _chunk_plan(themes: list[tuple[str, list[dict]]]) -> list[list[int]]:
    """算出每個主題要供應給哪幾課、各幾個字。

    主題 50 字、課 20 字，所以邊界一定錯開；這張表是純算術，不可調。
    """
    plans, pos = [], 0
    for _t, words in themes:
        plan, left = [], len(words)
        while left:
            take = min(left, 20 - pos % 20)
            plan.append(take)
            pos += take
            left -= take
        plans.append(plan)
    return plans


# 主題內由易到難的擺幅。整本書的「由易到難」做不到——二十個主題自己的難度
# 就是平的（都在 5.5 上下，只有飲料小吃、在學校、旅行節慶三個主題偏高），
# 主題順序又是語意決定的不能動。所以目標訂成「跟著各主題自己的水準走，
# 主題內由易到難」：沒有尖峰，每個新主題都從簡單的字開頭。
AMP = 0.5

# 第一課是孩子這輩子第一頁英文，硬壓到全書最簡單（I、you、hi、no…）。
# 這一步會在 L01→L02 之間留一個刻意的台階，不算震盪。
HEAD_EASE = (2.2, 0.8)

# 位移懲罰。調大＝更貼近原本人工排的順序、只搬極端值；調小＝難度曲線更漂亮
# 但常用字會被拼字長度擠到後面去。
MU = 0.10

# 成套序列（≥4 個字）的搬家代價倍率
BLOCK_ANCHOR = 12

_TARGETS: list[float] = []


def _build_targets(themes, plans) -> None:
    """算出每一課的目標難度，存進 _TARGETS（0-based）。"""
    cells: list[tuple[int, int, float]] = []   # (第幾課, 字數, 該格目標)
    pos = 0
    for (_t, words), plan in zip(themes, plans):
        mean = sum(score(w["en"]) for w in words) / len(words)
        span = len(plan)
        for k, take in enumerate(plan):
            shift = 0.0 if span == 1 else AMP * (2 * k / (span - 1) - 1)
            cells.append((pos // 20, take, mean + shift))
            pos += take
    _TARGETS[:] = [0.0] * 50
    for n in range(50):
        got = [(c, t) for lesson, c, t in cells if lesson == n]
        _TARGETS[n] = sum(c * t for c, t in got) / sum(c for c, _ in got)
    for n, ease in enumerate(HEAD_EASE):
        _TARGETS[n] -= ease


def _target(n: int) -> float:
    """第 n 課（1-based）的目標難度。"""
    return _TARGETS[n - 1]


def _lesson_means(seq: list[dict]) -> list[float]:
    return [sum(score(w["en"]) for w in seq[i:i + 20]) / 20 for i in range(0, 1000, 20)]


def _lesson_cost(total: float, n: int) -> float:
    """第 n 課（0-based）與目標曲線的平方偏離。"""
    return (total / 20 - _target(n + 1)) ** 2


def _pack(units: list[list[dict]], plan: list[int]) -> list[list[list[dict]]]:
    """把一個主題的單位裝進各課配額，每格必須**剛好**填滿。

    成套序列（最長 14 個字）不能拆，貪心會卡住——例如剩 3 格卻只剩 12 個字的
    月份區塊。所以照原順序回溯，第一組解就用。

    🚨 一定要照**原順序**放。原本那份一千字是人工排的，同一個主題裡本來就把
    常用字擺前面（I、you、hello 在前，wink、whisper 在後）。改成大的先放，
    she／you／hello 會被擠到第三課而 wink／whisper 留在第一課。
    """
    chunks: list[list[int]] = [[] for _ in plan]
    left = list(plan)

    def dfs(i: int) -> bool:
        if i == len(units):
            return True
        for c in range(len(plan)):
            if left[c] >= len(units[i]):
                left[c] -= len(units[i])
                chunks[c].append(i)
                if dfs(i + 1):
                    return True
                chunks[c].pop()
                left[c] += len(units[i])
        return False

    if not dfs(0):
        raise RuntimeError(f"裝不下：配額 {plan}，單位大小 {[len(u) for u in units]}")
    return [[units[u] for u in sorted(c)] for c in chunks]


def _drift(unit: list[dict], lesson: int) -> float:
    """把一個單位擺到第 lesson 課（0-based）要付的「離開原位」代價。

    原本那份一千字是人工排的，順序本身帶著常用度。只讓真正的極端值（拼字
    特別長、多字片語）值得付這個代價搬家，其餘維持原樣。

    🚨 成套序列另外加重。序列**彼此之間**也有先後（one..ten → eleven..twenty
    → thirty..million → 序數），但難度只看字母數：eleven..twenty 平均 7.3 比
    thirty..million 的 6.2 長，照難度排就會把序數與百千萬排到十一～二十之前。
    原順序本來是對的，加重代價讓它們留在原位最省事。
    """
    weight = MU * (BLOCK_ANCHOR if len(unit) >= 4 else 1)
    return weight * sum((lesson - (w["lesson"] - 1)) ** 2 for w in unit)


def _swap_block(chunks, totals, x, y, lx, ly) -> bool:
    """把 x 格裡的一個成套區塊，跟 y 格裡等量的單字對換；換了就回 True。

    成套區塊（8 個疑問詞、12 個月份…）全書找不到第二個同樣大的單位可換，
    只靠等大互換會永遠卡在初始被塞進的那一格。
    """
    usum = lambda unit: sum(score(w["en"]) for w in unit)
    for i, u in enumerate(chunks[x]):
        if len(u) < 2:
            continue
        ones = sorted((k for k, w in enumerate(chunks[y]) if len(w) == 1),
                      key=lambda k: score(chunks[y][k][0]["en"]))
        if len(ones) < len(u):
            continue
        for pick in (ones[:len(u)], ones[-len(u):]):
            delta = sum(usum(chunks[y][k]) for k in pick) - usum(u)
            if abs(delta) < 1e-9:
                continue
            swap = [chunks[y][k] for k in pick]
            now = (_lesson_cost(totals[lx], lx) + _lesson_cost(totals[ly], ly)
                   + _drift(u, lx) + sum(_drift(s, ly) for s in swap))
            new = (_lesson_cost(totals[lx] + delta, lx) + _lesson_cost(totals[ly] - delta, ly)
                   + _drift(u, ly) + sum(_drift(s, lx) for s in swap))
            if new >= now - 1e-9:
                continue
            moved = [chunks[y][k] for k in pick]
            for k in sorted(pick, reverse=True):
                chunks[y].pop(k)
            chunks[y].append(u)
            chunks[x].pop(i)
            chunks[x].extend(moved)
            totals[lx] += delta
            totals[ly] -= delta
            return True
    return False


def reorder(entries: list[dict]) -> list[dict]:
    themes = group_themes(entries)
    plans = _chunk_plan(themes)
    _build_targets(themes, plans)

    # 每個主題先照原順序填進自己的各課配額；同時記下每一格供應的是第幾課
    buckets: list[list[list[list[dict]]]] = []
    lesson_of: list[list[int]] = []
    pos = 0
    for (_t, words), plan in zip(themes, plans):
        buckets.append(_pack(build_units(words), plan))
        lesson_of.append([(pos + sum(plan[:k])) // 20 for k in range(len(plan))])
        pos += sum(plan)

    def flatten() -> list[dict]:
        return [w for chunks in buckets for got in chunks for unit in got for w in unit]

    usum = lambda unit: sum(score(w["en"]) for w in unit)
    totals = [sum(score(w["en"]) for w in flatten()[i:i + 20]) for i in range(0, 1000, 20)]

    # 局部搜尋：同主題內、大小相同的兩個單位互換（等大才不會撐破配額）。
    # 一次交換只動到那兩格所屬的兩課，所以成本用增量算——整本重算會慢上千倍。
    for _ in range(PASSES):
        improved = False
        for chunks, lessons in zip(buckets, lesson_of):
            for a in range(len(chunks)):
                for b in range(a + 1, len(chunks)):
                    la, lb = lessons[a], lessons[b]
                    if la == lb:
                        continue
                    for i in range(len(chunks[a])):
                        for j in range(len(chunks[b])):
                            u, v = chunks[a][i], chunks[b][j]
                            if len(u) != len(v):
                                continue
                            du = usum(v) - usum(u)
                            if abs(du) < 1e-9:
                                continue
                            now = (_lesson_cost(totals[la], la) + _lesson_cost(totals[lb], lb)
                                   + _drift(u, la) + _drift(v, lb))
                            new = (_lesson_cost(totals[la] + du, la)
                                   + _lesson_cost(totals[lb] - du, lb)
                                   + _drift(u, lb) + _drift(v, la))
                            if new < now - 1e-9:
                                chunks[a][i], chunks[b][j] = v, u
                                totals[la] += du
                                totals[lb] -= du
                                improved = True
                    # 成套區塊（8 個疑問詞、12 個月份…）全書找不到第二個同樣大的
                    # 單位可換，只靠等大互換會永遠卡在初始那一格。另外開一種換法：
                    # 整塊 ↔ 對面等量的單字。
                    for x, y in ((a, b), (b, a)):
                        while _swap_block(chunks, totals, x, y, lessons[x], lessons[y]):
                            improved = True
        if not improved:
            break

    # 課內先排單字（由易到難），成套序列擺後面並照原順序。
    # 🚨 成套序列不能跟著難度排：eleven..twenty 平均字母比 thirty..million 長，
    # 照難度排會在同一課裡把「三十～百萬」印在「十一～二十」前面。
    for chunks in buckets:
        for k, got in enumerate(chunks):
            ones = sorted((u for u in got if len(u) < 4),
                          key=lambda u: sum(score(w["en"]) for w in u) / len(u))
            blocks = sorted((u for u in got if len(u) >= 4), key=lambda u: u[0]["ordinal"])
            chunks[k] = ones + blocks
    return flatten()


def profile(entries: list[dict]) -> list[tuple[int, float, int]]:
    rows = []
    for n in range(1, 51):
        ws = [e["en"] for e in entries[(n - 1) * 20:n * 20]]
        rows.append((n, sum(score(w) for w in ws) / len(ws),
                     sum(1 for w in ws if " " in core(w))))
    return rows


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()

    data = json.loads(VOCAB.read_text(encoding="utf-8"))
    before = data["entries"]
    after = reorder(before)
    assert len(after) == len(before) == 1000
    assert {e["en"] for e in after} == {e["en"] for e in before}
    # 主題歸屬不可被動到：第 n 個字的主題必須跟原本第 n 個字的主題一致
    assert [e["theme"] for e in after] == [e["theme"] for e in before]

    old, new = profile(before), profile(after)
    print(f"{'課':>3} {'原':>6} {'新':>6} {'目標':>6}  {'原片語':>5} {'新片語':>5}")
    for (n, a, am), (_, b, bm) in zip(old, new):
        print(f"{n:3d} {a:6.1f} {b:6.1f} {_target(n):6.1f}  {am:5d} {bm:5d}  {'#' * int(b * 2)}")
    jag = lambda p: sum(abs(p[i][1] - p[i - 1][1]) for i in range(1, len(p)))
    dev = lambda p: sum(abs(x[1] - _target(x[0])) for x in p) / 50
    print(f"\n相鄰課震盪總和 {jag(old):.1f} -> {jag(new):.1f}")
    print(f"與目標曲線的平均偏離 {dev(old):.2f} -> {dev(new):.2f}")

    if not args.write:
        print("\n（沒加 --write，詞表沒有動）")
        return
    for i, e in enumerate(after, 1):
        e["ordinal"] = i
        e["lesson"] = (i - 1) // 20 + 1
    data["entries"] = after
    VOCAB.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n",
                     encoding="utf-8")
    print(f"\n已寫回 {VOCAB}")


if __name__ == "__main__":
    main()
