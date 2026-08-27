import {
  JIS_B5_READER_PROFILE,
  type OriginalReaderSelection,
  type OriginalReaderSource,
  type OriginalReaderToken,
  type OriginalReaderVolume,
} from "./types";
import greekVocabularyJson from "./vocabulary/greek-1000.json";

type SelectionDraft = Omit<OriginalReaderSelection, "ordinal">;

const curriculumSource: OriginalReaderSource = {
  edition: "希臘文原典讀本編輯規格 v0.1",
  versionCode: "GRC-READER-PLAN-0.1",
  licenseNote: "私人課程規劃；本來源只描述自編教學內容，不含第三方原文。",
  authorization: "private-authorized",
};

const mounceChineseVocabularySource: OriginalReaderSource = {
  edition:
    "William D. Mounce，《聖經希臘文基礎：課本》／Basics of Biblical Greek 官方 1,000 詞表",
  editor: "William D. Mounce；中譯書目責任資料待授權本核對",
  sourceUrl: "https://www.billmounce.com/basicsofbiblicalgreek/grammar",
  versionCode: "MOUNCE-BBG-1000-PRIVATE",
  licenseNote:
    "已由私人授權的本機詞表接入全部 1,000 詞：前 340 詞保留 BBG 章序，後 660 詞保留 Mounce 官方頻率延伸次序；逐詞保存原列印項、來源頁與核驗狀態。",
  authorization: "private-authorized",
};

const mounceGradedReaderSource: OriginalReaderSource = {
  edition:
    "William D. Mounce, A Graded Reader of Biblical Greek（進階閱讀路徑）",
  editor: "William D. Mounce",
  sourceUrl: "https://www.billmounce.com/gradedreader",
  versionCode: "MOUNCE-GRBG-PENDING",
  licenseNote:
    "此書沒有另行抽出的公開逐篇獨立詞序，因此只用來規劃二十篇進階讀文，不冒充 1,000 詞表的第二套排序。正式編排仍須保留篇章與頁碼。",
  authorization: "private-authorized",
};

const vocabularyCurriculumSource: OriginalReaderSource = {
  edition:
    "Mounce BBG 官方 1,000 詞表：340 詞 BBG 章序＋660 詞官方頻率延伸",
  editor: "William D. Mounce；希臘文原典讀本編輯計畫",
  sourceUrl: "https://www.billmounce.com/greek-alphabet",
  versionCode: "GRC-VOCAB-MOUNCE-1000-VERIFIED",
  licenseNote:
    "已接入私人授權的完整 1,000 詞來源次序與逐詞來源頁。A Graded Reader 只作二十篇進階閱讀路徑，不宣稱已從該書抽出另一套逐篇詞序。",
  authorization: "private-authorized",
};

const sblgntSource: OriginalReaderSource = {
  edition: "SBL Greek New Testament",
  editor: "Michael W. Holmes",
  sourceUrl: "https://sblgnt.com/",
  versionCode: "SBLGNT",
  licenseNote:
    "私人研究與排版規劃；匯入正文、印刷與音訊發布前，須再次核對 SBLGNT 現行授權條款與署名要求。",
  authorization: "private-authorized",
};

const lxxSource: OriginalReaderSource = {
  edition: "Septuaginta, editio altera (Rahlfs-Hanhart)",
  editor: "Alfred Rahlfs; revised by Robert Hanhart",
  versionCode: "LXX-RH",
  licenseNote:
    "私人研究用製作規劃；正式匯入、重製、印刷或錄音前，須取得或確認 Deutsche Bibelgesellschaft 的相應授權。",
  authorization: "private-authorized",
};

const tobitGiiSource: OriginalReaderSource = {
  edition: "Septuaginta, Tobit II (Codex Sinaiticus / GII)",
  editor: "Alfred Rahlfs; revised by Robert Hanhart",
  versionCode: "LXX-TOB-GII-S",
  licenseNote:
    "私人研究用製作規劃；正文須固定採 GII/Sinaiticus，並在排印前確認底本與授權，不得與 GI 混排。",
  authorization: "private-authorized",
};

const goarchLiturgySource: OriginalReaderSource = {
  edition:
    "Divine Liturgy of St. John Chrysostom, fixed text based on the Greek Hieratikon (2020)",
  editor: "Greek Orthodox Archdiocese of America",
  sourceUrl:
    "https://dcs.goarch.org/goa/dcs/h/b/skeleton/liturgy/chrys/gr-en/index.html",
  versionCode: "GOARCH-HIERATIKON-2020",
  licenseNote:
    "僅供私人讀本規劃與校勘；GOARCH 現行希臘文、英譯與編排可能受權利保護，印刷及公開音訊前須取得許可。",
  authorization: "private-authorized",
};

const orthodoxPrayerSource: OriginalReaderSource = {
  edition: "希臘正教祈禱、信經與聖詠選集：各篇禮書底本待逐項定本",
  versionCode: "GRC-ORTHODOX-PRAYERS-PENDING",
  licenseNote:
    "目前只定選目與通行希臘文題名／首句，不宣稱二十篇均出自同一禮書。每篇正文須另記禮書、教區版本、頁碼與權利狀態，校驗後才可入稿或錄音。",
  authorization: "private-authorized",
};

const patristicSource = (work: string): OriginalReaderSource => ({
  edition: `${work}：PG／公共領域底本與現代批判版待逐篇定本`,
  versionCode: "PATRISTIC-COLLATION-PENDING",
  licenseNote:
    "私人研究用選文規劃；古代作品本身屬公共領域，但實際希臘文須經可靠版本校勘，現代批判版與翻譯授權須另行確認。",
  authorization: "private-authorized",
});

const vocabularyCurriculumSelections: SelectionDraft[] = [
  {
    id: "grc-vocab-curriculum-mounce",
    partId: "vocabulary",
    kind: "vocabulary",
    title: "詞彙課程第一層：孟恩思《聖經希臘文基礎：課本》",
    subtitle: "與使用者指定的 2017 修訂中譯作課程對照；1,000 詞已接入：340 詞依 BBG 章序，660 詞依 Mounce 官方頻率延伸",
    difficulty: 1,
    track: "reference",
    estimatedPages: 2,
    status: "source_ready",
    source: mounceChineseVocabularySource,
    learningGoals: [
      "逐組學習已核對的原列印項、lemma、課本式音譯、英文釋義與 Strong 編號",
      "保留前 340 詞的 BBG 章次，以及後 660 詞的 Mounce 官方頻率延伸來源",
      "依逐詞 verification 辨認已與詞典吻合及仍待詞典核對的項目",
    ],
    tags: [
      "vocab-curriculum",
      "tier:1",
      "mounce-primary-layer",
      "source-loaded",
      "per-entry-verification",
    ],
  },
  {
    id: "grc-vocab-curriculum-graded-reader",
    partId: "vocabulary",
    kind: "bridge_text",
    title: "進階閱讀路徑：《A Graded Reader of Biblical Greek》",
    subtitle: "規劃二十篇進階讀文；沒有冒稱已抽出公開的逐篇獨立詞序",
    difficulty: 2,
    track: "reference",
    estimatedPages: 2,
    status: "planned",
    source: mounceGradedReaderSource,
    learningGoals: [
      "依 graded passages 的實際篇章設計二十篇進階閱讀路徑",
      "逐篇保留頁碼、閱讀難度與該篇才需要的補充詞彙，不改寫官方 1,000 詞排序",
      "沒有獨立來源詞序時保持明說，不以通用頻率表重建一套假詞序",
    ],
    tags: [
      "vocab-curriculum",
      "advanced-reading-route",
      "graded-reader",
      "awaiting-authorized-source",
      "no-invented-order",
    ],
  },
];

