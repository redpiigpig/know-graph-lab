# -*- coding: utf-8 -*-
"""《宗教系國文講義》簡報用圖的查詢詞與指名清單。

用法：python scripts/course_slide_images.py --course=sl
授權過濾、相關性評分、逐張存檔等機制沿用 course_slide_images.py。
"""

IMAGES_SL = {
    # ── 第 1 次：導論；漢字與最早的書寫 ──
    'oracle-bone': 'Oracle bone script Shang dynasty',
    'bronze-inscription': 'Chinese bronze inscription Western Zhou',
    'shuowen': 'Shuowen Jiezi',
    'seal-script': 'Chinese seal script small seal',
    'clerical-script': 'Cao Quan Stele',
    'chuci': 'Nine Songs Zhang Wo',
    'shanhaijing': 'Shan Hai Jing illustration',
    'sinographic-map': 'East Asian cultural sphere map',

    # ── 第 2 次：經典的成立；佛典漢譯 ──
    'stone-classics': 'Xiping Stone Classics',
    'confucius-temple-stele': 'Confucius temple stele China',
    'kumarajiva': 'Kumarajiva statue Kizil',
    'xuanzang': 'Xuanzang portrait',
    'heart-sutra-calligraphy': 'Heart Sutra calligraphy',
    'dunhuang-sutra-manuscript': 'Dunhuang manuscript Buddhist sutra',

    # ── 第 3 次：大藏經；六朝 ──
    'haeinsa-tripitaka': 'Haeinsa Tripitaka Koreana woodblocks',
    'tripitaka-printing-block': 'Tripitaka Koreana printing block',
    'revolving-sutra-case': 'Rinzo sutra',
    'baopuzi': 'Ge Hong Baopuzi',
    'daoist-talisman': 'Taoist talisman',
    'lanting-preface': 'Lantingji Xu calligraphy',

    # ── 第 4 次：唐代；敦煌變文 ──
    'huineng': 'Huineng Sixth Patriarch painting',
    'hanshan-shide': 'Hanshan Shide painting',
    'mogao-caves': 'Mogao Caves Dunhuang exterior',
    'dunhuang-library-cave': 'Cave 17 Mogao',
    'bianxiang-painting': 'Dunhuang wall painting sutra illustration',
    'baojuan': 'Chinese precious scroll baojuan',

    # ── 第 5 次：戲曲；明清神魔小說 ──
    'nuo-opera-mask': 'Nuo opera mask China',
    'temple-stage': 'Chinese temple theatre stage',
    'kunqu-mudanting': 'Kunqu opera performance',
    'glove-puppet': 'Taiwanese puppet theatre',
    'xiyouji-illustration': 'Journey to the West illustration Ming',
    'fengshen-illustration': 'Fengshen Yanyi',
    'nezha-statue': 'Nezha statue temple Taiwan',

    # ── 第 6 次：日本漢文學；韓半島漢文學 ──
    'nihon-shoki': 'Nihon Shoki',
    'kukai': 'Kukai portrait',
    'gozan-temple': 'Kyoto Zen temple Nanzenji',
    'ikkyu': 'Ikkyu',
    'samguk-yusa': 'Samguk Yusa',
    'choe-chiwon': 'Choe Chiwon',
    'hunminjeongeum': 'Hunminjeongeum Haerye',

    # ── 第 7 次：越南漢文學；台灣漢文學 ──
    'nom-script': 'Chu Nom script Vietnamese',
    'vietnam-stele': 'Temple of Literature Hanoi stele',
    'vietnam-pagoda-inscription': 'Vietnamese pagoda stele inscription',
    'caodai-temple': 'Cao Dai temple Tay Ninh',
    'tainan-confucius-temple': 'Tainan Confucius Temple',
    'taiwan-temple-couplet': 'Longshan Temple Lukang',
    'fortune-poem-slips': 'Chinese fortune sticks temple',
    'taiwan-poetry-society': 'Taiwan Japanese period newspaper',

    # ── 第 8 次：聖經漢譯；去漢字化 ──
    'nestorian-stele': 'Nestorian Stele Xian',
    'matteo-ricci': 'Matteo Ricci portrait',
    'morrison-robert': 'Robert Morrison missionary',
    'chinese-bible': 'Chinese Bible Union Version',
    'pehoeji-text': 'Pe̍h-ōe-jī romanized Taiwanese text',
    'barclay-thomas': 'Barclay missionary',
    'quoc-ngu': 'Gia Dinh Bao',

    # ── 補充：擴充版簡報新增的題材 ──
    'guodian-slips': 'Guodian Chu Slips',
    'mawangdui-silk': 'Mawangdui Silk Texts',
    'diamond-sutra-print': 'Diamond Sutra 868',
    'laozi-riding-ox': 'Laozi riding water buffalo painting',
    'zhuangzi-butterfly': 'Zhuangzi dreaming of a butterfly',
    'zhu-xi': 'Zhu Xi portrait',
    'kojiki': 'Kojiki manuscript',
    'genji-monogatari': 'Tale of Genji illustrated handscroll',
    'kanbun-marks': 'Kanbun kaeriten',
    'mulian-opera': 'Mulian opera performance',
    'temple-couplet-tainan': 'Tainan temple plaque calligraphy',
    'jesuit-china': 'Matteo Ricci and Xu Guangqi',
    'hu-shih': 'Hu Shih portrait',
    'manichaean-temple': 'Cao an Manichaean temple Jinjiang',
    'woodblock-printing': 'Chinese woodblock printing blocks',
    'thread-bound-book': 'Chinese thread bound books stack',
    'stone-rubbing': 'Chinese stele rubbing ink',
}

# 冷門題材：英文查詢詞對不上，直接指名 Commons 檔案。
EXACT_SL = {
    'nestorian-stele': 'File:Nestorian-Stele-Budge-plate-X.jpg',
    'shuowen': 'File:Shuowen.jpg',
}
