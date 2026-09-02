# -*- coding: utf-8 -*-
"""《基督宗教概論》簡報用圖的查詢詞與指名清單。

用法：python scripts/course_slide_images.py --course=ch
授權過濾、相關性評分、逐張存檔等機制沿用 course_slide_images.py。
"""

IMAGES_CH = {
    # ── 第 1 次：四項核心傳統；拿撒勒人耶穌 ──
    'st-peters-square': 'Saint Peters Basilica',
    'orthodox-liturgy': 'Orthodox Divine Liturgy service',
    'ethiopian-church': 'Lalibela rock hewn church',
    'protestant-interior': 'Protestant church interior pulpit',
    'pentecostal-worship': 'Pentecostal worship service',
    'sea-of-galilee': 'Sea of Galilee landscape',
    'dead-sea-scrolls': 'Great Isaiah Scroll Dead Sea Scrolls',
    'papyrus-p52': 'Rylands Library Papyrus P52',
    'josephus': 'Flavius Josephus engraving',
    'crucifixion-icon': 'Crucifixion icon Byzantine',

    # ── 第 2 次：初代教會；正典的形成 ──
    'catacomb-fresco': 'Catacomb of Priscilla fresco',
    'ichthys-symbol': 'Ichthys early Christian symbol',
    'good-shepherd': 'Good Shepherd early Christian art',
    'paul-apostle': 'Saint Paul apostle painting',
    'roman-road': 'Roman road Appian Way',
    'codex-sinaiticus': 'Codex Sinaiticus manuscript',
    'codex-vaticanus': 'Codex Vaticanus page',
    'nag-hammadi': 'Nag Hammadi codices',
    'vulgate-manuscript': 'Vulgate Bible manuscript illuminated',
    'gutenberg-bible': 'Gutenberg Bible page',

    # ── 第 3 次：兩千年的讀法；大公會議 ──
    'medieval-scriptorium': 'medieval scriptorium monk writing',
    'stained-glass-bible': 'Chartres Cathedral stained glass window',
    'luther-bible': 'Luther Bible 1534 title page',
    'erasmus': 'Erasmus of Rotterdam portrait Holbein',
    'nicaea-council': 'First Council of Nicaea icon',
    'constantine': 'Constantine the Great statue',
    'athanasius': 'Athanasius of Alexandria icon',
    'hagia-sophia': 'Hagia Sophia interior Istanbul',
    'chalcedon-icon': 'Council of Chalcedon',
    'apostles-creed': 'Apostles Creed',

    # ── 第 4 次：教父與東方教會；中世紀西方教會 ──
    'desert-monastery': 'Saint Catherine Monastery Sinai',
    'coptic-icon': 'Coptic icon Egypt',
    'armenian-manuscript': 'Armenian illuminated manuscript',
    'nestorian-stele-ch': 'Nestorian Stele Xian',
    'benedict-rule': 'Rule of Saint Benedict manuscript',
    'cluny-abbey': 'Cluny Abbey ruins',
    'gothic-cathedral': 'Notre Dame de Paris facade',
    'aquinas-thomas': 'Thomas Aquinas painting',
    'crusader-castle': 'Krak des Chevaliers castle',
    'black-death': 'Danse Macabre medieval painting',

    # ── 第 5 次：宗教改革；近代基督教 ──
    'luther-martin': 'Martin Luther Cranach portrait',
    'wittenberg-door': 'Schlosskirche Wittenberg door',
    'calvin-john': 'John Calvin portrait',
    'geneva-cathedral': 'St Pierre Cathedral Geneva interior',
    'trent-council': 'Council of Trent painting',
    'ignatius-loyola': 'Ignatius of Loyola portrait',
    'baroque-church': 'Baroque church interior Rome',
    'wesley-john': 'John Wesley portrait',
    'darwin-charles': 'Charles Darwin portrait',
    'scopes-trial': 'Scopes Trial 1925',

    # ── 第 6 次：二十世紀與當代；禮儀與聖事 ──
    'barth-karl': 'Karl Barth theologian',
    'bonhoeffer': 'Dietrich Bonhoeffer',
    'vatican-ii-ch': 'Second Vatican Council',
    'wcc-assembly': 'World Council of Churches assembly',
    'african-church': 'African Christian church worship',
    'romero-oscar': 'Oscar Romero',
    'baptism-font': 'baptismal font church',
    'eucharist-elements': 'bread and wine communion',
    'catholic-mass': 'Catholic Mass altar priest',
    'orthodox-icon-screen': 'iconostasis Orthodox church',

    # ── 第 7 次：聖職與體制；藝術與物質文化 ──
    'bishop-ordination': 'episcopal ordination laying on of hands',
    'presbyterian-assembly': 'General Assembly Church of Scotland',
    'nun-sisters': 'Catholic nuns habit',
    'christ-pantocrator-ch': 'Christ Pantocrator Sinai icon',
    'rublev-trinity': 'Trinity Andrei Rublev',
    'sistine-chapel': 'Sistine Chapel ceiling',
    'bernini-teresa': 'Ecstasy of Saint Teresa Bernini',
    'bach-manuscript': 'Johann Sebastian Bach manuscript',
    'crucifix-vs-cross': 'crucifix church wall',
    'guadalupe': 'Virgin of Guadalupe image',

    # ── 第 8 次：臺灣的基督宗教；生死觀與終末 ──
    'mackay-memorial': 'George Leslie Mackay Tamsui',
    'tainan-church': 'Taiwan Presbyterian church historic',
    'pehoeji-bible': 'Pe̍h-ōe-jī romanized Taiwanese text',
    'taipei-cathedral': 'Catholic cathedral Taiwan',
    'last-judgment': 'Last Judgment medieval painting',
    'catacomb-tomb': 'early Christian sarcophagus',
    'all-souls-day': 'All Souls Day cemetery candles',
    'resurrection-icon': 'Anastasis Harrowing of Hell icon',
}

# 冷門題材：英文查詢詞對不上，直接指名 Commons 檔案。
EXACT_CH = {
    'nestorian-stele-ch': 'File:Nestorian-Stele-Budge-plate-X.jpg',
    'christ-pantocrator-ch': 'File:Christ Icon Sinai 6th century.jpg',
}
