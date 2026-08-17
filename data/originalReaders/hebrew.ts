import {
  JIS_B5_READER_PROFILE,
  type OriginalReaderSegment,
  type OriginalReaderSelection,
  type OriginalReaderSource,
  type OriginalReaderToken,
  type OriginalReaderVolume,
} from "./types";
import hebrewVocabularyJson from "./vocabulary/hebrew-1000.json";

const AUDIO_PROFILE_ID = "biblical-masoretic-pedagogical";
const POINTED_TEXT_REQUIREMENT =
  "正文必須使用帶完整 niqqud 的教學文本；Tanakh 依底本保留必要 cantillation，不得以無母音的現代希伯來文拼法代替。";
const COMMON_TAGS = [
  "hbo",
  "pointed-hebrew-required",
  `audio:${AUDIO_PROFILE_ID}`,
];

const BBH_SOURCE: OriginalReaderSource = {
  edition:
    "Gary D. Pratico & Miles V. Van Pelt, Basics of Biblical Hebrew Grammar, 2nd ed.（BBH2 詞序，後接讀本頻率延伸）",
  editor: "Gary D. Pratico; Miles V. Van Pelt",
  sourceUrl: "https://hebrewsyntax.org/bbh2new/",
  versionCode: "BBH2-VOCAB-1000-PRIVATE",
  licenseNote:
    "已由私人授權的本機詞表接入 1,000 詞：前 552 詞保留 BBH2 原始次序，後 448 詞依讀本語料頻率延伸。每詞的來源類型、課次、Strong 與核驗狀態均原樣保留。",
  authorization: "private-authorized",
};

const MEMORY_SOURCE: OriginalReaderSource = {
  edition: "本卷選文衍生背誦課程（100 單元；20 組 × 5）",
  licenseNote:
    "只建立背誦單元槽位。每句須在來源選文、版本及授權確定後才可填入；不得由記憶補寫原文。",
  authorization: "private-authorized",
};

const WLC_SOURCE: OriginalReaderSource = {
  edition: "Westminster Leningrad Codex (WLC), Open Scriptures MorphHB",
  editor: "Westminster Hebrew Institute / Open Scriptures",
  sourceUrl: "https://github.com/openscriptures/morphhb",
  versionCode: "wlc",
  licenseNote:
    "希伯來經文文字為公版；MorphHB 詞法與詞元標註依 CC BY 4.0。印刷與線上版均須保存來源與 attribution。",
  authorization: "private-authorized",
};

const SIDDUR_SOURCE: OriginalReaderSource = {
  edition:
    "Traditional Jewish Liturgy / Siddur（nusach 與實際版本須在正文錄入前鎖定）",
  licenseNote:
    "傳統禱文的具體編排、標點、母音點、翻譯與現代校訂仍可能受版本權利限制；目前僅建立目錄，不含未核權正文。",
  authorization: "private-authorized",
};

const HAGGADAH_SOURCE: OriginalReaderSource = {
  edition:
    "Traditional Passover Haggadah（完整十五步；實際 nusach 與版本須在正文錄入前鎖定）",
  licenseNote:
    "傳統核心文本與現代編排、母音、翻譯、註釋、插圖的權利須分別審核；目前只建立十五步完整目錄。",
  authorization: "private-authorized",
};

const MISHNAH_SOURCE: OriginalReaderSource = {
  edition: "Mishnah（正文版本與分節系統待鎖定）",
  licenseNote:
    "目前只記錄指定 tractate/section；錄入前須選定可合法使用的原文版本並核對分節、niqqud 與校勘責任。",
  authorization: "private-authorized",
};

const HALAKHIC_MIDRASH_SOURCE: OriginalReaderSource = {
  edition: "Tannaitic Halakhic Midrash（指定段落；正文版本待鎖定）",
  licenseNote:
    "目前只建立指定段落的目錄。正文、教學母音與翻譯須由合法版本核對並記錄編者責任。",
  authorization: "private-authorized",
};

const GENESIS_RABBAH_SOURCE: OriginalReaderSource = {
  edition: "Genesis Rabbah（正文版本與分節系統待鎖定）",
  licenseNote:
    "目前只建立指定段落的目錄；錄入前須核對版本、分節、希伯來文／亞蘭文語層與權利。",
  authorization: "private-authorized",
};

const BAVLI_SOURCE: OriginalReaderSource = {
  edition: "Babylonian Talmud（daf/amud 參照；正文版本待鎖定）",
  licenseNote:
    "目前只建立指定 daf/amud 的目錄。正文、分行、教學母音與翻譯須由合法版本核對；不得把現代標點或母音層冒充抄本原貌。",
  authorization: "private-authorized",
};

const difficultyForVocabLesson = (
  lesson: number,
): OriginalReaderSelection["difficulty"] => {
  if (lesson <= 15) return 1;
  if (lesson <= 30) return 2;
  if (lesson <= 40) return 3;
  return 4;
};

interface HebrewVocabularyEntry {
  ordinal: number;
  pointed: string;
  sourcePointed: string;
  unpointed: string;
  textbookTransliteration: string;
  transliterationSystem: string;
  transliterationStatus: string;
  glossEn: string;
  glossZh: string;
  sourceType: string;
  sourceChapter: number | null;
  sourceOrder: number | null;
  sourceOrders: number[];
  frequency: number | null;
  strong: string;
  strongs: string[];
  partOfSpeech: string;
  isProperName: boolean;
  properNameTypes: string[];
  verification: string;
  lesson: number;
  lessonSlot: number;
}

const HEBREW_VOCABULARY = hebrewVocabularyJson as HebrewVocabularyEntry[];

if (HEBREW_VOCABULARY.length !== 1000) {
  throw new Error(
    `Hebrew reader vocabulary must contain 1,000 entries; received ${HEBREW_VOCABULARY.length}.`,
  );
}

function vocabularyEntriesForLesson(lesson: number): HebrewVocabularyEntry[] {
  const entries = HEBREW_VOCABULARY
    .filter((entry) => entry.lesson === lesson)
    .sort((left, right) => left.lessonSlot - right.lessonSlot);
  // Lesson size follows the textbook, not a quota: BBH2 chapters 3–35 become
  // lessons 1–33 at their real (uneven) sizes, and the frequency extension
  // fills lessons 34–50.  Only continuity of slots is invariant.
  if (
    entries.length === 0 ||
    entries.some((entry, index) => entry.lessonSlot !== index + 1)
  ) {
    throw new Error(`Hebrew vocabulary lesson ${lesson} has a broken slot sequence.`);
  }
  return entries;
}