interface GreekVocabularyEntry {
  ordinal: number;
  bbgChapter: number | null;
  printedEntry: string;
  sourcePage: number;
  productionGroup: number;
  groupSlot: number;
  headword: string;
  lemma: string;
  textbookTransliteration: string;
  transliterationSystem: string;
  transliterationStatus: string;
  glossEn: string;
  glossZh: string;
  strong: string;
  isProperName: boolean;
  properNameTypes: string[];
  verification: string;
}

const GREEK_VOCABULARY = greekVocabularyJson as GreekVocabularyEntry[];

if (GREEK_VOCABULARY.length !== 1000) {
  throw new Error(
    `Greek reader vocabulary must contain 1,000 entries; received ${GREEK_VOCABULARY.length}.`,
  );
}

function vocabularyEntriesForGroup(group: number): GreekVocabularyEntry[] {
  const entries = GREEK_VOCABULARY
    .filter((entry) => entry.productionGroup === group)
    .sort((left, right) => left.groupSlot - right.groupSlot);
  if (
    entries.length !== 50 ||
    entries.some((entry, index) => entry.groupSlot !== index + 1)
  ) {
    throw new Error(`Greek vocabulary group ${group} must contain slots 1–50.`);
  }
  return entries;
}

function greekVocabularyToken(
  entry: GreekVocabularyEntry,
  groupId: string,
): OriginalReaderToken {
  return {
    id: `grc-vocab-${groupId}-w${String(entry.groupSlot).padStart(2, "0")}`,
    ordinal: entry.groupSlot,
    surface: entry.headword,
    lemma: entry.lemma,
    reading: entry.textbookTransliteration,
    textbookTransliteration: entry.textbookTransliteration,
    transliterationSystem: entry.transliterationSystem,
    transliterationStatus: entry.transliterationStatus,
    glossEn: entry.glossEn,
    glossZh: entry.glossZh,
    strong: entry.strong || undefined,
    isProperName: entry.isProperName,
    properNameTypes: entry.properNameTypes,
    printedEntry: entry.printedEntry,
    sourceType: entry.bbgChapter
      ? "mounce_bbg_chapter_order"
      : "mounce_official_frequency_extension",
    sourcePage: entry.sourcePage,
    sourceOrder: entry.ordinal,
    bbgChapter: entry.bbgChapter ?? undefined,
    productionGroup: entry.productionGroup,
    groupSlot: entry.groupSlot,
    verification: entry.verification,
  };
}

const vocabularySelections: SelectionDraft[] = Array.from(
  { length: 20 },
  (_, index) => {
    const group = index + 1;
    const groupId = String(group).padStart(2, "0");
    const start = index * 50 + 1;
    const end = start + 49;
    const entries = vocabularyEntriesForGroup(group);
    const difficulty = (
      index < 4 ? 1 : index < 12 ? 2 : index < 18 ? 3 : 4
    ) as 1 | 2 | 3 | 4;

    return {
      id: `grc-vocab-${groupId}`,
      partId: "vocabulary",
      kind: "vocabulary",
      title: `核心詞彙第 ${groupId} 組（50 詞）`,
      subtitle: `第 ${String(start).padStart(4, "0")}–${String(end).padStart(4, "0")} 詞已接入；累積 ${end} 詞`,
      difficulty,
      track: "core",
      estimatedPages: 2,
      status: "source_ready",
      source: vocabularyCurriculumSource,
      segments: [
        {
          id: `grc-vocab-${groupId}-words`,
          ordinal: 1,
          ref: `Mounce vocabulary group ${group}`,
          sourceText: entries.map((entry) => entry.headword).join(" "),
          translationZh: "",
          tokens: entries.map((entry) => greekVocabularyToken(entry, groupId)),
          textualNotes: [
            "原列印項、課本式音譯、英文釋義、Strong 與核驗狀態均逐詞顯示；空缺不以推測補寫。",
            "前 340 詞保留 BBG 章序，後 660 詞保留 Mounce 官方頻率延伸；A Graded Reader 只另作進階閱讀路徑。",
          ],
        },
      ],
      learningGoals: [
        "以詞位而非單一屈折形式計數",
        "保留孟恩思 BBG 官方詞表的實際次序：340 詞章序＋660 詞官方頻率延伸",
        "為每個詞位顯示原列印項、來源頁與逐詞核驗狀態",
        "按 lemma 辨讀並區分已與 Strong 詞典吻合及仍待詞典核對的項目",
        "完成慢速與自然速度的詞形音訊索引",
      ],
      tags: [
        "1000-lemma-program",
        `range:${start}-${end}`,
        `cumulative:${end}`,
        "mounce-primary-layer",
        "source-loaded",
        "per-entry-verification",
      ],
    };
  },
);

const memoryGroupSpecs = [
  ["001–010", "福音敘事與直接引語", "Mark 1–4"],
  ["011–020", "路加敘事與比喻", "Luke 15"],
  ["021–030", "約翰著作的光、生命與道", "John 1; 1 John 1"],
  ["031–040", "山上寶訓與主禱文", "Matthew 5–6"],
  ["041–050", "使徒行傳與雅各書", "Acts 2; James 1"],
  ["051–060", "保羅書信的愛、基督與聖靈", "1 Corinthians 13; Philippians 2; Romans 8"],
  ["061–070", "希伯來書與啟示錄", "Hebrews 1; Revelation 21"],
  ["071–080", "七十士譯本：敘事與律法", "Ruth; Jonah; Genesis; Exodus"],
  ["081–090", "七十士譯本：詩篇、先知與次經", "Psalms; Isaiah; Deuterocanon"],
  ["091–100", "信經、祈禱、禮儀與教父", "Prayer; Liturgy; Fathers"],
] as const;

const memorySelections: SelectionDraft[] = memoryGroupSpecs.map(
  ([range, theme, corpus], index) => ({
    id: `grc-memory-${String(index + 1).padStart(2, "0")}`,
    partId: "memory",
    kind: "memory_unit",
    title: `記憶單元 ${range}：${theme}`,
    subtitle: `十個 4–12 詞的完整意義單位；來源範圍：${corpus}`,
    difficulty: (index < 2 ? 1 : index < 6 ? 2 : index < 9 ? 3 : 4) as
      | 1
      | 2
      | 3
      | 4,
    track: "core",
    estimatedPages: 2,
    status: "planned",
    source: curriculumSource,
    learningGoals: [
      "在完整語境中背誦，不把片語當成脫離上下文的格言",
      "能朗讀、斷句、回譯並指出每單元的一個關鍵形態",
      "每十單元至少配置一題延遲回憶與一題聽寫",
      "原文、繁中譯文與音訊均須在入稿前逐項校驗",
    ],
    tags: ["100-memory-units", `units:${range}`, "contextual-memory", "audio-required"],
  }),
);

