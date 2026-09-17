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
        path = os.path.join(IMAGES, v.get("file", ""))
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
    a = ap.parse_args()

    if a.list:
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
