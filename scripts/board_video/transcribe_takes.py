# -*- coding: utf-8 -*-
"""把實拍的片段逐句轉錄成時間戳，供剪接對點與字幕使用。

使用者錄的問好與序幕正文是真人原音，時間軸得照他實際講的速度走，
所以先用 whisper 拿逐句起訖，再據此決定哪一句要切畫面。

輸出：素材/片頭/逐句時間.json
"""
import json
from pathlib import Path

PROJ = Path(r"G:\我的雲端硬碟\創作\影片創作\人魚島解說")
SRC = PROJ / "素材" / "片頭"
OUT = SRC / "逐句時間.json"


def main():
    from faster_whisper import WhisperModel
    model = WhisperModel("small", device="cpu", compute_type="int8")
    result = {}
    for f in sorted(SRC.glob("*.mp4")):
        segs, _ = model.transcribe(str(f), language="zh", vad_filter=True)
        rows = [dict(t=round(s.start, 2), e=round(s.end, 2), text=s.text.strip()) for s in segs]
        result[f.name] = rows
        print(f"── {f.name}（{len(rows)} 句）")
        for r in rows:
            print(f"  {r['t']:6.2f}–{r['e']:6.2f}  {r['text']}")
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\n寫出 {OUT}")


if __name__ == "__main__":
    main()
