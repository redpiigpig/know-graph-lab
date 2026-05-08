"""
2020-2025 龐君華牧師 sermons metadata (per user 2026-05-08).

Used by: sermon_redo.py commit + ad-hoc metadata patches.

Note: 2020-2021 龐只在特別節期講道（聖灰日/受難日/聖誕/平安夜）.
"""

# 2020 special services (no regular 主日 龐 sermons listed by user)
SPECIAL_2020 = [
    {
        "date": "2020-02-26",
        "occasion": "聖灰日禮拜",
        "liturgical_season": "lent",
        "preacher": "龐君華牧師",
        "officiant": "龐君華牧師",
        "司會": "邱泰耀牧師",
        "司琴": "鍾歆宜姊妹",
    },
    {
        "date": "2020-04-10",
        "occasion": "受難日晚崇拜（Service of Tenebrae）",
        "liturgical_season": "lent",
        "preacher": "龐君華會督",
        "officiant": "龐君華會督",
        "襄禮司會": "邱泰耀牧師",
        "司琴": "鍾歆宜、石小凡、盧思寧",
        "領唱": "顧維筠傳道",
        "長笛": "安德石先生",
        "讀經": "黃安妮女士、簡大鈞先生",
        "合唱": "城中牧區詩班",
        "招待": "李幸真女士、楊秀惠女士",
    },
    {
        "date": "2020-12-24",
        "occasion": "衛理公會城中牧區平安夜燭光禮拜",
        "liturgical_season": "advent",
        "preacher": "龐君華會督",
        "officiant": "龐君華會督",
        "襄禮": "邱泰耀牧師",
        "鋼琴": "陳芝英女士、鍾歆宜女士",
        "領唱": "顧維筠女士",
        "指揮": "王微儂女士",
        "司數": "陳香杏女士、李幸真女士",
        "獻招待": "楊秀惠女士、李幸真女士",
        "音光": "林盈君女士",
        "讀經": "黃安妮女士、謝辛美女士、翁嘉慶先生",
        "詩班": "拉喇人歌手、城中牧區詩班",
        "佈置": "陳治旭先生、盧康潔女士",
        "燭台": "周慶同先生、王怡文女士（燭）、黃于庭女士、楊秀惠女士（台）",
    },
]

# 2021 special services (no regular 主日 龐 sermons — 龐 was 衛理會督 still)
SPECIAL_2021 = [
    {
        "date": "2021-02-17",
        "occasion": "聖灰日聯合禮拜",
        "liturgical_season": "lent",
        "preacher": "龐君華牧師",
        "officiant": "龐君華牧師",
        "襄禮": "黃寬裕牧師、邱泰耀牧師、李信政牧師、賴玲牧師",
        "讀經": "彭德全傳道、林裕恩傳道",
        "總務": "林盈君姊妹",
        "司琴": "鍾歆宜姊妹、盧思寧姊妹",
        "獻詩": "城中詩班",
        "接待": "北一區義務傳道",
        "四重唱": "王微儂、何和、林盈君、黃威銘",
        "指揮會前領唱": "王微儂老師",
    },
    {
        "date": "2021-04-02",  # Good Friday 2021
        "occasion": "衛理公會北區聖週五受難日晚聯合崇拜（熄燭禮拜：十架七言）",
        "liturgical_season": "lent",
        "preacher": "龐君華會督",
        "officiant": "龐君華會督",
        "司琴": "連明箴姐妹、盧思寧姊妹",
        "讀經默想": "黃寬裕牧師、邱泰耀牧師、李信政牧師、賴玲牧師、林裕恩傳道、賴明貞傳道、秋郁瑄傳道、侯富寶傳道、顧維筠姊妹、劉世凱弟兄、呂華光弟兄、牛履民弟兄、胡瑠美傳道、羅玉冰姊妹",
        "詩班": "台北衛理堂詩班（陳詩音指揮）、衛理公會城中牧區詩班、La Lay Singers（王微儂指揮）",
        "領唱": "王微儂老師、彭德全傳道",
    },
    {
        "date": "2021-11-20",
        "occasion": "城中教會成立六十週年感恩禮拜",
        "liturgical_season": "pentecost",
        "preacher": "龐君華會督",
        "officiant": "龐君華會督",
        "襄禮": "邱泰耀牧師",
        "司會": "周慶同弟兄",
        "司琴": "盧思寧姊妹",
        "讀經": "黃玲媛姊妹",
        "司獻": "楊秀惠姊妹、黃于庭姊妹",
        "獻詩": "城中牧區詩班",
        "招待": "招待組",
    },
    {
        "date": "2021-12-24",
        "occasion": "衛理公會城中牧區平安夜燭光禮拜",
        "liturgical_season": "advent",
        "preacher": "邱泰耀牧師",  # 龐 主禮, 邱 證道
        "officiant": "龐君華會督",
        "_note": "龐會督主禮, 邱牧師證道",
        "領唱": "顧維筠女士",
        "指揮": "王微儂女士",
        "鋼琴": "盧思寧女士、鍾歆宜女士",
        "司獻": "王怡文女士、周慶同先生、陳香杏女士、李幸真女士",
        "藝術": "陳治旭先生、盧康潔女士",
        "司數": "陳香杏女士、李幸真女士",
        "讀經": "黃安妮女士、黃熙婷女士、卿秀惠女士",
        "詩班": "Lalay Singers、城中牧區詩班",
        "招待": "周慶同先生、王怡文女士（燭）、黃于庭女士、楊秀惠女士（台）",
    },
]