function hebrewVocabularyToken(
  entry: HebrewVocabularyEntry,
  lessonId: string,
): OriginalReaderToken {
  return {
    id: `hbo-vocab-${lessonId}-w${String(entry.lessonSlot).padStart(2, "0")}`,
    ordinal: entry.lessonSlot,
    surface: entry.pointed,
    lemmaPointed: entry.pointed,
    lemmaUnpointed: entry.unpointed,
    normalized: entry.unpointed,
    lemma: entry.pointed,
    reading: entry.textbookTransliteration,
    textbookTransliteration: entry.textbookTransliteration,
    transliterationSystem: entry.transliterationSystem,
    transliterationStatus: entry.transliterationStatus,
    glossEn: entry.glossEn,
    glossZh: entry.glossZh,
    partOfSpeech: entry.partOfSpeech,
    strong: entry.strong || undefined,
    strongs: entry.strongs.length ? entry.strongs : undefined,
    isProperName: entry.isProperName,
    properNameTypes: entry.properNameTypes,
    sourceType: entry.sourceType,
    sourceChapter: entry.sourceChapter ?? undefined,
    sourceOrder: entry.sourceOrder ?? undefined,
    sourceOrders: entry.sourceOrders.length ? entry.sourceOrders : undefined,
    frequency: entry.frequency ?? undefined,
    lesson: entry.lesson,
    lessonSlot: entry.lessonSlot,
    verification: entry.verification,
  };
}

const vocabularySelections: OriginalReaderSelection[] = Array.from(
  { length: 50 },
  (_, index) => {
    const lesson = index + 1;
    const lessonId = String(lesson).padStart(2, "0");
    const entries = vocabularyEntriesForLesson(lesson);
    const firstSlot = entries[0].ordinal;
    const lastSlot = entries[entries.length - 1].ordinal;
    const wordCount = entries.length;
    const textbookChapter = entries[0].sourceType === "bbh2_order" ? entries[0].sourceChapter : null;
    return {
      id: `hbo-vocab-${lessonId}`,
      ordinal: lesson,
      partId: "hbo-part-vocabulary",
      kind: "vocabulary",
      title: `核心詞彙第 ${lessonId} 課（${wordCount} 字）`,
      subtitle: textbookChapter
        ? `BBH2 第 ${textbookChapter} 章全部 ${wordCount} 詞（總第 ${firstSlot}–${lastSlot} 詞）；逐詞保留來源與核驗狀態`
        : `頻率延伸 ${wordCount} 詞（總第 ${firstSlot}–${lastSlot} 詞）；逐詞保留來源與核驗狀態`,
      difficulty: difficultyForVocabLesson(lesson),
      track: "reference",
      estimatedPages: 2,
      status: "source_ready",
      source: BBH_SOURCE,
      segments: [
        {
          id: `hbo-vocab-${lessonId}-words`,
          ordinal: 1,
          ref: `BBH vocabulary lesson ${lesson}`,
          sourceText: entries.map((entry) => entry.pointed).join(" "),
          translationZh: "",
          tokens: entries.map((entry) => hebrewVocabularyToken(entry, lessonId)),
          textualNotes: [
            "所有原文字形保留完整 niqqud；無點字形只供索引，不取代畫面與讀本中的附點原文。",
            "課本式音譯為規則產生並保留逐詞核驗狀態；未核定項目不冒充人工定稿。",
          ],
        },
      ],
      learningGoals: [
        `依 Pratico–Van Pelt BBH2 課序與明確標記的讀本頻率延伸掌握本課 ${wordCount} 個詞。`,
        "分別辨識 pointed surface、pointed lemma 與只供搜尋的 unpointed lookup key。",
        POINTED_TEXT_REQUIREMENT,
      ],
      tags: [
        ...COMMON_TAGS,
        "vocabulary",
        "bbh",
        textbookChapter ? `bbh2-chapter:${textbookChapter}` : "frequency-extension",
        `words:${wordCount}`,
        "source-loaded",
        "per-entry-verification",
        `slots:${firstSlot}-${lastSlot}`,
      ],
    };
  },
);

const memorySelections: OriginalReaderSelection[] = Array.from(
  { length: 20 },
  (_, index) => {
    const group = index + 1;
    const firstUnit = index * 5 + 1;
    const lastUnit = firstUnit + 4;
    const groupId = String(group).padStart(2, "0");
    return {
      id: `hbo-memory-${groupId}`,
      ordinal: vocabularySelections.length + group,
      partId: "hbo-part-memory",
      kind: "memory_unit",
      title: `背誦單元第 ${groupId} 組（5 段）`,
      subtitle: `背誦單元 ${firstUnit}–${lastUnit}；由本卷定稿選文抽取`,
      difficulty:
        group <= 5 ? 1 : group <= 12 ? 2 : group <= 17 ? 3 : 4,
      track: "core",
      estimatedPages: 2,
      status: "planned",
      source: MEMORY_SOURCE,
      learningGoals: [
        "背誦五個已核定來源、版本及斷句的完整語意單元。",
        "朗讀、默寫與回譯使用同一穩定 segment id，供紙本與線上音訊共用。",
        POINTED_TEXT_REQUIREMENT,
      ],
      tags: [
        ...COMMON_TAGS,
        "memory",
        "five-units",
        `units:${firstUnit}-${lastUnit}`,
      ],
    };
  },
);

