"""
口述訪談音檔下載與轉錄流水線
- 使用 gdown 從 Google Drive 下載音檔
- 使用 faster-whisper 進行中文語音辨識
- 輸出帶有標準格式標頭的逐字稿
執行方式：python scripts/transcribe-interviews.py
"""

import os, sys, subprocess, textwrap, re
from pathlib import Path

try:
    import gdown
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "gdown", "-q"])
    import gdown

try:
    from faster_whisper import WhisperModel
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "faster-whisper", "-q"])
    from faster_whisper import WhisperModel

# ── 輸出目錄 ───────────────────────────────────────────────────
OUT_DIR = Path(__file__).parent.parent / "public" / "content" / "interviews"
TMP_DIR = Path(__file__).parent.parent / "_tmp_audio"
TMP_DIR.mkdir(exist_ok=True)

# ── 待轉錄訪談清單 ─────────────────────────────────────────────
# 格式：dict with keys:
#   file_id     - Google Drive file ID
#   out_file    - 輸出 txt 檔名（放到 OUT_DIR）
#   title       - 訪談標題（含受訪者名稱）
#   interviewee - 受訪者姓名
#   role        - 受訪者身分
#   date        - 訪問時間
#   location    - 訪問地點
#   category    - 分類（法師/學者/宗教對話/社運界/其他）
#   notes       - 備注（optional）

