"""家教《三國演義》二十回簡報的共用圖庫。

從維基共享資源抓圖、驗授權、存進 Drive 圖庫，並維護 credits.json。
十六回共用同一份圖庫，同一個人物只抓一次。

用法：
    python -X utf8 scripts/sanguo_image_library.py --list          # 看現有圖庫
    python -X utf8 scripts/sanguo_image_library.py --fetch core    # 抓某一批
    python -X utf8 scripts/sanguo_image_library.py --audit         # 重驗全部授權

🚨 授權閘：NC（非商業）與 ND（禁改作）一律擋下，不進圖庫。
   家教簡報雖然不營利，但這批圖之後可能進講義或上架，NC／ND 從源頭排除比較省事。
   參見 memory: feedback_cc_license_filter。
"""
import argparse
import io
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request

LIB = r"G:\我的雲端硬碟\資料\知識圖工作室\教學\家教_三國演義\_圖庫"
IMAGES = os.path.join(LIB, "images")
CREDITS = os.path.join(LIB, "credits.json")

API = "https://commons.wikimedia.org/w/api.php"
UA = {"User-Agent": "know-graph-lab tutoring slides/1.0 (redpiigpig@gmail.com)"}
MAX_WIDTH = 1400          # 簡報最大只會用到 800px 寬，1400 留一倍給放大檢視
REQUEST_GAP = 0.4         # 對 Commons 客氣一點

# 授權閘：命中就擋
FORBIDDEN = re.compile(r"\bNC\b|NonCommercial|non-commercial|\bND\b|NoDerivs|No[- ]Derivative", re.I)
# 允許的授權（其一命中才收）
ALLOWED = re.compile(r"public domain|PD|CC0|CC BY(?!.*(NC|ND))", re.I)