const orientationSelections: SelectionDraft[] = [
  {
    id: "grc-orientation-reader",
    partId: "orientation",
    kind: "orientation",
    title: "如何使用本讀本與線上逐句音訊",
    difficulty: 1,
    track: "core",
    estimatedPages: 4,
    status: "planned",
    source: curriculumSource,
    learningGoals: ["理解正文、頁下注、記憶單元、音訊與未見文測驗的工作流程"],
    tags: ["workflow", "audio-alignment", "b5-reader"],
  },
  {
    id: "grc-orientation-script",
    partId: "orientation",
    kind: "orientation",
    title: "希臘字母、附加符號、重音與標點",
    difficulty: 1,
    track: "core",
    estimatedPages: 6,
    status: "planned",
    source: curriculumSource,
    learningGoals: ["不依賴羅馬轉寫辨讀多調希臘文", "辨認重音、氣號、冠詞省音與常用標點"],
    tags: ["alphabet", "polytonic", "accent", "punctuation"],
  },
  {
    id: "grc-orientation-pronunciation",
    partId: "orientation",
    kind: "orientation",
    title: "兩套朗讀規約：重建通用希臘語與拜占庭教會讀音",
    difficulty: 1,
    track: "reference",
    estimatedPages: 4,
    status: "planned",
    source: curriculumSource,
    learningGoals: ["知道兩套讀音的用途與差異", "避免把現代教會讀音冒充唯一的古代發音"],
    tags: ["pronunciation", "reconstructed-koine", "byzantine"],
  },
  {
    id: "grc-orientation-editions",
    partId: "orientation",
    kind: "orientation",
    title: "底本、版本代碼與文本校勘邊界",
    difficulty: 2,
    track: "reference",
    estimatedPages: 5,
    status: "planned",
    source: curriculumSource,
    learningGoals: [
      "區分新約、LXX、Tobit GII、拜占庭禮文與教父版本",
      "辨識版本差異與翻譯差異，不把異文直接神學化",
    ],
    tags: ["textual-criticism", "edition-policy", "rights-review"],
  },
];

const referenceSelections: SelectionDraft[] = [
  {
    id: "grc-ref-morphology",
    partId: "reference",
    kind: "appendix",
    title: "名詞、形容詞、代名詞與冠詞速查",
    difficulty: 2,
    track: "reference",
    estimatedPages: 6,
    status: "planned",
    source: curriculumSource,
    learningGoals: ["由詞尾辨認格、數、性", "比較規則形與高頻不規則形"],
    tags: ["morphology", "nominal-system", "reference-table"],
  },
  {
    id: "grc-ref-verbs",
    partId: "reference",
    kind: "appendix",
    title: "動詞時態詞幹、語氣、分詞與主要形式速查",
    difficulty: 3,
    track: "reference",
    estimatedPages: 8,
    status: "planned",
    source: curriculumSource,
    learningGoals: ["辨認高頻動詞主要形式", "把時態、體貌、語氣與篇章功能分開描述"],
    tags: ["verbs", "principal-parts", "aspect", "participles"],
  },
  {
    id: "grc-ref-syntax",
    partId: "reference",
    kind: "appendix",
    title: "從句、分詞、語氣與篇章連接詞索引",
    difficulty: 3,
    track: "reference",
    estimatedPages: 6,
    status: "planned",
    source: curriculumSource,
    learningGoals: ["追蹤長句層級", "依語境解釋語序與資訊焦點"],
    tags: ["syntax", "discourse", "particles", "clause-map"],
  },
  {
    id: "grc-ref-register-bridge",
    partId: "reference",
    kind: "bridge_text",
    title: "新約、LXX、禮儀與教父橋接詞彙",
    difficulty: 3,
    track: "reference",
    estimatedPages: 8,
    status: "planned",
    source: curriculumSource,
    learningGoals: ["追蹤同一詞位跨語域的義項變化", "另列 1000 核心詞以外的語域詞"],
    tags: ["bridge-vocabulary", "semantic-shift", "register"],
  },
  {
    id: "grc-ref-numbering",
    partId: "reference",
    kind: "appendix",
    title: "LXX／MT 詩篇編號與次經版本對照",
    difficulty: 2,
    track: "reference",
    estimatedPages: 4,
    status: "planned",
    source: curriculumSource,
    learningGoals: ["正確雙標詩篇編號", "辨認 Tobit、Daniel additions 等版本分流"],
    tags: ["psalm-numbering", "recensions", "cross-reference"],
  },
  {
    id: "grc-ref-lemma-index",
    partId: "reference",
    kind: "appendix",
    title: "一千詞位總索引、經文索引與音訊 ID 索引",
    difficulty: 1,
    track: "reference",
    estimatedPages: 10,
    status: "planned",
    source: curriculumSource,
    learningGoals: ["由詞位、章節與音訊段落雙向查找", "維持印刷與線上內容的穩定 ID"],
    tags: ["index", "1000-lemma-program", "audio-id", "production"],
  },
];

