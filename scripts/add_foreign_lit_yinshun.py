# Add web-verified foreign-language scholarly works to yinshun-shengyan 研究回顧.
# Bibliography-only (no sections); fulltext_url kept so the reader shows the link.
# Idempotent: skips a ref_key already present on yinshun-shengyan.
import sys, json, requests
import lit_review as lr

DST = 'yinshun-shengyan'
APPLY = '--apply' in sys.argv

# theme buckets already used on yinshun-shengyan (copied from 大愛道)
T_YIN = '人間佛教思想與印順學脈絡'
T_FGS = '法鼓山與聖嚴法師人間佛教'
T_HIS = '史料與當代台灣佛教脈絡'
T_KNW = '佛教知識化、高教與電子佛典'

# (authors, year, title, venue, language, theme, url, oa, abstract_zh)
WORKS = [
 ("Marcus Bingenheimer",2004,"Der Mönchsgelehrte Yinshun (*1906) und seine Bedeutung für den Chinesisch-Taiwanischen Buddhismus im 20. Jahrhundert","Heidelberg: Edition Forum（Würzburger Sinologische Schriften）","de",T_YIN,"https://mbingenheimer.net/publications/bingenheimer_Yinshun.2004.pdf",True,"畢根海默以德文撰寫的印順研究專著，考察印順（1906年生）的生平與思想，論證其對二十世紀漢傳—台灣佛教的關鍵地位。作者個人網站提供全書掃描 PDF。"),
 ("Stefania Travagnin（史芬妮）",2007,"Master Yinshun and Buddhist Nuns in/for the Human Realm: Shift and Continuity from Theory to Practice of renjian fojiao in Contemporary Taiwan","In The Margins of Becoming, Wiesbaden: Harrassowitz, pp. 83–100","en",T_YIN,"https://stefaniatravagnin.net/buddhism-in-taiwan/",False,"探討印順「人間佛教」理論在當代台灣由理論落實為實踐，聚焦比丘尼在人間佛教中的角色，論其理念與實踐間的延續與轉變。連結為作者著作頁。"),
 ("Stefania Travagnin（史芬妮）",2017,"Genealogy and Taxonomy of the 'Twentieth-century Renjian Fojiao': Mapping a famen from Mainland China and Taiwan to Europe","Journal of Humanistic Buddhism, vol. 9","en",T_YIN,"https://stefaniatravagnin.net/buddhism-in-taiwan/",False,"為二十世紀「人間佛教」建立譜系與分類框架，追蹤此一法門如何自中國大陸、台灣傳布至歐洲，釐清太虛、印順一系的傳承與分流。連結為作者著作頁。"),
 ("Stefania Travagnin（史芬妮）",2020,"Renjian Fojiao from Taiwan to South East Asia: Yinshun, Yanpei, and a 'renjian fojiao network'?","In The Practice of Humanistic Buddhism in East and Southeast Asia, CUHK, pp. 467–500","en",T_YIN,"https://stefaniatravagnin.net/buddhism-in-taiwan/",False,"考察印順與演培如何將「人間佛教」自台灣傳播至東南亞，並質問是否存在跨地域的「人間佛教網絡」，藉以理解印順學派的國際擴散。連結為作者著作頁。"),
 ("Stefania Travagnin（史芬妮）",2016,"Yinshun and his Exposition of Madhyamaka: New Studies of the Da Zhidu Lun in Twentieth-century China and Taiwan","Sheffield: Equinox Publishing","en",T_YIN,"https://www.equinoxpub.com/home/yinshun/",False,"專書研究印順對中觀學的詮釋，特別是其對《大智度論》的考訂與運用，呈現二十世紀中國與台灣佛學中印順如何重構印度大乘中觀傳統。出版社頁。"),
 ("Justin R. Ritzinger",2020,"Original Buddhism and its Discontents: The Maitreya Lay Buddhist Lodge and Yinshun's Buddhism of the Human Realm","Journal of Chinese Buddhist Studies（中華佛學學報）, vol. 33, pp. 203–232","en",T_YIN,"https://chinesebuddhiststudies.org/wp-content/uploads/jcbs3306_Ritzinger203-232.pdf",True,"透過在家佛教團體「彌勒佛院」的田野研究，檢視印順「人間佛教」（人間淨土）理念在基層信眾中被接受與爭議的情形。中華佛學學報官網提供全文 PDF。"),
 ("Charles B. Jones（周文廣）",2021,"Taixu's 'On the Establishment of the Pure Land in the Human Realm': A Translation and Study","Honolulu: University of Hawai'i Press","en",T_YIN,"https://uhpress.hawaii.edu/title/taixus-on-the-establishment-of-the-pure-land-in-the-human-realm-a-translation-and-study/",False,"首度將太虛1926年〈建設人間淨土論〉英譯並研究，闡明人間佛教的思想源頭，追溯印順、聖嚴等後繼者如何承續與改造此理念。出版社頁。"),
 ("Jimmy Yu（俞永峰）",2022,"Reimagining Chan Buddhism: Sheng Yen and the Creation of the Dharma Drum Lineage of Chan","London: Routledge","en",T_FGS,"https://www.routledge.com/Reimagining-Chan-Buddhism-Sheng-Yen-and-the-Creation-of-the-Dharma-Drum-Lineage-of-Chan/Yu/p/book/9780367502973",False,"首部關於聖嚴所創「法鼓宗」禪法的社會—思想史專著，分析聖嚴如何融會話頭與默照、結合學術與修證，重構出現代漢傳禪宗法脈。出版社頁。"),
 ("Jimmy Yu（俞永峰）",2013,"A New Chan (Zen) School in Taiwan: Dharma Drum Lineage of Chan Buddhism","In The Oxford Handbook of Contemporary Buddhism, Oxford University Press","en",T_FGS,"https://academic.oup.com/edited-volume/41006",False,"論述聖嚴在台灣創立「法鼓宗」此一新禪宗法脈的過程，闡明其禪法淵源、制度化與當代意義。牛津手冊線上版。"),
 ("Esther-Maria Guggenmos",2018,"Fagushan (Dharma Drum Mountain)","In Handbook of East Asian New Religious Movements, Leiden: Brill, pp. 485–503","en",T_FGS,"https://brill.com/display/book/9789004362512/B9789004362512_024.xml",False,"系統介紹法鼓山的創立、聖嚴的思想與其學術與教育機構建設，將法鼓山置於東亞新興宗教運動的脈絡中分析。出版社頁。"),
 ("Marcus Bingenheimer",2020,"Digitization of Buddhism (Digital Humanities and Buddhist Studies)","Oxford Bibliographies in Buddhism, Oxford University Press","en",T_KNW,"https://mbingenheimer.net/publications/bingenheimer.2020.oxford-bib-digitizationOfBuddhism.pdf",True,"綜述佛教文獻數位化與佛學數位人文現況，將 CBETA 與日本 SAT 大正藏資料庫並列為兩大漢文佛典數位語料庫，評介相關工具與研究。作者網站提供全文 PDF。"),
 ("Marcus Bingenheimer",2014,"Collation Strategies for the Buddhist Canon — Concerning Variant Readings of the Chinese Buddhist Canon","Journal of East Asian Publishing and Society, vol. 4, no. 2","en",T_KNW,"https://mbingenheimer.net/publications/bingenheimer.2014.collationStrategiesForThe%20BuddhistCanon.pdf",True,"探討數位漢文大藏經（含 CBETA）在處理異文校勘上的策略與技術問題，論述如何在電子版中呈現版本差異。作者網站提供全文 PDF。"),
 ("Jiang Wu（吳疆）、Greg Wilkinson 編",2017,"Reinventing the Tripitaka: Transformation of the Buddhist Canon in Modern East Asia","Lanham: Lexington Books","en",T_KNW,"https://rowman.com/ISBN/9781498547574/Reinventing-the-Tripitaka-Transformation-of-the-Buddhist-Canon-in-Modern-East-Asia",False,"論文集，考察近代東亞佛教正典的轉型，收錄關於大正藏編纂、頻伽藏，及 SAT 大正藏資料庫簡史等數位化專章。出版社頁。"),
 ("Gregory Adam Scott",2017,"The 1913 Pinjia Canon and the Changing Role of the Buddhist Canon in Modern China","In Reinventing the Tripitaka, Lanham: Lexington Books","en",T_KNW,"https://rowman.com/ISBN/9781498547574/Reinventing-the-Tripitaka-Transformation-of-the-Buddhist-Canon-in-Modern-East-Asia",False,"以1913年上海頻伽藏為例，說明近代中國佛教界如何以現代印刷生產平價、現代化的佛教正典，反映大藏經角色之轉變。出版社頁。"),
 ("Scott Pacey",2020,"Buddhist Responses to Christianity in Postwar Taiwan: Awakening the World","Amsterdam: Amsterdam University Press","en",T_HIS,"https://www.aup.nl/en/book/9789463724111/buddhist-responses-to-christianity-in-postwar-taiwan",False,"研究戰後台灣佛教與基督教對話的專著，分析印順、星雲、聖嚴等高僧如何在與基督宗教競爭與現代性挑戰中回應、形塑宗教認同，推進人間佛教。出版社頁。"),
 ("Charles B. Jones（周文廣）",1999,"Buddhism in Taiwan: Religion and the State, 1660–1990","Honolulu: University of Hawai'i Press","en",T_HIS,"https://archive.org/details/buddhismintaiwan0000jone",True,"西方語言中首部全面考察台灣漢傳佛教制度與政治史的專著，自清代敘述至1980年代末，涵蓋戒律式微、比丘尼興起與大型國際教團（含法鼓山、慈濟）之興起。Internet Archive 借閱全文。"),
 ("Richard Madsen",2007,"Democracy's Dharma: Religious Renaissance and Political Development in Taiwan","Berkeley: University of California Press","en",T_HIS,"https://archive.org/details/democracysdharma0000mads",True,"論證台灣佛教與道教的宗教復興與民主化轉型互為支撐，透過慈濟、佛光山、法鼓山、行天宮四案例，說明此宗教復興如何孕育民主式現代性。Internet Archive 借閱全文。"),
 ("André Laliberté",2004,"The Politics of Buddhist Organizations in Taiwan, 1989–2003","London: RoutledgeCurzon","en",T_HIS,"https://buddhistuniversity.net/content/booklets/politics-of-buddhist-organizations-in-taiwan_laliberte-andre",True,"比較台灣三大佛教組織（中國佛教會、佛光山、慈濟）在國家監管、總統選舉與全民健保等議題上的政治態度差異，主張領袖個人特質是解釋其政治行為的關鍵。The Open Buddhist University 提供節錄。"),
 ("Yu-Shuang Yao（姚玉霜）",2012,"Taiwan's Tzu Chi as Engaged Buddhism: Origins, Organization, Appeal and Social Impact","Leiden: Global Oriental / Brill","en",T_HIS,"https://brill.com/display/title/24446",False,"研究慈濟作為入世佛教（人間佛教實踐）的起源、組織、吸引力與社會影響，分析其於1990年代迅速擴張成為華人世界最大在家佛教團體的原因。出版社頁。"),
]

