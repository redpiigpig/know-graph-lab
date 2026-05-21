import type { Creed } from '../types'

export const apostlesCreed: Creed = {
  slug: 'apostles-creed',
  category: 'apostolic-creed',
  order: 0,
  nameZh: '使徒信經',
  nameEn: "Apostles' Creed",
  nameLat: 'Symbolum Apostolorum',
  year: '2-8 世紀（漸成形）',
  location: '羅馬／高盧',
  topic: '基督徒最早期受洗時使用的「信仰宣告」；西方教會三大信經之一，廣被天主教、聖公會、信義會、改革宗、衛理會等接受',
  authors: ['傳說中為十二使徒共撰（後世托名）', '實際成形：8 世紀法蘭克教會最終定稿（textus receptus）'],
  acceptedBy: [
    'catholic', 'anglican', 'lutheran', 'reformed', 'methodist',
    'protestant', 'baptist',
  ],
  rejectedBy: ['orthodox', 'oriental-orthodox', 'assyrian'],
  versions: [
    {
      lang: 'zh-Hant-Anglican',
      label: '中華聖公會公禱書版',
      text: `我信上帝，全能的父，創造天地的主。
我信我主耶穌基督，上帝獨生的子；
因聖靈感孕，由童貞女馬利亞所生；
在本丟彼拉多手下受難，被釘於十字架，
受死，埋葬；降在陰間；
第三日從死人中復活；
升天，坐在全能父上帝的右邊；
將來必從那裡降臨，審判活人死人。
我信聖靈；
我信聖而公之教會；
我信聖徒相通；
我信罪得赦免；
我信身體復活；
我信永生。
阿們。`,
      source: '中華聖公會公禱書 / 香港聖公會禮儀本',
      translator: '中華聖公會',
    },
    {
      lang: 'zh-Hant-Lutheran',
      label: '中華信義會禮儀本',
      text: `我信上帝，全能的父，創造天地的主。
我信耶穌基督，上帝的獨生子，我們的主；
祂因聖靈感孕，由童女馬利亞所生，
在本丟彼拉多手下受難，被釘於十字架，受死，埋葬；
降在陰間，第三日從死裡復活，
升天，坐在全能父上帝的右邊；
將來必從那裡降臨，審判活人死人。
我信聖靈，
一聖基督教會，聖徒相通，
罪得赦免，
肉身復活，
並且永生。阿們。`,
      source: '中華信義會崇拜禮文',
      placeholder: true,
    },
    {
      lang: 'zh-Hant-Catholic',
      label: '思高中譯（天主教）',
      text: `我信全能者天主父，天地萬物的創造者。
我信祂的唯一聖子，我們的主耶穌基督；
祂因聖神由童貞瑪利亞取得肉軀，而成為人；
祂在比拉多執政時，為我們被釘在十字架上，受難而被埋葬；
祂下降陰府，第三日從死者中復活；
祂升了天，坐在全能者天主父的右邊；
祂要從天降來，審判生者死者。
我信聖神，
我信聖而公教會、諸聖的相通，
我信罪過的赦免，
我信肉身的復活，
我信永恆的生命。
亞孟。`,
      source: '思高聖經學會禮儀典譯文',
      translator: '思高聖經學會',
    },
    {
      lang: 'en',
      label: 'Traditional English (BCP 1662 / Schaff)',
      text: `I believe in God the Father Almighty, Maker of heaven and earth:
And in Jesus Christ his only Son our Lord,
Who was conceived by the Holy Ghost, Born of the Virgin Mary,
Suffered under Pontius Pilate, Was crucified, dead, and buried,
He descended into hell;
The third day he rose again from the dead,
He ascended into heaven,
And sitteth on the right hand of God the Father Almighty;
From thence he shall come to judge the quick and the dead.
I believe in the Holy Ghost;
The holy Catholick Church;
The Communion of Saints;
The forgiveness of sins;
The resurrection of the body,
And the life everlasting. Amen.`,
      source: 'Book of Common Prayer 1662 / Schaff, Creeds of Christendom Vol 2',
    },
    {
      lang: 'lat',
      label: 'Textus Receptus（8 世紀定稿拉丁版）',
      text: `Credo in Deum Patrem omnipotentem, Creatorem caeli et terrae.
Et in Iesum Christum, Filium eius unicum, Dominum nostrum:
qui conceptus est de Spiritu Sancto, natus ex Maria Virgine,
passus sub Pontio Pilato, crucifixus, mortuus, et sepultus,
descendit ad inferos,
tertia die resurrexit a mortuis,
ascendit ad caelos, sedet ad dexteram Dei Patris omnipotentis,
inde venturus est iudicare vivos et mortuos.
Credo in Spiritum Sanctum,
sanctam Ecclesiam catholicam, sanctorum communionem,
remissionem peccatorum,
carnis resurrectionem,
vitam aeternam. Amen.`,
      source: 'Catechismus Romanus / Schaff, Creeds of Christendom Vol 2',
    },
  ],
  summaryZh: `「使徒信經」是西方教會傳統最早的洗禮信仰宣告，起源於 2 世紀羅馬的「古羅馬信經」（Old Roman Creed），歷經數百年發展，於 8 世紀在法蘭克教會最終定稿（textus receptus）。

雖名為「使徒」，現代學者一致認為並非十二使徒親撰，而是早期教會逐步形塑而成的洗禮問答（baptismal interrogation）。其核心結構為三位一體三段式：對父、對子（含基督救贖事件清單）、對聖靈／教會／末日。

東方教會（東正教、東方東正教、亞述）不採用本信經作禮儀宣告，而是用尼西亞-君士坦丁堡信經 381。但東方教會學界承認其神學內涵與大公教義一致。

在新教改教後，路德、加爾文、克蘭默均在教理問答中保留本信經作要理教育核心，故新教各派幾乎皆接受。`,
  notes: `- 「降在陰間」（descendit ad inferos）一句約 4 世紀才加入；阿奎萊亞信經是最早含此句的拉丁版本
- 「諸聖相通」（communio sanctorum）一句在 5 世紀末才出現
- 中文「公教會」/「公之教會」/「大公教會」對應拉丁 catholicam = 普世的（universal），非「天主教專屬」之意
- 改教後，新教為避免歧義常譯為「聖而公教會」或「神聖大公教會」
- 路德《小要理問答》（1529）以本信經為三大教義骨幹之一（與十誡、主禱文並列）`,
  related: [
    'nicaea-325',
  ],
}