const ntSpecs = [
  {
    id: "grc-nt-mark-1",
    bookCode: "MRK",
    chapter: 1,
    title: "馬可福音 1：宣告、呼召與醫治",
    original: "Κατὰ Μᾶρκον 1",
    difficulty: 1,
    pages: 9,
    goals: ["辨認敘事中的歷史現在式與 εὐθύς", "分析分詞與主要動詞的事件鏈"],
  },
  {
    id: "grc-nt-mark-2",
    bookCode: "MRK",
    chapter: 2,
    title: "馬可福音 2：赦罪、召命與安息日爭論",
    original: "Κατὰ Μᾶρκον 2",
    difficulty: 1,
    pages: 8,
    goals: ["追蹤直接引語與間接質疑", "掌握屬格絕對與介系詞片語"],
  },
  {
    id: "grc-nt-mark-4",
    bookCode: "MRK",
    chapter: 4,
    title: "馬可福音 4：撒種比喻與平靜風浪",
    original: "Κατὰ Μᾶρκον 4",
    difficulty: 2,
    pages: 10,
    goals: ["辨認比喻中的條件與目的表達", "比較反覆詞彙在解釋段中的功能"],
  },
  {
    id: "grc-nt-luke-15",
    bookCode: "LUK",
    chapter: 15,
    title: "路加福音 15：失而復得的三個比喻",
    original: "Κατὰ Λουκᾶν 15",
    difficulty: 2,
    pages: 10,
    goals: ["處理長篇敘事中的時態轉換", "辨認間接引語與情感性語序"],
  },
  {
    id: "grc-nt-1john-1",
    bookCode: "1JN",
    chapter: 1,
    title: "約翰一書 1：生命之道、光與認罪",
    original: "Ἰωάννου Αʹ 1",
    difficulty: 1,
    pages: 5,
    goals: ["掌握關係代名詞鏈與條件句", "追蹤光／暗、真理／謊言的語義對比"],
  },
  {
    id: "grc-nt-john-1",
    bookCode: "JHN",
    chapter: 1,
    title: "約翰福音 1：序言、見證與首批門徒",
    original: "Κατὰ Ἰωάννην 1",
    difficulty: 2,
    pages: 11,
    goals: ["分析 ἦν、ἐγένετο 與 λόγος 的句法角色", "區分序言詩性段落與敘事段落"],
  },
  {
    id: "grc-nt-matthew-5",
    bookCode: "MAT",
    chapter: 5,
    title: "馬太福音 5：八福與律法詮釋",
    original: "Κατὰ Ματθαῖον 5",
    difficulty: 2,
    pages: 11,
    goals: ["辨認 μακάριος 句式、命令式與禁令", "分析反題段落的引述框架"],
  },
  {
    id: "grc-nt-matthew-6",
    bookCode: "MAT",
    chapter: 6,
    title: "馬太福音 6：施捨、祈禱、禁食與憂慮",
    original: "Κατὰ Ματθαῖον 6",
    difficulty: 2,
    pages: 11,
    goals: ["精讀主禱文的祈使語氣", "比較否定命令與目的子句"],
  },
  {
    id: "grc-nt-acts-2",
    bookCode: "ACT",
    chapter: 2,
    title: "使徒行傳 2：五旬節、彼得講論與群體生活",
    original: "Πράξεις Ἀποστόλων 2",
    difficulty: 3,
    pages: 12,
    goals: ["追蹤引文、講論與敘事的層級", "比較路加希臘文與 LXX 引文"],
  },
  {
    id: "grc-nt-james-1",
    bookCode: "JAS",
    chapter: 1,
    title: "雅各書 1：試煉、智慧、言語與實踐",
    original: "Ἰακώβου 1",
    difficulty: 3,
    pages: 8,
    goals: ["辨認智慧文學式命令與對偶", "分析分詞、關係子句與比喻"],
  },
  {
    id: "grc-nt-1corinthians-13",
    bookCode: "1CO",
    chapter: 13,
    title: "哥林多前書 13：愛的頌歌",
    original: "Πρὸς Κορινθίους Αʹ 13",
    difficulty: 2,
    pages: 6,
    goals: ["辨認無連詞排比與動詞語義", "比較現在、將來與完成語境"],
  },
  {
    id: "grc-nt-philippians-2",
    bookCode: "PHP",
    chapter: 2,
    title: "腓立比書 2：基督頌與共同生活",
    original: "Πρὸς Φιλιππησίους 2",
    difficulty: 3,
    pages: 7,
    goals: ["分析 2:6–11 的分詞與主句關係", "辨認勸勉、敘事與詩性材料的轉換"],
  },
  {
    id: "grc-nt-romans-8",
    bookCode: "ROM",
    chapter: 8,
    title: "羅馬書 8：聖靈、受苦與盼望",
    original: "Πρὸς Ῥωμαίους 8",
    difficulty: 4,
    pages: 12,
    goals: ["繪製保羅長句與論證連接詞", "辨認條件、因果與目的關係"],
  },
  {
    id: "grc-nt-hebrews-1",
    bookCode: "HEB",
    chapter: 1,
    title: "希伯來書 1：子與天使",
    original: "Πρὸς Ἑβραίους 1",
    difficulty: 4,
    pages: 7,
    goals: ["分析高度從屬化的開篇長句", "核對連續 LXX 引文與其論證功能"],
  },
  {
    id: "grc-nt-revelation-21",
    bookCode: "REV",
    chapter: 21,
    title: "啟示錄 21：新天、新地與新耶路撒冷",
    original: "Ἀποκάλυψις 21",
    difficulty: 4,
    pages: 9,
    goals: ["描述而非修正閃語化／非標準用法", "追蹤異象中的空間、量度與象徵詞彙"],
  },
] as const;

const ntSelections: SelectionDraft[] = ntSpecs.map((spec) => ({
  id: spec.id,
  partId: "new-testament",
  kind: "bible_chapter",
  title: spec.title,
  titleOriginal: spec.original,
  difficulty: spec.difficulty,
  track: spec.difficulty === 4 ? "advanced" : "core",
  estimatedPages: spec.pages,
  status: "planned",
  source: sblgntSource,
  scripture: {
    bookCode: spec.bookCode,
    chapter: spec.chapter,
    versionCode: "SBLGNT",
    parallelGroup: `${spec.bookCode.toLowerCase()}-${spec.chapter}`,
  },
  learningGoals: [...spec.goals, "完成逐節原文、繁中譯文、頁下注與句段音訊的校驗"],
  tags: ["new-testament", "full-chapter", "zh-tw-required", "aligned-audio"],
}));

