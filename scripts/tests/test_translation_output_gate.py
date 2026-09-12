# -*- coding: utf-8 -*-
"""譯文輸出閘：壞輸出一定要擋下，正常輸出一個都不能誤殺。

2026-09-11 補。此前譯文**從來沒有驗過「它到底是不是中文」**——唯一的守門員
`_looks_like_prompt_echo` 只認中文提示詞，所以推理模型外洩的英文思考過程
一路綠燈存進 checkpoint 並且上線。豪斯評傳 sec5[57] 存了 22,590 字的
「We need to translate the given English paragraph…」。

誤殺這一側同樣重要：穆勒與潘尼卡的書本來就滿是梵文轉寫（atman、Naighantuka），
拉丁字母比漢字多是**正常**的。分界靠英文虛詞密度，不是靠字母比例。
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from translate_ebook_to_zh import unusable_reason  # noqa: E402


# ── 要擋下的 ──────────────────────────────────────────────────────────────────
def test_truncated_reasoning_tag():
    """🚨 病灶本體：<think> 開了沒關，代表回應被截斷在推理中間。"""
    assert unusable_reason("<think>Okay, the user wants me to translate") == "truncated-reasoning"


def test_reasoning_leak_english():
    got = unusable_reason(
        "We need to translate the given English paragraph into Traditional Chinese, "
        "following all the rules. We must not add any preface, explanation, or notes.")
    assert got in ("reasoning-leak", "untranslated")


def test_reasoning_leak_even_when_mostly_chinese():
    """外洩的推理常常中英夾雜——比例判準看不出來，招牌句看得出來。"""
    t = ("We need to translate 「日本作為一個國家並未選擇回顧」。"
         "或「日本作為一個國家並未選擇回顧，而是一貫地向前看。」"
         "這樣讀起來比較自然，中文的引號要用「」。再看第二句怎麼處理比較好。")
    assert unusable_reason(t) == "reasoning-leak"


def test_untranslated_english_prose():
    assert unusable_reason(
        "The forms divi, dii, and dei do not enable us to establish an essential "
        "difference between the gods of Greece and those of Italy, and there is "
        "no reason to suppose that they were borrowed.") == "untranslated"


# ── 絕不可誤殺的 ──────────────────────────────────────────────────────────────
def test_plain_chinese_passes():
    assert unusable_reason("內村於1893年出版《基督信徒的慰藉》，時年三十二。") == ""


def test_sanskrit_transliteration_passes():
    """🚨 拉丁字母遠多於漢字，但那是術語轉寫不是沒譯——虛詞密度接近 0。"""
    t = ("《娑摩吠陀的尼達那經》（Nidana-sutra）與《波羅提娑佉》（Pratisakhya）、"
         "奈漢圖卡（Naighantuka）、奈伽瑪（Naigama）、Charana、Sruti、Smriti、"
         "Anupada-sutra、Asvalayana、Shadgurushishya、parsadam、atman、anila。")
    assert unusable_reason(t) == ""


def test_short_english_term_in_chinese_passes():
    assert unusable_reason("它們屬於語言科學（the science of language）發展的早期階段。") == ""


def test_english_sentence_buried_in_chinese_paragraph():
    """🚨 整段比例過得了關，中間卻夾著一整句沒譯的英文——比例判準看不到這種。"""
    t = ("在赫西俄德的敘述中，宙斯推翻克洛諾斯之後接掌了天界，並與兄弟均分世界："
         "海洋歸波塞冬，冥界歸哈得斯，而天空歸宙斯自己。這一段分配的敘事在後世"
         "神話學者之間引起長期爭論，穆勒本人也在此處留下了相當長的一段案語，"
         "以下是他徵引的原文段落。"
         "of Hesiod, we are told that Zeus, after having dethroned Kronos, took "
         "possession of the sky, and that he divided the world with his brothers, "
         "so that the sea fell to Poseidon and the nether world to Hades.")
    assert unusable_reason(t) == "partial-untranslated"


def test_short_english_quotation_passes():
    """引號裡的短句、書名、術語不該中——門檻是連續 120 個字母。"""
    assert unusable_reason(
        "穆勒稱之為「the science of language」，並在《比較神話學》中反覆申論此點。") == ""


def test_bilingual_verse_row_passes():
    """並列體例「原文　／　中譯」是刻意的，不是沒譯。"""
    assert unusable_reason("Trust in the Lord with all thine heart　／　你要專心仰賴耶和華") == ""


# ── 中文裡的自我商議與退化重複（2026-09-11 第二輪補）────────────────────────────
def test_self_talk_in_chinese_translation():
    """🚨 使用者在《基督信徒的慰藉》讀到的那一種：模型邊譯邊用中英夾雜自我商議。

    前面三條都擋不住——段落大半是漢字（比例過關），夾的英文碎片都很短
    （連續 120 字母那條不觸發），也沒有 <think> 和既有招牌句。
    """
    t = ("罪／罪愆; we used 罪過 which is okay? Might be considered a variant but still "
         "same meaning. Safer to use 罪. Let's change「罪過」to「罪」。"
         "So:「導致他死亡的罪，就在我身上」。Good. Check for「我其實是殺死了我所愛之人的兇手」。")
    assert unusable_reason(t) == "self-talk"


def test_self_talk_needs_two_markers():
    """門檻是 2。全庫 62,243 段中命中 1 個的只有 3 段，且都是正常的英文引文——
    取 1 會誤殺，取 2 命中的 4 段裡有 3 段是真外洩。"""
    assert unusable_reason("穆勒在此引用了一句諺語：「we must be patient」，並加以申論。") == ""


def test_degenerate_repetition_loop():
    """模型卡在迴圈抄同一句。用壓縮率量，不靠「找重複片段」——迴圈週期不固定，
    滑動視窗對不上就整段漏掉（第一版就是這樣漏掉 12,073 字那段的）。"""
    loop = "它是好的。現在檢查這個詞。這個詞或許可以這樣用。它沒有問題。" * 40
    assert unusable_reason(loop) == "degenerate-repetition"


def test_repetitive_scripture_is_not_degenerate():
    """🚨 原書就重複的東西不可誤殺：奧義書的問答、法句經的偈頌、目次的點漏。
    實測這類壓縮率 0.19–0.33，門檻 0.15 把它們留在界線外。"""
    t = ("『我的心靈不在，』他說，『我沒有覺知那個詞語。』"
         "沒有生命氣，鼻子不能認知任何氣味。"
         "『我的心靈不在，』他說，『我沒有覺知那個氣味。』"
         "沒有生命氣，眼睛不能認知任何形色。"
         "『我的心靈不在，』他說，『我沒有覺知那個形色。』"
         "沒有生命氣，耳朵不能認知任何聲音。"
         "『我的心靈不在，』他說，『我沒有覺知那個聲音。』")
    assert unusable_reason(t) == ""


def test_short_repetition_is_left_alone():
    """太短的東西壓縮率本來就不準（標頭、單行）——250 字以下不判。"""
    assert unusable_reason("聖哉、聖哉、聖哉，萬軍之耶和華。") == ""


# ── 整段日文沒譯（2026-09-11 第三輪補）──────────────────────────────────────────
def test_untranslated_japanese_paragraph():
    """🚨 前面四條都是拿拉丁字母在量，日文是漢字假名混寫，全部放行。
    《丹麥國的故事》《約伯記講演》有十幾段是這樣上線的。"""
    t = ("しかるに今を去る四十年前のデンマークはもっとも憐れなる國でありました。"
         "1864年にドイツ、オーストリアの二強國の圧迫するところとなり、"
         "その要求に応じて南部の二州を割譲するのやむなきに至りました。")
    assert unusable_reason(t) == "untranslated-japanese"


def test_japanese_article_title_inside_chinese_passes():
    """內文提到日文篇名是正常的——假名佔比低，不該中。"""
    t = ("內村隨後以兩篇文章跟進這則溫和的諷刺，討論國家偉大的必備條件："
         "〈何故に大文學は出ずるや？〉（「我們為何不能產生偉大文學？」）"
         "和〈如何にして大文學を援くや？〉（「我們如何才能扶助偉大文學？」）。")
    assert unusable_reason(t) == ""


def test_waka_with_translation_first_passes():
    """🚨 和歌並列體例的假名佔比（0.26）跟真傷（0.28+）幾乎貼在一起，
    光看比例分不開——分得開的是位置：並列一律**中譯在前**。"""
    t = "> 縱然異邦教法入侵，待其消融，終將蒙上日本的光澤。古國の如何なる教え入り來るも 溶かすは やがて御國振り。"
    assert unusable_reason(t) == ""


def test_empty_is_not_this_gates_problem():
    assert unusable_reason("") == ""
    assert unusable_reason(None) == ""
