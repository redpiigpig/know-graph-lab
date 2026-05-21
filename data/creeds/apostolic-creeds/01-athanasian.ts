import type { Creed } from '../types'

export const athanasianCreed: Creed = {
  slug: 'athanasian-creed',
  category: 'apostolic-creed',
  order: 1,
  nameZh: '亞他那修信經',
  nameEn: 'Athanasian Creed',
  nameLat: 'Symbolum Athanasianum / Quicunque Vult',
  year: '5-6 世紀（約 500 年）',
  location: '南高盧（Lerins 修道院傳統）',
  topic: '三一論 + 基督論完整版宣告；最詳細闡述「一個本體，三個位格」「兩性聯於一位」的西方信經',
  authors: ['托名亞他那修（Athanasius of Alexandria, 296-373）；實際作者不詳', '現代學界推測：5-6 世紀南高盧拉丁神學家（可能與 Vincent of Lérins 圈子有關）'],
  acceptedBy: [
    'catholic', 'anglican', 'lutheran', 'reformed',
    'protestant', 'methodist',
  ],
  rejectedBy: ['orthodox', 'oriental-orthodox', 'assyrian'],
  versions: [
    {
      lang: 'zh-Hant-Anglican',
      label: '中華聖公會公禱書版',
      text: `凡欲得救者，首要在於持守大公信仰。
此信仰若有人不能完全並純正持守，毋庸置疑，必永遠淪亡。

大公信仰即是：
我們敬拜獨一上帝於三位之中，三位於獨一上帝之內；
位格不混淆，本體不分割。
父為一位，子為一位，聖靈為一位。
然而父、子、聖靈之神性是同一的，榮耀同等，威嚴永恆。

父如何，子亦如何，聖靈亦如何。
父非受造，子非受造，聖靈非受造。
父無限，子無限，聖靈無限。
父永恆，子永恆，聖靈永恆。
然而非有三位永恆者，乃一位永恆者。
亦非有三位非受造者，亦非有三位無限者，乃一位非受造者、一位無限者。

同樣，父全能，子全能，聖靈全能；
然而非有三位全能者，乃一位全能者。
父是上帝，子是上帝，聖靈是上帝；
然而非有三位上帝，乃一位上帝。
父是主，子是主，聖靈是主；
然而非有三位主，乃一位主。

⋯⋯（中段論基督兩性聯合，詳如英文版）⋯⋯

此即大公信仰：人若不忠實堅信，必不得救。`,
      source: '中華聖公會公禱書 / 香港聖公會禮儀本',
      placeholder: true,
    },
    {
      lang: 'en',
      label: 'Traditional English (BCP / Schaff)',
      text: `Whosoever will be saved: before all things it is necessary that he hold the Catholick Faith.
Which Faith except every one do keep whole and undefiled: without doubt he shall perish everlastingly.

And the Catholick Faith is this: That we worship one God in Trinity, and Trinity in Unity;
Neither confounding the Persons: nor dividing the Substance.
For there is one Person of the Father, another of the Son: and another of the Holy Ghost.
But the Godhead of the Father, of the Son, and of the Holy Ghost, is all one: the Glory equal, the Majesty co-eternal.

Such as the Father is, such is the Son: and such is the Holy Ghost.
The Father uncreate, the Son uncreate: and the Holy Ghost uncreate.
The Father incomprehensible, the Son incomprehensible: and the Holy Ghost incomprehensible.
The Father eternal, the Son eternal: and the Holy Ghost eternal.
And yet they are not three eternals: but one eternal.
As also there are not three incomprehensibles, nor three uncreated: but one uncreated, and one incomprehensible.

So likewise the Father is Almighty, the Son Almighty: and the Holy Ghost Almighty.
And yet they are not three Almighties: but one Almighty.
So the Father is God, the Son is God: and the Holy Ghost is God.
And yet they are not three Gods: but one God.
So likewise the Father is Lord, the Son Lord: and the Holy Ghost Lord.
And yet not three Lords: but one Lord.

For like as we are compelled by the Christian verity: to acknowledge every Person by himself to be God and Lord;
So are we forbidden by the Catholick Religion: to say there be three Gods, or three Lords.

The Father is made of none: neither created, nor begotten.
The Son is of the Father alone: not made, nor created, but begotten.
The Holy Ghost is of the Father and of the Son: neither made, nor created, nor begotten, but proceeding.
So there is one Father, not three Fathers; one Son, not three Sons: one Holy Ghost, not three Holy Ghosts.
And in this Trinity none is afore, or after other: none is greater, or less than another;
But the whole three Persons are co-eternal together: and co-equal.
So that in all things, as is aforesaid: the Unity in Trinity, and the Trinity in Unity is to be worshipped.
He therefore that will be saved: must thus think of the Trinity.

Furthermore, it is necessary to everlasting salvation: that he also believe rightly the Incarnation of our Lord Jesus Christ.
For the right Faith is, that we believe and confess: that our Lord Jesus Christ, the Son of God, is God and Man;
God, of the Substance of the Father, begotten before the worlds: and Man, of the substance of his Mother, born in the world;
Perfect God, and perfect Man: of a reasonable soul and human flesh subsisting;
Equal to the Father, as touching his Godhead: and inferior to the Father, as touching his Manhood;
Who although he be God and Man: yet he is not two, but one Christ;
One, not by conversion of the Godhead into flesh: but by taking of the Manhood into God;
One altogether; not by confusion of Substance: but by unity of Person.
For as the reasonable soul and flesh is one man: so God and Man is one Christ;
Who suffered for our salvation: descended into hell, rose again the third day from the dead.
He ascended into heaven, he sitteth on the right hand of the Father, God Almighty:
From whence he shall come to judge the quick and the dead.
At whose coming all men shall rise again with their bodies: and shall give account for their own works.
And they that have done good shall go into life everlasting: and they that have done evil into everlasting fire.

This is the Catholick Faith: which except a man believe faithfully, he cannot be saved.`,
      source: 'Book of Common Prayer 1662 / Schaff, Creeds of Christendom Vol 2 pp. 66-71',
    },
    {
      lang: 'lat',
      label: 'Textus Receptus（拉丁標準版）',
      text: `Quicunque vult salvus esse, ante omnia opus est, ut teneat catholicam fidem:
Quam nisi quisque integram inviolatamque servaverit, absque dubio in aeternum peribit.

Fides autem catholica haec est: ut unum Deum in Trinitate, et Trinitatem in Unitate veneremur.
Neque confundentes personas, neque substantiam separantes.
Alia est enim persona Patris, alia Filii, alia Spiritus Sancti.
Sed Patris, et Filii, et Spiritus Sancti una est divinitas, aequalis gloria, coeterna maiestas.

Qualis Pater, talis Filius, talis Spiritus Sanctus.
Increatus Pater, increatus Filius, increatus Spiritus Sanctus.
Immensus Pater, immensus Filius, immensus Spiritus Sanctus.
Aeternus Pater, aeternus Filius, aeternus Spiritus Sanctus.
Et tamen non tres aeterni, sed unus aeternus.
Sicut non tres increati, nec tres immensi, sed unus increatus, et unus immensus.

⋯⋯（完整 44 句參見 Schaff Vol 2）⋯⋯

Haec est fides catholica, quam nisi quisque fideliter firmiterque crediderit, salvus esse non poterit.`,
      source: 'Breviarium Romanum / Schaff, Creeds of Christendom Vol 2 pp. 66-71',
      placeholder: false,
    },
    {
      lang: 'zh-Hant-Catholic',
      label: '思高中譯（天主教）',
      text: `凡欲得救者，首要持守大公信仰。
人若不完整、不虔守此信仰，必永遠淪亡。

大公信仰即是：
我們欽崇三位於一體，一體於三位之天主。
不混淆其位格，亦不分裂其本體。
聖父為一位，聖子為一位，聖神為一位。

⋯⋯（完整段落由天主教香港教區禮儀委員會編譯，請參思高聖經學會出版禮儀典）⋯⋯`,
      source: '天主教香港教區禮儀典 / 思高聖經學會',
      placeholder: true,
    },
  ],
  summaryZh: `「亞他那修信經」（Quicunque Vult，按拉丁首字命名）是西方教會三大信經之一（其他兩個為使徒信經與尼西亞-君士坦丁堡信經）。雖然托名 4 世紀亞歷山大主教亞他那修，現代學界一致認為實際成於 5-6 世紀拉丁西方（可能南高盧 Lerins 圈子），早於亞他那修去世約 150 年。

本信經是三大信經中最長最詳細的一份，44 句完整闡述：
- 三一論：一本體（substantia / οὐσία），三位格（personae / hypostases）；位格不混淆，本體不分割
- 基督論：完全的神性與完全的人性聯於一個位格（迦克墩定義的西方版闡述）
- 起頭與結尾兩次嚴厲警語：「人若不持守此信仰，必永遠淪亡」（damnatory clauses）

東方教會從未禮儀採用，因其拉丁背景與較晚成形；亦因其「聖靈由父和子發出」（Filioque）的隱含立場，與東方「僅由父發出」的立場衝突。

新教改教時：
- 路德、加爾文均高度肯定本信經；
- 路德宗《協同信條》（Book of Concord 1580）正式列為三大基督教信經之一；
- 改革宗《海德堡要理問答》（1563）默認其神學；
- 聖公會 39 條第 8 條明文採用本信經與其他兩信經為大公正統。`,
  notes: `- 「Damnatory clauses」（永遠淪亡的警語）在啟蒙時代以降被自由神學派強烈批評；1864 年 Pusey 與 Stanley 在英國國教就此爭辯
- 19-20 世紀，部分英國國教與美國聖公會禮儀本將本信經改為選用而非必用
- 「Filioque」隱含立場：「聖靈出於父與子」一句是西方「和子說」的早期表述之一
- 中譯版「永遠淪亡」/「沉淪」/「滅亡」各家用詞不同，反映對 damnatory clauses 的不同神學處理`,
  related: [
    'apostles-creed',
    'nicaea-325',
  ],
}