const psalm23Segments: OriginalReaderSegment[] = [
  {
    id: "hbo-psa-23-01",
    ordinal: 1,
    ref: "Psalm 23:1",
    sourceText: "יְהוָה רֹעִי לֹא אֶחְסָר׃",
    translationZh: "上主是我的牧者，我不致匱乏。",
    textualNotes: [
      "本行逐字核對自 server/data/coachPassages.ts 的 hbo-ps23-1 本機樣本；該樣本沒有詩題，正式 WLC 匯入時須確認是否補入 מִזְמוֹר לְדָוִד。",
      "繁中為本讀本工作譯，待全章校勘。",
    ],
    tokens: [
      {
        id: "hbo-psa-23-01-t02",
        ordinal: 2,
        surface: "רֹעִי",
        normalized: "רעי",
        lemma: "רֹעִי",
        glossZh: "我的牧者",
        syntaxNote:
          "本機樣本只核實 pointed surface 與語意；lemma 暫以 pointed surface 佔位，normalized 為無點查找鍵，正式詞元與附屬字尾分析待 MorphHB 匯入。",
      },
    ],
  },
  {
    id: "hbo-psa-23-02",
    ordinal: 2,
    ref: "Psalm 23:2",
    sourceText: "",
    translationZh: "祂使我安臥青草牧場，領我到安歇的水邊。",
    textualNotes: [
      "本回合無法讀取本機 WLC canonical gzip；依要求保留空字串，待 corpus 匯入後再填，不由記憶重建希伯來原文。",
      "繁中為本讀本工作譯，待原文匯入後逐詞校勘。",
    ],
  },
  {
    id: "hbo-psa-23-03",
    ordinal: 3,
    ref: "Psalm 23:3",
    sourceText: "",
    translationZh: "祂使我的生命復甦，為自己的名引導我走正義的路。",
    textualNotes: [
      "本回合無法讀取本機 WLC canonical gzip；依要求保留空字串，待 corpus 匯入後再填，不由記憶重建希伯來原文。",
      "繁中為本讀本工作譯，待原文匯入後逐詞校勘。",
    ],
  },
  {
    id: "hbo-psa-23-04",
    ordinal: 4,
    ref: "Psalm 23:4",
    sourceText: "",
    translationZh:
      "即使我走在深暗的幽谷，也不怕災禍，因為祢與我同在；祢的杖、祢的竿安慰我。",
    textualNotes: [
      "本回合無法讀取本機 WLC canonical gzip；依要求保留空字串，待 corpus 匯入後再填，不由記憶重建希伯來原文。",
      "繁中為本讀本工作譯；צַלְמָוֶת 的譯法須在全文詞彙政策中統一。",
    ],
  },
  {
    id: "hbo-psa-23-05",
    ordinal: 5,
    ref: "Psalm 23:5",
    sourceText:
      "תַּעֲרֹ֬ךְ לְפָנַ֨י׀ שֻׁלְחָ֗ן נֶ֥גֶד צֹרְרָ֑י דִּשַּׁ֖נְתָּ בַשֶּׁ֥מֶן רֹ֝אשִׁ֗י כּוֹסִ֥י רְוָיָֽה׃",
    translationZh:
      "祢在敵人面前為我擺設筵席，以油使我的頭豐潤；我的杯滿溢。",
    textualNotes: [
      "本行核對自 server/data/parseHebrew.json 的詩篇 23.5 TAHOT verse_words；只移除 harvester 用來標示分隔符的反斜線，保留 niqqud 與 cantillation。",
      "繁中為本讀本工作譯，待 WLC canonical corpus 逐字複核。",
    ],
    tokens: [
      {
        id: "hbo-psa-23-05-t06",
        ordinal: 6,
        surface: "דִּשַּׁ֖נְתָּ",
        normalized: "דשנת",
        lemma: "דִּשַּׁ֖נְתָּ",
        reading: "di.Shan.ta",
        glossZh: "你使……豐潤／更新",
        partOfSpeech: "動詞",
        morphology: {
          stem: "Piel",
          conjugation: "完成式",
          person: "第二",
          gender: "陽性",
          number: "單數",
          sourceCode: "HVpp2ms",
        },
        syntaxNote:
          "形態碼與 reading 來自本機 TAHOT 樣本；該 harvester 未提供真正 lemma，故 lemma 暫保留 pointed surface，正式匯入時須改為 pointed lexeme。",
      },
    ],
  },
  {
    id: "hbo-psa-23-06",
    ordinal: 6,
    ref: "Psalm 23:6",
    sourceText: "",
    translationZh:
      "一生一世，恩惠與慈愛必追隨我；我要住在上主的殿中，直到年日長久。",
    textualNotes: [
      "本回合無法讀取本機 WLC canonical gzip；依要求保留空字串，待 corpus 匯入後再填，不由記憶重建希伯來原文。",
      "繁中為本讀本工作譯；וְשַׁבְתִּי 的讀法與譯法須依所選底本校勘。",
    ],
  },
];

interface BibleSeed {
  id: string;
  title: string;
  titleOriginal: string;
  bookCode: string;
  chapter: number;
  difficulty: OriginalReaderSelection["difficulty"];
  track: OriginalReaderSelection["track"];
  estimatedPages: number;
  learningGoals: string[];
  tags: string[];
  status?: OriginalReaderSelection["status"];
  segments?: OriginalReaderSegment[];
}

const BIBLE_SEEDS: BibleSeed[] = [
  {
    id: "hbo-tanakh-jon-01",
    title: "約拿書 1：逃避、風暴與抽籤",
    titleOriginal: "יוֹנָה 1",
    bookCode: "jon",
    chapter: 1,
    difficulty: 2,
    track: "core",
    estimatedPages: 7,
    learningGoals: ["追蹤敘事動詞鏈、方向動詞與水手對話。"],
    tags: ["jonah", "narrative", "dialogue"],
  },
  {
    id: "hbo-tanakh-jon-03",
    title: "約拿書 3：宣告與尼尼微的回應",
    titleOriginal: "יוֹנָה 3",
    bookCode: "jon",
    chapter: 3,
    difficulty: 1,
    track: "core",
    estimatedPages: 4,
    learningGoals: ["熟悉簡短敘事、宣告公式與群體回應詞彙。"],
    tags: ["jonah", "narrative", "proclamation"],
  },
  {
    id: "hbo-tanakh-jon-04",
    title: "約拿書 4：憐憫、忿怒與民族邊界",
    titleOriginal: "יוֹנָה 4",
    bookCode: "jon",
    chapter: 4,
    difficulty: 2,
    track: "core",
    estimatedPages: 5,
    learningGoals: ["分析反問句、情緒詞彙及植物意象的敘事功能。"],
    tags: ["jonah", "narrative", "rhetorical-question"],
  },
  {
    id: "hbo-tanakh-rut-01",
    title: "路得記 1：遷徙、失落與盟誓",
    titleOriginal: "רוּת 1",
    bookCode: "rut",
    chapter: 1,
    difficulty: 2,
    track: "core",
    estimatedPages: 8,
    learningGoals: ["掌握家族、遷徙、返鄉與盟誓語彙。"],
    tags: ["ruth", "narrative", "kinship"],
  },
  {
    id: "hbo-tanakh-rut-02",
    title: "路得記 2：拾穗、恩惠與田間對話",
    titleOriginal: "רוּת 2",
    bookCode: "rut",
    chapter: 2,
    difficulty: 2,
    track: "core",
    estimatedPages: 8,
    learningGoals: ["辨識拾穗律例背景、祝福公式與禮貌對話。"],
    tags: ["ruth", "narrative", "gleaning"],
  },
  {
    id: "hbo-tanakh-rut-03",
    title: "路得記 3：禾場、請贖與指令鏈",
    titleOriginal: "רוּת 3",
    bookCode: "rut",
    chapter: 3,
    difficulty: 2,
    track: "core",
    estimatedPages: 7,
    learningGoals: ["追蹤命令式、連續動作與親屬贖回語彙。"],
    tags: ["ruth", "narrative", "redemption"],
  },
  {
    id: "hbo-tanakh-rut-04",
    title: "路得記 4：城門、贖回與家譜",
    titleOriginal: "רוּת 4",
    bookCode: "rut",
    chapter: 4,
    difficulty: 2,
    track: "core",
    estimatedPages: 9,
    learningGoals: ["閱讀法律交易、見證公式、祝福與家譜句式。"],
    tags: ["ruth", "legal-narrative", "genealogy"],
  },
  {
    id: "hbo-tanakh-1sa-03",
    title: "撒母耳記上 3：撒母耳蒙召",
    titleOriginal: "שְׁמוּאֵל א׳ 3",
    bookCode: "1sa",
    chapter: 3,
    difficulty: 2,
    track: "core",
    estimatedPages: 7,
    learningGoals: ["辨識呼喚—回答的反覆結構、直接引語與先知公式。"],
    tags: ["samuel", "call-narrative", "direct-speech"],
  },
  {
    id: "hbo-tanakh-gen-01",
    title: "創世記 1：創造秩序",
    titleOriginal: "בְּרֵאשִׁית 1",
    bookCode: "gen",
    chapter: 1,
    difficulty: 2,
    track: "core",
    estimatedPages: 11,
    learningGoals: ["掌握創造動詞、命名公式、日序與反覆句法。"],
    tags: ["genesis", "creation", "formulaic-language"],
  },
  {
    id: "hbo-tanakh-exo-03",
    title: "出埃及記 3：荊棘火焰與差遣",
    titleOriginal: "שְׁמוֹת 3",
    bookCode: "exo",
    chapter: 3,
    difficulty: 2,
    track: "core",
    estimatedPages: 7,
    learningGoals: ["分析呼召敘事、差遣公式、神名段落與未完成式。"],
    tags: ["exodus", "call-narrative", "divine-name"],
  },
  {
    id: "hbo-tanakh-exo-20",
    title: "出埃及記 20：十言與盟約律法",
    titleOriginal: "שְׁמוֹת 20",
    bookCode: "exo",
    chapter: 20,
    difficulty: 2,
    track: "core",
    estimatedPages: 9,
    learningGoals: ["掌握禁令式 לֹא + 未完成式、命令與盟約語彙。"],
    tags: ["exodus", "decalogue", "law"],
  },
  {
    id: "hbo-tanakh-deu-06",
    title: "申命記 6：示瑪與代際傳承",
    titleOriginal: "דְּבָרִים 6",
    bookCode: "deu",
    chapter: 6,
    difficulty: 1,
    track: "core",
    estimatedPages: 7,
    learningGoals: ["背誦示瑪核心段落，辨識愛、教導、記號與記憶語彙。"],
    tags: ["deuteronomy", "shema", "covenant"],
  },
  {
    id: "hbo-tanakh-psa-023",
    title: "詩篇 23：上主是我的牧者",
    titleOriginal: "תְּהִלִּים 23",
    bookCode: "psa",
    chapter: 23,
    difficulty: 1,
    track: "core",
    estimatedPages: 4,
    status: "sample_ready",
    segments: psalm23Segments,
    learningGoals: ["熟悉第一、第二人稱附屬字尾、詩歌平行與牧者意象。"],
    tags: ["psalms", "poetry", "memorization", "local-sample"],
  },
  {
    id: "hbo-tanakh-psa-121",
    title: "詩篇 121：守護者不打盹",
    titleOriginal: "תְּהִלִּים 121",
    bookCode: "psa",
    chapter: 121,
    difficulty: 1,
    track: "core",
    estimatedPages: 4,
    learningGoals: ["辨識守護語根的反覆、問答結構與朝聖詩語彙。"],
    tags: ["psalms", "poetry", "pilgrimage"],
  },
  {
    id: "hbo-tanakh-isa-40",
    title: "以賽亞書 40：安慰與重新出發",
    titleOriginal: "יְשַׁעְיָהוּ 40",
    bookCode: "isa",
    chapter: 40,
    difficulty: 3,
    track: "advanced",
    estimatedPages: 13,
    learningGoals: ["分析先知詩歌、分詞、比較句與創造—安慰語彙。"],
    tags: ["isaiah", "prophetic-poetry", "comfort"],
  },
];