# (date, occasion, liturgical_season, worship_leader, scripture_reader, choir)
# Note: 2022-05 龐會督退休前後. 2022 主日 preaching was less frequent.
SERMONS_2022 = [
    ("2022-06-12", "聖三一主日", "pentecost",
     "周慶同弟兄", "卿秀惠傳道", "城中男聲詩班"),
    ("2022-09-11", "聖靈降臨節後第十四主日", "pentecost",
     "龔祥生弟兄", "卿秀惠傳道", "城中男聲詩班"),
    ("2022-10-02", "聖靈降臨節後第十七主日", "pentecost",
     "周慶同弟兄", "謝辛美姊妹", "城中牧區詩班"),
    ("2022-11-13", "聖靈降臨節後第廿三主日", "pentecost",
     "龔祥生弟兄", "黃安妮姊妹", "城中男聲詩班"),
]

# 2022 special services (multi-role personnel)
SERMON_ASH_WEDNESDAY_2022 = {
    "date": "2022-03-02",
    "occasion": "聖灰日禮拜",
    "liturgical_season": "lent",
    "preacher": "龐君華牧師",
    "officiant": "龐君華牧師",
    "司會": "邱泰耀牧師",
    "司琴": "黃熙婷姊妹",
    "讀經": "簡大鈞弟兄、顧維筠傳道",
}

SERMON_GOOD_FRIDAY_2022 = {
    "date": "2022-04-15",
    "occasion": "聖週五受難日晚崇拜（熄燭禮拜：十架七言）",
    "liturgical_season": "lent",
    "preacher": "龐君華會督",
    "officiant": "龐君華會督",
    "司會": "邱泰耀牧師",
    "司琴": "鍾歆宜女士、盧思寧女士",
    "笛": "安德石先生",
    "攝影": "林盈君女士",
    "讀經": "卿秀惠女士、謝辛美女士",
    "領唱": "王微儂女士",
    "詩班": "城中牧區詩班、Lalay Singers",
    "招待燈光": "李幸真女士",
}

SERMON_CHRISTMAS_EVE_2022 = {
    "date": "2022-12-24",
    "occasion": "衛理公會城中牧區平安夜燭光禮拜",
    "liturgical_season": "advent",
    "preacher": "龐君華牧師",
    "officiant": "邱泰耀牧師",
    "司琴": "鍾歆宜、盧思寧、陳芝英女士",
    "領唱": "顧維筠女士",
    "藝術": "陳治旭先生",
    "指揮": "王微儂女士",
    "司獻": "陳杏杏女士、李幸真女士、周慶同先生、王怡文女士",
    "讀經": "黃雯華女士、卿秀惠女士、簡大鈞先生",
    "點燭": "周慶同先生、王怡文女士（燭）、李幸真女士、楊秀惠女士（台）",
    "詩班": "Lalay Singers、城中牧區詩班",
}

