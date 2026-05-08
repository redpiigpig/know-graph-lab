"""
2023-2025 龐君華牧師 sermons metadata (per user 2026-05-08).

Used by: sermon_redo.py commit + ad-hoc metadata patches.
"""

# (date, occasion, liturgical_season, worship_leader, scripture_reader, choir)
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
