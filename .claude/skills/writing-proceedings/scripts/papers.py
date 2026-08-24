# -*- coding: utf-8 -*-
"""第三屆論文集篇目表：順序、編號一律依大會議程（2026-08-17 版）。"""

SESSIONS = {
    "0":   "專題演講",
    "1":   "場次一：藏傳佛教與科學的對話",
    "2":   "場次二：社會、情緒與倫理學習（SEE Learning）",
    "3":   "場次三：人工智能與佛教倫理（AI）",
    "4.1": "場次四之一：藏傳佛教當前的教育體制（一）",
    "4.2": "場次四之二：藏傳佛教當前的教育體制（二）",
    "4.3": "場次四之三：藏傳佛教當前的教育體制（三）",
    "A":   "附錄",
}

# num, session, src, drop（原稿要丟掉的前 N 段＝原標題區）, title, subtitle,
# author（版面署名）, bio（首頁註腳；空字串＝待補）, agenda_title（議程題名）
PAPERS = [
    dict(num="0", ses="0", src="0. 董事長專題演講.docx", start=r"^前\s*言",
         title="從宗教交流到民主夥伴——臺藏關係的發展與展望（1997－2026）",
         sub="", author="格桑堅參",
         bio="財團法人達賴喇嘛西藏宗教基金會董事長。",
         agenda="從宗教交流到民主夥伴——臺藏關係的發展與展望（1997－2026）"),

    dict(num="1.1", ses="1", src="1.1. 預測編碼與佛學_謝伯讓.docx", start=r"^摘\s*要",
         title="從預測編碼理論理解佛教的苦、我執與禪修",
         sub="", author="謝伯讓", bio="",
         agenda="預測編碼理論與佛學"),

    dict(num="1.2", ses="1", src="1.2. 佛法緣起因果律STEM.docx", start=r"^摘\s*要",
         title="佛法緣起因果律在數理科技（STEM）驗證法的會通應用",
         sub="", author="張耀堂、陳世毓",
         bio="張耀堂，高苑科技大學退休教授、台鋼科技大學兼任教授；"
             "陳世毓，鈞能實業有限公司董事長。",
         agenda="佛法緣起因果律在數理科技(STEM)驗證法的會通應用"),

    dict(num="2.1", ses="2", src="2.1. 慈悲翻轉在台灣_關婉玲.docx", start=r"^摘\s*要",
         title="慈悲翻轉在台灣", sub="", author="關婉玲",
         bio="利仁教育基金會 SEE Learning® 促進者、CBCT® 教師。",
         agenda="慈悲翻轉在台灣（利仁基金會）"),

    dict(num="2.2", ses="2", src="2.2. SEE Learning敘事探究.docx", start=r"^摘\s*要",
         title="一位國中教師實踐 SEE Learning 教學之敘事探究",
         sub="", author="盧惠娟",
         bio="國立臺灣師範大學教育學院課程與教學研究所教育學博士；"
             "《西藏的天空》季刊主編。",
         agenda="一位國中教師實踐 SEE Learning 教學之敘事探究"),

    dict(num="3.1", ses="3", src="3.1. 當AI敲響雪域的鐘聲_秋浪法師.docx", start=r"^摘\s*要",
         title="當 AI 敲響雪域的鐘聲",
         sub="——AI 時代對於南印格魯三大寺教育體系的衝擊、應對與轉型實踐",
         author="秋浪法師", bio="般若文化研究學會理事長。",
         agenda="當 AI 敲響雪域的鐘聲"),

    dict(num="3.2", ses="3", src="3.2. WeBuddhist_鐵道_0811.docx", start=r"^摘\s*要",
         title="可信度與共鳴度",
         sub="——透過「鐵道」佛教資料工程與內容創作者合作，"
             "實現 WeBuddhist App 佛教現代化的雙軌策略",
         author="昂望聽列 等", bio="",
         agenda="可信度與共鳴度：透過「鐵道」佛教資料工程與內容創作者合作，"
                "實現 WeBuddhist App 佛教現代化的雙軌策略"),

    dict(num="3.3", ses="3", src="3.3. 覺察與演算_澤仁扎西堪布.docx", start=r"^摘\s*要",
         title="覺察與演算：AI 時代佛法的當代價值與傳播策略",
         sub="——兼論藏傳佛教現代化之轉型路徑",
         author="澤仁扎西 堪布",
         bio="現任：澳洲慧輪藏傳佛教協會知道上師；喜馬拉雅慧輪文化基金會創始者；"
             "榮松佛教頻道創始人。曾任：台灣國際藏傳佛教研究會主席。",
         agenda="覺察與演算：AI 時代佛法的當代價值與傳播策略"),

    dict(num="4.1.1", ses="4.1", src="4.1.1. 三學佛學院.docx", start=r"^摘\s*要",
         title="藏傳佛教於印度格魯派其學制學位及教法之研究",
         sub="", author="陳明茹",
         bio="台灣國際藏傳佛教研究會會長。",
         agenda="格魯派三大寺之佛學教育與台灣推廣"),

    dict(num="4.1.2", ses="4.1", src="噶舉派在台的發展及特色 (劉國威).docx", start=r"^噶舉派是現今",
         title="噶舉派在台的發展及特色", sub="", author="劉國威", bio="",
         agenda="藏傳佛教教育體制從傳統到現代化的變遷——以噶舉派教育體制為例"),

    # Google Docs 匯出會把頁碼「第 N 頁」落成內文段落，排版時濾掉
    dict(num="4.2.1", ses="4.2", src="nyingma.docx", start=r"^摘\s*要",
         strip=r"^第\s*\d+\s*頁$",
         title="藏傳佛教寧瑪派教育體制現代化轉型之研究",
         sub="——以南印度南卓林寺前譯寧瑪佛學院為例",
         author="堪布其美多吉",
         bio="玄奘大學宗教與文化系。",
         agenda="藏傳佛教教育體制從傳統到現代化的變遷——以寧瑪派教育體制為例"),

    dict(num="4.2.2", ses="4.2", src="4.2.1. 吉祥薩迦派的教育體制_堪布昂文克周.docx",
         start=r"^一、前言",
         title="吉祥薩迦派的教育體制", sub="", author="堪布昂旺克周", bio="",
         agenda="薩迦教派教育體制從傳統到現代"),

    # 2026-08-22 作者送來修訂版（術語更正＋新增格魯大考沿革），取代舊稿
    dict(num="4.2.3", ses="4.2", src="geshe_v3.docx", start=r"^摘\s*要",
         title="藏傳佛教南印度格魯派三大寺格西學制研究",
         sub="", author="哈欣仁波切", bio="拉然巴格西。",
         agenda="藏傳佛教教育體制從傳統到現代化的變遷——以格魯派教育體制為例"),

    dict(num="4.3.1", ses="4.3", src="4.3.1_liu.docx", start=r"^綜述",
         title="南印藏區三大寺田野紀行（2026 年 1 月）",
         sub="", author="劉宇光",
         bio="國立政治大學華人宗教研究中心客座研究員。",
         agenda="南印流亡三大寺僧團教育觀察與思考"),

    dict(num="4.3.2", ses="4.3", src="4.3.2. 教育與照護之間_盧佳慧.docx", start=r"^摘\s*要",
         title="教育與照護之間",
         sub="——拉達克尼僧的在地專業化與專業路徑選擇",
         author="盧佳慧", bio="臺北醫學大學醫學人文研究所。",
         agenda="教育與照護之間：拉達克 Ani 的藏醫實作"),

    dict(num="A1", ses="A", src="3.2. WeBuddhist_TTBF_Paper_EN_0811.docx", start=r"^Abstract",
         title="Reliable and Relatable",
         sub="A Two-Track Strategy for Modernizing Buddhism in the WeBuddhist "
             "App through “Railroads” and Creator Partnerships",
         author="Ngawang Trinley et al.", bio="",
         agenda="〔3.2 之英文版〕"),
]
