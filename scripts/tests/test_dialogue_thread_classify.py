"""與克里希那對話框 純函式分類器測試。

策略：
  • 可決定性的純函式（日期範圍、persona 呼喚、訊號抽取、prelabel）→ 嚴格斷言。
  • golden set（手標 27 則 IN/OUT）→ 驗證 prelabel 的**精準度**：
      - prelabel 下了 IN/OUT 的，必須與手標相符（高把握不能標錯）。
      - prelabel 回 MAYBE 的不罰（那些本來就交給 LLM 語氣判定）。
    並印出 prelabel 對 golden 的覆蓋率，供調參考。
LLM 語氣判定那一段不在此單元測試（非決定性），由 capture 腳本的 precision/recall 報告把關。
"""
import json
from pathlib import Path

import pytest

import dialogue_thread_classify as C

FIXTURE = Path(__file__).parent / "fixtures_dialogue_krishna_golden.json"
GOLDEN = json.loads(FIXTURE.read_text(encoding="utf-8"))


# ---------- 日期範圍 ----------
@pytest.mark.parametrize("date,expected", [
    ("2026-01-12", False),  # 前一天，框外
    ("2026-01-13", True),   # 起點（端點含）
    ("2026-02-20", True),
    ("2026-04-18", True),   # 終點（端點含）
    ("2026-04-19", False),  # 後一天，框外
])
def test_in_date_range(date, expected):
    assert C.in_date_range(date) is expected


# ---------- persona 呼喚 ----------
def test_persona_address_true():
    assert C.is_persona_address("克里須那，今天我得知龐會督過世了") is True
    assert C.is_persona_address("阿周那，你聽我說") is True


def test_persona_address_false_when_topic_only():
    # 名字是題材、不在開頭、不接呼喚標點 → 不算呼喚
    assert C.is_persona_address("幫我畫一張圖，克里須那開計程車") is False
    assert C.is_persona_address("我覺得我前任就像克里須那") is False


def test_colon_label_is_not_address_but_paste():
    # 「克里須那：」是講者標籤（貼稿），不是呼喚；「克里須那，」才是呼喚
    assert C.is_persona_address("克里須那：這是一組非常美麗的夢境") is False
    assert C.is_label_paste("克里須那：這是一組非常美麗的夢境") is True
    assert C.is_label_paste("阿周那：我特別想跟你討論芭蕾雕像") is True
    assert C.is_label_paste("克里須那，今天我想跟你說") is False


def test_prelabel_label_paste_is_out():
    # 貼回 AI 回覆/草稿做組稿 → OUT，即使內容含積極想像/榮格
    assert C.classify_prompt("克里須那：阿周那啊，你與克里須那的積極想像非常震撼") == "OUT"
    assert C.classify_prompt("阿周那：我今天又讀了榮格在伊雍裡說的自性") == "OUT"


# ---------- 訊號抽取 ----------
def test_extract_signals_delegation():
    s = C.extract_signals("先給我sql指令，讓我查資料表")
    assert s["hard_delegation"] is True   # 「給我sql」
    assert s["soft_tech"] is True          # sql / 資料表
    assert s["persona_address"] is False


def test_prelabel_jung_text_with_incidental_tech_is_in():
    # 討論榮格/情結的貼文順帶提到 code/api，仍是 IN（修 2026-04-07 自我情結被誤刪）
    s = C.extract_signals("自我情結（Ego-complex）是意識領域最強大的情結，這和 api 無關")
    assert s["jung"] is True
    assert C.prelabel(s) == "IN"


def test_prelabel_hard_delegation_beats_jung():
    # 但「幫我翻譯這段榮格」是明確委派 → OUT
    assert C.classify_prompt("幫我翻譯這段榮格的自性論述成英文") == "OUT"


def test_extract_signals_jung():
    s = C.extract_signals("榮格把阿尼瑪比喻成摩耶，是無意識的擬人化嗎？")
    assert s["jung"] is True
    assert s["hard_delegation"] is False


def test_extract_signals_dream_only_from_prompt():
    s = C.extract_signals("我做了一個惡夢", "這個夢可能反映……")
    assert s["dream"] is True