# ── 要抓的圖，分批列 ────────────────────────────────────────────────
# key: (Commons 檔名, 中文說明)
# 中文說明會直接變成簡報裡 CREDIT 的第一欄與圖片 alt，寫給小孩看得懂。
BATCHES = {
    # 十六回都會重複出現的主要人物
    "core": {
        "caocao":    ("Cao Cao Portrait ROTK.jpg",             "曹操像（清代繡像）"),
        "guanyu":    ("Guan Yu Portrait.jpg",                  "關羽像（清代繡像）"),
        # 🚨 不要用 "Zhuge Liang Portrait.jpg"：同一幅刻本，但被 Purple Cloud
        #    Institute 打了浮水印，還在公有領域掃描上主張 CC BY-SA 4.0。
        #    下面這張是同一幅的乾淨原掃描。
        "zhugeliang": ("Zhuge Kongming Sancai Tuhui.jpg",      "諸葛亮像（明《三才圖會》刻本）"),
        "zhugeliangcart": ("ZhugeLiang1.jpg",                  "諸葛亮乘車像（傳統木刻版畫）"),
        "zhangfeixiu": ("ZhangFei.jpg",                        "張飛像（清代繡像）"),
        "liubeixiu": ("Liu Bei Portrait.jpg",                  "劉備像（清代繡像）"),
        "sunquan":   ("Sun Quan Qing portrait.jpg",            "孫權像（清代繡像）"),
        "zhouyu":    ("ZhouYu.jpg",                            "周瑜像（清代繡像）"),
        "lvbu":      ("Lu Bu Qing dynasty portrait.jpg",       "呂布像（清代繡像）"),
        "zhaoyun":   ("ZhaoYun.jpg",                           "趙雲像（清代繡像）"),
        "machao":    ("MaChao.jpg",                            "馬超像（清代繡像）"),
        "huangzhong": ("Huang Zhong Portrait.jpg",             "黃忠像（清代繡像）"),
        "simayi":    ("SimaYi.jpg",                            "司馬懿像（清代繡像）"),
        "luxun":     ("LuXun.jpg",                             "陸遜像（清代繡像）"),
        "jiangwei":  ("JiangWei.jpg",                          "姜維像（清代繡像）"),
        "liushan":   ("Liu Shan Qing illustration.jpg",        "劉禪像（清代繡像）"),
        "caopi":     ("CaoPiPortrait.jpg",                     "曹丕像（清代繡像）"),
        "sunce":     ("Sun Ce Portrait.jpg",                    "孫策像（清代繡像）"),
        "lusu":      ("LuSu.jpg",                              "魯肅像（清代繡像）"),
    },
    # 同一套清代繡像系列剩下的，收齊備用（十六回不重複用圖，池子要夠大）
    "qing2": {
        "caohong":   ("Cao Hong Qing illustration.jpg",        "曹洪像（清代繡像）"),
        "caoren":    ("Cao Ren Qing illustration.jpg",         "曹仁像（清代繡像）"),
        "caozhang":  ("Cao Zhang - Qing ZQ-SGYY.jpg",          "曹彰像（清代繡像）"),
        "caozhen":   ("Cao Zhen Qing illustration.jpg",        "曹真像（清代繡像）"),
        "dingfeng":  ("DingFeng.jpg",                          "丁奉像（清代繡像）"),
        "fuwan":     ("Fu Wan Qing illustration.jpg",          "伏完像（清代繡像）"),
        "guanlu":    ("Guan Lu Qing portrait.jpg",             "管輅像（清代繡像）"),
        "guanxing":  ("Guan Xing Qing illustration.jpg",       "關興像（清代繡像）"),
        "hansui":    ("Han Sui Qing Dynasty portrait.jpg",     "韓遂像（清代繡像）"),
        "huangchengyan": ("Huang Chengyan Qing Illustration.jpg", "黃承彥像（清代繡像）"),
        "jiaxu":     ("Jia Xu2.jpg",                           "賈詡像（清代繡像）"),
        "kongrong":  ("Kong Rong Qing Portrait.jpg",           "孔融像（清代繡像）"),
        "madai":     ("Ma Dai Qing portrait.jpg",              "馬岱像（清代繡像）"),
        "mateng":    ("Ma Teng Qing illustration.jpg",         "馬騰像（清代繡像）"),
        "miheng":    ("Mi Heng Qing portait.jpg",              "禰衡像（清代繡像）"),
        "pujing":    ("Pujing Qing dynasty illustration.jpg",  "普淨像（清代繡像）"),
        "wangjing":  ("Wang Jing portrait Qing.jpg",           "王經像（清代繡像）"),
        "wangshuang": ("Wang Shuang Qing portrait.jpg",        "王雙像（清代繡像）"),
        "xiahouba":  ("XiahouBa.jpg",                          "夏侯霸像（清代繡像）"),
        "yangxiu":   ("YangXiu.jpg",                           "楊修像（清代繡像）"),
        "yuji":      ("Yu Ji Qing portrait.jpg",               "于吉像（清代繡像）"),
        "zhangbao":  ("Zhang Bao Qing portrait.jpg",           "張苞像（清代繡像）"),
        "zhangjue":  ("Zhang Jue Qing portrait.jpg",           "張角像（清代繡像）"),
        "zhangxiu":  ("Zhang Xiu Qing portrait.jpg",           "張繡像（清代繡像）"),
        "zhoutai":   ("Zhou Tai Qing illustration.jpg",        "周泰像（清代繡像）"),
        "zhugedan":  ("Zhuge Dan Qing illustration.jpg",       "諸葛誕像（清代繡像）"),
        "zhugejin":  ("Zhuge Jin Qing illustration.jpg",       "諸葛瑾像（清代繡像）"),
        "zhugeke":   ("Zhuge Ke Qing illustration.jpg",        "諸葛恪像（清代繡像）"),
        "zhugeshang": ("Zhuge Shang Qing portrait.jpg",        "諸葛尚像（清代繡像）"),
        # 場景版畫
        "slayguanhai": ("Guan Yu slays Guan Hai.jpg",          "關羽斬管亥（清代版畫）"),
        "sunjianliubiao": ("Sun Jian attacks Liu Biao.jpg",    "孫堅攻劉表（清代版畫）"),
        "wangkuang": ("Wang Kuanga and Lu Bu.jpg",             "王匡戰呂布（清代版畫）"),
        "shiting":   ("At Shiting, Lu Xun defeats Cao Xiu.jpg", "石亭之戰陸遜破曹休（清代版畫）"),
        "caozhenwu": ("Cao Zhen and Sima Yi assault the lands of Eastern Wu.jpg",
                      "曹真與司馬懿伐吳（清代版畫）"),
        # 這幾張內容待確認，抓下來要看過再用
        "rtk2":      ("RTK - 002.jpg",                         "三國演義插圖（清代版畫）"),
        "rtk3":      ("RTK - 003.jpg",                         "三國演義插圖（清代版畫）"),
        "rtk4":      ("RTK - 004.jpg",                         "三國演義插圖（清代版畫）"),
        "rtk5":      ("RTK - 005.jpg",                         "三國演義插圖（清代版畫）"),
        "rtk6":      ("RTK - 006.jpg",                         "三國演義插圖（清代版畫）"),
        "rtkc1":     ("RTK Chronicle - 001.jpg",               "三國志傳插圖（清代版畫）"),
        "rtkc2":     ("RTK Chronicle - 002.jpg",               "三國志傳插圖（清代版畫）"),
        "rtkc3":     ("RTK Chronicle - 003.jpg",               "三國志傳插圖（清代版畫）"),
    },

    # 文物與遺址：十六回不重複用圖，每回都要有自己的場景圖
    "sites": {
        "wuhougate": ("Gateway - Wuhou Shrine - Chengdu, China - DSC05423.jpg",
                      "成都武侯祠大門"),
        "wuhoucorridor": ("Corridor - Wuhou Shrine - Chengdu, China - DSC05483.jpg",
                          "成都武侯祠迴廊"),
        "wuhoustele": ("Inscription - Wuhou Shrine - Chengdu, China - DSC05441.jpg",
                       "武侯祠碑刻"),
        "jianmen":   ("Jianmen Pass.jpg",                      "劍門關"),
        "jianmenmt": ("The mountain in Jianmenguan.jpg",        "劍門關的山"),
        "baidicheng": ("Baidicheng 2014.jpg",                  "白帝城"),
        "tuogutang": ("Tuogutang.jpg",                          "白帝城託孤堂"),
        "woodenoxreplica": ("Wooden ox 2016 Temple of Marquis Wu (Wuzhang Plains).jpg",
                            "木牛複製品（五丈原武侯祠）"),
        "flowinghorse": ("Flowing horse 2016 Temple of Marquis Wu (Wuzhang Plains).jpg",
                         "流馬複製品（五丈原武侯祠）"),
        "chunqiulou": ("Chunqiu Lou 07.jpg",                    "許昌春秋樓（關羽夜讀處）"),
    },
    "relics": {
        "crossbow":  ("Han Bronze Crossbow Mechanism.jpg",      "東漢青銅弩機"),
        "bolts":     ("Han Bronze & Iron Crossbow Bolts, Han Tomb of Liu Wu, King of Chu, Xuzhou.jpg",
                      "漢代弩箭鏃"),
        "granary":   ("Eastern Han Pottery Granary.jpg",         "東漢陶倉"),
        "granary2":  ("Eastern Han Pottery Qun (Granary).jpg",   "東漢陶囷（圓形穀倉）"),
        "lamp":      ("Han Bronze Lamp 01.jpg",                  "漢代青銅燈"),
        "lamp2":     ("Han Bronze Lamp 03.jpg",                  "漢代青銅燈（另一件）"),
        "mirror":    ("Han Bronze Mirror, Palace Museum.jpg",    "漢代銅鏡"),
        "mirror2":   ("Han Bronze Mirror, Gongyi.jpg",           "漢代銅鏡（鞏義出土）"),
    },

    # 主角會在十幾回出現，但同一張圖只能用一次 → 同一個人要備多幅。
    # 備不到的回數就用樣板的 Q 版 chr() SVG。
    "alts": {
        "lvbu2":     ("Lü Bu Portrait.jpg",                     "呂布像（清代繡像，另一幅）"),
        "dongzhuo2": ("Dong Zhuo Qing Dynasty Illustration.jpg", "董卓像（清代繡像，另一幅）"),
        "diaochan2": ("DiaoChan.jpg",                           "貂蟬像（清代繡像，另一幅）"),
        "xiandi2":   ("Emperor Xian Qing illustration.jpg",     "漢獻帝像（清代繡像，另一幅）"),
        "hejin2":    ("He Jin Qing illustration.jpg",           "何進像（清代繡像，另一幅）"),
        "huanggai2": ("HuangGai.jpg",                           "黃蓋像（清代繡像，另一幅）"),
        "lvmeng2":   ("Lu Meng.jpg",                            "呂蒙像（清代繡像，另一幅）"),
        "lvmeng3":   ("Portrait of Lu Meng, Qing dynasty.jpg",  "呂蒙像（清代繡像，第三幅）"),
        "menghuo2":  ("MengHuo.jpg",                            "孟獲像（清代繡像，另一幅）"),
        "miheng2":   ("Portrait of Mi Heng.jpg",                "禰衡像（清代繡像，另一幅）"),
        "xunyu2":    ("Portrait of Xun Yu.jpg",                 "荀彧像（清代繡像，另一幅）"),
        "liubei2":   ("Portraits of Famous Men - Liu Bei.jpg",  "劉備像（歷代名臣像冊）"),
        "liubei3":   ("Portraits of Famous Men - Liu Bei 2.jpg", "劉備像（歷代名臣像冊，另一幅）"),
        "liubei4":   ("Liu Bei Tang.jpg",                       "劉備像（傳唐人畫）"),
        "sunquan2":  ("Portraits of Famous Men - Sun Quan.jpg", "孫權像（歷代名臣像冊）"),
        "sunquan3":  ("Portraits of Famous Men - Sun Quan 2.jpg", "孫權像（歷代名臣像冊，另一幅）"),
        "caopi2":    ("Cao Pi Tang.jpg",                        "曹丕像（傳唐人畫）"),
        "guanyustatue": ("Daxiangguo Temple - Guan Yu Statue.jpg", "大相國寺關羽像"),
        "guanyuhorse": ("Baling Qiao 33 Guan Yu on Red Hare.jpg", "關羽騎赤兔塑像"),
        "guanyubig": ("Chunqiu Lou 11 Guan Yu Temple, 15 Meter Statue of Guan Yu.jpg",
                      "許昌春秋樓十五公尺關羽像"),
    },

    # 江戶浮世繪的三國題材：彩色、動作感強，是日本漫畫的祖宗，
    # 而且全部公有領域——要「像動漫」又能公開發布，這一批是正解。
    "ukiyoe": {
        "changbanbridge": ("Sangokushi Chohan hashi no zu 三国志長坂橋圖 (The Three Kingdoms- Zhang Fei at Changban Bridge) MET DP147623.jpg",
                           "三國志長坂橋圖（歌川國芳浮世繪）"),
        "threevisits": ("Gentoku Miyuki chu Komei wo tazu no zu 玄徳三雪中孔明訪圖 (BM 2008,3037.18401).jpg",
                        "玄德雪中三訪孔明圖（浮世繪）"),
        "tankei":    ("Gentoku uma o odorashite tankei o koeru zu LCCN2008660468.jpg",
                      "玄德躍馬過檀溪圖（浮世繪）"),
        "zhangfeibridge": ("Zhang Fei on the Long Sloped Bridge Turning Away One Million Soldiers.jpg",
                           "張飛據長坂橋退百萬兵（月岡芳年浮世繪）"),
        "threevisits2": ("F90-12-1 Tsukioka Yoshitoshi-Gentoku Visits Komei in the Snow.jpg",
                         "玄德雪中訪孔明（月岡芳年浮世繪）"),
    },

    # 第一～四回原本彼此重複用圖（第二回 5 張有 3 張借自第一回），這批是替代品
    "fix14": {
        "slips2":   ("Military documents on bamboo slips scroll in Han Dynasty 01.jpg",
                      "漢代軍事文書木簡"),
        "relief2":  ("Han Pottery Farm Scene.jpg",              "東漢陶製農家場景"),
        "soldiers2": ("Han Terracotta Figurines, Han Tomb of Liu Wu, King of Chu (10084956736).jpg",
                      "漢代陶兵俑群（楚王劉戊墓）"),
        "que2":     ("Gaoyi Que(Front).jpg",                     "東漢高頤闕正面"),
        "chariot2": ("Eastern Han Bronze Cavalry and Chariots1.JPG", "東漢銅騎兵與車馬"),
        "map_3k":   ("Map of China During the Period of the Three Kingdoms.jpg",
                      "三國時期中國地圖"),
    },

    "maps": {
        "map_warlords": ("End of Han Dynasty Warlords.png",     "漢末群雄割據圖"),
        "map_guandu": ("Guanduzhizhan eng.png",                 "官渡之戰形勢圖"),
        "map_han189": ("Eastern Han in 189 AD.png",             "東漢疆域圖（189 年）"),
        "map_jin": ("China Western Jin.PNG",                     "西晉統一疆域圖（280 年）"),
    },

    # 第五回　十八路諸侯
    "r05": {
        "sunjian":   ("Sun Jian Qing dynasty illustration.jpg", "孫堅像（清代繡像）"),
        "chengong":  ("Chen Gong Qing Dynasty Illustration.jpg", "陳宮像（清代繡像）"),
        "luboshe":   ("Lu Boshe Qing portrait.jpg",            "呂伯奢像（清代繡像）"),
        "gongsunzan": ("Gongsun Zan Qing illustration.jpg",    "公孫瓚像（清代繡像）"),
        "presentblade": ("Cao Cao presents a blade to the tyrant Dong Zhuo.jpg",
                         "曹操獻刀（清代版畫）"),
        "jiaozhao":  ("發矯詔響應曹公.jpg",                      "發矯詔響應曹公（清代版畫）"),
        "hulao":     ("Lu Bu at Hulao.png",                    "虎牢關前的呂布（清代版畫）"),
        "sealquarrel": ("Sun Jian and Yuan Shao quarrel over the Heirloom Seal.jpg",
                        "孫堅與袁紹爭傳國玉璽（清代版畫）"),
        "jadeseal":  ("Jade Seal.png",                          "傳國玉璽（圖示）"),
    },
    # 第六回　連環計
    "r06": {
        "diaochan":  ("Diaochan Qing Dynasty Illustration.jpg", "貂蟬像（清代繡像）"),
        "wangyun":   ("Wang Yun.png",                          "王允像（清代繡像）"),
        "dingyuan":  ("Ding Yuan Qing Illustration.jpg",       "丁原像（清代繡像）"),
        "sackchangan": ("Li Jue and Guo Si sack the capital at Chang'an.jpg",
                        "李傕郭汜犯長安（清代版畫）"),
    },
    # 第七回　群雄割據
    "r07": {
        "yuanshu":   ("Yuan Shu Qing portrait.jpg",            "袁術像（清代繡像）"),
        "liubiao":   ("Liu Biao Qing portait.jpg",             "劉表像（清代繡像）"),
        "zhangliao": ("Zhang Liao Portrait.jpg",               "張遼像（清代繡像）"),
        "dianwei":   ("Dian Wei Qing illustration.jpg",        "典韋像（清代繡像）"),
        "xiahoudun": ("Xiahou Dun Portrait.jpg",               "夏侯惇像（清代繡像）"),
    },
    # 第八回　把皇帝請回家
    "r08": {
        "xunyu":     ("Xun Yu Qing illustration.jpg",          "荀彧像（清代繡像）"),
        "guojia":    ("GuoJia.jpg",                            "郭嘉像（清代繡像）"),
        "jiping":    ("Ji Ping Qing illustration.jpg",         "吉平像（清代繡像）"),
    },
    # 第九回　官渡
    "r09": {
        "yanliang":  ("Yan Liang Qing portrait.jpg",           "顏良像（清代繡像）"),
        "wenchou":   ("Wen Chou Qing portrait.jpg",            "文醜像（清代繡像）"),
        "tianfeng":  ("Tian Feng Qing dynasty illustration.jpg", "田豐像（清代繡像）"),
        "jushou":    ("Ju Shou Qing Illustration.jpg",         "沮授像（清代繡像）"),
        "xuchu":     ("Xu Chu Qing illustration.jpg",          "許褚像（清代繡像）"),
    },
    # 第十回　赤壁
    "r10": {
        "xushu":     ("XuShu.jpg",                             "徐庶像（清代繡像）"),
        "simahui":   ("Sima Hui Qing illustration.jpg",        "司馬徽（水鏡先生）像（清代繡像）"),
        "huanggai":  ("Huang Gai Qing illustration.jpg",       "黃蓋像（清代繡像）"),
        "ganning":   ("GanNing.jpg",                           "甘寧像（清代繡像）"),
        "taishici":  ("Taishi Ci Qing illustration.jpg",       "太史慈像（清代繡像）"),
        "ladygan":   ("Lady Gan Qing portrait.jpg",            "甘夫人像（清代繡像）"),
    },
    # 第十一回　三分天下
    "r11": {
        "sunshangxiang": ("SunShangxiang.jpg",                 "孫尚香像（清代繡像）"),
        "lvmeng":    ("Lu Meng Qing portrait.jpg",             "呂蒙像（清代繡像）"),
    },
    # 第十二回　入西川
    "r12": {
        "pangtong":  ("Pang Tong Qing illustration.jpg",       "龐統像（清代繡像）"),
        "liuzhang":  ("Liu Zhang Qing portrait.jpg",           "劉璋像（清代繡像）"),
        "xiahouyuan": ("Xiahou Yuan Qing dynasty portrait.jpg", "夏侯淵像（清代繡像）"),
        "zhangren":  ("Zhang Ren Qing illustration.jpg",       "張任像（清代繡像）"),
        "yanyan":    ("Yan Yan Qing illustration.jpg",         "嚴顏像（清代繡像）"),
    },
    # 第十三回　敗走麥城
    "r13": {
        "guanping":  ("Guan Ping Qing portrait.jpg",           "關平像（清代繡像）"),
    },
    # 第十四回　漢朝結束了
    "r14": {
        "caozhi":    ("CaoZhiPortrait.jpg",                    "曹植像（清代繡像）"),
        "ladyzhen":  ("Lady Zhen Qing dynasty portrait.jpg",   "甄夫人像（清代繡像）"),
    },
    # 第十六回　七擒孟獲
    "r16": {
        "menghuo":   ("Meng Huo Qing dynasty illustration.jpg", "孟獲像（清代繡像）"),
        "shamoke":   ("Shamoke Qing portrait.jpg",             "沙摩柯像（清代繡像）"),
    },
    # 第十七、十八回　出師表與空城計
    "r17": {
        "masu":      ("Ma Su Portrait.jpg",                    "馬謖像（清代繡像）"),
        "weiyan":    ("Wei Yan Qing dynasty illustration.jpg", "魏延像（清代繡像）"),
        "zhanghe":   ("Zhang He Portrait.jpg",                 "張郃像（清代繡像）"),
        "executemasu": ("Kongming subjects Ma Su to execution.jpg",
                        "孔明揮淚斬馬謖（清代版畫）"),
        "jiangwan":  ("JiangWan.jpg",                          "蔣琬像（清代繡像）"),
    },
    # 第十九回　五丈原
    "r19": {
        "woodenox":  ("Shu forces construct wooden oxen and flowing horses.jpg",
                      "蜀軍造木牛流馬（清代版畫）"),
        "weiriver":  ("Wei and Shu battle at the banks of River Wei.jpg",
                      "魏蜀渭水之戰（清代版畫）"),
        "fleezhongda": ("Living Zongda Fleeing.jpg",           "死諸葛走生仲達（清代版畫）"),
    },
    # 第二十回　三國歸晉
    "r20": {
        "dengai":    ("Deng Ai Qing portrait.jpg",             "鄧艾像（清代繡像）"),
        "simazhao":  ("SimaZhao.jpg",                          "司馬昭像（清代繡像）"),
        "simashi":   ("Sima Shi Qing dynasty portrait.jpg",    "司馬師像（清代繡像）"),
        "zhonghui":  ("Zhong Hui Qing portrait.jpg",           "鍾會像（清代繡像）"),
        "sunhao":    ("Sun Hao Qing portrait.jpg",             "孫皓像（清代繡像）"),
        "yanghu":    ("Yang Hu illustration Qing.jpg",         "羊祜像（清代繡像）"),
    },
}