const bibleOrdinalBase =
  vocabularySelections.length + memorySelections.length;
const bibleSelections: OriginalReaderSelection[] = BIBLE_SEEDS.map(
  (seed, index) => ({
    id: seed.id,
    ordinal: bibleOrdinalBase + index + 1,
    partId: "hbo-part-tanakh",
    kind: "bible_chapter",
    title: seed.title,
    titleOriginal: seed.titleOriginal,
    difficulty: seed.difficulty,
    track: seed.track,
    estimatedPages: seed.estimatedPages,
    status: seed.status ?? "source_ready",
    source: WLC_SOURCE,
    scripture: {
      bookCode: seed.bookCode,
      chapter: seed.chapter,
      versionCode: "wlc",
    },
    segments: seed.segments,
    learningGoals: [...seed.learningGoals, POINTED_TEXT_REQUIREMENT],
    tags: [...COMMON_TAGS, "tanakh", ...seed.tags],
  }),
);

interface ReadingSeed {
  id: string;
  title: string;
  titleOriginal?: string;
  subtitle?: string;
  difficulty: OriginalReaderSelection["difficulty"];
  track: OriginalReaderSelection["track"];
  estimatedPages: number;
  goal: string;
  tags: string[];
  source?: OriginalReaderSource;
}

const PRAYER_SEEDS: ReadingSeed[] = [
  {
    id: "hbo-prayer-01-shema",
    title: "示瑪（Shema Yisrael）",
    titleOriginal: "שְׁמַע יִשְׂרָאֵל",
    difficulty: 1,
    track: "core",
    estimatedPages: 3,
    goal: "背誦核心宣告，辨識命令式、神名與愛的盟約語彙。",
    tags: ["daily", "shema", "deuteronomy"],
  },
  {
    id: "hbo-prayer-02-amidah-avot",
    title: "阿彌達：列祖頌（Avot）",
    titleOriginal: "בִּרְכַּת אָבוֹת",
    difficulty: 2,
    track: "core",
    estimatedPages: 3,
    goal: "掌握列祖名號、祝福公式與關係子句。",
    tags: ["amidah", "daily", "patriarchs"],
  },
  {
    id: "hbo-prayer-03-amidah-gevurot",
    title: "阿彌達：大能頌（Gevurot）",
    titleOriginal: "גְּבוּרוֹת",
    difficulty: 2,
    track: "core",
    estimatedPages: 3,
    goal: "辨識神聖能力、生命、雨水與復活語彙。",
    tags: ["amidah", "daily", "resurrection"],
  },
  {
    id: "hbo-prayer-04-amidah-kedushat-hashem",
    title: "阿彌達：聖名頌（Kedushat HaShem）",
    titleOriginal: "קְדֻשַּׁת הַשֵּׁם",
    difficulty: 2,
    track: "core",
    estimatedPages: 2,
    goal: "學習聖潔詞族與第二人稱頌讚句法。",
    tags: ["amidah", "daily", "holiness"],
  },
  {
    id: "hbo-prayer-05-mourners-kaddish",
    title: "哀悼者加迪什（Mourner's Kaddish）",
    titleOriginal: "קַדִּישׁ יָתוֹם",
    difficulty: 3,
    track: "core",
    estimatedPages: 4,
    goal: "辨識亞蘭文讚頌公式，並清楚標出與 hbo 的語言切換。",
    tags: ["daily", "mourning", "aramaic"],
  },
  {
    id: "hbo-prayer-06-aleinu",
    title: "阿雷努（Aleinu）",
    titleOriginal: "עָלֵינוּ לְשַׁבֵּחַ",
    difficulty: 2,
    track: "core",
    estimatedPages: 4,
    goal: "閱讀宇宙主權、敬拜與末世盼望的固定語彙。",
    tags: ["daily", "closing-prayer", "kingship"],
  },
  {
    id: "hbo-prayer-07-modeh-ani",
    title: "我感謝祢（Modeh Ani）",
    titleOriginal: "מוֹדֶה אֲנִי",
    difficulty: 1,
    track: "core",
    estimatedPages: 1,
    goal: "以極短晨禱練習分詞、第一人稱與感謝語彙。",
    tags: ["morning", "memorization", "thanksgiving"],
  },
  {
    id: "hbo-prayer-08-yotzer-or",
    title: "晨光福祐（Yotzer Or）",
    titleOriginal: "יוֹצֵר אוֹר",
    difficulty: 2,
    track: "core",
    estimatedPages: 5,
    goal: "比較創造光暗的禮儀語彙與先知經文。",
    tags: ["morning", "creation", "blessing"],
  },
  {
    id: "hbo-prayer-09-ahavah-rabbah",
    title: "大愛頌（Ahavah Rabbah）",
    titleOriginal: "אַהֲבָה רַבָּה",
    difficulty: 2,
    track: "core",
    estimatedPages: 5,
    goal: "追蹤愛、教導、聆聽與誡命的詞彙鏈。",
    tags: ["morning", "shema-blessing", "torah"],
  },
  {
    id: "hbo-prayer-10-hashkiveinu",
    title: "求使我們安躺（Hashkiveinu）",
    titleOriginal: "הַשְׁכִּיבֵנוּ",
    difficulty: 2,
    track: "core",
    estimatedPages: 4,
    goal: "掌握使役形、保護、平安與夜間意象。",
    tags: ["evening", "protection", "hiphil"],
  },
  {
    id: "hbo-prayer-11-lecha-dodi",
    title: "來吧，我的良人（Lecha Dodi）",
    titleOriginal: "לְכָה דוֹדִי",
    difficulty: 3,
    track: "advanced",
    estimatedPages: 7,
    goal: "閱讀字母詩、安息日新娘意象與近代禮儀詩語。",
    tags: ["shabbat", "piyyut", "acrostic"],
  },
  {
    id: "hbo-prayer-12-shalom-aleichem",
    title: "願你們平安（Shalom Aleichem）",
    titleOriginal: "שָׁלוֹם עֲלֵיכֶם",
    difficulty: 1,
    track: "core",
    estimatedPages: 2,
    goal: "熟悉平安問候、複數介詞字尾與重複頌唱。",
    tags: ["shabbat", "home-liturgy", "angels"],
  },
  {
    id: "hbo-prayer-13-shabbat-kiddush",
    title: "安息日晚祝聖詞（Kiddush for Shabbat）",
    titleOriginal: "קִדּוּשׁ לְלֵיל שַׁבָּת",
    difficulty: 2,
    track: "core",
    estimatedPages: 5,
    goal: "連結創造敘事、酒杯祝福與安息日成聖語彙。",
    tags: ["shabbat", "kiddush", "home-liturgy"],
  },
  {
    id: "hbo-prayer-14-havdalah",
    title: "哈夫達拉（Havdalah）",
    titleOriginal: "הַבְדָּלָה",
    difficulty: 2,
    track: "core",
    estimatedPages: 4,
    goal: "辨識分別、光暗、聖俗與節期轉換的對偶。",
    tags: ["shabbat", "havdalah", "ritual-transition"],
  },
  {
    id: "hbo-prayer-15-mi-chamocha",
    title: "誰能像祢（Mi Chamocha）",
    titleOriginal: "מִי כָמֹכָה",
    difficulty: 1,
    track: "core",
    estimatedPages: 2,
    goal: "背誦反問式讚頌並連結出埃及救贖語彙。",
    tags: ["redemption", "exodus", "song"],
  },
  {
    id: "hbo-prayer-16-adon-olam",
    title: "宇宙之主（Adon Olam）",
    titleOriginal: "אֲדוֹן עוֹלָם",
    difficulty: 2,
    track: "core",
    estimatedPages: 4,
    goal: "閱讀神的永恆、王權與個人信靠語彙。",
    tags: ["piyyut", "kingship", "trust"],
  },
  {
    id: "hbo-prayer-17-yigdal",
    title: "尊崇永生神（Yigdal）",
    titleOriginal: "יִגְדַּל",
    difficulty: 3,
    track: "advanced",
    estimatedPages: 6,
    goal: "建立中世紀神學、神的屬性與信仰原則詞彙。",
    tags: ["piyyut", "maimonides", "theology"],
  },
  {
    id: "hbo-prayer-18-ashrei",
    title: "快樂頌（Ashrei）",
    titleOriginal: "אַשְׁרֵי",
    difficulty: 2,
    track: "core",
    estimatedPages: 7,
    goal: "閱讀以詩篇 145 為核心的字母詩與每日讚美語彙。",
    tags: ["psalms", "daily", "acrostic"],
  },
  {
    id: "hbo-prayer-19-birkat-hamazon",
    title: "餐後祝謝（Birkat Hamazon）",
    titleOriginal: "בִּרְכַּת הַמָּזוֹן",
    difficulty: 4,
    track: "advanced",
    estimatedPages: 10,
    goal: "分析長篇家庭禮儀中的祝福、土地、盟約與群體記憶。",
    tags: ["meal", "home-liturgy", "long-form"],
  },
  {
    id: "hbo-prayer-20-tachanun",
    title: "懇求（Tachanun）",
    titleOriginal: "תַּחֲנוּן",
    difficulty: 3,
    track: "advanced",
    estimatedPages: 7,
    goal: "閱讀悔改、哀求、恩慈與赦免的詩性語彙。",
    tags: ["daily", "supplication", "repentance"],
  },
];

