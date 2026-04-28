-- ================================================================
-- 和合本2010 譯名更新 + 多名人物備注
-- 參考：Genesis 35/36/46; Exodus 6; Numbers 13/26
-- ================================================================

-- ──────────────────────────────────────────────────────────────
-- 第一部分：更名（依族群整理）
-- 重要：先改有歧義的名字（如 以謝→耶色）再改同名者（以謝→以察）
-- ──────────────────────────────────────────────────────────────

-- 〔拿弗他利支派〕先改，避免與西珥族 以謝→以察 混淆
UPDATE biblical_people SET name_zh = '耶色（拿弗他利之子）' WHERE name_zh = '以謝（拿弗他利之子）';

-- 〔流便支派〕
UPDATE biblical_people SET name_zh = '呂便' WHERE name_zh = '流便';
UPDATE biblical_people SET name_zh = '哈諾（呂便之子）'  WHERE name_zh = '哈諾各（流便之子）';
UPDATE biblical_people SET name_zh = '希斯倫（呂便之子）' WHERE name_zh = '希斯崙（流便之子）';
UPDATE biblical_people SET name_zh = '迦米（呂便之子）'  WHERE name_zh = '迦米（流便之子）';
-- 以利押之子亞比蘭：以利押 children 欄已改為「呂便後裔」，需同步改名
UPDATE biblical_people SET name_zh = '亞比蘭（呂便後裔）' WHERE name_zh = '亞比蘭（流便後裔）';
-- 法路之子以利押代數正確，無需更名

-- 〔西緬支派〕
UPDATE biblical_people SET name_zh = '阿轄（西緬之子）' WHERE name_zh = '俄哈得（西緬之子）';
UPDATE biblical_people SET name_zh = '阿轄'              WHERE name_zh = '俄哈得'; -- 若有短名記錄

-- 〔以薩迦支派〕
UPDATE biblical_people SET name_zh = '雅述（以薩迦之子）' WHERE name_zh = '雅書比（以薩迦之子）';
UPDATE biblical_people SET name_zh = '雅述'               WHERE name_zh = '雅書比'; -- 若有短名記錄

-- 〔西布倫支派〕
UPDATE biblical_people SET name_zh = '雅利（西布倫之子）' WHERE name_zh = '雅利勒（西布倫之子）';
UPDATE biblical_people SET name_zh = '雅利'               WHERE name_zh = '雅利勒'; -- 若有短名記錄

-- 〔迦得支派〕
UPDATE biblical_people SET name_zh = '洗非芸（迦得之子）' WHERE name_zh = '洗奉（迦得之子）';
UPDATE biblical_people SET name_zh = '洗非芸'             WHERE name_zh = '洗奉'; -- 若有短名記錄
UPDATE biblical_people SET name_zh = '亞羅底（迦得之子）' WHERE name_zh = '亞羅德（迦得之子）';
UPDATE biblical_people SET name_zh = '亞羅底'             WHERE name_zh = '亞羅德'; -- 若有短名記錄

-- 〔亞設支派〕
UPDATE biblical_people SET name_zh = '希別（亞設之孫）' WHERE name_zh = '希伯（亞設之孫）';
-- 注意：勿改 希伯（以伯，第14代閃族長）— 原 catch-all 已刪除

-- 〔但支派〕
UPDATE biblical_people SET name_zh = '書含（但之子）' WHERE name_zh = '戶心（但之子）';
UPDATE biblical_people SET name_zh = '書含'           WHERE name_zh = '戶心'; -- 若有短名記錄

-- 〔拿弗他利支派〕（耶色已改，繼續改示稜）
UPDATE biblical_people SET name_zh = '示冷（拿弗他利之子）' WHERE name_zh = '示稜（拿弗他利之子）';
UPDATE biblical_people SET name_zh = '示冷'                 WHERE name_zh = '示稜'; -- 若有短名記錄

-- 〔便雅憫支派〕
UPDATE biblical_people SET name_zh = '乃幔（便雅憫之子）' WHERE name_zh = '拿艾（便雅憫之子）';
UPDATE biblical_people SET name_zh = '以希（便雅憫之子）' WHERE name_zh = '亞希（便雅憫之子）';
UPDATE biblical_people SET name_zh = '羅實（便雅憫之子）' WHERE name_zh = '羅示（便雅憫之子）';
UPDATE biblical_people SET name_zh = '羅實'               WHERE name_zh = '羅示'; -- 短名記錄
UPDATE biblical_people SET name_zh = '母平（便雅憫之子）' WHERE name_zh = '母辟（便雅憫之子）';
UPDATE biblical_people SET name_zh = '拿艾'               WHERE name_zh = '拿艾'; -- 實為短名，下面已改
UPDATE biblical_people SET name_zh = '亞勒（比拉之子）'   WHERE name_zh = '亞珥得（比拉之子）';
UPDATE biblical_people SET name_zh = '亞勒'               WHERE name_zh = '亞珥得'; -- 若有短名記錄

