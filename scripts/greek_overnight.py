# -*- coding: utf-8 -*-
"""古希臘全集‧整夜自動化 queue — 把柏拉圖＋亞里斯多德所有可得作品逐部三欄轉錄上架。

每部走 plato_build.run(slug, engine='haiku', --upload)：逐節快取（resumable）、per-work try/except
（一部失敗不中斷整夜）、成功寫 `<slug>.done` marker（重跑自動跳過已完成部）。整夜跑、隔夜續。

用法：
  python scripts/greek_overnight.py            # 跑完所有未完成部（apology 已完成，跳過）
  python scripts/greek_overnight.py --force    # 無視 done marker 全部重跑
  python scripts/greek_overnight.py --only nicomachean-ethics poetics   # 只跑指定部
"""
from __future__ import annotations
import io, sys, time, traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import plato_build as pb  # noqa: E402  (import 時已把 sys.stdout 設成 utf-8；勿再重包＝雙包會關掉 buffer)

LOG = Path("c:/tmp/greek_overnight.log")
# NVIDIA (deepseek-v4-flash, 4-key rotation + throttle) — generous free tier，
# 不像 Haiku(Claude Max) 那樣 bulk 撞 429。可 `--engine haiku/gemini` 覆蓋。
ENGINE = sys.argv[sys.argv.index("--engine") + 1] if "--engine" in sys.argv else "nvidia"


def log(msg: str) -> None:
    try:
        print(msg, flush=True)
    except (ValueError, OSError):
        pass  # stdout 被關（背景管線）仍續寫檔，不讓整夜 queue 掛掉
    with io.open(LOG, "a", encoding="utf-8") as f:
        f.write(msg + "\n")


def main() -> None:
    force = "--force" in sys.argv
    only = sys.argv[sys.argv.index("--only") + 1:] if "--only" in sys.argv else None
    # 佇列：republic 先（大部、續快取）→ 其餘柏拉圖 → 亞里斯多德；apology 已完成跳過
    order = [s for s in pb.WORKS if s != "apology"]
    if only:
        order = [s for s in order if s in only]
    log(f"=== greek overnight：{len(order)} 部待處理 ===")
    ok, fail, skip = [], [], []
    for slug in order:
        marker = pb.CACHE / f"{slug}.done"
        if marker.exists() and not force:
            skip.append(slug)
            log(f"[skip] {slug}（已完成）")
            continue
        d = pb.WORKS[slug]
        # 每部重試 3 次：NVIDIA 偶發 ConnectionError 會廢掉一整部（一節掛全部掛），
        # 但快取保住已翻節 → 重試只從掛掉處續，不重翻。
        done_ok = False
        for attempt in range(1, 4):
            try:
                log(f"[run ] {slug}  {d['author']}《{d['title_zh']}》 …（第 {attempt} 次）")
                chunks = pb.run(slug, engine=ENGINE, upload=True)
                marker.write_text("ok", encoding="utf-8")
                ok.append(slug)
                log(f"[ok  ] {slug}  {len(chunks)} chunks")
                done_ok = True
                break
            except KeyboardInterrupt:
                log("[中斷] 使用者停止；已完成部保留 marker，重跑自動續。")
                raise
            except Exception as e:  # noqa: BLE001
                log(f"[retry] {slug} 第 {attempt}/3 次失敗：{e}")
                time.sleep(20)
        if not done_ok:
            fail.append(slug)
            log(f"[FAIL] {slug}（3 次皆失敗，快取保留，之後重跑自動續）")
    log(f"=== 完成：{len(ok)} ok / {len(fail)} fail / {len(skip)} skip ===")
    log(f"ok={ok}")
    if fail:
        log(f"fail={fail}（重跑 greek_overnight.py 會自動續，快取不重翻）")


if __name__ == "__main__":
    main()
