---
name: reels-piigpig
description: 「豬豬相遇」風格搞笑短影片製作 — 拿一段手機生活影片（多半是娃娃/豬豬情境），配上中英雙語字幕、喜劇高潮打煙火＋彩色 emoji 轟炸、片尾懷舊泛黃定格＋催淚歌詞字幕，用 ffmpeg 全程本機合成。使用者會 po 上 IG @thomas.piigpig。Use when 使用者丟一支影片要「做成搞笑影片／配字幕／加煙火／配歌／出第 N 版／調音量」，或要新開一支日期專案、整理影片資料夾、寫 IG 文案。成品按日期歸檔在 `影片/YYYY-MM-DD_主題/`（文案 + 各版 mp4 + 製作素材）。
---

# reels-piigpig — 豬豬相遇風格搞笑短影片

使用者的個人 IG 短影片系列（@thomas.piigpig / https://www.instagram.com/thomas.piigpig/）。
第一支案例＝[2026-07-18 豬豬相遇](../../影片/2026-07-18_豬豬相遇/文案.md)（石垣島大豬 × 新加坡機場失散兄弟）。

## 風格特色（DNA，每支都要有）

1. **中英雙語字幕**：中文（Microsoft JhengHei 粗體白字黑邊）在上、English（淡黃斜體小字）在下，貼底置中。逐句對準旁白語音時間軸。
2. **喜劇高潮 = 煙火 + emoji 轟炸**：影片最好笑/最浮誇那一刻（豬豬案例是「豬叫」），疊真實煙火（黑底夜空，screen 疊加）＋ 6 顆彩色 emoji（🐷🐵🎆🎇💥❓）淡入抖動亂噴。
3. **片尾懷舊定格**：影片播完後 tpad clone 定格最後一幀約 8–14 秒，套泛黃暖色＋暈影（沙龍老照片感），催淚歌詞字幕逐句浮現。
4. **配樂雙段技法**：前段放歡樂/梗曲，定格才切進感人副歌當「情緒 payoff」，中間 crossfade。副歌落點對齊定格開始。**唱歌那段右上角標歌曲出處**（`♪ 歌手〈曲名〉`）。
5. **音量**：旁白對話永遠第一優先、要聽得清楚；配樂一律壓很小當鋪底（豬豬案例最終 前段 0.12 / 副歌 0.25）。使用者對音量很講究，會逐版微調——照數字改就好。
6. **每一版都保留**：使用者要看製作歷程，不要覆蓋。舊版留著、新版遞增版號（v1, v2a, v2b, v3…）。

## 產出流程（ffmpeg 全本機）

工具都在本機，**不同 python 各司其職**：
- `ffmpeg` / `ffprobe`：`C:/Users/user/AppData/Local/Microsoft/WinGet/Links/`
- **faster-whisper（字幕時間軸）＋ Pillow（emoji 貼圖）**：`C:/Users/user/Desktop/know-graph-lab/_whisper_venv/Scripts/python.exe`
- **yt-dlp（下歌／煙火）**：`C:/Users/user/AppData/Local/Python/pythoncore-3.14-64/python.exe -m yt_dlp`（第一次要 `pip install -U yt-dlp`，舊版會 403）
- 字型：中文 `C:\Windows\Fonts\msjhbd.ttc`(JhengHei Bold)；彩色 emoji `C:\Windows\Fonts\seguiemj.ttf`