INTERVIEWS = [
    {
        "file_id": "1t1_Lw01BPRiMqUP2-85HgXcTh9hVgmqM",
        "audio_name": "01.16 印悅法師訪談.m4a",
        "out_file": "01.16 釋印悅法師口述訪談紀錄.txt",
        "title": "戒律與弘誓的傳承：釋印悅法師訪談記",
        "interviewee": "釋印悅法師",
        "role": "佛教弘誓學院法師",
        "date": "2024年1月16日",
        "location": "佛教弘誓學院嵐園",
        "category": "法師",
    },
    {
        "file_id": "1uvAVlnG8MAQQkwFjBmGDfdS_Pz0FOw7L",
        "audio_name": "心皓法師訪談合併.mp3",
        "out_file": "01.17 釋心皓法師口述訪談紀錄.txt",
        "title": "人間菩薩道的日常：釋心皓法師訪談記",
        "interviewee": "釋心皓法師",
        "role": "佛教弘誓學院法師",
        "date": "2024年1月17日",
        "location": "佛教弘誓學院嵐園",
        "category": "法師",
    },
    {
        "file_id": "1TcuG-yP_3gQCfov4t0I4CIsisARxu-8b",
        "audio_name": "01.17 王彩虹居士訪談.m4a",
        "out_file": "01.17 王彩虹居士口述訪談紀錄.txt",
        "title": "護持弘誓的菩薩行：王彩虹居士訪談記",
        "interviewee": "王彩虹居士",
        "role": "佛教弘誓學院護持者",
        "date": "2024年1月17日",
        "location": "佛教弘誓學院嵐園",
        "category": "其他",
    },
    {
        "file_id": "1NHZtkZNok2VU-Dk4W7lbEOo19iMSqxqT",
        "audio_name": "02.14 悅萱老師訪問.m4a",
        "out_file": "02.14 陳悅萱老師口述訪談紀錄.txt",
        "title": "以音樂傳揚人間佛教：陳悅萱老師訪談記",
        "interviewee": "陳悅萱老師",
        "role": "佛教音樂工作者",
        "date": "2024年2月14日",
        "location": "台北市松山區咖啡廳",
        "category": "其他",
    },
    {
        "file_id": "12-SKyISny4BIqhYEeUMq0KnQVUftlULJ",
        "audio_name": "05.02 黃美瑜游雅婷訪談.m4a",
        "out_file": "05.02 黃美瑜女士游雅婷女士口述訪談紀錄.txt",
        "title": "親歷社運現場的見證：黃美瑜女士、游雅婷女士訪談記",
        "interviewee": "黃美瑜女士、游雅婷女士",
        "role": "社會運動工作者",
        "date": "2024年5月2日",
        "location": "台北市萬華區黃宅",
        "category": "社運界",
    },
    {
        "file_id": "1BjzJCOgmolU4xCAfcOjymtRwkDkAWGTk",
        "audio_name": "05.07 張章得先生訪談.m4a",
        "out_file": "05.07 張章得先生口述訪談紀錄.txt",
        "title": "以慈悲守護眾生：張章得先生訪談記",
        "interviewee": "張章得先生",
        "role": "關懷生命協會工作者",
        "date": "2024年5月7日",
        "location": "台北市中山區關懷生命協會",
        "category": "社運界",
    },
    {
        "file_id": "1fqVwOEqk9gt0p1oEueDy9lx3NTODvey_",
        "audio_name": "05.11 見岸法師訪談.m4a",
        "out_file": "05.11 釋見岸法師口述訪談紀錄.txt",
        "title": "佛教弘誓學院的修行生活：釋見岸法師訪談記",
        "interviewee": "釋見岸法師",
        "role": "佛教弘誓學院法師",
        "date": "2024年5月11日",
        "location": "電話訪談",
        "category": "法師",
    },
    {
        "file_id": "17MSxtDpwXnkULZKYXsT0DLqSZ7vG9o3t",
        "audio_name": "05.23 詹錫奎先生訪問.m4a",
        "out_file": "05.23 詹錫奎先生口述訪談紀錄.txt",
        "title": "動保運動與人間佛教的相遇：詹錫奎先生訪談記",
        "interviewee": "詹錫奎先生",
        "role": "動物保護運動人士",
        "date": "2024年5月23日",
        "location": "新北市汐止區詹宅",
        "category": "社運界",
    },
    {
        "file_id": "1ESA-HHBJ50u0yqoWmYUjKCRIIzJhRx6t",
        "audio_name": "05.28 朱增宏先生口述訪談.m4a",
        "out_file": "05.28 朱增宏先生口述訪談紀錄.txt",
        "title": "台灣動保運動的奠基者：朱增宏先生訪談記",
        "interviewee": "朱增宏先生",
        "role": "台灣動物社會研究會創辦人",
        "date": "2024年5月28日",
        "location": "台北市中正區台灣動物社會研究會",
        "category": "社運界",
    },
    {
        "file_id": "1UMjKcRCuIPHEUCpPNzENZF-gnq2wY6XX",
        "audio_name": "06.17 長叡法師訪談.m4a",
        "out_file": "06.17 釋長叡法師口述訪談紀錄.txt",
        "title": "都會弘法的人間菩薩：釋長叡法師訪談記",
        "interviewee": "釋長叡法師",
        "role": "台北市中山區慧日講堂住持",
        "date": "2024年6月17日",
        "location": "台北市中山區慧日講堂",
        "category": "法師",
    },
    {
        "file_id": "1CsVWt3rsP4-3xDle-IKGL9xN7lKnvbBY",
        "audio_name": "09.03 林蓉芝居士訪談.m4a",
        "out_file": "09.03 林蓉芝居士口述訪談紀錄.txt",
        "title": "南台灣佛教協力網絡：林蓉芝居士訪談記",
        "interviewee": "林蓉芝居士",
        "role": "中華佛寺協會工作者",
        "date": "2024年9月3日",
        "location": "高雄市鼓山區中華佛寺協會",
        "category": "其他",
    },
    {
        "file_id": "1VUsPks2ZBkaXm1uPACSTIacZcnzxFuzL",  # 新錄音 38.m4a
        "audio_name": "03.01 心謙法師訪談.m4a",
        "out_file": "03.01 釋心謙法師口述訪談紀錄.txt",
        "title": "禪修與弘誓精神的實踐：釋心謙法師訪談記",
        "interviewee": "釋心謙法師",
        "role": "佛教弘誓學院法師",
        "date": "2025年3月1日",
        "location": "佛教弘誓學院嵐園",
        "category": "法師",
    },
    {
        "file_id": "16fOw5bCD4Tgn5WwEx2pqtykE4ONCocbs",  # 新錄音 60.m4a
        "audio_name": "03.15 心玄法師訪談.m4a",
        "out_file": "03.15 釋心玄法師口述訪談紀錄.txt",
        "title": "從求法到弘法的菩薩之路：釋心玄法師訪談記",
        "interviewee": "釋心玄法師",
        "role": "玄奘大學宗教與文化學系",
        "date": "2025年3月15日",
        "location": "玄奘大學雲來二館",
        "category": "法師",
    },
]