def api(params):
    url = API + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=60) as fh:
        return json.load(fh)


def sniff_ext(raw):
    """從檔頭判斷圖檔格式，不信任網址副檔名。"""
    if raw[:3] == b"\xff\xd8\xff":
        return "jpg"
    if raw[:8] == b"\x89PNG\r\n\x1a\n":
        return "png"
    if raw[:6] in (b"GIF87a", b"GIF89a"):
        return "gif"
    if raw[:4] == b"RIFF" and raw[8:12] == b"WEBP":
        return "webp"
    raise ValueError("認不出的圖檔格式，檔頭是 %r" % raw[:8])


def strip_html(s):
    s = re.sub(r"<[^>]+>", "", s or "")
    return re.sub(r"\s+", " ", s).strip()


def license_of(extmeta):
    """回傳 (授權短名, 作者, 是否過閘, 擋下的理由)。"""
    short = strip_html(extmeta.get("LicenseShortName", {}).get("value", ""))
    artist = strip_html(extmeta.get("Artist", {}).get("value", ""))
    if FORBIDDEN.search(short):
        return short, artist, False, "NC／ND 授權，不收"
    if not ALLOWED.search(short):
        return short, artist, False, "認不出是公有領域或可商用 CC，不收"
    return short, artist, True, ""