-- 〔以法蓮支派〕
UPDATE biblical_people SET name_zh = '書提拉（以法蓮之子）' WHERE name_zh = '書鐵拉（以法蓮之子）';
UPDATE biblical_people SET name_zh = '他罕（以法蓮之子）'   WHERE name_zh = '大罕（以法蓮之子）';
UPDATE biblical_people SET name_zh = '以蘭（書提拉之子）'   WHERE name_zh = '以蘭（書鐵拉之子）';

-- 〔瑪拿西後裔〕
UPDATE biblical_people SET name_zh = '密迦（洗羅非哈之女）' WHERE name_zh = '米迦（洗羅非哈之女）';

-- 〔以利法之子（亞瑪力族）〕
UPDATE biblical_people SET name_zh = '阿抹' WHERE name_zh = '俄瑪';
UPDATE biblical_people SET name_zh = '洗玻' WHERE name_zh = '洗弗';
UPDATE biblical_people SET name_zh = '迦坦' WHERE name_zh = '迦頓';
UPDATE biblical_people SET name_zh = '基納斯' WHERE name_zh = '基拿斯';

-- 〔流珥（以掃之子）的兒子〕
UPDATE biblical_people SET name_zh = '拿哈' WHERE name_zh = '拿轄';

-- 〔西珥族〕
UPDATE biblical_people SET name_zh = '羅坍' WHERE name_zh = '羅單';
UPDATE biblical_people SET name_zh = '亭納（以利法的妾）' WHERE name_zh = '亭拿（以利法的妾）';
-- 西珥之子 以謝（gen=22）→ 以察（不要改到耶色（拿弗他利之子））
UPDATE biblical_people SET name_zh = '以察' WHERE name_zh = '以謝' AND generation IS NOT NULL AND generation <= 25 AND children LIKE '%比利罕%';
-- 以察之孫 亞干更名
UPDATE biblical_people SET name_zh = '亞干（以察之子）' WHERE name_zh = '亞干（以謝之子）';

-- 〔以東王〕
UPDATE biblical_people SET name_zh = '桑拉'             WHERE name_zh = '薩拉';
UPDATE biblical_people SET name_zh = '巴勒‧哈南（亞革波之子）' WHERE name_zh = '巴力哈南（亞革波之子）';
UPDATE biblical_people SET name_zh = '哈達爾（以東末王）' WHERE name_zh = '哈達（以東末王）';

-- 〔十二探子〕
UPDATE biblical_people SET name_zh = '沙母亞（沙刻之子）' WHERE name_zh = '撒母亞（撒刻之子）';
UPDATE biblical_people SET name_zh = '以迦（約色之子）'   WHERE name_zh = '以迦勒（約瑟之子）';
UPDATE biblical_people SET name_zh = '迦疊（梭底之子）'   WHERE name_zh = '迦底業（索底之子）';
UPDATE biblical_people SET name_zh = '迦底（穌西之子）'   WHERE name_zh = '迦底（書西之子）';
UPDATE biblical_people SET name_zh = '西帖（米迦勒之子）' WHERE name_zh = '西突（米迦勒之子）';
UPDATE biblical_people SET name_zh = '拿比（縛西之子）'   WHERE name_zh = '拿比（沃甫西之子）';
UPDATE biblical_people SET name_zh = '臼利（瑪基之子）'   WHERE name_zh = '基利勒（瑪基之子）';

-- 〔摩西岳父〕
UPDATE biblical_people SET name_zh = '葉特羅', notes = '米甸祭司，摩西岳父；出埃及記 2:18 稱之為流珥，3:1 及18章稱葉特羅'
  WHERE name_zh = '葉忒羅';

-- 〔哥轄族〕
UPDATE biblical_people SET name_zh = '希伯倫（哥轄之子）' WHERE name_zh = '希伯崙（哥轄之子）';

-- ──────────────────────────────────────────────────────────────
-- 第二部分：更新各人的 children 欄位（同步改名）
-- ──────────────────────────────────────────────────────────────

-- 雅各 children 中的流便 → 呂便
UPDATE biblical_people SET children = REPLACE(children, '流便', '呂便') WHERE children LIKE '%流便%';

