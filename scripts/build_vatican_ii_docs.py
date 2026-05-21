"""
Build 15 Vatican II document .ts files (everything except SC, which is already manual-built).

Source: vatican.va official HTML in Latin + English.
Chinese: PDF placeholder (vatican.va Chinese versions are PDF, need separate OCR pass).

For each doc:
  1. Fetch _lt.html + _en.html from vatican.va
  2. Strip nav/footer noise; extract main <p> text
  3. Write data/creeds/ecumenical-councils/vatican-ii/{code-lower}-latin.txt + -english.txt
  4. Generate data/creeds/ecumenical-councils/vatican-ii-{NN}-{code-lower}.ts

Run from project root:
  python scripts/build_vatican_ii_docs.py
"""
import os
import re
import sys
import time
import requests
from bs4 import BeautifulSoup

# (code, url_type, date, url_slug, nameZh, nameEn, doc_order, location, topic, summary_zh, notes_zh, accepted_by, related_codes)
DOCS = [
    (
        "IM", "decree", "19631204", "inter-mirifica",
        "大眾傳播工具法令", "Decree on the Media of Social Communications", 2,
        "羅馬‧聖伯多祿大殿（梵二第二會期）",
        "教會對廣播、電視、電影、報刊等大眾傳播工具的態度與牧民方針",
        "1963 年 12 月 4 日與《禮儀憲章》同日頒佈。梵二爭議較少、票數差距較大的文件之一（1960 反 vs 164 贊成 — 反對票相對偏高），批評者認為內容偏淺、未及神學深度。但首次以教會官方文件層級肯定大眾傳播工具的價值。",
        "後續 1971 牧靈訓令《Communio et Progressio》具體展開本文件原則；1992《Aetatis Novae》再更新。",
        ["catholic"],
        ["vatican-ii-sc-sacrosanctum-concilium"],
    ),
    (
        "LG", "const", "19641121", "lumen-gentium",
        "教會憲章", "Dogmatic Constitution on the Church", 3,
        "羅馬‧聖伯多祿大殿（梵二第三會期）",
        "教會本質、結構、職能 — 8 章涵蓋天主子民、主教團、平信徒、修會、教會的末世性、聖母瑪利亞",
        "1964 年 11 月 21 日頒佈，是梵二最具神學份量的文件，與《啟示憲章》《禮儀憲章》《牧靈憲章》並列四大憲章。最重要的突破：① 教會自我定義從「完美社會」轉向「天主子民」（Chapter 2）② 確立主教團與教宗共同治理教會的「合議性」（collegiality, Chapter 3, §22）③ 平信徒在教會內的「使徒性」地位（Chapter 4）④ 普世聖召（universal call to holiness, Chapter 5）⑤ 第八章專論聖母瑪利亞，不另立獨立文件。",
        "Nota explicativa praevia（前置說明）— 為平衡主教合議性與教宗首席地位，保祿六世下令加入此「前置註解」附於文件之後，是當時神學辯論的關鍵折衷產物。",
        ["catholic"],
        ["vatican-ii-sc-sacrosanctum-concilium", "vatican-ii-dv-dei-verbum", "vatican-ii-gs-gaudium-et-spes"],
    ),
    (
        "OE", "decree", "19641121", "orientalium-ecclesiarum",
        "東方公教會法令", "Decree on the Catholic Churches of the Eastern Rite", 4,
        "羅馬‧聖伯多祿大殿（梵二第三會期）",
        "與羅馬合一的東方禮天主教會（Eastern Catholic Churches）的地位、禮儀傳統保存、與東正教關係",
        "本文件明確肯定 23 個與羅馬合一的東方禮教會（馬龍尼、希臘公教、烏克蘭希臘公教、敘利亞公教、亞美尼亞公教、迦勒底、馬蘭卡、科普特公教、衣索匹亞公教等）的「同等尊嚴」地位，禁止強制其拉丁化，並期待其成為與東正教合一的橋樑。",
        "對應的 1990 年《東方教會法典》（CCEO）為其法律具體化。",
        ["catholic"],
        ["vatican-ii-ur-unitatis-redintegratio"],
    ),
    (
        "UR", "decree", "19641121", "unitatis-redintegratio",
        "大公主義法令", "Decree on Ecumenism", 5,
        "羅馬‧聖伯多祿大殿（梵二第三會期）",
        "天主教投入普世合一運動的原則與方向；對東正教、東方東正教、聖公宗、新教各宗派的承認與對話框架",
        "本文件徹底改變天主教對其他基督宗派的態度，從「分離弟兄」（fratres seiuncti）的牧靈用語、承認非天主教共同體在某種意義上的「教會性」、肯定共同祈禱與神學對話。是 1995 年若望保祿二世《Ut Unum Sint》通諭的根基。",
        "後續具體化：1965 年取消東西教會 1054 互革除（共同宣言）；1973 與科普特、1984 與敘利亞正教、1994 與亞述東方教會等系列共同基督論宣言；1999 與信義宗 JDDJ。",
        ["catholic"],
        ["vatican-ii-oe-orientalium-ecclesiarum", "vatican-ii-na-nostra-aetate", "vatican-ii-dh-dignitatis-humanae"],
    ),
    (
        "CD", "decree", "19651028", "christus-dominus",
        "主教在教會內牧靈職務法令", "Decree concerning the Pastoral Office of Bishops in the Church", 6,
        "羅馬‧聖伯多祿大殿（梵二第四會期）",
        "主教的牧靈職權、與教宗的關係、主教團合議性、教區結構、主教會議等具體建制",
        "本文件把《教會憲章》第三章的「主教合議性」原則落實為具體建制：教區界線重劃、主教退休年齡 75 歲、設立主教會議（Synod of Bishops, 1965 由保祿六世先期設立）作為與教宗共同治理的常設機制。",
        "首次明確肯定主教應與本國其他主教合作（主教團 Episcopal Conference）並建議定期區域會議。",
        ["catholic"],
        ["vatican-ii-lg-lumen-gentium"],
    ),
    (
        "PC", "decree", "19651028", "perfectae-caritatis",
        "修會生活革新法令", "Decree on the Adaptation and Renewal of Religious Life", 7,
        "羅馬‧聖伯多祿大殿（梵二第四會期）",
        "天主教修會（本篤、方濟、道明、耶穌會等）的會憲、靈修、生活方式革新原則",
        "本文件要求所有修會「回到創會神恩」（aggiornamento ad fontes）並對應現代世界更新會憲。直接後果是 1960s-70s 大批修會修訂會憲（如耶穌會 1974 GC32、本篤會 1967 修訂會規詮釋），改革派與保守派衝突激烈，許多修會聖召銳減。",
        "與《教會憲章》第六章修會章節互補。",
        ["catholic"],
        ["vatican-ii-lg-lumen-gentium"],
    ),
    (
        "OT", "decree", "19651028", "optatam-totius",
        "司鐸之培養法令", "Decree on the Training of Priests", 8,
        "羅馬‧聖伯多祿大殿（梵二第四會期）",
        "天主教神職培育（修院）的革新方向：靈修陶成、學識陶成、牧靈陶成、人格陶成四面向整合",
        "本文件要求神學教育以聖經為核心、深化教父研究、與時並進處理當代問題（哲學、人文社會科學的對話）。直接後果是各國神學院課綱大改、聖經學系大幅擴張。",
        "後續 1985《Ratio Fundamentalis Institutionis Sacerdotalis》與 1992 若望保祿二世《Pastores Dabo Vobis》具體化。",
        ["catholic"],
        ["vatican-ii-po-presbyterorum-ordinis"],
    ),
    (
        "GE", "decl", "19651028", "gravissimum-educationis",
        "天主教教育宣言", "Declaration on Christian Education", 9,
        "羅馬‧聖伯多祿大殿（梵二第四會期）",
        "天主教學校（小中大學）的教育理念、與公立教育的關係、信仰自由與宗教教育權",
        "本文件肯定天主教學校的權利與使命，並要求世俗政府保障父母選擇宗教教育的自由。對北美天主教學校系統、菲律賓、拉丁美洲等天主教教育網絡具直接政策意涵。",
        "宗座教育部 1977《教會學校》訓令 + 1988《天主教學校的宗教面向》具體化。",
        ["catholic"],
        ["vatican-ii-dh-dignitatis-humanae"],
    ),
    (
        "NA", "decl", "19651028", "nostra-aetate",
        "教會對非基督宗教態度宣言", "Declaration on the Relation of the Church to Non-Christian Religions", 10,
        "羅馬‧聖伯多祿大殿（梵二第四會期）",
        "天主教對印度教、佛教、伊斯蘭教、猶太教的態度 — 特別著名的是第 4 段否認集體性「猶太人殺基督」指控、譴責任何形式的反猶太主義",
        "本文件僅 5 段，是梵二最短文件之一，但歷史意義巨大：第 4 段徹底改變天主教與猶太教關係（後續對話常稱「梵二後猶太關係」分水嶺），第 3 段首次以官方文件層級正面承認伊斯蘭教與基督宗教共享亞伯拉罕信仰根源。亦肯定佛教、印度教的精神追求價值。",
        "1974 設立「與猶太教關係委員會」；1986 若望保祿二世訪問羅馬大會堂（首位現代教宗）；2000 千禧大赦時 mea culpa；後續宗教對話運動的根基。",
        ["catholic"],
        ["vatican-ii-ur-unitatis-redintegratio", "vatican-ii-dh-dignitatis-humanae"],
    ),
    (
        "DV", "const", "19651118", "dei-verbum",
        "啟示憲章", "Dogmatic Constitution on Divine Revelation", 11,
        "羅馬‧聖伯多祿大殿（梵二第四會期）",
        "啟示論：聖經與聖傳的關係、聖經默感與無謬性、聖經詮釋學原則、聖經在教會生活中的中心地位",
        "1965 年 11 月 18 日頒佈，是梵二四大憲章之一。最關鍵突破：① 拒絕「兩源論」（聖經與聖傳為兩個獨立啟示源）改採「同一啟示之兩種傳承方式」（§9）② 肯定歷史批判方法的合法性（§12）③ 強調聖經應成為神學的「靈魂」與教會生活中心 ④ 鼓勵信徒閱讀聖經，鼓勵公版聖經多語翻譯（§22-25）。",
        "與 Trent 第四會期（1546 De canonicis Scripturis）對話：保留 Trent 對 deuterocanonical canon 的肯定，但詮釋學方法上大幅開放。也與梵一《Dei Filius》（1870）對話：保留客觀啟示概念，但加上「歷史性」維度。",
        ["catholic"],
        ["vatican-ii-sc-sacrosanctum-concilium", "vatican-ii-lg-lumen-gentium"],
    ),
    (
        "AA", "decree", "19651118", "apostolicam-actuositatem",
        "教友傳教法令", "Decree on the Apostolate of the Laity", 12,
        "羅馬‧聖伯多祿大殿（梵二第四會期）",
        "平信徒在教會內外的使徒性使命：堂區、職場、家庭、社會行動、政治參與",
        "本文件徹底改變天主教對「平信徒」的角色定位 — 不再是「神職的協助者」，而是因聖洗本身就有的「使徒性聖召」（apostolate by virtue of baptism）。後續神學發展：1988 若望保祿二世《Christifideles Laici》宗座勸諭。",
        "後續具體建制：堂區牧靈委員會、教區牧靈委員會、各國平信徒大會、Catholic Action 等運動的合法化。",
        ["catholic"],
        ["vatican-ii-lg-lumen-gentium"],
    ),
    (
        "DH", "decl", "19651207", "dignitatis-humanae",
        "信仰自由宣言", "Declaration on Religious Freedom", 13,
        "羅馬‧聖伯多祿大殿（梵二第四會期）",
        "宗教自由是基於人性尊嚴的基本人權；國家不得強制或禁止任何宗教信仰；與十九世紀天主教反現代主義立場的歷史轉向",
        "本文件是梵二爭議最大的文件之一，反對派（Lefebvre 領頭）認為與 Pius IX 1864《Syllabus Errorum》 § 15-18 譴責「宗教自由」相矛盾。最終 2308 贊成 vs 70 反對通過，但成為 SSPX 後續分裂的關鍵理由。主筆者：John Courtney Murray（耶穌會美籍神學家）。",
        "與 Pius IX 19 世紀立場的「發展連續性 vs 斷裂」之爭，至今仍是天主教傳統派與主流派的議題。1986 若望保祿二世亞西西宗教聚會將本文件原則付諸實踐。",
        ["catholic"],
        ["vatican-ii-na-nostra-aetate", "vatican-ii-ge-gravissimum-educationis"],
    ),
    (
        "AG", "decree", "19651207", "ad-gentes",
        "教會傳教工作法令", "Decree on the Mission Activity of the Church", 14,
        "羅馬‧聖伯多祿大殿（梵二第四會期）",
        "教會的「傳教使命」（missio ad gentes）— 為什麼傳教、向誰傳教、如何傳教，特別是非基督文化地區的本土化與文化適應",
        "本文件確立「教會本性就是傳教」（Ecclesia per se missionaria, §2）的原則；強調傳教必須「本土化」（accommodatio / inculturation），尊重當地文化、語言、思想形式；不可簡單複製西方教會模式。亞洲、非洲傳教學的根基文件。",
        "1975 保祿六世《Evangelii Nuntiandi》宗座勸諭、1990 若望保祿二世《Redemptoris Missio》通諭、2013 方濟各《Evangelii Gaudium》使徒勸諭依序具體化本文件原則。",
        ["catholic"],
        ["vatican-ii-na-nostra-aetate", "vatican-ii-ur-unitatis-redintegratio"],
    ),
    (
        "PO", "decree", "19651207", "presbyterorum-ordinis",
        "司鐸職務與生活法令", "Decree on the Ministry and Life of Priests", 15,
        "羅馬‧聖伯多祿大殿（梵二第四會期）",
        "天主教司鐸（priests / presbyters）的職務、靈修生活、獨身、終身陶成、與主教及修生關係",
        "本文件補充《教會憲章》的主教神學，集中討論「次於主教的司鐸職」。確認司鐸獨身為「至寶」但區別於聖事性必要（拉丁禮紀律）；強調司鐸的「兄弟團」（presbyterium）作為教會性建制；要求終身陶成。",
        "後續具體化：1992 若望保祿二世《Pastores Dabo Vobis》宗座勸諭、各地司鐸進修課程。",
        ["catholic"],
        ["vatican-ii-ot-optatam-totius", "vatican-ii-lg-lumen-gentium"],
    ),
    (
        "GS", "const", "19651207", "gaudium-et-spes",
        "牧靈憲章", "Pastoral Constitution on the Church in the Modern World", 16,
        "羅馬‧聖伯多祿大殿（梵二第四會期）",
        "教會與當代世界的關係 — 人性尊嚴、社會共善、婚姻家庭、文化、經濟、政治、和平 — 教會對 20 世紀世界處境的總體性回應",
        "1965 年 12 月 7 日（梵二閉幕前一日）頒佈，是梵二最長文件（93 段，分兩部）。最重要特色：① 首份以「牧靈」（pastoral）為名而非「教義」（dogmatic）的大公會議文件 ② 第一部分討論教會對人的本質、社會、活動、命運的看法；第二部分具體討論婚姻家庭、文化、經濟、政治、和平五大議題 ③ 開創天主教「公共神學」與「社會教導」現代傳統。",
        "與《教會憲章》互補：LG 是「教會 ad intra」（教會內部）；GS 是「教會 ad extra」（教會面對世界）。標題開頭「Gaudium et Spes」（喜樂與希望）成為本文件代稱。",
        ["catholic"],
        ["vatican-ii-lg-lumen-gentium", "vatican-ii-dh-dignitatis-humanae"],
    ),
]