# ── 格式化輸出 ─────────────────────────────────────────────────
def format_transcript(iv: dict, segments) -> str:
    """將 Whisper 分段輸出格式化為標準訪談文字稿"""
    lines = []

    # 標題
    lines.append(iv["title"])
    lines.append(f"受訪者：{iv['interviewee']}")
    lines.append(f"訪問時間：{iv['date']}")
    lines.append(f"訪問地點：{iv['location']}")
    lines.append("")

    # 合併 segments 為段落（靜默 > 2s 換行）
    text_blocks = []
    current_block = []
    prev_end = 0.0

    for seg in segments:
        gap = seg.start - prev_end
        if gap > 2.0 and current_block:
            text_blocks.append("".join(current_block).strip())
            current_block = []
        current_block.append(seg.text)
        prev_end = seg.end

    if current_block:
        text_blocks.append("".join(current_block).strip())

    # 輸出段落
    lines.append("【以下為語音轉錄逐字稿，尚待分段、加標題、區分問答】")
    lines.append("")
    for block in text_blocks:
        if block:
            # 在「筆者：」或人名後的冒號處嘗試辨識換行
            block = re.sub(r'([。！？])\s*([筆者昭慧法師性廣侯坤宏邱敏捷黃運喜楊惠南闞正宗林建德])', r'\1\n\2', block)
            lines.append(block)
            lines.append("")

    if iv.get("notes"):
        lines.append(f"【備注：{iv['notes']}】")

    return "\n".join(lines)


# ── 主程式 ─────────────────────────────────────────────────────
def main():
    print("載入 Whisper 模型（tiny）...")
    model = WhisperModel("tiny", device="cpu", compute_type="int8")
    print("模型載入完成")

    for i, iv in enumerate(INTERVIEWS, 1):
        out_path = OUT_DIR / iv["out_file"]
        if out_path.exists():
            print(f"[{i}/{len(INTERVIEWS)}] 跳過（已存在）：{iv['out_file']}")
            continue

        audio_path = TMP_DIR / iv["audio_name"]

        # 下載
        if not audio_path.exists():
            print(f"[{i}/{len(INTERVIEWS)}] 下載：{iv['audio_name']} ...")
            try:
                url = f"https://drive.google.com/uc?id={iv['file_id']}"
                gdown.download(url, str(audio_path), quiet=False)
            except Exception as e:
                print(f"  下載失敗：{e}")
                continue
        else:
            print(f"[{i}/{len(INTERVIEWS)}] 已有音檔：{iv['audio_name']}")

        # 轉換為 WAV（避免 Windows 上 m4a/mp3 解碼 crash）
        wav_path = TMP_DIR / (audio_path.stem + ".wav")
        if not wav_path.exists():
            print(f"  轉換 WAV...")
            ret = subprocess.call(
                ["ffmpeg", "-i", str(audio_path), "-ar", "16000", "-ac", "1",
                 "-c:a", "pcm_s16le", str(wav_path), "-y"],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
            if ret != 0:
                print(f"  ffmpeg 轉換失敗，嘗試直接使用原始檔...")
                wav_path = audio_path

        # 轉錄
        print(f"  轉錄中（faster-whisper medium）...")
        try:
            segments, info = model.transcribe(
                str(wav_path),
                language="zh",
                beam_size=5,
                vad_filter=True,
                vad_parameters={"min_silence_duration_ms": 1000},
            )
            segments = list(segments)
            print(f"  語言：{info.language}，時長：{info.duration:.0f}s，{len(segments)} 段")
        except Exception as e:
            print(f"  轉錄失敗：{e}")
            continue

        # 格式化並儲存
        text = format_transcript(iv, segments)
        out_path.write_text(text, encoding="utf-8")
        print(f"  已儲存：{iv['out_file']} ({len(text)} chars)")

    print("\n全部完成！")
    print(f"輸出目錄：{OUT_DIR}")


if __name__ == "__main__":
    main()