const lxxSpecs = [
  {
    id: "grc-lxx-ruth-1",
    bookCode: "RUT",
    chapter: 1,
    title: "路得記 1：離鄉、喪親與盟誓",
    original: "Ῥούθ 1",
    difficulty: 2,
    pages: 8,
    goals: ["比較翻譯希臘文的敘事連接方式", "辨認親屬與移居詞彙"],
  },
  {
    id: "grc-lxx-jonah-1",
    bookCode: "JON",
    chapter: 1,
    title: "約拿書 1：逃亡、風暴與拈鬮",
    original: "Ἰωνᾶς 1",
    difficulty: 2,
    pages: 7,
    goals: ["追蹤 καί 串連的敘事節奏", "與希伯來文平行文本比較翻譯選擇"],
  },
  {
    id: "grc-lxx-tobit-1-gii",
    bookCode: "TOB",
    chapter: 1,
    title: "多俾亞傳 1（GII／Sinaiticus）：流亡中的虔敬",
    original: "Τωβίτ 1 (GII)",
    difficulty: 3,
    pages: 9,
    goals: ["只依 GII/Sinaiticus 定本精讀", "在註記中區分 GI 與 GII 異文"],
    source: tobitGiiSource,
    versionCode: "LXX-TOB-GII-S",
  },
  {
    id: "grc-lxx-judith-13",
    bookCode: "JDT",
    chapter: 13,
    title: "友弟德傳 13：行動、凱旋與祝福",
    original: "Ἰουδίθ 13",
    difficulty: 3,
    pages: 8,
    goals: ["分析動作密集敘事中的分詞鏈", "辨認戰爭、身體與祝福詞彙"],
  },
  {
    id: "grc-lxx-genesis-1",
    bookCode: "GEN",
    chapter: 1,
    title: "創世記 1：創造秩序",
    original: "Γένεσις 1",
    difficulty: 2,
    pages: 9,
    goals: ["追蹤重複公式與命令／實現結構", "與 MT 及拉丁文平行章比較"],
  },
  {
    id: "grc-lxx-genesis-22",
    bookCode: "GEN",
    chapter: 22,
    title: "創世記 22：亞伯拉罕受試驗",
    original: "Γένεσις 22",
    difficulty: 2,
    pages: 8,
    goals: ["分析命令、目的與直接引語", "比較 LXX 對關鍵希伯來詞的處理"],
  },
  {
    id: "grc-lxx-exodus-3",
    bookCode: "EXO",
    chapter: 3,
    title: "出埃及記 3：荊棘、呼召與神名",
    original: "Ἔξοδος 3",
    difficulty: 2,
    pages: 8,
    goals: ["精讀 ἐγώ εἰμι ὁ ὤν 的句法與翻譯史", "與 MT 及拉丁文平行章比較"],
  },
  {
    id: "grc-lxx-psalm-22",
    bookCode: "PSA",
    chapter: 22,
    verseFrom: 1,
    verseTo: 6,
    title: "詩篇 22 LXX（MT 23）：主是牧者",
    original: "Ψαλμός 22 (MT 23)",
    difficulty: 2,
    pages: 6,
    goals: [
      "最終正文必須包含 1–6 節全部經文，不得只放節選",
      "繁中譯文須逐節由編輯與第二位校者核對後才可標為完成",
      "只為已核對的關鍵詞加入詞位、形態與句法分析",
      "與 MT 23 及拉丁 Psalmus 22/23 比較編號與翻譯",
    ],
    tags: [
      "all-verses-required",
      "zh-tw-translation-pending-verification",
      "token-analysis-pending-verification",
      "no-unverified-segments",
    ],
  },
  {
    id: "grc-lxx-psalm-50",
    bookCode: "PSA",
    chapter: 50,
    title: "詩篇 50 LXX（MT 51）：憐憫與更新",
    original: "Ψαλμός 50 (MT 51)",
    difficulty: 3,
    pages: 8,
    goals: ["辨認祈求式、平行體與潔淨詞彙", "比較禮儀使用與 MT 編號"],
  },
  {
    id: "grc-lxx-isaiah-6",
    bookCode: "ISA",
    chapter: 6,
    title: "以賽亞書 6：寶座、聖哉與差遣",
    original: "Ἠσαΐας 6",
    difficulty: 3,
    pages: 7,
    goals: ["分析異象語彙與直接引語", "連結 Sanctus 與 Trisagion 的經文來源"],
  },
  {
    id: "grc-lxx-isaiah-7",
    bookCode: "ISA",
    chapter: 7,
    title: "以賽亞書 7：記號、危機與翻譯史",
    original: "Ἠσαΐας 7",
    difficulty: 4,
    pages: 8,
    goals: ["在上下文中分析 παρθένος", "區分詞義、翻譯史與後世引用"],
  },
  {
    id: "grc-lxx-1maccabees-1",
    bookCode: "1MA",
    chapter: 1,
    title: "馬加比一書 1：帝國、禁令與抵抗",
    original: "Μακκαβαίων Αʹ 1",
    difficulty: 3,
    pages: 11,
    goals: ["掌握希臘化政治與宗教詞彙", "追蹤時間標記與敘事壓縮"],
  },
  {
    id: "grc-lxx-2maccabees-7",
    bookCode: "2MA",
    chapter: 7,
    title: "馬加比二書 7：七兄弟殉道",
    original: "Μακκαβαίων Βʹ 7",
    difficulty: 4,
    pages: 11,
    goals: ["分析修辭性直接引語與殉道詞彙", "比較復活與創造語彙"],
  },
  {
    id: "grc-lxx-wisdom-7",
    bookCode: "WIS",
    chapter: 7,
    title: "所羅門智訓 7：智慧的本性與祈求",
    original: "Σοφία Σαλωμῶνος 7",
    difficulty: 4,
    pages: 10,
    goals: ["解析抽象名詞與長形容詞列", "比較猶太智慧傳統與希臘修辭"],
  },
  {
    id: "grc-lxx-sirach-24",
    bookCode: "SIR",
    chapter: 24,
    title: "德訓篇 24：智慧、創造與妥拉",
    original: "Σοφία Σιράχ 24",
    difficulty: 4,
    pages: 10,
    goals: ["追蹤智慧第一人稱論述", "標示希臘本、希伯來殘卷與章節差異"],
  },
] as const;

const lxxSelections: SelectionDraft[] = lxxSpecs.map((spec) => ({
  id: spec.id,
  partId: "septuagint",
  kind: "bible_chapter",
  title: spec.title,
  titleOriginal: spec.original,
  difficulty: spec.difficulty,
  track: spec.difficulty === 4 ? "advanced" : "core",
  estimatedPages: spec.pages,
  status: "planned",
  source: "source" in spec ? spec.source : lxxSource,
  scripture: {
    bookCode: spec.bookCode,
    chapter: spec.chapter,
    ...("verseFrom" in spec ? { verseFrom: spec.verseFrom } : {}),
    ...("verseTo" in spec ? { verseTo: spec.verseTo } : {}),
    versionCode: "versionCode" in spec ? spec.versionCode : "LXX-RH",
    parallelGroup: `${spec.bookCode.toLowerCase()}-${spec.chapter}`,
  },
  learningGoals: [...spec.goals, "完成逐節原文、繁中譯文、頁下注與句段音訊的校驗"],
  tags: [
    "septuagint",
    "full-chapter",
    "zh-tw-required",
    "aligned-audio",
    ...("tags" in spec ? spec.tags : []),
  ],
}));

const prayerSpecs = [
  ["trisagion", "三聖頌", "Ἅγιος ὁ Θεός", 1, 2, "core"],
  ["small-doxology", "小榮耀頌", "Δόξα Πατρὶ καὶ Υἱῷ", 1, 1, "core"],
  ["lords-prayer", "主禱文", "Πάτερ ἡμῶν", 1, 2, "core"],
  ["nicene-creed", "尼西亞－君士坦丁堡信經", "Πιστεύω εἰς ἕνα Θεόν", 3, 5, "core"],
  ["jesus-prayer", "耶穌禱文", "Κύριε Ἰησοῦ Χριστέ", 1, 1, "core"],
  ["heavenly-king", "天上的君王", "Βασιλεῦ οὐράνιε", 2, 2, "core"],
  ["holy-trinity", "至聖三一禱文", "Παναγία Τριάς, ἐλέησον ἡμᾶς", 2, 2, "core"],
  ["phos-hilaron", "歡慰之光", "Φῶς ἱλαρόν", 2, 2, "core"],
  ["only-begotten", "獨生子聖詩", "Ὁ Μονογενὴς Υἱός", 2, 2, "core"],
  ["axion-estin", "常當讚美你", "Ἄξιόν ἐστιν", 2, 2, "core"],
  ["theotokos-rejoice", "童貞誕神女，請喜樂", "Θεοτόκε Παρθένε, χαῖρε", 2, 2, "core"],
  ["ephrem-prayer", "聖厄弗冷四旬期禱文", "Κύριε καὶ Δέσποτα τῆς ζωῆς μου", 3, 3, "core"],
  ["great-doxology", "大榮耀頌", "Δόξα σοι τῷ δείξαντι τὸ φῶς", 3, 4, "advanced"],
  ["paschal-troparion", "逾越節讚詞", "Χριστὸς ἀνέστη", 1, 1, "advanced"],
  ["nativity-troparion", "聖誕節讚詞", "Ἡ γέννησίς σου, Χριστὲ ὁ Θεὸς ἡμῶν", 2, 2, "advanced"],
  ["theophany-troparion", "神顯節讚詞", "Ἐν Ἰορδάνῃ βαπτιζομένου σου", 2, 2, "advanced"],
  ["pentecost-troparion", "五旬節讚詞", "Εὐλογητὸς εἶ, Χριστὲ ὁ Θεὸς ἡμῶν", 2, 2, "advanced"],
  ["cross-troparion", "十字架讚詞", "Σῶσον, Κύριε, τὸν λαόν σου", 2, 2, "advanced"],
  ["resurrection-hymn", "既見基督復活", "Ἀνάστασιν Χριστοῦ θεασάμενοι", 3, 2, "advanced"],
  ["akathist-proem", "向護衛統帥", "Τῇ ὑπερμάχῳ στρατηγῷ", 3, 2, "advanced"],
] as const;

