-- ============================================================
-- 創世記族譜人物年代更新 — 創造紀元（Anno Mundi）換算
-- 依據：馬所拉文本（MT）族譜數字，烏雪年表（Ussher Chronology）
--   創造紀元 AM 0 ≈ 主前 4004 年（BC 4004）
--   換算公式：主前年份 = 4004 − AM年
--   birth_year 以負數表示主前（例：-4004 = 主前 4004 年）
-- 注意：此為其中一種聖經年代推算法，學術界對確切年份有不同意見
-- ============================================================

-- ── 第一節：洪水前族譜（創世記 5章）────────────────────────

-- 亞當：AM 0，壽 930，逝 AM 930
UPDATE biblical_people SET birth_year = -4004, death_year = -3074 WHERE name_zh = '亞當';

-- 夏娃：創造紀元與亞當同期，確切年份未記載
UPDATE biblical_people SET birth_year = -4004 WHERE name_zh = '夏娃';

-- 塞特：AM 130（亞當 130 歲所生），壽 912，逝 AM 1042
UPDATE biblical_people SET birth_year = -3874, death_year = -2962 WHERE name_zh = '塞特';

-- 以挪士：AM 235，壽 905，逝 AM 1140
UPDATE biblical_people SET birth_year = -3769, death_year = -2864 WHERE name_zh = '以挪士';

-- 該南：AM 325，壽 910，逝 AM 1235
UPDATE biblical_people SET birth_year = -3679, death_year = -2769 WHERE name_zh = '該南';

-- 瑪哈拉利：AM 395，壽 895，逝 AM 1290
UPDATE biblical_people SET birth_year = -3609, death_year = -2714 WHERE name_zh = '瑪哈拉利';

-- 雅列：AM 460，壽 962，逝 AM 1422
UPDATE biblical_people SET birth_year = -3544, death_year = -2582 WHERE name_zh = '雅列';

-- 以諾（雅列之子）：AM 622，壽/被取 365，AM 987 被神取去（非死亡）
UPDATE biblical_people SET birth_year = -3382, death_year = -3017 WHERE name_zh = '以諾（雅列之子）';

-- 瑪土撒拉：AM 687，壽 969，逝 AM 1656（大洪水當年）
UPDATE biblical_people SET birth_year = -3317, death_year = -2348 WHERE name_zh = '瑪土撒拉';

-- 拉麥（挪亞之父）：AM 874，壽 777，逝 AM 1651（洪水前 5 年）
UPDATE biblical_people SET birth_year = -3130, death_year = -2353 WHERE name_zh = '拉麥（挪亞之父）';

-- 挪亞：AM 1056，壽 950，逝 AM 2006
-- 大洪水：AM 1656（挪亞 600 歲）= 主前 2348 年
UPDATE biblical_people SET birth_year = -2948, death_year = -1998 WHERE name_zh = '挪亞';

-- ── 第二節：洪水後族譜（創世記 11章）────────────────────────
-- 大洪水：AM 1656 = 主前 2348 年

-- 閃：AM 1558（挪亞 502 歲所生），壽 600，逝 AM 2158
--（創 11:10：洪水後 2 年閃 100 歲，故閃生於 AM 1558）
UPDATE biblical_people SET birth_year = -2446, death_year = -1846 WHERE name_zh = '閃';

-- 亞法撒：AM 1658（洪水後 2 年閃 100 歲所生），壽 438，逝 AM 2096
UPDATE biblical_people SET birth_year = -2346, death_year = -1908 WHERE name_zh = '亞法撒';

-- 沙拉：AM 1693（亞法撒 35 歲所生），壽 433，逝 AM 2126
UPDATE biblical_people SET birth_year = -2311, death_year = -1878 WHERE name_zh = '沙拉';

-- 希伯：AM 1723（沙拉 30 歲所生），壽 464，逝 AM 2187
UPDATE biblical_people SET birth_year = -2281, death_year = -1817 WHERE name_zh = '希伯';

-- 法勒：AM 1757（希伯 34 歲所生），壽 239，逝 AM 1996
UPDATE biblical_people SET birth_year = -2247, death_year = -2008 WHERE name_zh = '法勒';