URL_TMPL = "https://www.vatican.va/archive/hist_councils/ii_vatican_council/documents/vat-ii_{type}_{date}_{slug}_{lang}.html"
ZH_PDF_TMPL = "https://www.vatican.va/chinese/concilio/vat-ii_{slug}_zh-t.pdf"

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TXT_DIR = os.path.join(ROOT, "data", "creeds", "ecumenical-councils", "vatican-ii")
TS_DIR = os.path.join(ROOT, "data", "creeds", "ecumenical-councils")

os.makedirs(TXT_DIR, exist_ok=True)


def fetch_html(url: str) -> str:
    r = requests.get(url, timeout=60, headers={"User-Agent": "Mozilla/5.0 know-graph-lab/1.0"})
    r.raise_for_status()
    r.encoding = "utf-8"
    return r.text


def extract_text(html: str) -> str:
    """Extract plain text from vatican.va document HTML.

    Strategy: collect all <p> tags, filter noise, join.
    """
    soup = BeautifulSoup(html, "html.parser")

    # Remove nav / footer hints
    for tag in soup.find_all(["nav", "footer", "header", "script", "style"]):
        tag.decompose()

    paragraphs = []
    for p in soup.find_all("p"):
        text = p.get_text(" ", strip=True)
        text = re.sub(r"\s+", " ", text).strip()
        if not text or len(text) < 6:
            continue
        # Filter common nav noise
        lc = text.lower()
        if lc in ("home", "search", "previous", "next", "index", "back"):
            continue
        if lc.startswith("copyright") and len(text) < 80:
            continue
        paragraphs.append(text)

    # Drop the first few short paragraphs (often title / headers); keep if 1st is body-length.
    return "\n\n".join(paragraphs)