SERMONS_2023 = [
    ("2023-01-08", "主受洗日", "epiphany",
     "龔祥生弟兄", "黃安妮姊妹", "城中男聲詩班"),
    ("2023-02-12", "顯現節後第六主日", "epiphany",
     "龔祥生弟兄", "謝辛美姊妹", "黃威銘弟兄"),
    ("2023-04-09", "復活主日", "easter",
     "龔祥生弟兄", "黃安妮姊妹", "城中牧區詩班"),
    ("2023-05-14", "復活期第六主日", "easter",
     "龔祥生弟兄", "黃安妮姊妹", "盧思寧姊妹"),
    ("2023-06-11", "聖靈降臨節後第二主日", "pentecost",
     "龔祥生弟兄", "黃玲媛姊妹", "城中牧區詩班"),
    ("2023-07-09", "聖靈降臨節後第六主日", "pentecost",
     "龔祥生弟兄", "黃安妮姊妹", "城中牧區詩班"),
    ("2023-07-30", "聖靈降臨節後第九主日", "pentecost",
     "林盈君姊妹", "簡大鈞弟兄", "城中牧區詩班"),
    ("2023-08-27", "聖靈降臨節後第十三主日", "pentecost",
     "卿秀惠傳道", "黃雯華姊妹", "城中小詩班"),
    ("2023-09-17", "聖靈降臨節後第十六主日", "pentecost",
     "楊一梅姊妹", "翁嘉慶弟兄", "盧思寧姊妹"),
    ("2023-10-08", "聖靈降臨節後第十九主日", "pentecost",
     "龔祥生弟兄", "謝辛美姊妹", "城中牧區詩班"),
    ("2023-11-19", "聖靈降臨節後第廿五主日", "pentecost",
     "楊一梅姊妹", "謝辛美姊妹", "城中兒童主日學"),
    ("2023-12-10", "將臨期第二主日", "advent",
     "龔祥生弟兄", "簡大鈞弟兄", "城中牧區詩班"),
]

# 2023-04-07 受難日 special: preacher 龐 only does 默想, 主禮 is 邱
SERMON_GOOD_FRIDAY_2023 = {
    "date": "2023-04-07",
    "occasion": "聖週五受難日晚崇拜（熄燭禮拜：十架七言）",
    "liturgical_season": "lent",
    "preacher": "龐君華牧師",
    "officiant": "邱泰耀牧師",
    "司琴": "鍾歆宜女士、盧思寧女士、陳芝英女士",
    "讀經": "卿秀惠女士、黃安妮女士",
    "攝影": "林盈君女士",
    "領唱": "林吉晉先生",
    "招待燈光": "周慶同先生",
    "詩班": "城中牧區詩班",
    "_note": "龐牧師為默想 (meditation), 不是傳統證道",
}

SERMONS_2024 = [
    ("2024-01-14", "顯現節後第二主日", "epiphany",
     "龔祥生弟兄", "簡大鈞弟兄", "城中衛理幼兒園教師"),
    ("2024-02-11", "登山變相主日", "epiphany",
     "楊一梅姊妹", "翁嘉慶弟兄", "城中四重唱"),
    ("2024-03-10", "大齋期第四主日", "lent",
     "龔祥生弟兄", "謝辛美姊妹", "MYF 學生團契"),
    ("2024-04-14", "復活期第三主日", "easter",
     "龔祥生弟兄", "謝辛美姊妹", "城中四重唱"),
    ("2024-05-12", "復活期第七主日", "easter",
     "龔祥生弟兄", "黃雯華姊妹", "城中牧區詩班"),
    ("2024-06-09", "聖靈降臨節後第三主日", "pentecost",
     "龔祥生弟兄", "簡大鈞弟兄", "城中四重唱"),
    ("2024-07-14", "聖靈降臨節後第八主日", "pentecost",
     "龔祥生弟兄", "翁嘉慶弟兄", "城中四重唱"),
    ("2024-08-11", "聖靈降臨節後第十二主日", "pentecost",
     "龔祥生弟兄", "黃安妮姊妹", "黃威銘弟兄"),
    ("2024-09-08", "聖靈降臨節後第十六主日", "pentecost",
     "龔祥生弟兄", "黃玲媛姊妹", "城中牧區詩班"),
    ("2024-10-13", "聖靈降臨節後第廿一主日", "pentecost",
     "龔祥生弟兄", "黃安妮姊妹", "城中四重唱"),
    ("2024-11-10", "聖靈降臨節後第廿五主日", "pentecost",
     "龔祥生弟兄", "黃雯華姊妹", "城中男聲四重唱"),
    ("2024-12-08", "將臨期第二主日", "advent",
     "龔祥生弟兄", "黃玲媛姊妹", "城中牧區詩班"),
]