env = {}
for line in open('.env', encoding='utf-8'):
    line = line.strip()
    if '=' in line and not line.startswith('#'):
        k, v = line.split('=', 1); env[k] = v.strip().strip('"')
U = env['SUPABASE_URL']; K = env['SUPABASE_SERVICE_ROLE_KEY']
H = {'apikey': K, 'Authorization': 'Bearer ' + K, 'Content-Type': 'application/json'}

existing = {e['ref_key'] for e in requests.get(
    U + '/rest/v1/lit_review_entries', params={'select': 'ref_key', 'project_slug': 'eq.' + DST},
    headers=H).json()}

rows, do = [], 650
for authors, year, title, venue, lang, theme, url, oa, abs in WORKS:
    rk = lr.make_ref_key(authors, year, title)
    if rk in existing:
        print('skip dup:', rk); continue
    rows.append({'project_slug': DST, 'ref_key': rk, 'authors': authors, 'year': year,
                 'title': title, 'venue': venue, 'language': lang, 'theme': theme,
                 'abstract_zh': abs, 'fulltext_url': url,
                 'fulltext_status': 'unavailable', 'display_order': do})
    print(f'do={do} [{theme[:10]}] {lang} {authors[:18]} ({year}) {title[:38]}')
    do += 1

print(f'\n{len(rows)} new foreign entries')
if APPLY and rows:
    r = requests.post(U + '/rest/v1/lit_review_entries',
                      headers={**H, 'Prefer': 'return=minimal'}, data=json.dumps(rows))
    r.raise_for_status()
    print('✓ inserted')
elif not APPLY:
    print('(dry-run; pass --apply)')
