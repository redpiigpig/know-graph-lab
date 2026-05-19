#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""演講／講座 Gemini Audio 轉錄器（單檔）。

模型 gemini-2.5-flash + PPT 文字 context；輸出未潤稿的繁體中文逐字稿，
講者多半是「講者：」，Q&A 區分「提問者A：」「講者：」。

用法：
  python scripts/transcribe_talk_gemini.py AUDIO --out FILE \\
        --ppt-text PPT_TXT --speaker "張辰瑋" \\
        --title "台灣佛教具有「民主基因」嗎？"
"""
import argparse
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

REPO_DIR = Path(__file__).parent.parent
_env: dict[str, str] = {}
for _line in (REPO_DIR / ".env").read_text(encoding="utf-8").splitlines():
    if "=" in _line and not _line.startswith("#"):
        _k, _, _v = _line.partition("=")
        _env[_k.strip()] = _v.strip().strip('"')


def _find_keys() -> list[str]:
    raw: list[str] = []
    for name in ("GEMINI_API_KEY", "Gemini_API_Key"):
        v = _env.get(name)
        if v:
            raw.append(v); break
    for n in range(1, 11):
        for base in ("Gemini_API_Key", "GEMINI_API_KEY"):
            v = _env.get(f"{base}_{n}")
            if v:
                raw.append(v); break
    keys, seen = [], set()
    for r in raw:
        for p in r.split(","):
            k = p.strip()
            if k and k not in seen:
                seen.add(k); keys.append(k)
    return keys


GEMINI_KEYS = _find_keys()
if not GEMINI_KEYS:
    sys.exit("ERROR: 沒找到 GEMINI_API_KEY 在 .env")


AUDIO_MIME = {".m4a": "audio/mp4", ".mp4": "audio/mp4", ".mp3": "audio/mpeg",
              ".wav": "audio/wav", ".webm": "audio/webm", ".opus": "audio/ogg"}


def transcribe(audio_path: Path, ppt_text: str, speaker: str, title: str) -> str:
    try:
        from google import genai
        from google.genai import types
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "google-genai", "-q"])
        from google import genai
        from google.genai import types

    last_err = None
    # 每把 key 最多重試 3 次，每次間隔 15 秒（對付 503 high demand）
    for key_idx, key in enumerate(GEMINI_KEYS, 1):
      for attempt in range(1, 4):
        try:
            client = genai.Client(api_key=key)
            sz_mb = audio_path.stat().st_size / 1024 / 1024
            print(f"[key #{key_idx}] uploading {audio_path.name} ({sz_mb:.1f} MB)...", flush=True)

            with tempfile.NamedTemporaryFile(suffix=audio_path.suffix, delete=False) as tmp:
                tmp_path = Path(tmp.name)
            shutil.copyfile(audio_path, tmp_path)
            try:
                mime = AUDIO_MIME.get(audio_path.suffix.lower(), "audio/mp4")
                uploaded = client.files.upload(
                    file=tmp_path,
                    config=types.UploadFileConfig(
                        display_name=f"talk_{audio_path.stem[:40]}", mime_type=mime,
                    ),
                )
            finally:
                try: tmp_path.unlink()
                except Exception: pass

            for _ in range(120):
                fi = client.files.get(name=uploaded.name)
                state = fi.state.name if hasattr(fi.state, "name") else str(fi.state)
                if state == "ACTIVE": break
                if state == "FAILED": raise RuntimeError("Gemini file processing failed")
                print(f"  state={state}, waiting...", flush=True)
                time.sleep(3)

            ctx_section = ""
            if ppt_text:
                ctx_section = (
                    "以下是本場講座的 PPT 投影片文字內容，請作為人名、書名、"
                    "術語、引用文獻、章節標題的轉錄參考（講者所說的話請完整轉錄）：\n"
                    f"---PPT---\n{ppt_text}\n---PPT END---\n\n"
                )

            prompt = f"""你正在聆聽一段繁體中文的學術講座錄音。

講座資訊：
- 場合：玄奘大學宗教學系專題講座
- 標題：{title}
- 主講人：{speaker}（兼任講師）
- 對象：宗教學系學生

{ctx_section}請將整段音訊完整轉錄成繁體中文逐字稿。

轉錄要求：
1. 使用繁體中文（台灣用語），不要簡體。
2. 講者改變時新起一段，標出說話者：
   - 主講人寫成「講者：」（不要寫名字）
   - 聽眾／學生提問寫成「提問：」（若有多位提問者，第一位用「提問A：」、第二位「提問B：」⋯⋯）
   - 主持人寫成「主持人：」
3. 完整保留講者原話，不改寫、不摘要、不潤飾語法錯誤。保留口語語助詞（嘛、啊、喔、那）和重複，但連續重複超過 3 次的相同字詞可只保留 1 次。
4. 正確使用全形標點：，。：；？！「」《》——……（）
5. 學術人名、書名、術語、寺院名請對照 PPT 文字：
   - 人名：Richard Madsen / 趙文詞、Robert Bellah / 貝拉、印順、昭慧、聖嚴、星雲、證嚴、惟覺
   - 書名：《民主妙法》Democracy's Dharma、《心靈的習性》Habits of the Heart
   - 教團：法鼓山、慈濟、佛光山、中台禪寺、福智、靈鷲山、弘誓
   - 概念：人間佛教、解嚴、政教互動、公民社會、宗教復興
6. 若有靜音、休息時段、與第三人短暫對話、設備調整，可省略或用「（休息／中斷）」標註。
7. 不加時間戳記、不加章節標號、不加前言或後記，直接輸出整段內容。

請開始輸出："""

            print("  generating transcription...", flush=True)
            resp = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[uploaded, prompt],
            )
            try: client.files.delete(name=uploaded.name)
            except Exception: pass
            return resp.text.strip()
        except Exception as e:
            msg = str(e)
            print(f"  [key #{key_idx} try {attempt}] failed: {e}", flush=True)
            last_err = e
            # 503 high demand → 同 key sleep 後重試；其他錯誤直接換 key
            if "503" in msg or "UNAVAILABLE" in msg.upper():
                if attempt < 3:
                    time.sleep(15 * attempt)
                    continue
            break  # 換下一把 key

    raise RuntimeError(f"所有 Gemini API key 都失敗，最後錯誤：{last_err}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("audio")
    ap.add_argument("--out", required=True)
    ap.add_argument("--ppt-text", help="PPT 已抽出的純文字 txt 路徑")
    ap.add_argument("--speaker", default="主講人")
    ap.add_argument("--title", default="")
    args = ap.parse_args()

    audio_path = Path(args.audio)
    if not audio_path.exists():
        sys.exit(f"音檔不存在：{audio_path}")

    ppt_text = ""
    if args.ppt_text:
        pp = Path(args.ppt_text)
        if pp.exists():
            ppt_text = pp.read_text(encoding="utf-8")
            print(f"PPT context: {len(ppt_text)} chars", flush=True)

    text = transcribe(audio_path, ppt_text, args.speaker, args.title)
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(text + "\n", encoding="utf-8", newline="\n")
    print(f"\n✓ 寫出 {len(text)} 字 → {out_path}")


if __name__ == "__main__":
    main()
