"""
抓取衛理公會城中牧區各年段播放清單中的證道影片，寫入城中教會講道_YYYY.txt
用法：
  python fetch_chengzhong_sermons.py --year=2014          # 從播放清單跑單一年份
  python fetch_chengzhong_sermons.py --all                # 從播放清單跑所有年份
  python fetch_chengzhong_sermons.py --from-channel       # 從頻道影片頁抓全部（最完整）
  python fetch_chengzhong_sermons.py                      # 預設跑 2013 播放清單
"""
import subprocess, json, re, sys, os, argparse, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

PLAYLISTS = {
    "2012": "PLWc5vK0Yoq0WrvGbAA7h9fqIzvTP3zHWR",
    "2013": "PLWc5vK0Yoq0Vb339YuPmXbDF40rL1Ivb2",
    "2014": "PLWc5vK0Yoq0Wo9XCe_sVhCjfB4SqrRU7n",
    "2015": "PLWc5vK0Yoq0XMsuHHLg-ou8tvbEDf1jwt",
    "2016": "PLWc5vK0Yoq0UM4IV0q-km9Bd8IQYIplOe",
    "2017": "PLWc5vK0Yoq0W8jycsD5-VdCIvKd2uyJ9t",
    "2018": "PLWc5vK0Yoq0UxluLk6xJEHiNhzzi5aWdT",
    "2019": "PLWc5vK0Yoq0XatQhK4nkDSiKzP_j4xYNt",
    "2020": "PLWc5vK0Yoq0WJIQ8LBjZ7lx1pxAY-i8Fm",
    "2021": "PLWc5vK0Yoq0UQueq-cA65ZZCjAxodL38m",
    "2022": "PLWc5vK0Yoq0W8JaTMZrj6IaOnVudgsXNU",
}

CHANNEL_URL = "https://www.youtube.com/@cmpctaipei/videos"
STREAMS_URL = "https://www.youtube.com/@cmpctaipei/streams"

STORES_DIR = os.path.join(os.path.dirname(__file__), "..", "stores", "城中教會講道清單")

SERMON_KEYWORDS = [
    "證道", "講道", "受難日", "主日崇拜", "受難日崇拜",
    "SundayService", "Sunday Service", "主日",
]
EXCLUDE_KEYWORDS = ["主日學", "詩歌", "詩班", "四重唱", "讀經", "禱告會", "獻詩"]

CHANNEL_PREFIXES = [
    "衛理公會 城中教會 ",
    "衛理公會城中教會 ",
    "城中教會 ",
]
SUFFIX_STRIP = re.compile(r'\s*[\(（][^)）]*[\)）]')


def is_sermon_title(title):
    if any(bad in title for bad in EXCLUDE_KEYWORDS):
        return False
    return any(kw in title for kw in SERMON_KEYWORDS)


def parse_title(title):
    """回傳 (date_str, clean_title) 或 None。支援日期在開頭或結尾的各種格式。"""
    # SundayServiceYYYYMMDD 開頭（特殊格式：20200614...）
    m = re.match(r'^SundayService(\d{4})(\d{2})(\d{2})[_ ]?(.*)', title)
    if m:
        date_str = f"{m.group(1)}-{m.group(2)}-{m.group(3)}"
        clean = m.group(4).strip()
        return date_str, clean

    # 日期在結尾：YYYY-MM-DD（可能後面有 HH:MM）
    m = re.search(r'(\d{4})-(\d{2})-(\d{2})(?:\s+\d{2}:\d{2})?\s*$', title)
    if m:
        date_str = f"{m.group(1)}-{m.group(2)}-{m.group(3)}"
        clean = title[:m.start()].strip()
        return date_str, clean

    # 日期在結尾：YYYYMM0DD（9位，直播頁的特殊格式，必須在 YYYYMMDD 前判斷）
    m = re.search(r'(\d{4})(\d{2})0(\d{2})(?:\s+\d{2}:\d{2})?\s*$', title)
    if m and 1 <= int(m.group(2)) <= 12 and 1 <= int(m.group(3)) <= 31:
        date_str = f"{m.group(1)}-{m.group(2)}-{m.group(3)}"
        clean = title[:m.start()].strip()
        return date_str, clean

    # 日期在結尾：YYYYMMDD（可能後面有 HH:MM）
    m = re.search(r'(\d{4})(\d{2})(\d{2})(?:\s+\d{2}:\d{2})?\s*$', title)
    if m:
        date_str = f"{m.group(1)}-{m.group(2)}-{m.group(3)}"
        clean = title[:m.start()].strip()
        return date_str, clean

    # 日期在開頭：YYYY-MM-DD
    m = re.match(r'^(\d{4})-(\d{2})-(\d{2})\s*(.*)', title)
    if m:
        date_str = f"{m.group(1)}-{m.group(2)}-{m.group(3)}"
        clean = m.group(4).strip()
        return date_str, clean

    # 日期在開頭：YYYYMMDD（含無分隔符版）
    m = re.match(r'^(\d{4})(\d{2})(\d{2})[_ ]?(.*)', title)
    if m:
        date_str = f"{m.group(1)}-{m.group(2)}-{m.group(3)}"
        clean = m.group(4).strip()
        return date_str, clean

    # 日期在開頭：YYMMDD
    m = re.match(r'^(\d{2})(\d{2})(\d{2})(.*)', title)
    if m:
        date_str = f"20{m.group(1)}-{m.group(2)}-{m.group(3)}"
        clean = m.group(4).strip()
        return date_str, clean

    # 兜底：在標題任意位置搜尋 YYYYMMDD（日期後面跟括號等修飾詞的情況）
    m = re.search(r'\b(\d{4})(\d{2})(\d{2})\b', title)
    if m and 1 <= int(m.group(2)) <= 12 and 1 <= int(m.group(3)) <= 31:
        date_str = f"{m.group(1)}-{m.group(2)}-{m.group(3)}"
        clean = title[:m.start()].strip() + " " + title[m.end():].strip()
        clean = clean.strip()
        return date_str, clean

    return None


