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
import io, sys, traceback
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.path.insert(0, str(Path(__file__).resolve().parent))
import plato_build as pb  # noqa: E402

LOG = Path("c:/tmp/greek_overnight.log")


def log(msg: str) -> None:
    print(msg, flush=True)
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
        try:
            log(f"[run ] {slug}  {d['author']}《{d['title_zh']}》 …")
            chunks = pb.run(slug, engine="haiku", upload=True)
            marker.write_text("ok", encoding="utf-8")
            ok.append(slug)
            log(f"[ok  ] {slug}  {len(chunks)} chunks")
        except KeyboardInterrupt:
            log("[中斷] 使用者停止；已完成部保留 marker，重跑自動續。")
            raise
        except Exception as e:  # noqa: BLE001
            fail.append(slug)
            log(f"[FAIL] {slug}: {e}")
            log(traceback.format_exc())
    log(f"=== 完成：{len(ok)} ok / {len(fail)} fail / {len(skip)} skip ===")
    log(f"ok={ok}")
    if fail:
        log(f"fail={fail}（重跑 greek_overnight.py 會自動續，快取不重翻）")


if __name__ == "__main__":
    main()