const prayerSelections: SelectionDraft[] = prayerSpecs.map(
  ([id, title, original, difficulty, pages, track]) => ({
    id: `grc-prayer-${id}`,
    partId: "prayers",
    kind: id === "nicene-creed" ? "creed" : "prayer",
    title,
    titleOriginal: original,
    difficulty,
    track,
    estimatedPages: pages,
    status: "planned",
    source: orthodoxPrayerSource,
    learningGoals: [
      "核對完整希臘文與繁中譯文後再入稿",
      "標示禮儀位置、語域、主要形態與神學術語",
      "完成拜占庭教會讀音；核心單元另製慢速教學音軌",
    ],
    tags: ["greek-prayer", id === "nicene-creed" ? "creed" : "hymn", "byzantine-audio"],
  }),
);

const liturgySpecs = [
  ["opening-great-litany", "開端祝福與大連禱", "Εὐλογημένη ἡ Βασιλεία · Εἰρηνικά", 2, 5, "core", ["priest", "deacon", "assembly"]],
  ["first-antiphon", "第一對經與第一對經祝文", "Ἀντίφωνον Αʹ", 2, 3, "core", ["priest", "assembly"]],
  ["second-antiphon", "小連禱、第二對經與祝文", "Ἀντίφωνον Βʹ", 2, 4, "core", ["priest", "deacon", "assembly"]],
  ["only-begotten", "獨生子聖詩", "Ὁ Μονογενὴς Υἱός", 2, 2, "core", ["assembly"]],
  ["third-antiphon", "小連禱、第三對經與祝文", "Ἀντίφωνον Γʹ", 2, 4, "core", ["priest", "deacon", "assembly"]],
  ["small-entrance", "小聖入與進堂祝文", "Μικρὰ Εἴσοδος", 2, 4, "core", ["priest", "deacon", "assembly"]],
  ["variable-hymn-frame", "進堂聖詠、節期讚詞與集禱的固定框架", "Εἰσοδικόν · Ἀπολυτίκια · Κοντάκιον", 2, 3, "reference", ["priest", "assembly"]],
  ["trisagion", "三聖頌與三聖祝文", "Τρισάγιος Ὕμνος", 2, 4, "core", ["priest", "deacon", "assembly"]],
  ["epistle-frame", "Prokeimenon、書信與 Alleluia 固定框架", "Προκείμενον · Ἀπόστολος · Ἀλληλούϊα", 2, 3, "reference", ["deacon", "reader", "assembly"]],
  ["gospel", "福音前祝文、宣讀對答與福音後對答", "Εὐαγγέλιον", 2, 4, "core", ["priest", "deacon", "assembly"]],
  ["fervent-litany", "熱切祈禱連禱", "Ἐκτενὴς Ἱκεσία", 3, 4, "advanced", ["priest", "deacon", "assembly"]],
  ["catechumens", "慕道者連禱、祝文與遣散", "Εὐχὴ ὑπὲρ τῶν Κατηχουμένων", 3, 4, "advanced", ["priest", "deacon", "assembly"]],
  ["faithful-first", "信友第一連禱與祝文", "Εὐχὴ Πιστῶν Αʹ", 3, 3, "advanced", ["priest", "deacon"]],
  ["faithful-second", "信友第二連禱與祝文", "Εὐχὴ Πιστῶν Βʹ", 3, 3, "advanced", ["priest", "deacon"]],
  ["cherubic-hymn", "基路伯之歌與大聖入祝文", "Χερουβικὸς Ὕμνος", 3, 5, "core", ["priest", "deacon", "assembly"]],
  ["great-entrance", "大聖入、紀念與奉獻完成連禱", "Μεγάλη Εἴσοδος · Πληρωτικὰ", 3, 5, "core", ["priest", "deacon", "assembly"]],
  ["kiss-creed", "平安之吻與信經", "Ἀγαπήσωμεν ἀλλήλους · Πιστεύω", 3, 5, "core", ["priest", "deacon", "assembly"]],
  ["anaphora-dialogue", "感恩祭典開端對答", "Ἡ Ἁγία Ἀναφορά", 2, 3, "core", ["priest", "deacon", "assembly"]],
  ["anaphora-preface", "感恩序文與天使頌讚", "Ἄξιον καὶ δίκαιον", 4, 5, "advanced", ["priest"]],
  ["sanctus-postsanctus", "聖哉經與聖哉經後祝文", "Ἅγιος, Ἅγιος, Ἅγιος", 3, 4, "core", ["priest", "assembly"]],
  ["institution", "建立聖體敘事", "Λάβετε, φάγετε · Πίετε ἐξ αὐτοῦ πάντες", 3, 4, "core", ["priest", "deacon", "assembly"]],
  ["anamnesis-offering", "紀念與奉獻", "Μεμνημένοι τοίνυν · Τὰ σὰ ἐκ τῶν σῶν", 4, 4, "advanced", ["priest", "assembly"]],
  ["epiclesis", "聖靈降臨祈禱", "Κατάπεμψον τὸ Πνεῦμά σου τὸ Ἅγιον", 4, 5, "advanced", ["priest", "deacon"]],
  ["intercessions", "為教會、生者與亡者的紀念祈禱", "Ἔτι προσφέρομέν σοι", 4, 6, "advanced", ["priest", "deacon", "assembly"]],
  ["theotokos-megalynarion", "誕神女紀念與稱揚頌", "Ἐξαιρέτως · Ἄξιόν ἐστιν", 3, 3, "core", ["priest", "assembly"]],
  ["anaphora-conclusion", "感恩祭典代禱結語與頌榮", "Καὶ δὸς ἡμῖν ἐν ἑνὶ στόματι", 4, 4, "advanced", ["priest", "deacon", "assembly"]],
  ["pre-lords-prayer", "主禱文前連禱與祝文", "Πάντων τῶν ἁγίων μνημονεύσαντες", 3, 4, "advanced", ["priest", "deacon", "assembly"]],
  ["lords-prayer", "主禱文與頌榮", "Πάτερ ἡμῶν", 2, 3, "core", ["priest", "assembly"]],
  ["bowing-heads", "平安、俯首與俯首祝文", "Εἰρήνη πᾶσι · Τὰς κεφαλὰς ἡμῶν", 3, 3, "advanced", ["priest", "deacon", "assembly"]],
  ["holy-things-fraction", "聖物歸於聖者、擘餅與注入熱水", "Τὰ ἅγια τοῖς ἁγίοις", 4, 5, "advanced", ["priest", "deacon", "assembly"]],
  ["precommunion", "領聖體前禱文與信仰宣認", "Πιστεύω, Κύριε, καὶ ὁμολογῶ", 3, 4, "core", ["priest", "deacon"]],
  ["clergy-communion", "司祭與執事領聖體", "Μεταλαμβάνει ὁ ἱερεύς", 4, 4, "advanced", ["priest", "deacon"]],
  ["faithful-communion", "信友領聖體與領受聖體聖詠", "Μετὰ φόβου Θεοῦ", 3, 5, "core", ["priest", "deacon", "assembly"]],
  ["postcommunion", "領聖體後感恩、連禱與祝文", "Ὀρθοί, μεταλαβόντες", 3, 4, "core", ["priest", "deacon", "assembly"]],
  ["ambo-prayer", "台後祝文", "Εὐχὴ ὀπισθάμβωνος", 3, 3, "advanced", ["priest", "assembly"]],
  ["dismissal", "祝福、遣散與禮成", "Εἴη τὸ ὄνομα Κυρίου · Ἀπόλυσις", 3, 4, "core", ["priest", "deacon", "assembly"]],
] as const;