SERMONS_2025 = [
    ("2025-01-12", "顯現節後第一主日（主受洗日）", "epiphany",
     "龔祥生弟兄", "黃玲媛姊妹", "林盈君姊妹", "龐君華牧師"),
    ("2025-02-09", "顯現節後第五主日", "epiphany",
     "周慶同弟兄", "黃雯華姊妹", "城中牧區詩班", "龐君華牧師"),
    ("2025-03-09", "大齋期第一主日", "lent",
     "龔祥生弟兄", "黃玲媛姊妹", "城中牧區詩班", "龐君華牧師"),
    ("2025-04-13", "棕樹主日", "lent",
     "龔祥生弟兄", "黃玲媛姊妹", "MYF 學生團契", "龐君華牧師"),
    ("2025-05-11", "復活期第四主日", "easter",
     "龔祥生弟兄", "黃雯華姊妹", "城中牧區詩班", "龐君華牧師"),
    ("2025-06-08", "聖靈降臨節", "pentecost",
     "龔祥生弟兄", "黃玲媛姊妹", "城中四重唱", "龐君華牧師"),
    ("2025-07-13", "聖靈降臨節後第五主日", "pentecost",
     "龔祥生弟兄", "簡大鈞弟兄", "城中牧區詩班", "龐君華牧師"),
    ("2025-08-10", "聖靈降臨節後第九主日", "pentecost",
     "龔祥生弟兄", "謝辛美姊妹", "城中牧區詩班", "龐君華牧師"),
    ("2025-09-14", "聖靈降臨節後第十四主日", "pentecost",
     "龔祥生弟兄", "黃雯華姊妹", "城中牧區詩班", "龐君華牧師"),
    ("2025-10-12", "聖靈降臨節後第十八主日", "pentecost",
     "龔祥生弟兄", "黃安妮姊妹", "城中牧區詩班", "龐君華牧師"),
    ("2025-11-09", "聖靈降臨節後第廿二主日", "pentecost",
     "龔祥生弟兄", "黃安妮姊妹", "城中四重唱", "龐君華牧師"),
    # 2025-12-14: 主禮 = 邱泰耀, 證道 = 龐
    ("2025-12-14", "將臨期第三主日", "advent",
     "龔祥生弟兄", "黃玲媛姊妹", "城中小詩班", "邱泰耀牧師"),
]

# 平安夜 (Christmas Eve candlelight service) — special structure with multiple roles
SERMON_CHRISTMAS_EVE_2025 = {
    "date": "2025-12-24",
    "occasion": "衛理公會城中牧區平安夜燭光禮拜",
    "liturgical_season": "advent",
    "preacher": "龐君華牧師",
    "officiant": "邱泰耀牧師",
    "司琴": "盧思寧女士",
    "藝術": "陳治旭先生",
    "獻曲": "安德石先生",
    "讀經": "翁嘉慶先生、謝辛美女士、卿秀惠女士",
    "點燭": "周慶同先生、袁淑靜女士（燭）、黃于庭女士、楊秀惠女士（台）",
    "司獻": "陳杏杏女士、曾慧如女士",
    "領唱": "林吉晉先生",
    "指揮": "王微儂女士",
    "詩班": "城中牧區詩班",
}