const prayerOrdinalBase = bibleOrdinalBase + bibleSelections.length;
const prayerSelections: OriginalReaderSelection[] = PRAYER_SEEDS.map(
  (seed, index) => ({
    id: seed.id,
    ordinal: prayerOrdinalBase + index + 1,
    partId: "hbo-part-prayers",
    kind: "prayer",
    title: seed.title,
    titleOriginal: seed.titleOriginal,
    subtitle: seed.subtitle,
    difficulty: seed.difficulty,
    track: seed.track,
    estimatedPages: seed.estimatedPages,
    status: "planned",
    source: SIDDUR_SOURCE,
    learningGoals: [seed.goal, POINTED_TEXT_REQUIREMENT],
    tags: [...COMMON_TAGS, "jewish-liturgy", ...seed.tags],
  }),
);

const HAGGADAH_SEEDS: ReadingSeed[] = [
  {
    id: "hbo-haggadah-01-kadesh",
    title: "1. Kadesh：祝聖",
    titleOriginal: "קַדֵּשׁ",
    difficulty: 1,
    track: "core",
    estimatedPages: 2,
    goal: "掌握第一杯酒、祝福與節期成聖公式。",
    tags: ["kadesh", "wine", "sanctification"],
  },
  {
    id: "hbo-haggadah-02-urchatz",
    title: "2. Urchatz：洗手",
    titleOriginal: "וּרְחַץ",
    difficulty: 1,
    track: "core",
    estimatedPages: 1,
    goal: "辨識簡短儀式指示與動作詞。",
    tags: ["urchatz", "washing", "ritual-action"],
  },
  {
    id: "hbo-haggadah-03-karpas",
    title: "3. Karpas：沾食蔬菜",
    titleOriginal: "כַּרְפַּס",
    difficulty: 1,
    track: "core",
    estimatedPages: 1,
    goal: "學習食物、祝福與沾食的家庭禮儀語彙。",
    tags: ["karpas", "food", "blessing"],
  },
  {
    id: "hbo-haggadah-04-yachatz",
    title: "4. Yachatz：分餅",
    titleOriginal: "יַחַץ",
    difficulty: 1,
    track: "core",
    estimatedPages: 1,
    goal: "掌握擘開、藏起與無酵餅的儀式詞彙。",
    tags: ["yachatz", "matzah", "ritual-action"],
  },
  {
    id: "hbo-haggadah-05-maggid",
    title: "5. Maggid：講述出埃及",
    titleOriginal: "מַגִּיד",
    difficulty: 4,
    track: "core",
    estimatedPages: 35,
    goal: "完整閱讀四問、四子、十災、Dayenu 與申命記 26 的拉比式講解。",
    tags: ["maggid", "four-questions", "four-sons", "midrash", "dayenu"],
  },
  {
    id: "hbo-haggadah-06-rachtzah",
    title: "6. Rachtzah：祝福後洗手",
    titleOriginal: "רָחְצָה",
    difficulty: 1,
    track: "core",
    estimatedPages: 1,
    goal: "比較兩次洗手步驟與相應祝福公式。",
    tags: ["rachtzah", "washing", "blessing"],
  },
  {
    id: "hbo-haggadah-07-motzi",
    title: "7. Motzi：餅的祝福",
    titleOriginal: "מוֹצִיא",
    difficulty: 1,
    track: "core",
    estimatedPages: 1,
    goal: "背誦產生食糧的祝福句並解析分詞。",
    tags: ["motzi", "bread", "blessing"],
  },
  {
    id: "hbo-haggadah-08-matzah",
    title: "8. Matzah：食無酵餅",
    titleOriginal: "מַצָּה",
    difficulty: 1,
    track: "core",
    estimatedPages: 2,
    goal: "掌握無酵餅誡命及相關介詞結構。",
    tags: ["matzah", "commandment", "food"],
  },
  {
    id: "hbo-haggadah-09-maror",
    title: "9. Maror：食苦菜",
    titleOriginal: "מָרוֹר",
    difficulty: 1,
    track: "core",
    estimatedPages: 2,
    goal: "連結苦味、奴役記憶與食物祝福。",
    tags: ["maror", "memory", "food"],
  },
  {
    id: "hbo-haggadah-10-korech",
    title: "10. Korech：夾餅",
    titleOriginal: "כּוֹרֵךְ",
    difficulty: 2,
    track: "core",
    estimatedPages: 2,
    goal: "閱讀希列傳統及引經公式。",
    tags: ["korech", "hillel", "citation"],
  },
  {
    id: "hbo-haggadah-11-shulchan-orech",
    title: "11. Shulchan Orech：筵席",
    titleOriginal: "שֻׁלְחָן עוֹרֵךְ",
    difficulty: 1,
    track: "core",
    estimatedPages: 2,
    goal: "辨識筵席、家庭與款待語彙。",
    tags: ["shulchan-orech", "meal", "family"],
  },
  {
    id: "hbo-haggadah-12-tzafun",
    title: "12. Tzafun：尋回 Afikoman",
    titleOriginal: "צָפוּן",
    difficulty: 1,
    track: "core",
    estimatedPages: 2,
    goal: "掌握藏起、尋回與餐後無酵餅語彙。",
    tags: ["tzafun", "afikoman", "ritual-action"],
  },
  {
    id: "hbo-haggadah-13-barech",
    title: "13. Barech：餐後祝謝",
    titleOriginal: "בָּרֵךְ",
    difficulty: 3,
    track: "core",
    estimatedPages: 10,
    goal: "完整閱讀餐後祝謝與第三、第四杯相關祝福。",
    tags: ["barech", "birkat-hamazon", "long-form"],
  },
  {
    id: "hbo-haggadah-14-hallel",
    title: "14. Hallel：讚美詩篇",
    titleOriginal: "הַלֵּל",
    difficulty: 3,
    track: "core",
    estimatedPages: 15,
    goal: "閱讀 Hallel 詩篇、會眾回應與讚美動詞。",
    tags: ["hallel", "psalms", "chant"],
  },
  {
    id: "hbo-haggadah-15-nirtzah",
    title: "15. Nirtzah：蒙悅納與結語",
    titleOriginal: "נִרְצָה",
    difficulty: 3,
    track: "core",
    estimatedPages: 8,
    goal: "閱讀結語詩歌及『明年在耶路撒冷』的終末盼望。",
    tags: ["nirtzah", "closing", "jerusalem", "songs"],
  },
];