def get_year(date: str) -> int:
    return int(date[:4])


def safe_text(s: str) -> str:
    """Escape backtick + ${ for TypeScript template literal."""
    return s.replace("\\", "\\\\").replace("`", "\\`").replace("${", "\\${")


TS_TEMPLATE = """import type {{ Creed }} from '../types'
// @ts-expect-error — Vite raw-text import
import latText from './vatican-ii/{code_lc}-latin.txt?raw'
// @ts-expect-error — Vite raw-text import
import enText from './vatican-ii/{code_lc}-english.txt?raw'

export const vaticanII{code_pascal}: Creed = {{
  slug: 'vatican-ii-{code_lc}-{url_slug}',
  category: 'ecumenical-council',
  councilNo: 21,
  councilDocCode: '{code}',
  councilDocOrder: {doc_order},
  order: {order},
  nameZh: '{name_zh}',
  nameEn: '{name_en}',
  nameLat: '{name_lat}',
  year: {year},
  location: '{location}',
  topic: '{topic}',
  authors: [
    '教宗保祿六世（Paul VI）頒佈',
  ],
  acceptedBy: [{accepted_by_str}],
  versions: [
    {{
      lang: 'zh-Hant-Catholic',
      label: '思高／天主教中文版（vatican.va 官方繁體 PDF）',
      text: '待補：vatican.va 中文版為 PDF 檔，需手動下載抽字後填入。\\n下載：{zh_pdf}',
      source: '{zh_pdf}',
      translator: '台灣地區主教團 / 香港教區禮儀委員會',
      placeholder: true,
    }},
    {{
      lang: 'en',
      label: 'Vatican official English translation',
      text: enText as string,
      source: '{en_url}',
    }},
    {{
      lang: 'lat',
      label: 'Editio Typica Latina',
      text: latText as string,
      source: '{lat_url}',
    }},
  ],
  summaryZh: `{summary_zh}`,
  notes: `{notes}`,
  related: [{related_str}],
}}
"""


