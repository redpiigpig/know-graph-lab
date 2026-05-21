import type { Creed } from '../types'

export const nicaea325: Creed = {
  slug: 'nicaea-325',
  category: 'ecumenical-council',
  councilNo: 1,
  order: 1,
  nameZh: '尼西亞信經（325 原版）',
  nameEn: 'Original Nicene Creed',
  nameLat: 'Symbolum Nicaenum',
  year: 325,
  location: '比提尼亞‧尼西亞（今土耳其伊茲尼克）',
  topic: '回應亞流主義（Arianism）；確立聖子與聖父「同質」（ὁμοούσιος / homoousios）',
  authors: ['亞他那修（Athanasius）為神學主筆', '亞歷山大的亞歷山大（Alexander of Alexandria）'],
  acceptedBy: [
    'catholic', 'orthodox', 'oriental-orthodox', 'assyrian',
    'protestant', 'anglican', 'lutheran', 'reformed', 'methodist', 'baptist',
  ],
  versions: [
    {
      lang: 'zh-Hant-Catholic',
      label: '思高中譯（天主教）',
      text: `我們信唯一的天主，全能的聖父，
創造一切有形無形萬物者。

我們信唯一的主耶穌基督，天主的聖子，
由聖父所生，獨生唯一者，
即出自聖父的本體，
出自天主的天主，出自光明的光明，
出自真天主的真天主，
受生而非受造，
與聖父同性同體者，
萬物藉祂而造成，
無論天上的或地上的；
祂為了我們人類，並為了我們的得救，從天降下，
取得肉身，成為人，
受苦，並於第三日復活，
升天，
將要再來審判生者與死者。

我們也信聖神。

凡是說：「他曾經不存在」、
「他未出生前並不存在」、
「他是由烏有而成」，
或主張天主之子是出自另一位格、另一本體，
或受造、可變、可改變者──
凡此皆為大公及宗徒的教會所譴責。`,
      source: '思高聖經學會禮儀典譯文',
      translator: '思高聖經學會',
    },
    {
      lang: 'zh-Hant-Orthodox',
      label: '東正教中華主教區譯本',
      text: `我們信獨一上帝，全能的父，
為一切有形與無形萬物的創造者。

我們信獨一主耶穌基督，上帝的兒子，
從父所生的獨生子，
即出於父的本質，
從上帝出來的上帝、從光出來的光、
從真上帝出來的真上帝，
受生而非受造，
與父同一本質，
萬物都是藉著祂受造，
凡在天上的，在地上的；
祂為了我們人類及我們的得救，從天降臨，
取了肉身、成為人，
受了苦，第三日復活，
升了天，
將要來審判活人與死人。

並信於聖神。

凡說「祂曾經不存在」、
「未受生前祂不存在」、
「祂是從無中而有」，
或說上帝之子是出於另一位格或本質、
或是受造的、可變的、可改的──
大公及使徒教會皆嚴加擯斥之。`,
      source: '中華東正教會禮儀譯本（依俄羅斯傳統翻校）',
      translator: '中華正教會',
    },
    {
      lang: 'zh-Hant-Protestant',
      label: '新教中譯（基督教協會通用譯本）',
      text: `我們信獨一上帝，全能的父，
創造有形無形萬物的主。

我們信獨一主耶穌基督，上帝獨生的子，
在萬世之先為父所生，
出自父的本體，
是從上帝出來的上帝，從光出來的光，
從真神出來的真神，
受生而非被造，
與父同質，
萬物都是藉著祂造的，
無論天上、地上的；
祂為了我們人類，為了我們的得救，從天降下，
成了肉身，並成為人，
受了苦，第三日復活，
升了天，
將要再來審判活人死人。

我們信聖靈。

至於那些說：「祂曾有一時不在」、
「祂未生之先並不在」、
「祂從無中而有」、
或稱上帝的兒子是出於另一個位格或本體、
或是受造的、可變的、可改的──
這些言論都為大公及使徒教會所定罪。`,
      source: '依 Schaff 英譯本中譯（網站自譯，2026 修訂）',
    },
    {
      lang: 'en',
      label: '英譯（Schaff 經典譯本）',
      text: `We believe in one God, the Father Almighty,
Maker of all things visible and invisible.

And in one Lord Jesus Christ, the Son of God,
begotten of the Father, the Only-begotten,
that is, of the substance of the Father,
God of God, Light of Light,
very God of very God,
begotten, not made,
being of one substance (homoousion) with the Father,
by whom all things were made,
both things in heaven and things on earth;
who for us men and for our salvation came down
and was incarnate and was made man;
he suffered, and rose again the third day,
ascended into heaven,
and shall come to judge the living and the dead.

And in the Holy Spirit.

But those who say: "There was when he was not,"
and: "Before being born he was not,"
and that he came into existence out of nothing,
or who profess that the Son of God is of a different person or substance,
or that he is created, or changeable, or alterable,
are anathematized by the Catholic and Apostolic Church.`,
      source: 'Philip Schaff《Creeds of Christendom》Vol II, pp. 60–61',
    },
    {
      lang: 'grc',
      label: '原文希臘文（325 原版）',
      text: `Πιστεύομεν εἰς ἕνα Θεὸν Πατέρα παντοκράτορα,
πάντων ὁρατῶν τε καὶ ἀοράτων ποιητήν.

Καὶ εἰς ἕνα Κύριον Ἰησοῦν Χριστόν, τὸν Υἱὸν τοῦ Θεοῦ,
γεννηθέντα ἐκ τοῦ Πατρὸς μονογενῆ,
τουτέστιν ἐκ τῆς οὐσίας τοῦ Πατρός,
Θεὸν ἐκ Θεοῦ, Φῶς ἐκ Φωτός,
Θεὸν ἀληθινὸν ἐκ Θεοῦ ἀληθινοῦ,
γεννηθέντα, οὐ ποιηθέντα,
ὁμοούσιον τῷ Πατρί,
δι' οὗ τὰ πάντα ἐγένετο,
τά τε ἐν τῷ οὐρανῷ καὶ τὰ ἐν τῇ γῇ·
τὸν δι' ἡμᾶς τοὺς ἀνθρώπους καὶ διὰ τὴν ἡμετέραν σωτηρίαν κατελθόντα,
καὶ σαρκωθέντα, καὶ ἐνανθρωπήσαντα,
παθόντα, καὶ ἀναστάντα τῇ τρίτῃ ἡμέρᾳ,
ἀνελθόντα εἰς τοὺς οὐρανούς,
ἐρχόμενον κρῖναι ζῶντας καὶ νεκρούς.

Καὶ εἰς τὸ Ἅγιον Πνεῦμα.

Τοὺς δὲ λέγοντας· ἦν ποτε ὅτε οὐκ ἦν,
καὶ πρὶν γεννηθῆναι οὐκ ἦν,
καὶ ὅτι ἐξ οὐκ ὄντων ἐγένετο,
ἢ ἐξ ἑτέρας ὑποστάσεως ἢ οὐσίας φάσκοντας εἶναι,
ἢ κτιστόν, ἢ τρεπτὸν, ἢ ἀλλοιωτὸν τὸν Υἱὸν τοῦ Θεοῦ,
ἀναθεματίζει ἡ καθολικὴ καὶ ἀποστολικὴ ἐκκλησία.`,
      source: 'Philip Schaff《Creeds of Christendom》Vol II, pp. 60–61',
    },
    {
      lang: 'lat',
      label: '拉丁譯（古典 Hilary / Athanasius 譯本，無 filioque）',
      text: `Credimus in unum Deum Patrem omnipotentem,
omnium visibilium et invisibilium factorem.

Et in unum Dominum Iesum Christum, Filium Dei,
natum ex Patre unigenitum,
hoc est de substantia Patris,
Deum ex Deo, Lumen ex Lumine,
Deum verum ex Deo vero,
natum, non factum,
consubstantialem Patri,
per quem omnia facta sunt,
sive quae in caelo sive quae in terra;
qui propter nos homines et propter nostram salutem descendit,
incarnatus est et homo factus est,
passus est et resurrexit tertia die,
ascendit in caelos,
venturus iudicare vivos et mortuos.

Et in Spiritum Sanctum.

Eos autem qui dicunt: "Erat quando non erat",
et: "Antequam nasceretur non erat",
et quod ex non extantibus factus est,
vel ex alia substantia aut essentia dicunt esse,
aut creatum, aut convertibilem, aut mutabilem Filium Dei,
anathematizat catholica et apostolica Ecclesia.`,
      source: 'Denzinger‐Schönmetzer §125–126；Hilary of Poitiers《De Synodis》',
    },
    {
      lang: 'hye',
      label: '亞美尼亞使徒教會版（古典亞美尼亞文 grabar）',
      text: '（待補：亞美尼亞使徒教會禮儀本 Հաւատամք ի մի Աստուած…）\n\n資料源：armenianchurch.org Divine Liturgy text；亞美尼亞使徒教會禮典 Sharaknots',
      source: 'Armenian Apostolic Church Divine Liturgy；待從 armenianchurch.org 採稿',
      placeholder: true,
    },
    {
      lang: 'cop',
      label: '科普特正教版（Bohairic Coptic）',
      text: '（待補：科普特正教會禮儀本 Ⲧⲉⲛⲛⲁϩϯ ⲉⲩⲛⲟⲩϯ ⲛ̀ⲟⲩⲱⲧ…）\n\n資料源：copticchurch.net Divine Liturgy of St. Basil；Coptic Orthodox Church 禮儀手冊',
      source: 'Coptic Orthodox Divine Liturgy；待從 copticchurch.net 採稿',
      placeholder: true,
    },
    {
      lang: 'syr-east',
      label: '亞述東方教會版（東敘利亞傳統）',
      text: '（待補：Holy Apostolic Catholic Assyrian Church of the East 禮儀本）\n\n資料源：assyrianchurch.org Liturgy of Addai & Mari',
      source: 'Holy Apostolic Catholic Assyrian Church of the East；待採稿',
      placeholder: true,
    },
    {
      lang: 'gez',
      label: '衣索匹亞 Tewahedo 版（Geʿez 古典文）',
      text: '（待補：衣索匹亞東正教會 Tewahedo 禮儀本）\n\n資料源：ethiopianorthodox.org / Tewahedo Liturgical Books；數位化稀少，可能需從 Codex Aksumitae 採集',
      source: 'Ethiopian Orthodox Tewahedo Church；待採稿',
      placeholder: true,
    },
  ],
  summaryZh: `第一次尼西亞大公會議（325 年 6-8 月）由羅馬皇帝君士坦丁召集，318 位主教與會（傳統說法），主要回應亞歷山大長老亞流（Arius）所提的「聖子並非永恆，受生前不存在」之說。會議定下歷史性的「ὁμοούσιος（同質）」用語，宣告聖子與聖父「同一本體」。本信經 325 原版只到「我們信聖神」就結束，未展開聖靈論；末段是針對亞流派的譴責 anathema。

381 年第二次君士坦丁堡會議修訂並擴展本信經（加長聖靈段、刪除 anathema 段），即今日各教會禮儀通用的「尼西亞-君士坦丁堡信經」。`,
  notes: `- ὁμοούσιος（同質）是會議神學焦點，亞流派與「相似派」(ὁμοιούσιος, homoiousios) 都無法接受。
- 末段 anathema 譴責四點亞流主義：「曾經不在」「受生前不在」「從無中而有」「異質異格」。
- 西方拉丁譯本後來分流，**filioque（和聖子）** 段 6 世紀加入，800 年正式進入西方禮儀，為 1054 大分裂的神學導火線之一。
- 亞美尼亞、科普特、敘利亞、衣索匹亞教會皆有自己語言的禮儀本，逐步從各教會官方禮儀採稿補入。`,
  related: ['constantinople-381', 'chalcedonian-451', 'apostles-creed'],
}