def credit_line(short, artist):
    """組成簡報 CREDIT 第二欄的字串，格式對齊現有四回。"""
    if re.search(r"public domain|PD", short, re.I):
        return "維基共享資源，公有領域"
    who = ("%s 攝，" % artist) if artist and len(artist) < 40 else ""
    return "%s維基共享資源，%s" % (who, short)


def load_credits():
    if os.path.exists(CREDITS):
        return json.load(io.open(CREDITS, encoding="utf-8"))
    return {}


def save_credits(data):
    io.open(CREDITS, "w", encoding="utf-8").write(
        json.dumps(data, ensure_ascii=False, indent=1, sort_keys=True))


def search_pick(query, want=6):
    """搜尋 Commons，回傳過得了授權閘的候選（檔名, 授權, 寬, 高, 位元組）。"""
    r = api({"action": "query", "format": "json", "list": "search",
             "srnamespace": "6", "srsearch": query, "srlimit": str(want * 3)})
    hits = [x["title"][5:] for x in r.get("query", {}).get("search", [])]
    hits = [h for h in hits if h.lower().rsplit(".", 1)[-1] in ("jpg", "jpeg", "png")]
    if not hits:
        return []
    r2 = api({"action": "query", "format": "json",
              "titles": "|".join("File:" + h for h in hits[:20]),
              "prop": "imageinfo", "iiprop": "url|size|extmetadata"})
    out = []
    for p in r2.get("query", {}).get("pages", {}).values():
        if "imageinfo" not in p:
            continue
        ii = p["imageinfo"][0]
        short, artist, ok, _ = license_of(ii.get("extmetadata", {}))
        if not ok:
            continue
        out.append((p["title"][5:], short, ii.get("width"), ii.get("height"), ii.get("size")))
    return out[:want]


