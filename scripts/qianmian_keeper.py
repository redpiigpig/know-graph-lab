# -*- coding: utf-8 -*-
"""千面上帝寫作艦隊的看門人：斷了就接回去，寫完就收尾並關掉自己。

排程每 30 分鐘叫一次，做三件事之一：

  1. 還有線在跑            → 什麼都不做
  2. 沒線在跑但章沒寫齊    → 重新拉起四條線（章寫完會留檔，重跑一律跳過）
  3. 28 章全齊            → 跑收尾（補殘留註記號、統一譯名、上架、出 Word），
                            然後 Disable 自己

第 3 步的自我停用很重要：任務結束的排程會無限空轉，而且判準要看**產出**
（chapters/ 有沒有 28 個檔），不是看排程狀態（見 [[feedback_disable_finished_schedules]]）。

寫作模型每天有額度上限（每型號 20 次/key），撞牆之後只能等隔天；這支就是
用來讓「等隔天」這件事不需要人在旁邊盯。
"""
import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parent.parent
CH = ROOT / "output" / "qianmian" / "chapters"
SCRIPTS = ROOT / "scripts"
LANES = ["1-7", "8-14", "15-21", "22-28"]
TASK = "KGL_Qianmian_Keeper"

# 只套用「同一個對象、拼法不同」的定名。指涉不同的（拜占庭／君士坦丁堡、
# 征服者／穆罕默德二世）絕不能自動換，那會毀掉正文。
NAME_FIXES = ["蘇美", "歐西里斯", "克里希那", "馬利亞", "撒馬利亞",
              "歐麥爾", "查拉圖斯特拉", "馬克思"]


def run(*args):
    print("  $", " ".join(str(a) for a in args), flush=True)
    subprocess.run([sys.executable, "-u", *[str(a) for a in args]],
                   cwd=str(ROOT), check=False)


def running():
    out = subprocess.run(
        ["wmic", "process", "where", "name='python.exe'", "get", "commandline"],
        capture_output=True, text=True, errors="ignore").stdout
    return "qianmian_write" in out


def finish():
    """全書寫完之後的收尾，每一步都可以重跑。"""
    run(SCRIPTS / "qianmian_repair.py")
    for name in NAME_FIXES:
        run(SCRIPTS / "qianmian_names.py", "--fix", name)
    run(SCRIPTS / "qianmian_check.py")
    run(SCRIPTS / "qianmian_publish.py")
    run(SCRIPTS / "qianmian_docx.py")
    subprocess.run(["powershell", "-NoProfile", "-Command",
                    f"Disable-ScheduledTask -TaskName {TASK}"], check=False)
    print(f"收尾完成，排程 {TASK} 已停用。")


def main():
    done = sorted(int(p.stem[2:]) for p in CH.glob("ch*.md"))
    print(f"已完成 {len(done)}/28 章")
    if len(done) >= 28:
        finish()
        return
    if running():
        print("還有線在跑，這輪不動。")
        return
    missing = [n for n in range(1, 29) if n not in done]
    print(f"缺：{missing}，重新拉起四條線")
    for lane in LANES:
        subprocess.Popen(
            [sys.executable, "-u", str(SCRIPTS / "qianmian_write.py"), "--chapters", lane],
            stdout=open(f"c:/tmp/qm_keeper_{lane}.log", "a", encoding="utf-8"),
            stderr=subprocess.STDOUT, cwd=str(ROOT),
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))


if __name__ == "__main__":
    main()