-- 呂便 children：清除重複，統一用全名
UPDATE biblical_people SET children = '哈諾（呂便之子）、法路、希斯倫（呂便之子）、迦米（呂便之子）'
  WHERE name_zh = '呂便';

-- 法路 children 更新（法路之子是以利押，名字未改）
-- 法路→以利押 已正確，不需修改

-- 西緬 children：移除重複，更新阿轄
UPDATE biblical_people SET children = '耶母利、雅憫（西緬之子）、阿轄（西緬之子）、雅斤（西緬之子）、瑣轄（西緬之子）、掃羅（西緬之子）'
  WHERE name_zh = '西緬';

-- 利未 children：修正重複
UPDATE biblical_people SET children = '革順（利未之子）、哥轄、米拉利（利未之子）'
  WHERE name_zh = '利未';

-- 猶大 children：更新（已含正確名稱）
UPDATE biblical_people SET children = '珥（猶大之子）、俄南（猶大之子）、示拉（猶大之子）、法勒斯、謝拉（猶大之子）'
  WHERE name_zh = '猶大';

-- 以薩迦 children：清除重複，更新雅述
UPDATE biblical_people SET children = '陀拉（以薩迦之子）、普瓦、雅述（以薩迦之子）、伸崙（以薩迦之子）'
  WHERE name_zh = '以薩迦';

-- 西布倫 children：清除重複，更新雅利
UPDATE biblical_people SET children = '西烈（西布倫之子）、以倫（西布倫之子）、雅利（西布倫之子）'
  WHERE name_zh = '西布倫';

-- 約瑟 children：無需更改
UPDATE biblical_people SET children = '瑪拿西（約瑟之子）、以法蓮（約瑟之子）'
  WHERE name_zh = '約瑟';

-- 便雅憫 children：清除重複，更新全部
UPDATE biblical_people SET children = '比拉（便雅憫之子）、比結（便雅憫之子）、亞實別（便雅憫之子）、基拉（便雅憫之子）、乃幔（便雅憫之子）、以希（便雅憫之子）、羅實（便雅憫之子）、母平（便雅憫之子）、戶平（便雅憫之子）、亞勒（比拉之子）'
  WHERE name_zh = '便雅憫';

-- 但 children：更新書含
UPDATE biblical_people SET children = '書含（但之子）' WHERE name_zh = '但';

-- 亞設 children：清除重複，更新希別
UPDATE biblical_people SET children = '音拿（亞設之子）、亦施瓦、亦施韋、比利亞（亞設之子）、西拉（亞設之女）'
  WHERE name_zh = '亞設';

-- 比利亞（亞設之子）children：更新希別
UPDATE biblical_people SET children = '希別（亞設之孫）、瑪結（亞設之孫）'
  WHERE name_zh = '比利亞（亞設之子）';

-- 拿弗他利 children：清除重複，更新耶色、示冷
UPDATE biblical_people SET children = '雅薛（拿弗他利之子）、沽尼（拿弗他利之子）、耶色（拿弗他利之子）、示冷（拿弗他利之子）'
  WHERE name_zh = '拿弗他利';

-- 迦得 children：清除重複，更新洗非芸、亞羅底
UPDATE biblical_people SET children = '洗非芸（迦得之子）、哈基、書尼（迦得之子）、以斯本（迦得之子）、以利（迦得之子）、亞羅底（迦得之子）、亞列利（迦得之子）'
  WHERE name_zh = '迦得';

-- 比拉（便雅憫之子）children：更新亞勒
UPDATE biblical_people SET children = '亞勒（比拉之子）、乃幔（便雅憫之子）'
  WHERE name_zh = '比拉（便雅憫之子）';

-- 以法蓮 children：更新書提拉、他罕
UPDATE biblical_people SET children = '書提拉（以法蓮之子）、比結（以法蓮之子）、他罕（以法蓮之子）'
  WHERE name_zh = '以法蓮（約瑟之子）';

-- 書提拉 children：更新父名
UPDATE biblical_people SET children = '以蘭（書提拉之子）'
  WHERE name_zh = '書提拉（以法蓮之子）';

-- 以利法 children：更新阿抹、洗玻、迦坦、基納斯
UPDATE biblical_people SET children = '提幔、阿抹、洗玻、迦坦、基納斯、亞瑪力'
  WHERE name_zh = '以利法（以掃之子）';

-- 流珥（以掃之子）children：更新拿哈
UPDATE biblical_people SET children = '拿哈、謝拉（流珥之子）、沙瑪、米撒'
  WHERE name_zh = '流珥（以掃之子）';