const haggadahOrdinalBase = prayerOrdinalBase + prayerSelections.length;
const haggadahSelections: OriginalReaderSelection[] = HAGGADAH_SEEDS.map(
  (seed, index) => ({
    id: seed.id,
    ordinal: haggadahOrdinalBase + index + 1,
    partId: "hbo-part-haggadah",
    kind: "haggadah",
    title: seed.title,
    titleOriginal: seed.titleOriginal,
    difficulty: seed.difficulty,
    track: seed.track,
    estimatedPages: seed.estimatedPages,
    status: "planned",
    source: HAGGADAH_SOURCE,
    learningGoals: [seed.goal, POINTED_TEXT_REQUIREMENT],
    tags: [...COMMON_TAGS, "pesach", "haggadah", ...seed.tags],
  }),
);

const RABBINIC_SEEDS: ReadingSeed[] = [
  {
    id: "hbo-rabbinic-01-mishnah-peah-1-1",
    title: "1. 《米示拿・Peah》1:1",
    subtitle: "核心選文 1/12",
    difficulty: 2,
    track: "core",
    estimatedPages: 2,
    goal: "辨識米示拿列舉句式、農業律法與無定量公式。",
    tags: ["mishnah", "peah", "halakhah"],
    source: MISHNAH_SOURCE,
  },
  {
    id: "hbo-rabbinic-02-mishnah-berakhot-1-1-3",
    title: "2. 《米示拿・Berakhot》1:1–3",
    subtitle: "核心選文 2/12",
    difficulty: 2,
    track: "core",
    estimatedPages: 5,
    goal: "閱讀示瑪時間、姿勢與拉比意見的並列結構。",
    tags: ["mishnah", "berakhot", "shema"],
    source: MISHNAH_SOURCE,
  },
  {
    id: "hbo-rabbinic-03-mishnah-berakhot-2-1-2",
    title: "3. 《米示拿・Berakhot》2:1–2",
    subtitle: "核心選文 3/12",
    difficulty: 2,
    track: "core",
    estimatedPages: 4,
    goal: "分析意向、打斷與禮儀有效性的條件句。",
    tags: ["mishnah", "berakhot", "intention"],
    source: MISHNAH_SOURCE,
  },
  {
    id: "hbo-rabbinic-04-mishnah-yoma-8-9",
    title: "4. 《米示拿・Yoma》8:9",
    subtitle: "核心選文 4/12",
    difficulty: 2,
    track: "core",
    estimatedPages: 3,
    goal: "閱讀贖罪、悔改及人神／人際罪責的對比。",
    tags: ["mishnah", "yoma", "atonement", "repentance"],
    source: MISHNAH_SOURCE,
  },
  {
    id: "hbo-rabbinic-05-mishnah-pesachim-10-1-5",
    title: "5. 《米示拿・Pesachim》10:1–5",
    subtitle: "核心選文 5/12",
    difficulty: 3,
    track: "core",
    estimatedPages: 7,
    goal: "把逾越節筵席的米示拿規範與 Haggadah 實際次序對讀。",
    tags: ["mishnah", "pesachim", "pesach", "seder"],
    source: MISHNAH_SOURCE,
  },
  {
    id: "hbo-rabbinic-06-mishnah-rosh-hashanah-2-8-9",
    title: "6. 《米示拿・Rosh Hashanah》2:8–9",
    subtitle: "核心選文 6/12",
    difficulty: 3,
    track: "core",
    estimatedPages: 5,
    goal: "閱讀曆法見證、權威衝突與服從的敘事段落。",
    tags: ["mishnah", "rosh-hashanah", "calendar", "authority"],
    source: MISHNAH_SOURCE,
  },
  {
    id: "hbo-rabbinic-07-mishnah-sanhedrin-4-5",
    title: "7. 《米示拿・Sanhedrin》4:5",
    subtitle: "核心選文 7/12",
    difficulty: 3,
    track: "core",
    estimatedPages: 4,
    goal: "分析司法警告、單一人類起源與生命價值的修辭。",
    tags: ["mishnah", "sanhedrin", "law", "human-dignity"],
    source: MISHNAH_SOURCE,
  },
  {
    id: "hbo-rabbinic-08-mishnah-avot-1-1-6",
    title: "8. 《米示拿・Avot》1:1–6",
    subtitle: "核心選文 8/12",
    difficulty: 2,
    track: "core",
    estimatedPages: 7,
    goal: "掌握傳承鏈、格言式命令與倫理詞彙。",
    tags: ["mishnah", "avot", "ethics", "transmission"],
    source: MISHNAH_SOURCE,
  },
  {
    id: "hbo-rabbinic-09-mishnah-avot-1-14-2-5-2-16",
    title: "9. 《米示拿・Avot》1:14；2:5；2:16",
    subtitle: "核心選文 9/12",
    difficulty: 2,
    track: "core",
    estimatedPages: 4,
    goal: "背誦三則格言，辨識反問、否定命令與工作—報酬語彙。",
    tags: ["mishnah", "avot", "ethics", "aphorism"],
    source: MISHNAH_SOURCE,
  },
  {
    id: "hbo-rabbinic-10-mishnah-avot-3-14-15",
    title: "10. 《米示拿・Avot》3:14–15",
    subtitle: "核心選文 10/12",
    difficulty: 2,
    track: "core",
    estimatedPages: 3,
    goal: "分析『被愛／按形像』與知識—審判的平行句。",
    tags: ["mishnah", "avot", "image-of-god", "ethics"],
    source: MISHNAH_SOURCE,
  },
  {
    id: "hbo-rabbinic-11-mishnah-avot-4-1-2",
    title: "11. 《米示拿・Avot》4:1–2",
    subtitle: "核心選文 11/12",
    difficulty: 2,
    track: "core",
    estimatedPages: 3,
    goal: "閱讀『誰是……』定義句與誡命引出誡命的連鎖修辭。",
    tags: ["mishnah", "avot", "virtue", "aphorism"],
    source: MISHNAH_SOURCE,
  },
  {
    id: "hbo-rabbinic-12-sifra-kedoshim-4-12",
    title: "12. 《Sifra Kedoshim》4:12",
    subtitle: "核心選文 12/12",
    difficulty: 3,
    track: "core",
    estimatedPages: 4,
    goal: "辨識 tannaitic halakhic midrash 的引經、釋詞與推論格式。",
    tags: ["sifra", "kedoshim", "halakhic-midrash"],
    source: HALAKHIC_MIDRASH_SOURCE,
  },
  {
    id: "hbo-rabbinic-13-mekhilta-bahodesh-5-1-3",
    title: "13. 《Mekhilta de-Rabbi Ishmael・Bahodesh》5:1–3",
    subtitle: "進階選文 1/8",
    difficulty: 4,
    track: "advanced",
    estimatedPages: 8,
    goal: "追蹤十誡相關 halakhic midrash 的引文、異說與釋經推論。",
    tags: ["mekhilta", "bahodesh", "halakhic-midrash", "decalogue"],
    source: HALAKHIC_MIDRASH_SOURCE,
  },
  {
    id: "hbo-rabbinic-14-genesis-rabbah-1-1",
    title: "14. 《Genesis Rabbah》1:1",
    subtitle: "進階選文 2/8",
    difficulty: 4,
    track: "advanced",
    estimatedPages: 6,
    goal: "分析創世記開篇的 proem、引經鏈與智慧意象。",
    tags: ["genesis-rabbah", "aggadic-midrash", "creation"],
    source: GENESIS_RABBAH_SOURCE,
  },
  {
    id: "hbo-rabbinic-15-genesis-rabbah-38-13",
    title: "15. 《Genesis Rabbah》38:13",
    subtitle: "進階選文 3/8",
    difficulty: 4,
    track: "advanced",
    estimatedPages: 6,
    goal: "閱讀亞伯蘭與偶像故事中的敘事對話、反諷與釋經改寫。",
    tags: ["genesis-rabbah", "aggadic-midrash", "abraham", "idolatry"],
    source: GENESIS_RABBAH_SOURCE,
  },
  {
    id: "hbo-rabbinic-16-bavli-shabbat-31a",
    title: "16. 《巴比倫塔木德・Shabbat》31a",
    subtitle: "進階選文 4/8",
    difficulty: 4,
    track: "advanced",
    estimatedPages: 8,
    goal: "辨識希列故事群、直接引語與希伯來文—亞蘭文切換。",
    tags: ["bavli", "shabbat", "hillel", "aramaic"],
    source: BAVLI_SOURCE,
  },
  {
    id: "hbo-rabbinic-17-bavli-eruvin-13b",
    title: "17. 《巴比倫塔木德・Eruvin》13b",
    subtitle: "進階選文 5/8",
    difficulty: 4,
    track: "advanced",
    estimatedPages: 8,
    goal: "分析學派爭論、天上聲音與『永生神的話』段落。",
    tags: ["bavli", "eruvin", "beit-hillel", "beit-shammai", "aramaic"],
    source: BAVLI_SOURCE,
  },
  {
    id: "hbo-rabbinic-18-bavli-berakhot-61b",
    title: "18. 《巴比倫塔木德・Berakhot》61b",
    subtitle: "進階選文 6/8",
    difficulty: 4,
    track: "advanced",
    estimatedPages: 8,
    goal: "閱讀拉比阿奇瓦敘事、示瑪引文與殉道語彙。",
    tags: ["bavli", "berakhot", "rabbi-akiva", "martyrdom", "aramaic"],
    source: BAVLI_SOURCE,
  },
  {
    id: "hbo-rabbinic-19-bavli-bava-metzia-59b",
    title: "19. 《巴比倫塔木德・Bava Metzia》59b",
    subtitle: "進階選文 7/8",
    difficulty: 4,
    track: "advanced",
    estimatedPages: 10,
    goal: "追蹤 Akhnai 烤爐爭論的論證、神蹟、引經與法律權威。",
    tags: ["bavli", "bava-metzia", "oven-of-akhnai", "law", "aramaic"],
    source: BAVLI_SOURCE,
  },
  {
    id: "hbo-rabbinic-20-bavli-taanit-23a",
    title: "20. 《巴比倫塔木德・Taanit》23a",
    subtitle: "進階選文 8/8",
    difficulty: 4,
    track: "advanced",
    estimatedPages: 10,
    goal: "閱讀圓圈者霍尼故事群中的祈雨、寓言與時間敘事。",
    tags: ["bavli", "taanit", "honi", "rain", "aramaic"],
    source: BAVLI_SOURCE,
  },
];