def normalize_clean(clean):
    for prefix in CHANNEL_PREFIXES:
        if clean.startswith(prefix):
            clean = clean[len(prefix):]
    clean = re.sub(r"\.(flv|mp4|mov)$", "", clean, flags=re.IGNORECASE).strip()
    clean = clean.lstrip("_").strip()
    reduced = SUFFIX_STRIP.sub("", clean).strip()
    generic = {"", "證道", "講道", "主日崇拜", "SundayService", "Sunday Service"}
    if reduced in generic:
        return "主日證道"
    return reduced if reduced else clean


def yt_dump(url):
    result = subprocess.run(
        ["yt-dlp", "--flat-playlist", "--dump-json", url],
        capture_output=True, encoding="utf-8"
    )
    if result.returncode != 0:
        print(f"yt-dlp 錯誤：{result.stderr[:500]}")
        return []
    return result.stdout.strip().splitlines()


def process_entries(lines, playlist_id=None):
    """解析 yt-dlp JSON 輸出，回傳 (date_str, clean, url) 的 list。"""
    videos = []
    skipped = []
    for line in lines:
        if not line.strip():
            continue
        data = json.loads(line)
        title = data.get("title", "")
        if not title or title in ("[Private video]", "[Deleted video]"):
            continue

        if not is_sermon_title(title):
            skipped.append(title)
            continue

        parsed = parse_title(title)
        if not parsed:
            skipped.append(f"[無法解析日期] {title}")
            continue

        date_str, clean = parsed
        clean = normalize_clean(clean)
        video_id = data["id"]

        if playlist_id:
            index = data.get("playlist_index") or data.get("playlist_autonumber", "")
            url = f"https://www.youtube.com/watch?v={video_id}&list={playlist_id}&index={index}"
        else:
            url = f"https://www.youtube.com/watch?v={video_id}"

        videos.append((date_str, clean, url))

    return videos, skipped


def write_year_file(year, videos):
    output_file = os.path.join(STORES_DIR, f"城中教會講道_{year}.txt")
    videos.sort(key=lambda x: x[0])
    lines = []
    for i, (date, vtitle, url) in enumerate(videos):
        lines.append(f"{date} {vtitle}")
        lines.append(url)
        if i < len(videos) - 1:
            lines.append("")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    return output_file


def fetch_from_channel():
    """從頻道影片頁 + 直播頁抓全部影片，依年份寫入各檔。"""
    all_videos = {}  # video_id → (date_str, clean, url)，用 id 去重

    for label, url in [("影片頁", CHANNEL_URL), ("直播頁", STREAMS_URL)]:
        print(f"正在抓取{label}...")
        lines = yt_dump(url)
        videos, skipped = process_entries(lines, playlist_id=None)
        for date_str, clean, vid_url in videos:
            vid_id = vid_url.split("v=")[1]
            if vid_id not in all_videos:
                all_videos[vid_id] = (date_str, clean, vid_url)
        print(f"  → {len(videos)} 筆講道（略過 {len(skipped)} 筆非講道）")

    # 依年份分組
    by_year = {}
    for date_str, clean, url in all_videos.values():
        year = date_str[:4]
        by_year.setdefault(year, []).append((date_str, clean, url))

    total = 0
    for year in sorted(by_year.keys()):
        out = write_year_file(year, by_year[year])
        n = len(by_year[year])
        total += n
        print(f"[{year}] {n} 筆 → {out}")

    print(f"\n全部完成，總計 {total} 筆，共 {len(by_year)} 個年份")


def fetch_year(year, playlist_id):
    playlist_url = f"https://www.youtube.com/playlist?list={playlist_id}"
    print(f"\n[{year}] 正在抓取播放清單 {playlist_id}...")
    lines = yt_dump(playlist_url)
    videos, skipped = process_entries(lines, playlist_id=playlist_id)
    out = write_year_file(year, videos)
    print(f"[{year}] 完成，共 {len(videos)} 筆 → {out}")
    if skipped:
        print(f"[{year}] 略過 {len(skipped)} 筆（非證道或無法解析日期）")
    return len(videos)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--year", default="2013")
    parser.add_argument("--playlist", default=None)
    parser.add_argument("--all", action="store_true", help="從播放清單跑所有年份")
    parser.add_argument("--from-channel", action="store_true", help="從頻道影片頁抓全部（最完整）")
    args = parser.parse_args()

    os.makedirs(STORES_DIR, exist_ok=True)

    if args.from_channel:
        fetch_from_channel()
    elif args.all:
        total = 0
        for year in sorted(PLAYLISTS.keys()):
            total += fetch_year(year, PLAYLISTS[year])
        print(f"\n全部完成，總計 {total} 筆")
    else:
        playlist_id = args.playlist or PLAYLISTS.get(args.year)
        if not playlist_id:
            print(f"找不到 {args.year} 的 playlist ID，請用 --playlist 指定")
            sys.exit(1)
        fetch_year(args.year, playlist_id)


if __name__ == "__main__":
    main()
