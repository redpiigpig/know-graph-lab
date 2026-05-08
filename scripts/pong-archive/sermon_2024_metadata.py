"""
2024 龐君華牧師 sermons metadata (per user 2026-05-08).

Used by: sermon_redo.py commit + ad-hoc metadata patches.
"""

# (date, occasion, liturgical_season, worship_leader, scripture_reader, choir)
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

METADATA = {
    d: {
        "occasion": occasion,
        "liturgical_season": season,
        "worship_leader": leader,
        "scripture_reader": reader,
        "choir": choir,
        "officiant": "龐君華牧師",
        "preacher": "龐君華牧師",
    }
    for d, occasion, season, leader, reader, choir in SERMONS_2024
}