def fetch(batch_names, force=False):
    os.makedirs(IMAGES, exist_ok=True)
    lib = load_credits()
    todo = {}
    for b in batch_names:
        if b not in BATCHES:
            sys.exit("沒有這一批：%s（有的是 %s）" % (b, "、".join(BATCHES)))
        todo.update(BATCHES[b])

    ok = skip = blocked = fail = 0
    for key, (title, desc) in sorted(todo.items()):
        if key in lib and not force:
            print("  跳過 %-14s 已在圖庫" % key)
            skip += 1
            continue
        try:
            r = api({"action": "query", "format": "json",
                     "titles": "File:" + title,
                     "prop": "imageinfo",
                     "iiprop": "url|size|extmetadata",
                     "iiurlwidth": str(MAX_WIDTH)})
            pages = r["query"]["pages"]
            page = list(pages.values())[0]
            if "imageinfo" not in page:
                print("  ✗ %-14s 找不到檔案：%s" % (key, title))
                fail += 1
                continue
            ii = page["imageinfo"][0]
            short, artist, passed, why = license_of(ii.get("extmetadata", {}))
            if not passed:
                print("  ⛔ %-14s %s（%s）" % (key, why, short or "無授權標示"))
                blocked += 1
                continue
            src_url = ii.get("thumburl") or ii["url"]
            req = urllib.request.Request(src_url, headers=UA)
            with urllib.request.urlopen(req, timeout=90) as fh:
                raw = fh.read()
            # 🚨 副檔名要看檔頭，不要看網址：Commons 的 PNG 縮圖網址可能長得像 .jpg，
            #    存錯副檔名會讓 data URI 標成 image/jpeg 卻塞 PNG 位元組。
            ext = sniff_ext(raw)
            fn = "%s.%s" % (key, ext)
            io.open(os.path.join(IMAGES, fn), "wb").write(raw)
            lib[key] = {
                "file": fn,
                "bytes": len(raw),
                "desc": desc,
                "license": credit_line(short, artist),
                "license_raw": short,
                "commons": title,
                "width": ii.get("thumbwidth", ii.get("width")),
            }
            print("  ✓ %-14s %6.0f KB  %s  [%s]" % (key, len(raw) / 1024.0, desc, short))
            ok += 1
            time.sleep(REQUEST_GAP)
        except Exception as exc:                       # noqa: BLE001
            print("  ✗ %-14s %s" % (key, exc))
            fail += 1

    save_credits(lib)
    print("\n收 %d 張，跳過 %d，擋下 %d，失敗 %d；圖庫現有 %d 張"
          % (ok, skip, blocked, fail, len(lib)))
    return fail