def build_one(doc):
    (code, url_type, date, url_slug, name_zh, name_en, doc_order,
     location, topic, summary_zh, notes_zh, accepted_by, related) = doc
    code_lc = code.lower()
    code_pascal = code  # SC/LG already uppercase; use as-is for var name
    name_lat = url_slug.replace("-", " ").title()  # e.g. "Lumen Gentium"
    year = get_year(date)
    order = 2100 + doc_order

    lat_url = URL_TMPL.format(type=url_type, date=date, slug=url_slug, lang="lt")
    en_url = URL_TMPL.format(type=url_type, date=date, slug=url_slug, lang="en")
    zh_pdf = ZH_PDF_TMPL.format(slug=url_slug)

    lat_path = os.path.join(TXT_DIR, f"{code_lc}-latin.txt")
    en_path = os.path.join(TXT_DIR, f"{code_lc}-english.txt")

    print(f"[{code}] Fetching Latin ...", flush=True)
    try:
        lat_html = fetch_html(lat_url)
        lat_text = extract_text(lat_html)
    except Exception as e:
        print(f"  [{code}] Latin FAILED: {e}", flush=True)
        lat_text = f"[Fetch failed: {lat_url}]"

    print(f"[{code}] Fetching English ...", flush=True)
    try:
        en_html = fetch_html(en_url)
        en_text = extract_text(en_html)
    except Exception as e:
        print(f"  [{code}] English FAILED: {e}", flush=True)
        en_text = f"[Fetch failed: {en_url}]"

    with open(lat_path, "w", encoding="utf-8") as f:
        f.write(lat_text)
    with open(en_path, "w", encoding="utf-8") as f:
        f.write(en_text)

    accepted_by_str = ", ".join(f"'{x}'" for x in accepted_by)
    related_str = ", ".join(f"'{x}'" for x in related)

    ts_content = TS_TEMPLATE.format(
        code=code, code_lc=code_lc, code_pascal=code_pascal,
        url_slug=url_slug, name_zh=name_zh, name_en=name_en, name_lat=name_lat,
        year=year, location=location, topic=topic,
        accepted_by_str=accepted_by_str,
        zh_pdf=zh_pdf, en_url=en_url, lat_url=lat_url,
        summary_zh=safe_text(summary_zh),
        notes=safe_text(notes_zh),
        related_str=related_str,
        doc_order=doc_order, order=order,
    )

    ts_path = os.path.join(TS_DIR, f"vatican-ii-{doc_order:02d}-{code_lc}.ts")
    with open(ts_path, "w", encoding="utf-8") as f:
        f.write(ts_content)
    print(f"  [{code}] -> {ts_path} ({len(lat_text)} L / {len(en_text)} E)")

    return code, doc_order, code_lc


def main():
    results = []
    for doc in DOCS:
        try:
            results.append(build_one(doc))
            time.sleep(1.5)
        except Exception as e:
            print(f"ERROR on {doc[0]}: {e}", flush=True)
            sys.exit(1)

    print("\n=== Registry import lines (paste into data/creeds/index.ts) ===")
    print("// SC (already imported)")
    for code, doc_order, code_lc in results:
        print(f"import {{ vaticanII{code} }} from './ecumenical-councils/vatican-ii-{doc_order:02d}-{code_lc}'")

    print("\n=== ECUMENICAL_COUNCILS array additions ===")
    print("  vaticanIISC,  // 已加")
    for code, _, _ in results:
        print(f"  vaticanII{code},")


if __name__ == "__main__":
    main()
