# -*- coding: utf-8 -*-
"""把 R2 上的 JSONL／txt 就地改存 gzip。

為什麼：時間幾乎全花在 R2→伺服器的下載上，不是解析。實測教會公報 2011 整包
  原樣  下載 5.6 MB 1,829 ms ｜ 解析  5 ms                 ｜ 合計 1,834 ms
  gzip  下載 2.5 MB   795 ms ｜ 解壓 42 ms ｜ 解析 17 ms   ｜ 合計   855 ms
所以壓縮同時省容量（中文純文字壓到 43%）又快一倍以上，瀏覽器端毫無感覺。

🚨 **先寫 .gz、讀回來比對、相同才刪原檔**。反過來做（先刪再寫）只要中途斷線
   就是永久資料損失，而 R2 沒有版本控制可回溯。
🚨 讀取端（server/utils/r2-text.ts 與 dadaodao_fulltext.r2_get_text）都是
   「先試 .gz、沒有才退回原檔」＋認 gzip 魔術位元組，所以遷移中途兩種並存也不會壞。

  python -X utf8 scripts/r2_gzip_migrate.py <前綴> [--go]
  python -X utf8 scripts/r2_gzip_migrate.py pct-fulltext/tcnn --go
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import dadaodao_fulltext as df  # noqa: E402


def migrate(prefix: str, go: bool):
    keys = sorted(k for k in df.r2_existing_keys(prefix) if not k.endswith(".gz"))
    if not keys:
        print(f"{prefix}：沒有未壓縮的物件")
        return
    before = after = 0
    done = skipped = 0
    for k in keys:
        head = df.s3.head_object(Bucket=df.R2_BUCKET, Key=k)
        size = head["ContentLength"]
        before += size
        text = df.r2_get_text(k)
        gz_key = k + ".gz"
        if not go:
            import gzip
            after += len(gzip.compress(text.encode("utf-8"), 6))
            done += 1
            continue
        df.r2_put_text_gz(gz_key, text)
        # 驗證：讀回來要一字不差，才敢刪原檔
        if df.r2_get_text(gz_key) != text:
            print(f"  ! {k}：壓縮後讀回不一致，保留原檔", flush=True)
            df.s3.delete_object(Bucket=df.R2_BUCKET, Key=gz_key)
            skipped += 1
            continue
        after += df.s3.head_object(Bucket=df.R2_BUCKET, Key=gz_key)["ContentLength"]
        df.s3.delete_object(Bucket=df.R2_BUCKET, Key=k)
        done += 1
        if done % 200 == 0:
            print(f"  …已轉 {done}/{len(keys)}", flush=True)
    tag = "" if go else "（dry-run，加 --go 才真的轉）"
    print(f"{prefix}：{done} 個{'、驗證失敗保留 ' + str(skipped) if skipped else ''} "
          f"{before/1024**2:.1f} MB → {after/1024**2:.1f} MB "
          f"（{after/before*100:.0f}%，省 {(before-after)/1024**2:.1f} MB）{tag}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("prefix")
    ap.add_argument("--go", action="store_true")
    a = ap.parse_args()
    migrate(a.prefix, a.go)


if __name__ == "__main__":
    main()