def show():
    lib = load_credits()
    if not lib:
        print("圖庫是空的")
        return
    total = sum(v.get("bytes", 0) for v in lib.values())
    print("圖庫 %d 張，共 %.1f MB\n" % (len(lib), total / 1048576.0))
    for k in sorted(lib):
        v = lib[k]
        print("  %-15s %6.0f KB  %-34s %s"
              % (k, v.get("bytes", 0) / 1024.0, v.get("desc", ""), v.get("license", "")))


def audit():
    """重驗每一張的授權字串，並確認檔案真的在。"""
    lib = load_credits()
    bad = 0
    for k in sorted(lib):
        v = lib[k]
        rel = v.get("file", "")
        path = os.path.join(LIB, rel) if "/" in rel else os.path.join(IMAGES, rel)
        if not os.path.exists(path):
            print("  ✗ %-15s 檔案不見了：%s" % (k, v.get("file")))
            bad += 1
            continue
        lic = v.get("license", "") + " " + v.get("license_raw", "")
        if FORBIDDEN.search(lic):
            print("  ⛔ %-15s 授權有問題：%s" % (k, lic))
            bad += 1
    print("\n稽核 %d 張，%d 張有問題" % (len(lib), bad))
    return bad


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fetch", nargs="+", metavar="BATCH",
                    help="要抓的批次，或 all；可用的有 " + "、".join(BATCHES))
    ap.add_argument("--force", action="store_true", help="已在圖庫的也重抓")
    ap.add_argument("--list", action="store_true", help="列出圖庫現況")
    ap.add_argument("--audit", action="store_true", help="重驗授權與檔案")
    ap.add_argument("--search", nargs="+", metavar="QUERY",
                    help="搜尋 Commons 看有什麼可用的（只列出，不下載）")
    a = ap.parse_args()

    if a.search:
        for q in a.search:
            print("【%s】" % q)
            for t, lic, w, h, sz in search_pick(q):
                print("   %-58s %-14s %sx%s" % (t[:58], lic, w, h))
    elif a.list:
        show()
    elif a.audit:
        sys.exit(1 if audit() else 0)
    elif a.fetch:
        batches = list(BATCHES) if a.fetch == ["all"] else a.fetch
        sys.exit(1 if fetch(batches, a.force) else 0)
    else:
        ap.print_help()


if __name__ == "__main__":
    main()