METADATA = {}
for d, occasion, season, leader, reader, choir in SERMONS_2023 + SERMONS_2024:
    METADATA[d] = {
        "occasion": occasion,
        "liturgical_season": season,
        "worship_leader": leader,
        "scripture_reader": reader,
        "choir": choir,
        "officiant": "龐君華牧師",
        "preacher": "龐君華牧師",
    }

# 2023 受難日 — 龐 默想 + 邱 主禮, multi-role personnel in worship_team
gf = SERMON_GOOD_FRIDAY_2023
METADATA[gf["date"]] = {
    "occasion": gf["occasion"],
    "liturgical_season": gf["liturgical_season"],
    "preacher": gf["preacher"],
    "officiant": gf["officiant"],
    "scripture_reader": gf["讀經"],
    "choir": gf["詩班"],
    "worship_team": {
        "司琴": gf["司琴"],
        "讀經": gf["讀經"],
        "攝影": gf["攝影"],
        "領唱": gf["領唱"],
        "招待/燈光": gf["招待燈光"],
        "_note": gf["_note"],
    },
}

for d, occasion, season, leader, reader, choir, officiant in SERMONS_2025:
    METADATA[d] = {
        "occasion": occasion,
        "liturgical_season": season,
        "worship_leader": leader,
        "scripture_reader": reader,
        "choir": choir,
        "officiant": officiant,
        "preacher": "龐君華牧師",
    }

# Christmas Eve has different fields — store extra info in worship_team JSON
ce = SERMON_CHRISTMAS_EVE_2025
METADATA[ce["date"]] = {
    "occasion": ce["occasion"],
    "liturgical_season": ce["liturgical_season"],
    "preacher": ce["preacher"],
    "officiant": ce["officiant"],
    "worship_leader": ce["司獻"],  # 司獻
    "scripture_reader": ce["讀經"],
    "choir": ce["詩班"],
    "worship_team": {
        "司琴": ce["司琴"],
        "藝術": ce["藝術"],
        "獻曲": ce["獻曲"],
        "點燭": ce["點燭"],
        "司獻": ce["司獻"],
        "領唱": ce["領唱"],
        "指揮": ce["指揮"],
    },
}


def _special_to_meta(s):
    """Convert a special-service dict into pong_sermons fields.

    Maps known fields (司會/讀經/詩班/獻詩) into structured columns,
    everything else goes into worship_team JSON.
    """
    KNOWN = {"date", "occasion", "liturgical_season", "preacher", "officiant"}
    out = {
        "occasion": s["occasion"],
        "liturgical_season": s["liturgical_season"],
        "preacher": s["preacher"],
        "officiant": s["officiant"],
    }
    if "司會" in s:
        out["worship_leader"] = s["司會"]
    if "讀經" in s:
        out["scripture_reader"] = s["讀經"]
    if "詩班" in s:
        out["choir"] = s["詩班"]
    elif "獻詩" in s:
        out["choir"] = s["獻詩"]
    elif "合唱" in s:
        out["choir"] = s["合唱"]
    # Everything else goes to worship_team JSON
    extras = {k: v for k, v in s.items() if k not in KNOWN | {"司會", "讀經", "詩班", "獻詩", "合唱"}}
    if extras:
        out["worship_team"] = extras
    return out


# Wire 2022 specials + regular sermons
for d, occasion, season, leader, reader, choir in SERMONS_2022:
    METADATA[d] = {
        "occasion": occasion,
        "liturgical_season": season,
        "worship_leader": leader,
        "scripture_reader": reader,
        "choir": choir,
        "officiant": "龐君華牧師",
        "preacher": "龐君華牧師",
    }

for s in [SERMON_ASH_WEDNESDAY_2022, SERMON_GOOD_FRIDAY_2022, SERMON_CHRISTMAS_EVE_2022]:
    METADATA[s["date"]] = _special_to_meta(s)

# Wire 2020-2021 specials (no regular 主日 龐 sermons)
for s in SPECIAL_2020 + SPECIAL_2021:
    METADATA[s["date"]] = _special_to_meta(s)