const liturgySelections: SelectionDraft[] = liturgySpecs.map(
  ([id, title, original, difficulty, pages, track, roles]) => ({
    id: `grc-liturgy-chrysostom-${id}`,
    partId: "chrysostom-liturgy",
    kind: "liturgy",
    title,
    titleOriginal: original,
    difficulty,
    track,
    estimatedPages: pages,
    status: "source_ready",
    source: goarchLiturgySource,
    learningGoals: [
      "保留司祭、執事、讀經員與會眾角色，不刪除低聲祝文",
      "固定經文完整收錄；可變經文以明確插槽與一個完整主日實例處理",
      "完成拜占庭教會讀音的分角色音訊與逐句 cue",
    ],
    tags: ["chrysostom-liturgy", "fixed-text", ...roles.map((role) => `role:${role}`)],
  }),
);

const patristicCoreSpecs = [
  ["didache-two-ways", "《十二使徒遺訓》1.1–2.1：兩條道路", "Διδαχή 1.1–2.1", 2, 4],
  ["didache-prayer-eucharist", "《十二使徒遺訓》8–10：禁食、主禱文與感恩禱", "Διδαχή 8–10", 2, 6],
  ["1clement-13", "革利免一書 13.1–4：謙卑與互待", "Πρὸς Κορινθίους Αʹ 13.1–4", 2, 3],
  ["ignatius-romans-4-5", "安提阿的依納爵《致羅馬人》4–5：殉道意象", "Πρὸς Ῥωμαίους 4–5", 2, 4],
  ["martyrdom-polycarp-9-12", "《坡旅甲殉道記》9–12：審訊與見證", "Μαρτύριον Πολυκάρπου 9–12", 2, 6],
  ["justin-apology-61", "游斯丁《第一護教辭》61：洗禮", "Ἀπολογία πρώτη 61", 2, 4],
  ["justin-apology-65-67", "游斯丁《第一護教辭》65–67：聖餐與主日聚會", "Ἀπολογία πρώτη 65–67", 2, 7],
  ["origen-prayer-13", "俄利根《論祈禱》13.1–3：我們在天上的父", "Περὶ εὐχῆς 13.1–3", 3, 4],
  ["athanasius-incarnation-54", "亞他那修《論道成肉身》54.1–3：成為人與神化", "Περὶ ἐνανθρωπήσεως 54.1–3", 2, 3],
  ["apophthegmata-antony-1-5", "《沙漠教父語錄》安東尼 1–5", "Ἀποφθέγματα Πατέρων, Ἀντώνιος 1–5", 2, 5],
  ["cyril-mystagogy-1", "耶路撒冷的區利羅《奧秘教理》1.1–3：洗禮的意義", "Μυσταγωγικὴ Κατήχησις Αʹ 1.1–3", 2, 5],
  ["chrysostom-matthew-50", "金口若望《馬太福音講道》50.3–4：聖體與窮人", "Ὁμιλία Νʹ εἰς Ματθαῖον 3–4", 3, 7],
] as const;

const patristicAdvancedSpecs = [
  ["clement-protrepticus-1", "亞歷山大的革利免《勸勉希臘人》1.1–3：新的歌", "Προτρεπτικὸς πρὸς Ἕλληνας 1.1–3", 4, 5],
  ["basil-holy-spirit-9", "該撒利亞的巴西流《論聖靈》9.22–23", "Περὶ τοῦ Ἁγίου Πνεύματος 9.22–23", 4, 5],
  ["gregory-nazianzen-oration-27", "納齊安的貴格利《神學講辭》27.3–4", "Λόγος ΚΖʹ Θεολογικός 3–4", 4, 5],
  ["gregory-nyssa-life-moses", "尼撒的貴格利《摩西生平》II.162–169：幽暗中的認識", "Περὶ τοῦ βίου Μωυσέως II.162–169", 4, 6],
  ["cyril-third-letter", "亞歷山大的區利羅《致聶斯多留第三書》譴責條文 1–3", "Τρίτη ἐπιστολὴ πρὸς Νεστόριον, ἀναθεματισμοί 1–3", 4, 5],
  ["pseudo-dionysius-mystical-theology", "偽狄奧尼修《神秘神學》1.1–3", "Περὶ μυστικῆς θεολογίας 1.1–3", 4, 6],
  ["maximus-centuries-love", "認信者馬克西姆《愛德百章》I.1–10", "Κεφάλαια περὶ ἀγάπης I.1–10", 4, 5],
  ["john-damascene-orthodox-faith", "大馬士革的約翰《正統信仰詳解》I.8 節選", "Ἔκδοσις ἀκριβὴς τῆς ὀρθοδόξου πίστεως I.8", 4, 7],
] as const;