-- 巴實抹（以實瑪利之女）children：仍是流珥（以掃之子），無需改
-- 巴實抹 children 更新：她是流珥（以掃之子）的母親
UPDATE biblical_people SET children = '流珥（以掃之子）'
  WHERE name_zh = '巴實抹（以實瑪利之女）';

-- 西珥 children：更新羅坍、以察，清除重複
UPDATE biblical_people SET children = '羅坍、朔巴（西珥之子）、祭便、亞拿（西珥之子）、底順（西珥之子）、以察、底珊'
  WHERE name_zh = '西珥';

-- 以察 children：更新（以謝→以察 已改，此處更新 children）
UPDATE biblical_people SET children = REPLACE(children, '以謝', '以察')
  WHERE name_zh = '以察';

-- 羅坍 children：保持現狀（何里（羅坍之子）、黑幔）
UPDATE biblical_people SET children = '何里（羅坍之子）、黑幔'
  WHERE name_zh = '羅坍';
-- 更新 何里（羅單之子） → 何里（羅坍之子）
UPDATE biblical_people SET name_zh = '何里（羅坍之子）' WHERE name_zh = '何里（羅單之子）';

-- 洗羅非哈 children：更新密迦
UPDATE biblical_people SET children = '瑪拉（洗羅非哈之女）、挪阿（洗羅非哈之女）、曷拉、密迦（洗羅非哈之女）、得撒（洗羅非哈之女）'
  WHERE name_zh = '洗羅非哈';

-- 基列 children：移除重複
UPDATE biblical_people SET children = '以謝珥、希勒（基列之子）、亞斯列（基列之子）、示劍（基列之子）、示米大（基列之子）、希弗（基列之子）'
  WHERE name_zh = '基列（瑪吉之子）';

-- 葉特羅 children：保持（西坡拉）
UPDATE biblical_people SET children = '西坡拉' WHERE name_zh = '葉特羅';

-- 摩西 children：保持
-- 西坡拉 children：保持

-- ──────────────────────────────────────────────────────────────
-- 第三部分：名字中含「流便」的更新
-- ──────────────────────────────────────────────────────────────
UPDATE biblical_people SET children = REPLACE(children, '以謝（拿弗他利之子）', '耶色（拿弗他利之子）')
  WHERE children LIKE '%以謝（拿弗他利之子）%';
UPDATE biblical_people SET children = REPLACE(children, '以謝珥', 'PLACEHOLDER_YIEZER')
  WHERE children LIKE '%以謝珥%'; -- 保護 以謝珥（基列之子），這不是 Jezer
UPDATE biblical_people SET children = REPLACE(children, 'PLACEHOLDER_YIEZER', '以謝珥')
  WHERE children LIKE '%PLACEHOLDER_YIEZER%';

-- ──────────────────────────────────────────────────────────────
-- 第四部分：多名備注
-- ──────────────────────────────────────────────────────────────

-- 以掃/以東
UPDATE biblical_people SET notes = COALESCE(notes || '；', '') || '又名以東（創世記 36:1）'
  WHERE name_zh = '以掃' AND (notes IS NULL OR notes NOT LIKE '%以東%');

-- 亞伯蘭/亞伯拉罕（若 name_zh 是亞伯拉罕）
UPDATE biblical_people SET notes = COALESCE(notes || '；', '') || '原名亞伯蘭（創世記 17:5）'
  WHERE name_zh = '亞伯拉罕' AND (notes IS NULL OR notes NOT LIKE '%亞伯蘭%');

-- 撒萊/撒拉
UPDATE biblical_people SET notes = COALESCE(notes || '；', '') || '原名撒萊（創世記 17:15）'
  WHERE name_zh = '撒拉' AND (notes IS NULL OR notes NOT LIKE '%撒萊%');

-- 雅各/以色列
UPDATE biblical_people SET notes = COALESCE(notes || '；', '') || '後改名以色列（創世記 32:28）'
  WHERE name_zh = '雅各' AND (notes IS NULL OR notes NOT LIKE '%以色列%');

-- 何西阿/約書亞（十二探子中的約書亞）
UPDATE biblical_people SET notes = COALESCE(notes, '') || '原名何西阿（民數記 13:8），摩西為他改名約書亞（民數記 13:16）'
  WHERE name_zh = '約書亞（嫩之子）' AND (notes IS NULL OR notes = '');

-- 流珥/葉特羅（葉特羅記錄的備注已在第一部分更新）
