# -*- coding: utf-8 -*-
"""自己合成一組解說片音效（原創、零授權風險）。

Openverse 匿名額度太低、Freesound／Pixabay 要金鑰、BBC 音效庫禁商業用，
所以這一組乾脆自己算出來：黑板片需要的其實就是 whoosh、叮、重擊、粉筆、擦板那幾種，
都能用雜訊與正弦波合成。純 stdlib（wave + math + random），不吃額外套件。

輸出 48kHz 單聲道 16-bit WAV 到 素材/音效/合成/。
"""
import math
import random
import struct
import wave
from pathlib import Path

OUT = Path(r"G:\我的雲端硬碟\創作\影片創作\人魚島解說\素材\音效\合成")
SR = 48000


def write_wav(name: str, samples: list[float]):
    OUT.mkdir(parents=True, exist_ok=True)
    peak = max(1e-9, max(abs(s) for s in samples))
    data = b"".join(struct.pack("<h", int(max(-1, min(1, s / peak * 0.89)) * 32767)) for s in samples)
    with wave.open(str(OUT / name), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(data)
    print(f"  {name}  {len(samples) / SR:.2f}s")


def env(i, n, attack=0.01, release=0.5):
    """簡單的起音／衰減包絡（比例制）。"""
    a, r = int(n * attack), int(n * release)
    if i < a:
        return i / max(a, 1)
    if i > n - r:
        return max(0.0, (n - i) / max(r, 1))
    return 1.0


def lowpass(sig, cutoff):
    """一階 RC 低通，用來把白雜訊修成「有材質」的聲音。"""
    alpha = 1 / (1 + SR / (2 * math.pi * cutoff))
    out, prev = [], 0.0
    for s in sig:
        prev += alpha * (s - prev)
        out.append(prev)
    return out


def whoosh(dur=0.55, sweep=(500, 4200)):
    n = int(SR * dur)
    noise = [random.uniform(-1, 1) for _ in range(n)]
    out, prev = [], 0.0
    for i, s in enumerate(noise):
        u = i / n
        cut = sweep[0] + (sweep[1] - sweep[0]) * math.sin(math.pi * u)  # 中段最亮
        alpha = 1 / (1 + SR / (2 * math.pi * cut))
        prev += alpha * (s - prev)
        out.append(prev * env(i, n, 0.18, 0.55) * (0.55 + 0.45 * math.sin(math.pi * u)))
    return out


def ding(freq=1760.0, dur=1.1):
    n = int(SR * dur)
    return [(math.sin(2 * math.pi * freq * i / SR) * 0.7
             + math.sin(2 * math.pi * freq * 2.01 * i / SR) * 0.22
             + math.sin(2 * math.pi * freq * 2.98 * i / SR) * 0.1)
            * math.exp(-4.2 * i / n) for i in range(n)]


def impact(dur=1.4):
    n = int(SR * dur)
    out = []
    for i in range(n):
        u = i / n
        f = 120 * math.exp(-3.5 * u) + 38          # 下墜的低頻
        body = math.sin(2 * math.pi * f * i / SR) * math.exp(-3.0 * u)
        crack = random.uniform(-1, 1) * math.exp(-38 * u) * 0.5
        out.append(body + crack)
    return lowpass(out, 2600)


def chalk_write(dur=1.0, strokes=7):
    """粉筆寫字：一連串短促的高頻摩擦。"""
    n = int(SR * dur)
    out = [0.0] * n
    for k in range(strokes):
        start = int(n * (k / strokes) + random.uniform(0, n * 0.03))
        ln = int(SR * random.uniform(0.05, 0.11))
        burst = lowpass([random.uniform(-1, 1) for _ in range(ln)], random.uniform(3200, 6000))
        for i, s in enumerate(burst):
            if start + i < n:
                out[start + i] += s * env(i, ln, 0.12, 0.5) * random.uniform(0.5, 1.0)
    return [s * 0.8 for s in out]


def chalk_erase(dur=0.9):
    n = int(SR * dur)
    noise = [random.uniform(-1, 1) for _ in range(n)]
    band = lowpass(noise, 1800)
    return [s * env(i, n, 0.15, 0.5) * (0.6 + 0.4 * math.sin(2 * math.pi * 3.5 * i / SR))
            for i, s in enumerate(band)]


def page_turn(dur=0.6):
    n = int(SR * dur)
    noise = [random.uniform(-1, 1) for _ in range(n)]
    hp = [noise[i] - noise[i - 1] if i else 0 for i in range(n)]   # 一階高通＝紙的脆度
    return [s * math.exp(-6.5 * (i / n)) * (0.4 + 0.6 * (i / n) ** 0.4) for i, s in enumerate(hp)]


def heartbeat(dur=2.0, bpm=64):
    n = int(SR * dur)
    out = [0.0] * n
    beat = int(SR * 60 / bpm)
    for b in range(0, n, beat):
        for off, amp in ((0, 1.0), (int(SR * 0.16), 0.62)):
            ln = int(SR * 0.22)
            for i in range(ln):
                p = b + off + i
                if p >= n:
                    break
                out[p] += math.sin(2 * math.pi * 52 * i / SR) * math.exp(-16 * i / ln) * amp
    return out


def riser(dur=2.2):
    """揭露真相前的爬升。"""
    n = int(SR * dur)
    out = []
    for i in range(n):
        u = i / n
        f = 180 * (1 + 6 * u ** 2)
        out.append((math.sin(2 * math.pi * f * i / SR) * 0.5
                    + random.uniform(-1, 1) * 0.35 * u) * (u ** 1.4))
    return out


def pop(dur=0.22, freq=660):
    n = int(SR * dur)
    return [math.sin(2 * math.pi * freq * (1 + 0.6 * (1 - i / n)) * i / SR)
            * math.exp(-14 * i / n) for i in range(n)]


def main():
    random.seed(20260906)
    write_wav("whoosh_短.wav", whoosh(0.45))
    write_wav("whoosh_長.wav", whoosh(0.85, (300, 3000)))
    write_wav("叮_提示.wav", ding())
    write_wav("叮_低.wav", ding(1174.7, 1.3))
    write_wav("重擊.wav", impact())
    write_wav("粉筆_寫字.wav", chalk_write())
    write_wav("粉筆_寫字短.wav", chalk_write(0.55, 4))
    write_wav("擦黑板.wav", chalk_erase())
    write_wav("翻頁.wav", page_turn())
    write_wav("心跳.wav", heartbeat())
    write_wav("爬升_揭露前.wav", riser())
    write_wav("彈出.wav", pop())
    (OUT / "說明.txt").write_text(
        "這批音效是用 scripts/board_video/make_sfx.py 合成出來的，原創、無授權問題，\n"
        "說明欄不必標示。要調長度或音色改那支腳本的參數即可。\n\n"
        "用途對照：\n"
        "  whoosh_短／長    鏡頭在黑板上移動（跨區塊用長的）\n"
        "  叮_提示／低      關鍵詞浮現、標重點\n"
        "  重擊             揭露真相、轉折（第五幕黑暗反轉、第九幕）\n"
        "  粉筆_寫字／短    節點與條目寫上黑板\n"
        "  擦黑板           換幕\n"
        "  翻頁             切換神話案例\n"
        "  心跳             懸疑鋪陳\n"
        "  爬升_揭露前      真相揭曉前 2 秒\n"
        "  彈出             小提示、吐槽\n", encoding="utf-8")
    print(f"\n合成完成，輸出在 {OUT}")


if __name__ == "__main__":
    main()