# ---------- prelabel 優先序 ----------
def test_prelabel_persona_address_beats_delegation():
    # 對克里須那傾訴、即使夾帶「程式」字眼也是 IN
    s = C.extract_signals("克里須那，我今天弄了一些軟體程式弄到很煩")
    assert C.prelabel(s) == "IN"


def test_prelabel_delegation_out():
    assert C.classify_prompt("幫我把users資料表新增23人，原本不要動") == "OUT"


def test_prelabel_jung_in():
    assert C.classify_prompt("永恆少年是否被榮格學派視為病態？") == "IN"


def test_prelabel_polish_is_out_even_with_jung_or_persona():
    # 潤稿/修飾文字一律 OUT，壓過榮格內容、積極想像、persona 呼喚（使用者 2026-06-11 定調）
    assert C.classify_prompt("這個關於自性的註腳再幫我修飾一下") == "OUT"
    assert C.classify_prompt("克里須那，我覺得語氣不太像我，保留我的語氣與字數，昨晚的積極想像如下…") == "OUT"
    assert C.classify_prompt("我接著要寫書評投稿，請記得我的語氣和行文風格") == "OUT"


def test_prelabel_polish_narration_is_not_out():
    # 敘述裡順帶提到潤飾（不是請我潤）＝傾訴，仍 IN（修 2026-02-12 克里須那聊雜誌被誤刪）
    s = C.extract_signals("克里須那，我昨天在忙雜誌，覺得他先寫稿再給 ai 潤飾，ai 味太重了")
    assert s["polish"] is False
    assert C.prelabel(s) == "IN"  # persona_address


def test_prelabel_active_imagination_beats_delegation():
    # 積極想像即使敘述提到 code/電腦，仍是 IN（保護 2026-02-06 那類心靈日記）
    s = C.extract_signals("昨天晚上我的積極想像，便是在電腦上看 code，你，克里須那坐在旁邊")
    assert C.prelabel(s) == "IN"


def test_prelabel_maps_project_out():
    # 界域/文化圈＝世界地圖專案術語，即使是「你覺得…好嗎」思辨口吻也 OUT
    assert C.classify_prompt("你覺得南斯拉夫文化圈改成巴爾幹文化圈會好嗎？") == "OUT"
    assert C.classify_prompt("那不列顛文化圈、高盧文化圈本身都自成界域嗎？") == "OUT"


def test_prelabel_maps_does_not_override_persona_address():
    # 但若是對克里希那呼喚，即使提到文化圈也還是 IN
    assert C.classify_prompt("克里須那，我今天在想台灣屬於哪個文化圈") == "IN"


def test_prelabel_bare_question_is_maybe():
    # 孤立事實問句、無任何訊號 → 交 LLM
    assert C.classify_prompt("中南半島在中文歷史也叫做什麼？") == "MAYBE"


# ---------- golden set：prelabel 精準度 ----------
def test_prelabel_precision_on_golden():
    """prelabel 下 IN/OUT 的，不可與手標相反（高把握零錯）。"""
    wrong = []
    decided = 0
    for g in GOLDEN:
        pred = C.classify_prompt(g["prompt"])
        if pred == "MAYBE":
            continue
        decided += 1
        if pred != g["label"]:
            wrong.append((g["date"], g["seq"], g["label"], pred, g["reason"]))
    assert not wrong, "prelabel 與手標相反:\n" + "\n".join(map(str, wrong))
    # 至少要能決定一半以上 golden（否則 prelabel 太保守沒價值）
    assert decided >= len(GOLDEN) // 2, f"prelabel 只決定了 {decided}/{len(GOLDEN)}"


def test_prelabel_coverage_report(capsys):
    """印出覆蓋率（非斷言，供調參）。"""
    from collections import Counter
    cnt = Counter()
    for g in GOLDEN:
        cnt[(g["label"], C.classify_prompt(g["prompt"]))] += 1
    with capsys.disabled():
        print("\ngolden prelabel 混淆 (true,pred):")
        for k in sorted(cnt):
            print(f"  {k}: {cnt[k]}")