-- 拉吳：AM 1787（法勒 30 歲所生），壽 239，逝 AM 2026
UPDATE biblical_people SET birth_year = -2217, death_year = -1978 WHERE name_zh = '拉吳';

-- 西鹿：AM 1819（拉吳 32 歲所生），壽 230，逝 AM 2049
UPDATE biblical_people SET birth_year = -2185, death_year = -1955 WHERE name_zh = '西鹿';

-- 拿鶴（西鹿之子）：AM 1849（西鹿 30 歲所生），壽 148，逝 AM 1997
UPDATE biblical_people SET birth_year = -2155, death_year = -2007 WHERE name_zh = '拿鶴（西鹿之子）';

-- 他拉：AM 1878（拿鶴 29 歲所生），壽 205，逝 AM 2083
UPDATE biblical_people SET birth_year = -2126, death_year = -1921 WHERE name_zh = '他拉';

-- ── 第三節：亞伯拉罕家族（創世記 11-25章）────────────────
-- 注意：亞伯拉罕生年有兩種推算
--   MT直算：他拉 70 歲 → AM 1948 = 主前 2056 年
--   使徒行傳 7:4 推算：他拉 130 歲 → AM 2008 = 主前 1996 年（烏雪採用）
-- 此處採烏雪年表（AM 2008）

-- 亞伯拉罕：AM 2008，壽 175，逝 AM 2183
UPDATE biblical_people SET birth_year = -1996, death_year = -1821 WHERE name_zh = '亞伯拉罕';

-- 撒拉：比亞伯拉罕小 10 歲（創 17:17），壽 127（創 23:1），逝 AM 2145
UPDATE biblical_people SET birth_year = -1986, death_year = -1859 WHERE name_zh = '撒拉';

-- 以撒：亞伯拉罕 100 歲所生（創 21:5），AM 2108，壽 180（創 35:28），逝 AM 2288
UPDATE biblical_people SET birth_year = -1896, death_year = -1716 WHERE name_zh = '以撒';

-- 利百加：生年不詳，約與以撒同期
-- （以撒娶利百加時 40 歲，AM 2148 約 = 主前 1856 年）
UPDATE biblical_people SET birth_year = -1856 WHERE name_zh = '利百加';

-- 以掃、雅各：以撒 60 歲所生（創 25:26），AM 2168
-- 雅各壽 147（創 47:28），逝 AM 2315
UPDATE biblical_people SET birth_year = -1836, death_year = -1689 WHERE name_zh = '雅各';
UPDATE biblical_people SET birth_year = -1836 WHERE name_zh = '以掃';

-- 以實瑪利：亞伯拉罕 86 歲所生（創 16:16），AM 2094，壽 137（創 25:17），逝 AM 2231
UPDATE biblical_people SET birth_year = -1910, death_year = -1773 WHERE name_zh = '以實瑪利';

-- 夏甲：生年不詳，約主前 2000 年前後
UPDATE biblical_people SET birth_year = -2000 WHERE name_zh = '夏甲';

-- 羅得：生年不詳，約與亞伯拉罕同期，比亞伯拉罕稍晚
UPDATE biblical_people SET birth_year = -1960 WHERE name_zh = '羅得';

-- ============================================================
-- 同時更新出生年備注（說明年代推算依據）
-- ============================================================
UPDATE biblical_people
  SET notes = CASE
    WHEN notes IS NULL OR notes = '' THEN '年代依馬所拉文本族譜、烏雪年表推算（AM→BC）'
    ELSE notes || chr(10) || '年代依馬所拉文本族譜、烏雪年表推算（AM→BC）'
  END
WHERE name_zh IN (
  '亞當','夏娃','塞特','以挪士','該南','瑪哈拉利','雅列',
  '以諾（雅列之子）','瑪土撒拉','拉麥（挪亞之父）','挪亞',
  '閃','亞法撒','沙拉','希伯','法勒','拉吳','西鹿',
  '拿鶴（西鹿之子）','他拉','亞伯拉罕','撒拉','以撒','雅各','以掃','以實瑪利'
);