const rabbinicOrdinalBase =
  haggadahOrdinalBase + haggadahSelections.length;
const rabbinicSelections: OriginalReaderSelection[] = RABBINIC_SEEDS.map(
  (seed, index) => ({
    id: seed.id,
    ordinal: rabbinicOrdinalBase + index + 1,
    partId:
      seed.track === "advanced"
        ? "hbo-part-rabbinic-advanced"
        : "hbo-part-rabbinic-core",
    kind: "rabbinic",
    title: seed.title,
    subtitle: seed.subtitle,
    difficulty: seed.difficulty,
    track: seed.track,
    estimatedPages: seed.estimatedPages,
    status: "planned",
    source: seed.source ?? MISHNAH_SOURCE,
    learningGoals: [
      seed.goal,
      "正式讀文須以人工校讀的教學母音完整標示；任何編者補入的 niqqud 必須與底本文字分層記錄。",
      POINTED_TEXT_REQUIREMENT,
    ],
    tags: [
      ...COMMON_TAGS,
      "rabbinic",
      seed.track === "advanced" ? "advanced-8" : "core-12",
      ...seed.tags,
    ],
  }),
);

export const hebrewOriginalReader: OriginalReaderVolume = {
  id: "original-reader-hbo",
  slug: "hbo",
  language: "hbo",
  title: "希伯來文原文讀本",
  subtitle:
    "一千詞、百段背誦、十五章 Tanakh、二十篇猶太禱文、完整十五步 Haggadah 與二十篇拉比選文",
  privateUse: true,
  rtl: true,
  print: JIS_B5_READER_PROFILE,
  pronunciationProfiles: [
    {
      id: AUDIO_PROFILE_ID,
      label: "BBH 古典／馬所拉教學式（Classical/Masoretic）",
      description:
        "不是 modern Israeli。Tanakh 依馬所拉 niqqud，底本有 cantillation 時保留；禱文、Haggadah 與拉比文本使用明確標為編者層的完整教學母音，音訊與 pointed segment 逐段對齊。",
      referenceUrl: "https://hebrewsyntax.org/bbh2new/",
    },
  ],
  textPolicy: {
    scriptStandard: "Biblical Hebrew（hbo）的完整馬所拉附點正文",
    requiredMarks: [
      "所有正文完整顯示 niqqud（母音點）",
      "Tanakh 底本所含 cantillation／te'amim（重音與抑揚符號）必須保留",
      "禱文、Haggadah 與拉比文本若由編者補入教學母音，須與底本文字分層記錄並註明責任",
    ],
    prohibitedSubstitutions: [
      "不得以無母音的 modern Israeli Hebrew 拼法替代附點正文",
      "lemmaUnpointed 或 normalized 僅供索引與搜尋，不得顯示為 running text",
      "不得因只分析部分 tokens 而截斷、重建或取代完整 sourceText",
    ],
    notes:
      "sourceText 永遠完整顯示；tokens 只另列已校驗的關鍵詞。所有音訊採 biblical/Masoretic pedagogical 規約，不以 modern Israeli 裝置音色冒充。",
  },
  vocabularyCurriculum: {
    lessonCount: 50,
    orderingRule:
      "50 課、1,000 詞，每課詞數依課本而定：第 1–33 課即 BBH2 第 3–35 章，逐章原封不動（4 至 39 詞不等，共 552 個不重複詞位；原表 554 筆中的兩筆完全重複，以 sourceOrders 保存原位置）；第 34–50 課為 448 個經 WLC／OSHB 詞頻與詞典核驗的延伸詞位。",
    primarySources: [
      "Gary D. Pratico and Miles V. Van Pelt, Basics of Biblical Hebrew Grammar, 2nd ed.（前 552 詞位）",
      "Westminster Leningrad Codex／Open Scriptures Hebrew Bible 詞頻延伸（後 448 詞位）",
    ],
    exactOrderingStatus: "verified",
  },
  parts: [
    {
      id: "hbo-part-vocabulary",
      ordinal: 1,
      title: "第一部　一千核心詞彙與查考索引",
      description:
        "50 課 × 20 字；前 552 詞保留 Pratico & Van Pelt 的 BBH2 次序，後 448 詞依 WLC／OSHB 頻率延伸，逐詞顯示來源與核驗狀態。",
    },
    {
      id: "hbo-part-memory",
      ordinal: 2,
      title: "第二部　一百背誦單元",
      description:
        "20 組 × 5 段；全部由本卷定稿選文抽取，使用與正文及音訊相同的 segment id。",
    },
    {
      id: "hbo-part-tanakh",
      ordinal: 3,
      title: "第三部　Tanakh 十五章精讀",
      description:
        "約拿 1、3、4；路得 1–4；撒母耳記上 3；創世記 1；出埃及記 3、20；申命記 6；詩篇 23、121；以賽亞書 40。",
    },
    {
      id: "hbo-part-prayers",
      ordinal: 4,
      title: "第四部　猶太教核心禱文二十篇",
      description:
        "每日、晨昏、安息日、家庭與節期禱文；正文錄入前須鎖定 nusach、版本、權利及教學母音政策。",
    },
    {
      id: "hbo-part-haggadah",
      ordinal: 5,
      title: "第五部　逾越節 Haggadah 完整十五步",
      description:
        "從 Kadesh 至 Nirtzah，保留完整 Maggid、Barech、Hallel 與結語，不把全本縮成摘要。",
    },
    {
      id: "hbo-part-rabbinic-core",
      ordinal: 6,
      title: "第六部　拉比文獻核心十二選",
      description:
        "米示拿十一組與 Sifra 一組，建立拉比希伯來文、倫理格言、禮儀法與 halakhic midrash 基礎。",
    },
    {
      id: "hbo-part-rabbinic-advanced",
      ordinal: 7,
      title: "第七部　拉比文獻進階八選",
      description:
        "Mekhilta、Genesis Rabbah 與巴比倫塔木德五組；明確標示希伯來文／亞蘭文語層與編者補入的教學母音。",
    },
  ],
  selections: [
    ...vocabularySelections,
    ...memorySelections,
    ...bibleSelections,
    ...prayerSelections,
    ...haggadahSelections,
    ...rabbinicSelections,
  ],
};

export default hebrewOriginalReader;
