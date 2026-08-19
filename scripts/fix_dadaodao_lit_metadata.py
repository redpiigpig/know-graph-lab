"""Repair literature metadata/statuses and add core open-access sources.

This script is intentionally narrow: it only touches the
``mahaprajapati-revolution`` bibliography and preserves existing section rows by
patching entries in place whenever possible.
"""
from __future__ import annotations

from urllib.parse import quote

from ingest_lit_review import rest_get, rest_patch, rest_upsert


PROJECT = "mahaprajapati-revolution"


def patch_by_key(ref_key: str, body: dict) -> None:
    rows = rest_get(
        "lit_review_entries",
        f"project_slug=eq.{PROJECT}&book_id=eq.&ref_key=eq.{quote(ref_key, safe='')}&select=id,ref_key",
    )
    if len(rows) != 1:
        raise RuntimeError(f"expected one row for {ref_key!r}, got {len(rows)}")
    rest_patch("lit_review_entries", f"id=eq.{rows[0]['id']}", body)
    print(f"patched {ref_key}")


def main() -> None:
    # Entries whose status or attribution was misleading in the first ingest.
    patch_by_key(
        "marcus-bingenheimer-2009-writing-the-history-of-buddhist-thought-in-the-twentieth-century-yinshun",
        {
            "title": "Writing History of Buddhist Thought in the Twentieth Century: Yinshun (1906–2005) in the Context of Chinese Buddhist Historiography",
            "venue": "Journal of Global Buddhism 10 (2009): 255–290",
            "fulltext_url": "https://www.globalbuddhism.org/article/download/1152/987/2199",
            "fulltext_status": "pending",
        },
    )
    patch_by_key(
        "zh752c0205-2020",
        {"fulltext_status": "pending"},
    )
    patch_by_key(
        "anonymous-ntu-the-gurudharmas-in-taiwanese-buddhist-nunneries",
        {
            "ref_key": "ann-heirman-tzu-lung-chiu-2012-the-gurudharmas-in-taiwanese-buddhist-nunneries",
            "authors": "Ann Heirman; Tzu-Lung Chiu",
            "year": 2012,
            "title": "The Gurudharmas in Taiwanese Buddhist Nunneries",
            "venue": "Buddhist Studies Review 29(2): 273–300",
            "fulltext_url": "https://buddhism.lib.ntu.edu.tw/FULLTEXT/JR-MAG/mag390773.pdf",
            "fulltext_status": "pending",
        },
    )
    patch_by_key(
        "hsiao-lan-hu-chen-2011-buddhist-nuns-and-the-eight-heavy-rules-in-taiwan",
        {
            "ref_key": "chiung-hwang-chen-2011-feminist-debate-in-taiwans-buddhism-eight-garudhammas",
            "authors": "Chiung Hwang Chen",
            "year": 2011,
            "title": "Feminist Debate in Taiwan’s Buddhism: The Issue of the Eight Garudhammas",
            "venue": "Journal of Feminist Scholarship 1: 16–32",
        },
    )
    patch_by_key(
        "tzu-lung-chiu-ann-heirman-buddhist-modernism-and-animal-welfare-in-taiwan",
        {
            "ref_key": "wei-yi-cheng-2013-buddhist-modernism-and-animal-welfare-in-taiwan",
            "authors": "Wei-Yi Cheng",
            "year": 2013,
            "title": "Buddhist Modernism and Animal Welfare in Taiwan",
            "venue": "Journal of Dharma Seals 3: 1–13",
        },
    )
    patch_by_key(
        "ucsd-humanistic-buddhism",
        {"fulltext_status": "fetched"},
    )
    for key in (
        "jimmy-yu-2010-a-tentative-exploration-into-the-development-of-master-sheng-yen-s-chan-teachings",
        "teresa-zimmerman-liu-2023-the-fourfold-environmental-protection-initiative-of-dharma-drum-mountain",
        "christian-wittern-2002-chinese-buddhist-texts-for-the-new-millennium-cbeta-and-its-digital-tripitaka",
    ):
        patch_by_key(key, {"fulltext_status": "pending"})
    patch_by_key(
        "rita-m-gross-1993-buddhism-after-patriarchy-a-feminist-history-analysis-and-reconstruction-of",
        {"fulltext_status": "unavailable"},
    )

    # Copyright books/chapters without an OA text stay citable at bibliography
    # level, but should not be presented as awaiting an automatic full-text job.
    copyright_only = (
        "stuart-chandler-2004-establishing-a-pure-land-on-earth-the-foguang-buddhist-perspective-on",
        "shih-chao-hweipeter-singer-2023-the-buddhist-and-the-ethicist-conversations-on-effective-altruism",
        "andre-laliberte-yu-shuang-yao-2018-the-roles-of-secular-states-in-the-development-of-contemporary",
        "scott-pacey-2005-a-buddhism-for-the-human-world-interpretations-of-renjian-fojiao-in-contemporary",
        "stefania-travagnin-2017-concepts-and-institutions-for-a-new-buddhist-education-reforming-the-samgha",
        "wei-yi-cheng-2007-buddhist-nuns-in-taiwan-and-sri-lanka-a-critique-of-the-feminist-perspective",
        "elise-anne-devido-2010-taiwan-s-buddhist-nuns",
        "christopher-s-queensallie-b-king-1996-engaged-buddhism-buddhist-liberation-movements-in-asia",
        "sallie-b-king-2005-being-benevolence-the-social-ethics-of-engaged-buddhism",
        "sallie-b-king-2009-socially-engaged-buddhism",
        "andre-laliberte-2004-the-politics-of-buddhist-organizations-in-taiwan-19892003-safeguard-the-faith",
        "richard-madsen-2007-democracy-s-dharma-religious-renaissance-and-political-development-in-taiwan",
        "sulak-sivaraksa-1992-seeds-of-peace-a-buddhist-vision-for-renewing-society",
        "david-l-mcmahan-2008-the-making-of-buddhist-modernism",
        "guo-gu-2021-silent-illumination-a-chan-buddhist-path-to-natural-awakening",
        "charles-b-jones-1999-buddhism-in-taiwan-religion-and-the-state-16601990",
        "c-julia-huang-2009-charisma-and-compassion-cheng-yen-and-the-buddhist-tzu-chi-movement",
        "andre-laliberte-2004-the-politics-of-buddhist-organizations-in-taiwan-19892003-safeguarding-the",
        "gregory-adam-scott-2020-building-the-buddhist-revival-reconstructing-monasteries-in-modern-china",
        "jiang-wulucille-chia-2016-spreading-buddha-s-word-in-east-asia-the-formation-and-transformation-of",
    )
    for key in copyright_only:
        patch_by_key(key, {"fulltext_status": "unavailable"})

    existing = rest_get(
        "lit_review_entries",
        f"project_slug=eq.{PROJECT}&select=display_order&order=display_order.desc&limit=1",
    )
    next_order = (existing[0]["display_order"] if existing else 0) + 1
    additions = [
        {
            "project_slug": PROJECT,
            "book_id": "",
            "ref_key": "elise-devido-2009-influence-of-chinese-master-taixu-on-buddhism-in-vietnam",
            "authors": "Elise Anne DeVido",
            "year": 2009,
            "title": "The Influence of Chinese Master Taixu on Buddhism in Vietnam",
            "venue": "Journal of Global Buddhism 10: 413–458",
            "language": "en",
            "theme": "人間佛教的跨國流動",
            "dimension": "思想傳播與在地轉化",
            "stance": "以越南案例檢驗改革佛教並非單一路徑的輸出",
            "abstract_zh": "追蹤太虛思想進入越南佛教的路徑，提供人間佛教跨國傳播與在地轉化的比較背景。",
            "fulltext_url": "https://www.globalbuddhism.org/article/download/1155/990/2202",
            "fulltext_status": "pending",
            "display_order": next_order,
        },
        {
            "project_slug": PROJECT,
            "book_id": "",
            "ref_key": "yu-chen-li-2022-taiwanese-nuns-and-education-issues-in-contemporary-taiwan",
            "authors": "Yu-Chen Li",
            "year": 2022,
            "title": "Taiwanese Nuns and Education Issues in Contemporary Taiwan",
            "venue": "Religions 13(9): 847",
            "language": "en",
            "theme": "臺灣比丘尼與教育",
            "dimension": "制度、性別與教育實踐",
            "stance": "把女性僧團的能動性放回教育制度與臺灣佛教史中考察",
            "abstract_zh": "討論當代臺灣比丘尼的教育處境及其制度背景，可補足本書對女性僧團、性別與組織能力的比較分析。",
            "fulltext_url": "https://mdpi-res.com/d_attachment/religions/religions-13-00847/article_deploy/religions-13-00847.pdf",
            "fulltext_status": "pending",
            "display_order": next_order + 1,
        },
        {
            "project_slug": PROJECT,
            "book_id": "",
            "ref_key": "chengpang-lee-ling-han-2016-mothers-and-moral-activists",
            "authors": "Chengpang Lee; Ling Han",
            "year": 2016,
            "title": "Mothers and Moral Activists: Two Models of Women’s Social Engagement in Contemporary Taiwanese Buddhism",
            "venue": "Nova Religio 19(3): 54–77",
            "language": "en",
            "theme": "女性佛教行動者",
            "dimension": "公共參與的角色模型",
            "stance": "比較慈母與道德行動者兩種女性公共參與模式",
            "abstract_zh": "以兩種女性社會參與模型比較當代臺灣佛教，適合用來檢驗本書人物敘事是否把差異壓成單一的進步故事。",
            "fulltext_url": "https://doi.org/10.1525/nr.2016.19.3.54",
            "fulltext_status": "unavailable",
            "display_order": next_order + 2,
        },
        {
            "project_slug": PROJECT,
            "book_id": "",
            "ref_key": "ling-han-chengpang-lee-2024-engaging-animals-in-taiwanese-buddhism",
            "authors": "Ling Han; Chengpang Lee",
            "year": 2024,
            "title": "Engaging Animals in Taiwanese Buddhism: Two Case Studies",
            "venue": "Review of Religion and Chinese Society 11(1): 31–57",
            "language": "en",
            "theme": "佛教與動物倫理",
            "dimension": "倡議框架與組織行動",
            "stance": "以兩個案例比較臺灣佛教如何把動物納入道德實踐",
            "abstract_zh": "提供近年的比較研究，協助本書把動物倫理放入臺灣佛教的組織與倡議脈絡，而非只做人物讚頌。",
            "fulltext_url": "https://doi.org/10.1163/22143955-12340025",
            "fulltext_status": "unavailable",
            "display_order": next_order + 3,
        },
    ]
    rest_upsert(
        "lit_review_entries",
        additions,
        on_conflict="project_slug,book_id,ref_key",
    )
    print(f"upserted {len(additions)} core comparison sources")


if __name__ == "__main__":
    main()
