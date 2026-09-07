# -*- coding: utf-8 -*-
"""OCR 重複幻覺偵測 —— 視覺 OCR 最陰險的一種「看起來像成功的失敗」。

模型讀不動某一頁時，不見得回空白，可能把上一頁再吐一次。管線這端毫無異狀：
頁數對、字數正常、chunk 寫好、`✓ Haiku 7 pages, 1K chars` 照印，parsed_at
也蓋上去了。書進了館藏，讀者拿到的是一本重複又摻雜訊的書。

fixture 取自 2026-09-06《梁發傳略》真實輸出：p4 開頭是一段雜訊，之後與 p3
逐字相同。注意重複在尾巴 —— DB 只存 100 字 preview，拿 preview 比對抓不到，
所以這道閘一定要在 OCR 當下、全文還在手上時關。
"""
import ocr_with_gemini as O

# 兩頁共同的尾段（真實資料）
_TAIL = (
    "運牧師手下洗淨在教會培養聖靈初欲英俠仰佛法競師馬會訪時當第二年四月初八日遇見牧師之後"
    "因而信主受洗入教會活躍在教會服侍主迨後感覺主之大愛願盡己力傳揚基督之救恩於同胞如同牧"
    "師之志以為奉獻終身於傳教工作其時中國未有本國教牧人員故往往差遣外國傳教師赴華佈道梁先"
    "生乃毛遂自薦願往南洋傳教而經會中同意旋即派往馬來亞及新加坡等地傳教每有所往輙能感化多"
    "數回悔向善皈依基督者由於成績卓著故被派回國傳教經過廣東江西浙江等省佈道轉化數千人靡不"
    "感格其中尤多文人學者當時聞名於朝野非但教會人士推崇即政府當權者亦鹹推重其人品學識與傳"
)
P3 = "中國基督教會第一宣教師梁發先生傳略\n\n兩戰一月告日百里" + _TAIL
P4 = "他突地誌要略解凡三十七年有一始方妙情其無六年在有九年" + _TAIL


def _page(n, text):
    return {"page": n, "text": text}


class TestDetectRepeatedPages:
    def test_the_liangfa_case(self):
        dups = O.detect_repeated_pages([_page(3, P3), _page(4, P4)])
        assert len(dups) == 1
        assert dups[0][0] == 3 and dups[0][1] == 4
        assert dups[0][2] >= 0.90

    def test_distinct_pages_are_clean(self):
        a = "第一章 論信心的根據。" + "甲" * 300
        b = "第二章 論盼望的次序。" + "乙" * 300
        assert O.detect_repeated_pages([_page(1, a), _page(2, b)]) == []

    def test_short_repeats_are_ignored(self):
        # 書眉／頁碼／分隔頁本來就會重複，不能拿來當證據。
        hdr = "神學輯要選材"
        assert O.detect_repeated_pages([_page(i, hdr) for i in range(1, 8)]) == []

    def test_blank_pages_do_not_link_across(self):
        body = "丙" * 400
        out = O.detect_repeated_pages([_page(1, body), _page(2, ""), _page(3, body)])
        # 中間夾空白頁，1 與 3 仍屬相鄰的有字頁 → 該抓到
        assert len(out) == 1 and out[0][:2] == (1, 3)


class TestRepetitionVerdict:
    def test_rejects_a_book_that_is_mostly_repeats(self):
        chunks = [_page(1, P3), _page(2, P4), _page(3, P3), _page(4, P4)]
        ok, why = O.repetition_verdict(chunks)
        assert ok is False
        assert "重複" in why and "p" in why

    def test_one_repeat_in_a_long_book_still_passes(self):
        # 偶發一頁不該讓整本重跑；門檻是佔比不是有無。
        # 🚨 每頁內容必須真的不同：早先這裡用「第N節＋400 個同字」，各頁只差一個
        #    編號，字元層相似度 0.99 —— 整本互相判為重複，測出來的是 fixture 的
        #    毛病不是程式的。
        import random
        rnd = random.Random(20260907)
        pool = "信望愛義理恩典聖潔公義憐憫救贖悔改重生成聖稱義揀選預定護理啟示"
        chunks = [_page(i, "".join(rnd.choice(pool) for _ in range(400)))
                  for i in range(1, 30)]
        chunks.append(_page(30, chunks[-1]["text"]))
        ok, _ = O.repetition_verdict(chunks)
        assert ok is True

    def test_empty_input_passes(self):
        assert O.repetition_verdict([])[0] is True

    def test_verdict_message_names_the_pages(self):
        ok, why = O.repetition_verdict([_page(3, P3), _page(4, P4)])
        assert ok is False
        assert "p3" in why and "p4" in why