步驟：
1. **探勘**：`ffprobe` 看長度/尺寸/fps；抽 4×4 frame montage 看內容、定位高潮鏡頭。
2. **字幕時間軸**：抽 16k 單聲道 wav → faster-whisper（model `small`, `language="zh"`, `word_timestamps=True`, `vad_filter=False`）。**whisper 只用它的時間戳**，字幕文字用使用者給的台詞（終端顯示中文亂碼沒關係，時間才是重點）。
3. **下歌**：`yt_dlp -x --audio-format mp3 --audio-quality 0 --no-update`。歌詞落點也用 whisper 轉錄那段確認秒數。
4. **emoji 貼圖**：Pillow + seguiemj.ttf，`ImageFont.truetype(...,220)` + `draw.text(...,embedded_color=True,anchor="mm")` 存透明 PNG（見 `製作素材/em_*.png`，可直接重用）。⚠️ print emoji 會 cp950 崩，用 `\U0001F437` 或別 print emoji 本身。
5. **煙火素材**：`yt_dlp ... "ytsearch3:fireworks overlay black background free"`（黑底夜空，見 `fw.mp4`，可重用）。
6. **ASS 字幕**：PlayResX 1280/720，樣式 CN/EN/SQ(豬叫)/END(定格中文)/ENDen/CREDIT(右上出處)。用 python 寫 `utf-8-sig`。範本＝ `製作素材/subs2b.ass`。
7. **ffmpeg 合成**（濾鏡圖存檔用 `-/filter_complex file.txt`）。範本＝ `製作素材/f_full4.txt`（雙歌）/`f_full6.txt`（最終音量）。骨架：
   - `[0:v]scale=1280:720,setsar=1,fps=30,tpad=stop_mode=clone:stop_duration=<定格秒>,format=gbrp` → 定格延長
   - 煙火：黑底片 `trim` + `tpad`（前後補黑填滿全長）→ `[base][fw]blend=all_mode=screen`
   - emoji：`-loop 1 -framerate 30 -t <全長> -i em_x.png` → `scale,format=rgba,fade in/out(alpha)` → `overlay` 帶 `enable='between(t,..)'` 與 `y='..+..*sin(..t..)'` 抖動
   - 定格上色：`eq=saturation=0.28:...,colorbalance=...,vignette` 全掛 `enable='gte(t,<定格起>)'`
   - `subtitles=xxx.ass,format=yuv420p`
   - 音訊：`[前段歌]atrim,volume=小` + `[副歌]atrim=副歌起:,volume=小,afade out` → `acrossfade=d=1.5` → 與旁白 `[0:a]apad,volume=1.25` `amix=normalize=0` → `alimiter`
   - 編碼 `libx264 -crf 20 -preset veryfast -pix_fmt yuv420p -c:a aac -b:a 192k -movflags +faststart`
8. **驗收**：抽關鍵幀（高潮/定格）貼進對話看；`volumedetect` 量前段 vs 定格段音量差。
9. **歸檔**：見下。

## 🚨 技術地雷（血淚）

- **screen 疊加煙火一定要在 RGB（gbrp）做，不能在 YUV**：YUV 的中性灰 chroma 128 被 screen 會位移、整片染色。轉 `format=gbrp` 再 blend，最後才 `format=yuv420p`。
- **emoji 用 `-loop 1` 圖片輸入，不要用 `movie=...:loop=0`**：無限 movie 迴圈會讓濾鏡圖卡死 <1fps（幾乎不出幀）。
- **libass 只渲染單色 emoji**（外框），彩色 emoji 一律走 PNG overlay。單色 emoji 拿來當「豬叫亂碼字幕」反而有喜感、可留。
- yt-dlp 太舊會 403，先 `-U`。多個 python 別搞錯：whisper venv 沒 yt_dlp、pythoncore 才有。
- 大檔案別進 git：`影片/**` 的 mp4/mov/mp3 已 gitignore，只追蹤 `文案.md` 與本 skill。

## 歸檔慣例

```
影片/
  YYYY-MM-DD_主題/
    文案.md            # 台詞逐句時間軸 + IG 貼文文案 + 配樂出處/URL + 版本紀錄
    主題_v0_原始素材.mp4
    主題_v1_….mp4 … vN   # 每版遞增、都保留
    製作素材/           # subs .ass、f_full*.txt 濾鏡圖、em_*.png、fw.mp4、歌 mp3（可重製）
```

`文案.md` 一定要有：**IG 貼文文案（可直接複製貼上，含 hashtag）** + **配樂出處與 YouTube URL** + **版本紀錄**。使用者發布平台固定 IG @thomas.piigpig。