const patristicSelections: SelectionDraft[] = [
  ...patristicCoreSpecs.map(([id, title, original, difficulty, pages]) => ({
    id: `grc-patristic-${id}`,
    partId: "patristic-core",
    kind: "patristic" as const,
    title,
    titleOriginal: original,
    difficulty,
    track: "core" as const,
    estimatedPages: pages,
    status: "planned" as const,
    source: patristicSource(title),
    learningGoals: [
      "以可靠希臘文版本定本並保留標準章節號",
      "提供繁中譯文、語域說明與關鍵句法註解",
      "以拜占庭教會讀音錄自然速度；必要時另加慢速軌",
    ],
    tags: ["greek-fathers", "patristic-core", "critical-edition-required"],
  })),
  ...patristicAdvancedSpecs.map(([id, title, original, difficulty, pages]) => ({
    id: `grc-patristic-${id}`,
    partId: "patristic-advanced",
    kind: "patristic" as const,
    title,
    titleOriginal: original,
    difficulty,
    track: "advanced" as const,
    estimatedPages: pages,
    status: "planned" as const,
    source: patristicSource(title),
    learningGoals: [
      "以可靠希臘文版本定本並保留標準章節號",
      "繪製長句或技術概念結構，不把神學術語縮成單一中文對應",
      "配置高密度頁下注，作為第二年或高階課程選讀",
    ],
    tags: ["greek-fathers", "patristic-advanced", "critical-edition-required"],
  })),
];

const selectionDrafts: SelectionDraft[] = [
  ...orientationSelections,
  ...vocabularyCurriculumSelections,
  ...vocabularySelections,
  ...memorySelections,
  ...ntSelections,
  ...lxxSelections,
  ...prayerSelections,
  ...liturgySelections,
  ...patristicSelections,
  ...referenceSelections,
];

const selections: OriginalReaderSelection[] = selectionDrafts.map(
  (selection, index) => ({
    ...selection,
    ordinal: index + 1,
  }),
);

export const greekOriginalReader: OriginalReaderVolume = {
  id: "original-reader-grc",
  slug: "grc",
  language: "grc",
  title: "希臘文原典讀本",
  subtitle: "新約、七十士譯本、東方禮儀與希臘教父：B5 私人學習版",
  privateUse: true,
  rtl: false,
  print: JIS_B5_READER_PROFILE,
  pronunciationProfiles: [
    {
      id: "mounce-erasmian-pedagogical",
      label: "Mounce 教科書式／Erasmian",
      description:
        "用於一千詞表的課本式音譯與字母辨讀；官方參考頁提供字母及發音示範，不以 el-GR 現代裝置語音代替。",
      referenceUrl: "https://www.billmounce.com/greek-alphabet",
    },
    {
      id: "reconstructed-koine",
      label: "重建通用希臘語",
      description: "用於新約與七十士譯本的教學慢速及自然速度音軌；實際規約須在錄音前另立說明。",
    },
    {
      id: "byzantine-ecclesiastical",
      label: "拜占庭／教會希臘語",
      description: "用於祈禱、金口若望禮與教父選文，保留禮儀角色及詠唱音軌。",
    },
  ],
  textPolicy: {
    scriptStandard: "Unicode NFC 的 polytonic Koine／Byzantine Greek 正文",
    requiredMarks: [
      "保留底本的呼氣記號、銳音／抑音／揚抑音與 iota subscript",
      "版本所載的標點、段落與 textual variants 必須可追溯至 selection source 及 textualNotes",
    ],
    prohibitedSubstitutions: [
      "不得以 monotonic modern Greek 或 transliteration 取代 polytonic 原文",
      "不得因只分析部分 tokens 而截斷、重建或取代完整 sourceText",
      "不得把 normalized／lemma 查找鍵冒充實際 surface form",
    ],
    notes:
      "sourceText 永遠完整顯示；tokens 僅另列已校驗的關鍵詞。新約、LXX、禮儀與教父文本各自保留明確版本邊界，異文放入 textualNotes。",
  },
  vocabularyCurriculum: {
    lessonCount: 20,
    wordsPerLesson: 50,
    orderingRule:
      "一千詞位分為二十個五十詞單元：前 340 詞保留 Mounce BBG 章序，後 660 詞保留 Mounce 官方頻率延伸次序。A Graded Reader 只作二十篇進階閱讀路徑，不冒充另一套詞彙排序。本頁是這一千詞的課程規劃；實際做出來的讀本已擴為兩冊兩千詞（上冊新約與七十士譯本、下冊教父文獻與希臘教會文獻），見 /original-readers/grc-lessons。",
    primarySources: [
      "William D. Mounce, Basics of Biblical Greek 官方 1,000 詞表（340 詞 BBG 章序＋660 詞官方頻率延伸）",
      "William D. Mounce, A Graded Reader of Biblical Greek（只作二十篇進階閱讀路徑，不作本詞表排序來源）",
    ],
    exactOrderingStatus: "verified",
  },
  parts: [
    {
      id: "orientation",
      ordinal: 1,
      title: "導論：文字、讀音與版本",
      description: "建立不依賴轉寫的辨讀能力，並明示兩套發音規約與底本邊界。",
    },
    {
      id: "vocabulary",
      ordinal: 2,
      title: "一千核心詞位（讀本上冊）",
      description:
        "二十組 × 50 詞已接入：340 詞依 BBG 章序，660 詞依 Mounce 官方頻率延伸；逐詞顯示來源、Strong 與核驗狀態。A Graded Reader 另作進階讀文路徑。這一千詞構成兩冊讀本的上冊；下冊另一千詞取教父與希臘教會文獻語料，與上冊不重複。",
    },
    {
      id: "memory",
      ordinal: 3,
      title: "一百個脈絡化記憶單元",
      description: "十組各十單元；每單元 4–12 詞，均取自本冊已校驗文本。",
    },
    {
      id: "new-testament",
      ordinal: 4,
      title: "新約十五章",
      description: "由敘事與約翰短句進入保羅論證、希伯來書與啟示錄。",
    },
    {
      id: "septuagint",
      ordinal: 5,
      title: "七十士譯本與次經十五章",
      description: "涵蓋翻譯敘事、詩篇、先知、歷史與智慧文本；嚴格標明編號與版本。",
    },
    {
      id: "prayers",
      ordinal: 6,
      title: "二十篇祈禱、信經與聖詠",
      description: "從短禱與主禱文，進入信經、節期讚詞與長篇禮儀聖詠。",
    },
    {
      id: "chrysostom-liturgy",
      ordinal: 7,
      title: "金口若望事奉聖禮：固定全文",
      description: "從開端祝福至遣散，保留所有角色、低聲祝文與可變經文插槽。",
    },
    {
      id: "patristic-core",
      ordinal: 8,
      title: "希臘教父選讀：正文核心十二則",
      description: "由使徒教父、護教家與早期教理文本進入亞他那修、區利羅與金口若望。",
    },
    {
      id: "patristic-advanced",
      ordinal: 9,
      title: "希臘教父選讀：進階附錄八則",
      description: "卡帕多家、基督論、神秘神學與拜占庭綜合；供第二年或高階選讀。",
    },
    {
      id: "reference",
      ordinal: 10,
      title: "形態、句法、語域與索引",
      description: "提供紙本速查、LXX/MT 編號、橋接詞彙、詞位與音訊 ID 索引。",
    },
  ],
  selections,
};

export default greekOriginalReader;
