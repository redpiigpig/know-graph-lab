# -*- coding: utf-8 -*-
"""千面上帝寫作艦隊的看門人：斷了就把它接回去。

排程每 30 分鐘叫一次。只有在「一條線都沒在跑」的時候才重新拉起四條線，
所以不會跟還活著的行程搶同一章（章寫完會留下 chNN.md，重跑一律跳過）。

🚨 28 章全部寫完之後要記得把排程停掉，不要讓它空轉：
       Disable-ScheduledTask -TaskName KGL_Qianmian_Keeper
   判準看 output/qianmian/chapters/ 有沒有 28 個檔，不是看排程狀態。
   （見 [[feedback_disable_finished_schedules]]）
"""
import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parent.parent
CH = ROOT / "output" / "qianmian" / "chapters"
LANES = ["1-7", "8-14", "15-21", "22-28"]


def running():
    """還有沒有 qianmian_write 在跑。"""
    out = subprocess.run(
        ["wmic", "process", "where", "name='python.exe'", "get", "commandline"],
        capture_output=True, text=True, errors="ignore").stdout
    return "qianmian_write" in out


def main():
    done = sorted(int(p.stem[2:]) for p in CH.glob("ch*.md"))
    print(f"已完成 {len(done)}/28 章：{done}")
    if len(done) >= 28:
        print("全書寫完了。請停掉排程：Disable-ScheduledTask -TaskName KGL_Qianmian_Keeper")
        return
    if running():
        print("還有線在跑，這輪不動。")
        return
    for lane in LANES:
        subprocess.Popen(
            [sys.executable, "-u", str(ROOT / "scripts" / "qianmian_write.py"), "--chapters", lane],
            stdout=open(f"c:/tmp/qm_keeper_{lane}.log", "a", encoding="utf-8"),
            stderr=subprocess.STDOUT, cwd=str(ROOT),
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        print(f"  重新拉起 {lane}")


if __name__ == "__main__":
    main()
