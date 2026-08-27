import {
  JIS_B5_READER_PROFILE,
  type OriginalReaderSegment,
  type OriginalReaderSelection,
  type OriginalReaderSource,
  type OriginalReaderVolume,
} from "./types";

type SelectionSeed = Omit<OriginalReaderSelection, "ordinal">;

const EDITORIAL_SOURCE: OriginalReaderSource = {
  edition: "Original Readers editorial production manifest",
  versionCode: "la-editorial-v1",
  licenseNote:
    "Planning metadata only. No source text is supplied by this record; every production item must receive a pinned edition, checksum, and rights review before publication.",
  authorization: "private-authorized",
};

const VOCABULARY_SOURCE: OriginalReaderSource = {
  edition: "Ecclesiastical Latin 1,000-lemma frequency list (to be frozen from the reader corpus)",
  versionCode: "la-vocab-1000-v1",
  licenseNote:
    "The ranked lemma inventory has not yet been generated. Derive it only from the pinned Vulgate, prayer, liturgy, patristic, and bridge-text corpora; record corpus checksums before filling the groups.",
  authorization: "private-authorized",
};

const MEMORY_SOURCE: OriginalReaderSource = {
  edition: "Ecclesiastical Latin 100-unit memory syllabus (production slots)",
  versionCode: "la-memory-100-v1",
  licenseNote:
    "The one hundred slots are complete, but their exact sentences remain intentionally blank. A slot may be filled only after the quoted edition and its reuse rights have been verified.",
  authorization: "private-authorized",
};

const VULGATE_SOURCE: OriginalReaderSource = {
  edition: "Biblia Sacra Vulgata Clementina, editio 1598 (eBible latVUC transcription)",
  editor: "Clementine Vulgate Project / eBible.org",
  sourceUrl: "https://ebible.org/details.php?id=latVUC",
  versionCode: "latVUC",
  licenseNote:
    "Public Domain source as declared by eBible.org. Freeze the downloaded source and add a checksum before production; label it Clementine Vulgate, not Stuttgart Vulgate or Nova Vulgata.",
  authorization: "private-authorized",
};

const PSALM_22_SOURCE: OriginalReaderSource = {
  ...VULGATE_SOURCE,
  sourceUrl: "https://ebible.org/study/content/texts/latVUC/PS22.html",
};

const HISTORICAL_PRAYER_SOURCE: OriginalReaderSource = {
  edition: "Historical Latin prayer, creed, and hymn texts (exact public-domain/open edition pending)",
  versionCode: "la-prayers-source-pending",
  licenseNote:
    "The work may be ancient or public-domain, but that does not clear a modern edition, transcription, translation, musical setting, or recording. No prayer text is included here; pin and audit each edition separately.",
  authorization: "private-authorized",
};

const PRIVATE_MISSAL_SOURCE: OriginalReaderSource = {
  edition: "Missale Romanum, editio typica tertia emendata — Ordo Missae (privately authorized source placeholder)",
  versionCode: "mr-ordo-missae-private",
  licenseNote:
    "Current Roman Missal text is rights-controlled. This manifest stores only section metadata and assumes a privately authorized source. Do not add, print, publish, record, or redistribute the Latin text until the written authorization and exact edition are attached.",
  authorization: "private-authorized",
};

const PATRISTIC_SOURCE = (citation: string): OriginalReaderSource => ({
  edition: `${citation} — exact Latin edition/transcription pending`,
  versionCode: "la-patristic-source-pending",
  licenseNote:
    "The ancient work is public-domain in principle, but the modern edition or digital transcription may not be. No source text is bundled in this manifest; pin an explicitly reusable edition and checksum it before adding segments.",
  authorization: "private-authorized",
});

const SCHOLASTIC_SOURCE = (citation: string): OriginalReaderSource => ({
  edition: `${citation} — exact public-domain/open Latin edition pending`,
  versionCode: "la-scholastic-source-pending",
  licenseNote:
    "No source text is included. Verify the exact edition and digitization license independently, then freeze and checksum the production source.",
  authorization: "private-authorized",
});

const SACROSANCTUM_CONCILIUM_SOURCE: OriginalReaderSource = {
  edition: "Concilium Vaticanum II, Sacrosanctum Concilium (1963), nn. 1, 10, 14",
  sourceUrl:
    "https://www.vatican.va/archive/hist_councils/ii_vatican_council/documents/vat-ii_const_19631204_sacrosanctum-concilium_lt.html",
  versionCode: "sc-1963-la-private",
  licenseNote:
    "Modern conciliar text. The official web page is a reference, not an assumed open redistribution license. Keep this as a private-authorized placeholder until written reuse permission is documented.",
  authorization: "private-authorized",
};

const vocabularySelections: SelectionSeed[] = Array.from(
  { length: 20 },
  (_, index): SelectionSeed => {
    const from = index * 50 + 1;
    const to = from + 49;
    const difficulty: OriginalReaderSelection["difficulty"] =
      index < 4 ? 1 : index < 10 ? 2 : index < 16 ? 3 : 4;
    const band =
      index < 4
        ? "最高頻核心詞"
        : index < 10
          ? "聖經與禮儀常用詞"
          : index < 16
            ? "教父與神學擴充詞"
            : "低頻辨讀與查典詞";

    return {
      id: `la-vocab-${String(from).padStart(4, "0")}-${String(to).padStart(4, "0")}`,
      partId: "la-vocabulary-reference",
      kind: "vocabulary",
      title: `一千詞彙 ${String(from).padStart(4, "0")}–${String(to).padStart(4, "0")}`,
      titleOriginal: `Vocabula ${from}–${to}`,
      subtitle: `${band}；每組 50 個詞元，詞形、核心義、例句與音訊索引待語料凍結後生成。`,
      difficulty,
      track: "reference",
      estimatedPages: 6,
      status: "planned",
      source: VOCABULARY_SOURCE,
      learningGoals: [
        `辨認頻率序位 ${from}–${to} 的五十個拉丁詞元。`,
        "能從屈折詞形還原詞元，並區分一般義與教會語境義。",
        "能用本組詞彙回查武加大、禮儀與教父例句。",
      ],
      tags: ["latin", "ecclesiastical-latin", "vocabulary", "frequency", `rank-${from}-${to}`],
    };
  },
);

const referenceSelections: SelectionSeed[] = [
  {
    id: "la-reference-pronunciation",
    partId: "la-vocabulary-reference",
    kind: "orientation",
    title: "教會拉丁文發音與重音",
    titleOriginal: "Pronuntiatio Latina ecclesiastica",
    subtitle: "羅馬式教會發音為主軌，古典重建音為比較軌；不得混用錄音標準。",
    difficulty: 1,
    track: "reference",
    estimatedPages: 8,
    status: "planned",
    source: EDITORIAL_SOURCE,
    learningGoals: ["穩定朗讀母音、雙母音、c/g/sc/gn/ti 等拼讀規則。", "依音節重量與詞尾判斷重音。"],
    tags: ["latin", "pronunciation", "ecclesiastical", "audio-policy"],
  },
  {
    id: "la-reference-nouns-adjectives",
    partId: "la-vocabulary-reference",
    kind: "appendix",
    title: "名詞、形容詞與代名詞屈折表",
    titleOriginal: "Declinationes nominum, adiectivorum et pronominum",
    difficulty: 2,
    track: "reference",
    estimatedPages: 12,
    status: "planned",
    source: EDITORIAL_SOURCE,
    learningGoals: ["由詞尾辨識格、數、性。", "辨識同位語、所有格、與格及奪格的常見功能。"],
    tags: ["latin", "grammar", "declension", "reference"],
  },
  {
    id: "la-reference-verbs",
    partId: "la-vocabulary-reference",
    kind: "appendix",
    title: "動詞變位與主要部分表",
    titleOriginal: "Coniugationes et partes principales",
    difficulty: 2,
    track: "reference",
    estimatedPages: 14,
    status: "planned",
    source: EDITORIAL_SOURCE,
    learningGoals: ["辨識人稱、數、時態、語態與語氣。", "由完成式與分詞詞幹回查字典詞元。"],
    tags: ["latin", "grammar", "conjugation", "reference"],
  },
  {
    id: "la-reference-nonfinite",
    partId: "la-vocabulary-reference",
    kind: "appendix",
    title: "分詞、不定詞、動名詞與目的分詞",
    titleOriginal: "Participia, infinitivi, gerundium, gerundivum et supinum",
    difficulty: 3,
    track: "reference",
    estimatedPages: 10,
    status: "planned",
    source: EDITORIAL_SOURCE,
    learningGoals: ["拆解拉丁長句中的非限定動詞結構。", "辨識間接敘述、義務與目的表達。"],
    tags: ["latin", "grammar", "participles", "infinitives", "reference"],
  },
  {
    id: "la-reference-subjunctive",
    partId: "la-vocabulary-reference",
    kind: "appendix",
    title: "虛擬語氣與教會文本常見子句",
    titleOriginal: "Coniunctivus et propositiones ecclesiasticae",
    difficulty: 3,
    track: "reference",
    estimatedPages: 12,
    status: "planned",
    source: EDITORIAL_SOURCE,
    learningGoals: ["辨識 ut/ne、cum、條件、願望與間接問句。", "說明祈禱文中虛擬語氣的語用功能。"],
    tags: ["latin", "grammar", "subjunctive", "clauses", "reference"],
  },
  {
    id: "la-reference-late-ecclesiastical",
    partId: "la-vocabulary-reference",
    kind: "appendix",
    title: "晚期與教會拉丁文閱讀提示",
    titleOriginal: "Notae Latinitatis serae et ecclesiasticae",
    difficulty: 3,
    track: "reference",
    estimatedPages: 8,
    status: "planned",
    source: EDITORIAL_SOURCE,
    learningGoals: ["辨識聖經翻譯腔、基督教語義轉移與較自由的介系詞用法。", "避免把古典規範機械套用於每一時期。"],
    tags: ["latin", "late-latin", "ecclesiastical-latin", "reference"],
  },
  {
    id: "la-reference-lexicon-workflow",
    partId: "la-vocabulary-reference",
    kind: "appendix",
    title: "原文查典與版本比對流程",
    titleOriginal: "Ratio lexica et critica",
    difficulty: 2,
    track: "reference",
    estimatedPages: 8,
    status: "planned",
    source: EDITORIAL_SOURCE,
    learningGoals: ["從表面詞形回到詞元、語法與上下文義。", "分清古代作品、現代校勘版、翻譯、標註與錄音的權利層。"],
    tags: ["latin", "lexicon", "textual-criticism", "licensing", "workflow"],
  },
];

const memoryArea = (unit: number) => {
  if (unit <= 30) return { label: "武加大核心句", tag: "vulgate" };
  if (unit <= 50) return { label: "禱文與信經", tag: "prayer-creed" };
  if (unit <= 75) return { label: "羅馬彌撒固定經文", tag: "ordo-missae" };
  if (unit <= 87) return { label: "核心拉丁教父", tag: "patristic-core" };
  if (unit <= 95) return { label: "進階拉丁教父", tag: "patristic-advanced" };
  if (unit <= 99) return { label: "經院橋接文本", tag: "scholastic" };
  return { label: "百句總複習", tag: "capstone" };
};

const memorySelections: SelectionSeed[] = Array.from(
  { length: 100 },
  (_, index): SelectionSeed => {
    const unit = index + 1;
    const area = memoryArea(unit);
    const difficulty: OriginalReaderSelection["difficulty"] =
      unit <= 20 ? 1 : unit <= 50 ? 2 : unit <= 80 ? 3 : 4;
    const track: OriginalReaderSelection["track"] = unit <= 87 ? "core" : "advanced";

    return {
      id: `la-memory-${String(unit).padStart(3, "0")}`,
      partId: "la-memory-units",
      kind: "memory_unit",
      title: `記憶單元 ${String(unit).padStart(3, "0")}｜${area.label}`,
      titleOriginal: `Unitas memoriae ${String(unit).padStart(3, "0")}`,
      subtitle: "精確原句、出處、繁中直譯、關鍵詞形與音訊須於文本來源凍結後填入。",
      difficulty,
      track,
      estimatedPages: 2,
      status: "planned",
      source: MEMORY_SOURCE,
      learningGoals: [
        "逐字準確背誦本單元的拉丁原句與繁中直譯。",
        "不看提示辨認核心屈折詞形與句法骨架。",
        "依指定教會發音完成慢速與自然速朗讀。",
      ],
      tags: ["latin", "memory-unit", area.tag, "text-pending", `unit-${String(unit).padStart(3, "0")}`],
    };
  },
);

const psalm22Segments: OriginalReaderSegment[] = [
  {
    id: "la-ps22-v1",
    ordinal: 1,
    ref: "Ps 22:1 Vulgata Clementina",
    sourceText: "Psalmus David. Dominus regit me, et nihil mihi deerit:",
    translationZh: "達味詩。上主牧養我，我必一無所缺。",
    grammarNotes: [
      "regit 是 rego 的直陳式現在時主動語態第三人稱單數；此處以『管理／牧養』表達牧者意象。",
      "mihi 是第一人稱單數與格；desum 可用與格標示『對某人而言缺少』。",
    ],
    textualNotes: ["本讀本按武加大編號為詠 22；馬所拉文本及多數現代譯本編為詩 23。繁中為本計畫依拉丁文所作直譯，非官方禮儀譯文。"],
    tokens: [
      {
        id: "la-ps22-v1-dominus",
        ordinal: 3,
        surface: "Dominus",
        normalized: "dominus",
        lemma: "dominus",
        glossZh: "主、上主",
        partOfSpeech: "noun",
        morphology: { case: "nominative", number: "singular", gender: "masculine" },
        syntaxNote: "regit 的主語。",
      },
      {
        id: "la-ps22-v1-regit",
        ordinal: 4,
        surface: "regit",
        lemma: "rego",
        glossZh: "管理、引領、牧養",
        partOfSpeech: "verb",
        morphology: { person: "3", number: "singular", tense: "present", mood: "indicative", voice: "active" },
      },
      {
        id: "la-ps22-v1-mihi",
        ordinal: 8,
        surface: "mihi",
        lemma: "ego",
        glossZh: "對我、給我",
        partOfSpeech: "pronoun",
        morphology: { case: "dative", number: "singular", person: "1" },
      },
      {
        id: "la-ps22-v1-deerit",
        ordinal: 9,
        surface: "deerit",
        lemma: "desum",
        glossZh: "將缺少",
        partOfSpeech: "verb",
        morphology: { person: "3", number: "singular", tense: "future", mood: "indicative", voice: "active" },
        syntaxNote: "nihil 為中性單數主格，mihi 為受事與格。",
      },
    ],
  },
  {
    id: "la-ps22-v2",
    ordinal: 2,
    ref: "Ps 22:2 Vulgata Clementina",
    sourceText: "in loco pascuæ, ibi me collocavit. Super aquam refectionis educavit me;",
    translationZh: "祂使我安置在牧草之地；祂在使人復甦的水邊滋養了我。",
    grammarNotes: ["loco 是 in 支配奪格的地點用法；pascuæ 是屬格，限定『地方』。", "collocavit 與 educavit 都是完成式，主語承接上一節的 Dominus。"],
    textualNotes: ["繁中為本計畫直譯；保留 refectionis 的『恢復、復甦』意象。"],
    tokens: [
      {
        id: "la-ps22-v2-loco",
        ordinal: 2,
        surface: "loco",
        lemma: "locus",
        glossZh: "地方",
        partOfSpeech: "noun",
        morphology: { case: "ablative", number: "singular", gender: "masculine" },
      },
      {
        id: "la-ps22-v2-pascuae",
        ordinal: 3,
        surface: "pascuæ",
        normalized: "pascuae",
        lemma: "pascua",
        glossZh: "牧草、牧場",
        partOfSpeech: "noun",
        morphology: { case: "genitive", number: "singular", gender: "feminine" },
      },
      {
        id: "la-ps22-v2-collocavit",
        ordinal: 6,
        surface: "collocavit",
        lemma: "colloco",
        glossZh: "安置了",
        partOfSpeech: "verb",
        morphology: { person: "3", number: "singular", tense: "perfect", mood: "indicative", voice: "active" },
      },
      {
        id: "la-ps22-v2-refectionis",
        ordinal: 9,
        surface: "refectionis",
        lemma: "refectio",
        glossZh: "恢復、復甦",
        partOfSpeech: "noun",
        morphology: { case: "genitive", number: "singular", gender: "feminine" },
      },
      {
        id: "la-ps22-v2-educavit",
        ordinal: 10,
        surface: "educavit",
        lemma: "educo (educare)",
        glossZh: "養育了、滋養了",
        partOfSpeech: "verb",
        morphology: { person: "3", number: "singular", tense: "perfect", mood: "indicative", voice: "active" },
        syntaxNote: "第一變位 educo, educare 的完成式；不是第三變位 educere（其完成式為 eduxit）。",
      },
    ],
  },
  {
    id: "la-ps22-v3",
    ordinal: 3,
    ref: "Ps 22:3 Vulgata Clementina",
    sourceText: "animam meam convertit. Deduxit me super semitas justitiæ propter nomen suum.",
    translationZh: "祂使我的靈魂回轉；為了祂的名，祂引領我走上正義的道路。",
    grammarNotes: [
      "convertit 的無長音拼寫可同形於現在式或完成式；此處依相鄰完成式敘事作完成式理解。",
      "propter 支配受格 nomen；suum 回指本句主語。",
    ],
    textualNotes: ["本來源保存 Clementine 拼法 justitiæ；normalized 欄位採 iustitia。"],
    tokens: [
      {
        id: "la-ps22-v3-animam",
        ordinal: 1,
        surface: "animam",
        lemma: "anima",
        glossZh: "靈魂、生命",
        partOfSpeech: "noun",
        morphology: { case: "accusative", number: "singular", gender: "feminine" },
      },
      {
        id: "la-ps22-v3-convertit",
        ordinal: 3,
        surface: "convertit",
        lemma: "converto",
        glossZh: "使回轉、恢復了",
        partOfSpeech: "verb",
        morphology: { person: "3", number: "singular", tense: "perfect (contextual)", mood: "indicative", voice: "active" },
        syntaxNote: "表面形與現在式第三人稱單數相同；時態判定依上下文。",
      },
      {
        id: "la-ps22-v3-deduxit",
        ordinal: 4,
        surface: "Deduxit",
        normalized: "deduxit",
        lemma: "deduco",
        glossZh: "引領了",
        partOfSpeech: "verb",
        morphology: { person: "3", number: "singular", tense: "perfect", mood: "indicative", voice: "active" },
      },
      {
        id: "la-ps22-v3-semitas",
        ordinal: 7,
        surface: "semitas",
        lemma: "semita",
        glossZh: "小徑、道路",
        partOfSpeech: "noun",
        morphology: { case: "accusative", number: "plural", gender: "feminine" },
      },
      {
        id: "la-ps22-v3-justitiae",
        ordinal: 8,
        surface: "justitiæ",
        normalized: "iustitiae",
        lemma: "iustitia",
        glossZh: "正義、公義",
        partOfSpeech: "noun",
        morphology: { case: "genitive", number: "singular", gender: "feminine" },
      },
    ],
  },
  {
    id: "la-ps22-v4",
    ordinal: 4,
    ref: "Ps 22:4 Vulgata Clementina",
    sourceText: "Nam etsi ambulavero in medio umbræ mortis, non timebo mala, quoniam tu mecum es. Virga tua, et baculus tuus, ipsa me consolata sunt.",
    translationZh: "即使我行走在死亡陰影之中，我也不怕災禍，因為祢與我同在。祢的棍、祢的杖，正是它們安慰了我。",
    grammarNotes: [
      "ambulavero 可形式上解析為未來完成直陳式或完成虛擬式；與 etsi、timebo 構成未來條件時，以未來完成直陳式理解。",
      "mecum 是 cum me 的後置合寫。",
      "consolata sunt 是反身動詞 consolor 的完成式第三人稱複數；ipsa 以中性複數集合指前面的 virga 與 baculus。",
    ],
    tokens: [
      {
        id: "la-ps22-v4-ambulavero",
        ordinal: 3,
        surface: "ambulavero",
        lemma: "ambulo",
        glossZh: "即使我將走過",
        partOfSpeech: "verb",
        morphology: { person: "1", number: "singular", tense: "future perfect (contextual)", mood: "indicative", voice: "active" },
        syntaxNote: "形式亦可能是完成虛擬式；本句依未來條件語境判定。",
      },
      {
        id: "la-ps22-v4-timebo",
        ordinal: 9,
        surface: "timebo",
        lemma: "timeo",
        glossZh: "我將害怕",
        partOfSpeech: "verb",
        morphology: { person: "1", number: "singular", tense: "future", mood: "indicative", voice: "active" },
      },
      {
        id: "la-ps22-v4-mecum",
        ordinal: 13,
        surface: "mecum",
        lemma: "ego",
        glossZh: "與我同在",
        partOfSpeech: "pronoun + preposition",
        morphology: { case: "ablative", number: "singular", person: "1" },
      },
      {
        id: "la-ps22-v4-virga",
        ordinal: 15,
        surface: "Virga",
        normalized: "virga",
        lemma: "virga",
        glossZh: "棍、杖",
        partOfSpeech: "noun",
        morphology: { case: "nominative", number: "singular", gender: "feminine" },
      },
      {
        id: "la-ps22-v4-baculus",
        ordinal: 18,
        surface: "baculus",
        lemma: "baculus",
        glossZh: "手杖、牧杖",
        partOfSpeech: "noun",
        morphology: { case: "nominative", number: "singular", gender: "masculine" },
      },
      {
        id: "la-ps22-v4-consolata",
        ordinal: 22,
        surface: "consolata",
        lemma: "consolor",
        glossZh: "安慰了",
        partOfSpeech: "participle (deponent)",
        morphology: { case: "nominative", number: "plural", gender: "neuter", tense: "perfect", voice: "deponent" },
        syntaxNote: "與 sunt 合成完成直陳式第三人稱複數。",
      },
    ],
  },
  {
    id: "la-ps22-v5",
    ordinal: 5,
    ref: "Ps 22:5 Vulgata Clementina",
    sourceText: "Parasti in conspectu meo mensam adversus eos qui tribulant me; impinguasti in oleo caput meum: et calix meus inebrians, quam præclarus est!",
    translationZh: "祢在我面前擺設筵席，對著那些苦害我的人；祢用油滋潤我的頭；我那使人陶醉的杯，是何等華美！",
    grammarNotes: ["parasti 是 paravisti 的縮合完成式。", "inebrians 是現在主動分詞，主格單數，修飾 calix。"],
    tokens: [
      {
        id: "la-ps22-v5-parasti",
        ordinal: 1,
        surface: "Parasti",
        normalized: "parasti",
        lemma: "paro",
        glossZh: "祢預備了",
        partOfSpeech: "verb",
        morphology: { person: "2", number: "singular", tense: "perfect", mood: "indicative", voice: "active", form: "syncopated for paravisti" },
      },
      {
        id: "la-ps22-v5-conspectu",
        ordinal: 3,
        surface: "conspectu",
        lemma: "conspectus",
        glossZh: "視線、面前",
        partOfSpeech: "noun",
        morphology: { case: "ablative", number: "singular", gender: "masculine" },
      },
      {
        id: "la-ps22-v5-mensam",
        ordinal: 5,
        surface: "mensam",
        lemma: "mensa",
        glossZh: "桌子、筵席",
        partOfSpeech: "noun",
        morphology: { case: "accusative", number: "singular", gender: "feminine" },
      },
      {
        id: "la-ps22-v5-tribulant",
        ordinal: 9,
        surface: "tribulant",
        lemma: "tribulo",
        glossZh: "苦害、壓迫",
        partOfSpeech: "verb",
        morphology: { person: "3", number: "plural", tense: "present", mood: "indicative", voice: "active" },
      },
      {
        id: "la-ps22-v5-impinguasti",
        ordinal: 11,
        surface: "impinguasti",
        lemma: "impinguo",
        glossZh: "祢使豐潤、以油滋潤了",
        partOfSpeech: "verb",
        morphology: { person: "2", number: "singular", tense: "perfect", mood: "indicative", voice: "active" },
      },
      {
        id: "la-ps22-v5-inebrians",
        ordinal: 19,
        surface: "inebrians",
        lemma: "inebrio",
        glossZh: "使人陶醉的",
        partOfSpeech: "participle",
        morphology: { case: "nominative", number: "singular", gender: "masculine", tense: "present", voice: "active" },
      },
      {
        id: "la-ps22-v5-praeclarus",
        ordinal: 21,
        surface: "præclarus",
        normalized: "praeclarus",
        lemma: "praeclarus",
        glossZh: "卓越的、華美的",
        partOfSpeech: "adjective",
        morphology: { case: "nominative", number: "singular", gender: "masculine", degree: "positive" },
      },
    ],
  },
  {
    id: "la-ps22-v6",
    ordinal: 6,
    ref: "Ps 22:6 Vulgata Clementina",
    sourceText: "Et misericordia tua subsequetur me omnibus diebus vitæ meæ; et ut inhabitem in domo Domini in longitudinem dierum.",
    translationZh: "祢的慈悲必在我一生所有日子追隨我；使我得以居住在上主的家中，直到長久的歲月。",
    grammarNotes: ["subsequetur 是 subsequor 的未來直陳式第三人稱單數，形被動而義主動。", "ut inhabitem 使用現在虛擬式，表達目的或結果。"],
    tokens: [
      {
        id: "la-ps22-v6-misericordia",
        ordinal: 2,
        surface: "misericordia",
        lemma: "misericordia",
        glossZh: "慈悲、憐憫",
        partOfSpeech: "noun",
        morphology: { case: "nominative", number: "singular", gender: "feminine" },
        syntaxNote: "subsequetur 的主語。",
      },
      {
        id: "la-ps22-v6-subsequetur",
        ordinal: 4,
        surface: "subsequetur",
        lemma: "subsequor",
        glossZh: "將追隨",
        partOfSpeech: "verb (deponent)",
        morphology: { person: "3", number: "singular", tense: "future", mood: "indicative", voice: "deponent" },
      },
      {
        id: "la-ps22-v6-diebus",
        ordinal: 7,
        surface: "diebus",
        lemma: "dies",
        glossZh: "日子",
        partOfSpeech: "noun",
        morphology: { case: "ablative", number: "plural", gender: "masculine" },
        syntaxNote: "omnibus 修飾 diebus，作時間範圍的奪格。",
      },
      {
        id: "la-ps22-v6-inhabitem",
        ordinal: 12,
        surface: "inhabitem",
        lemma: "inhabito",
        glossZh: "使我得以居住",
        partOfSpeech: "verb",
        morphology: { person: "1", number: "singular", tense: "present", mood: "subjunctive", voice: "active" },
      },
      {
        id: "la-ps22-v6-longitudinem",
        ordinal: 17,
        surface: "longitudinem",
        lemma: "longitudo",
        glossZh: "長久、長度",
        partOfSpeech: "noun",
        morphology: { case: "accusative", number: "singular", gender: "feminine" },
        syntaxNote: "由 in 支配受格，表示延伸至長久歲月。",
      },
    ],
  },
];

interface ScriptureSpec {
  id: string;
  bookCode: string;
  chapter: number;
  title: string;
  titleOriginal: string;
  subtitle: string;
  difficulty: OriginalReaderSelection["difficulty"];
  pages: number;
  goals: string[];
  tags: string[];
}

const scriptureSpecs: ScriptureSpec[] = [
  { id: "gen-1", bookCode: "GEN", chapter: 1, title: "創世紀 1｜創造", titleOriginal: "Genesis 1", subtitle: "創造敘事、完成式與命令／願望表達。", difficulty: 2, pages: 16, goals: ["辨識創造敘事的重複公式。", "比較拉丁譯文與希伯來／希臘平行文本的關鍵詞。"], tags: ["torah", "creation"] },
  { id: "exod-3", bookCode: "EXO", chapter: 3, title: "出谷紀 3｜燃燒的荊棘與聖名", titleOriginal: "Exodus 3", subtitle: "召命敘事、神聖顯現與 sum 的核心形式。", difficulty: 2, pages: 14, goals: ["追蹤召命對話的說話者與命令式。", "辨識聖名段落的存在動詞。"], tags: ["torah", "vocation", "divine-name"] },
  { id: "ps-22", bookCode: "PSA", chapter: 22, title: "詠篇 22｜上主是我的牧者", titleOriginal: "Psalmi 22", subtitle: "武加大編號 22；馬所拉及多數現代譯本編號 23。", difficulty: 1, pages: 6, goals: ["背誦六節拉丁文並辨識第一、第二人稱轉換。", "掌握牧者詩中的與格、奪格與未來式。"], tags: ["psalm", "shepherd", "memory"] },
  { id: "ps-50", bookCode: "PSA", chapter: 50, title: "詠篇 50｜天主，求祢垂憐", titleOriginal: "Psalmi 50", subtitle: "武加大編號 50；馬所拉及多數現代譯本編號 51。", difficulty: 2, pages: 10, goals: ["辨識悔罪詩的祈使與虛擬語氣。", "建立 misericordia、iniquitas、cor 等靈修詞彙網。"], tags: ["psalm", "penitential"] },
  { id: "isa-7", bookCode: "ISA", chapter: 7, title: "依撒意亞 7｜厄瑪奴耳記號", titleOriginal: "Isaias 7", subtitle: "先知敘事、政治危機與記號語彙。", difficulty: 3, pages: 14, goals: ["拆解先知言說與敘事轉換。", "比較 virgo、signum、Emmanuel 的翻譯史。"], tags: ["prophets", "immanuel"] },
  { id: "mark-1", bookCode: "MRK", chapter: 1, title: "馬爾谷福音 1｜福音的開始", titleOriginal: "Marcus 1", subtitle: "快速敘事、洗禮、召叫與醫治。", difficulty: 2, pages: 18, goals: ["追蹤敘事中的現在式與完成式。", "建立福音宣講與醫治詞彙。"], tags: ["gospel", "narrative"] },
  { id: "matt-5", bookCode: "MAT", chapter: 5, title: "瑪竇福音 5｜山中聖訓（一）", titleOriginal: "Matthaeus 5", subtitle: "真福、鹽與光、法律詮釋。", difficulty: 3, pages: 20, goals: ["辨識 beatus 句式與關係子句。", "分析 antithesis 中的命令與義務表達。"], tags: ["gospel", "sermon-on-the-mount", "ethics"] },
  { id: "matt-6", bookCode: "MAT", chapter: 6, title: "瑪竇福音 6｜山中聖訓（二）", titleOriginal: "Matthaeus 6", subtitle: "施捨、祈禱、主禱文與信靠。", difficulty: 3, pages: 18, goals: ["精讀主禱文的祈願虛擬式。", "辨識否定命令與目的子句。"], tags: ["gospel", "sermon-on-the-mount", "pater-noster"] },
  { id: "luke-1", bookCode: "LUK", chapter: 1, title: "路加福音 1｜預報與尊主頌", titleOriginal: "Lucas 1", subtitle: "序言、報喜、Magnificat 與 Benedictus。", difficulty: 3, pages: 30, goals: ["區分敘事散文與聖經頌歌語域。", "掌握間接敘述、分詞與預言完成式。"], tags: ["gospel", "magnificat", "benedictus"] },
  { id: "luke-2", bookCode: "LUK", chapter: 2, title: "路加福音 2｜聖誕與西面頌", titleOriginal: "Lucas 2", subtitle: "戶籍、誕生、牧人、奉獻與 Nunc dimittis。", difficulty: 3, pages: 24, goals: ["閱讀出生敘事中的時間與地點結構。", "背誦 Nunc dimittis 並辨識其格位。"], tags: ["gospel", "nativity", "nunc-dimittis"] },
  { id: "john-1", bookCode: "JHN", chapter: 1, title: "若望福音 1｜聖言成了血肉", titleOriginal: "Ioannes 1", subtitle: "Logos 序言、見證與首批門徒。", difficulty: 3, pages: 20, goals: ["辨識 erat、factum est 與 caro 的神學句法。", "建立 verbum、lux、vita、gratia、veritas 詞彙網。"], tags: ["gospel", "logos", "incarnation"] },
  { id: "acts-2", bookCode: "ACT", chapter: 2, title: "宗徒大事錄 2｜五旬節", titleOriginal: "Actus Apostolorum 2", subtitle: "聖神降臨、伯多祿演說與初代團體。", difficulty: 3, pages: 22, goals: ["拆解長篇演說與舊約引文。", "辨識團體生活與洗禮詞彙。"], tags: ["acts", "pentecost", "church"] },
  { id: "1cor-13", bookCode: "1CO", chapter: 13, title: "格林多前書 13｜愛德之歌", titleOriginal: "I ad Corinthios 13", subtitle: "caritas 的修辭、否定與比較。", difficulty: 2, pages: 10, goals: ["背誦 caritas 的動詞與形容詞鏈。", "辨識條件句、對比與最高級。"], tags: ["paul", "charity", "rhetoric"] },
  { id: "phil-2", bookCode: "PHP", chapter: 2, title: "斐理伯書 2｜基督虛己之歌", titleOriginal: "Ad Philippenses 2", subtitle: "勸勉、謙卑與基督論頌歌。", difficulty: 3, pages: 12, goals: ["拆解分詞密集的基督論段落。", "辨識 forma、servus、exinanivit、exaltavit 的語義關係。"], tags: ["paul", "christ-hymn", "kenosis"] },
  { id: "rom-8", bookCode: "ROM", chapter: 8, title: "羅馬書 8｜聖神內的生命", titleOriginal: "Ad Romanos 8", subtitle: "法律、肉身、聖神、收養與盼望。", difficulty: 4, pages: 26, goals: ["追蹤長篇論證中的連接詞與代名詞指涉。", "建立 lex、caro、spiritus、adoptio、gloria 詞彙網。"], tags: ["paul", "spirit", "argument"] },
];

const scriptureSelections: SelectionSeed[] = scriptureSpecs.map(
  (spec): SelectionSeed => ({
    id: `la-vulgate-${spec.id}`,
    partId: "la-vulgate",
    kind: "bible_chapter",
    title: spec.title,
    titleOriginal: spec.titleOriginal,
    subtitle: spec.subtitle,
    difficulty: spec.difficulty,
    track: spec.difficulty === 4 ? "advanced" : "core",
    estimatedPages: spec.pages,
    status: spec.id === "ps-22" ? "sample_ready" : "planned",
    source: spec.id === "ps-22" ? PSALM_22_SOURCE : VULGATE_SOURCE,
    scripture: {
      bookCode: spec.bookCode,
      chapter: spec.chapter,
      ...(spec.id === "ps-22" ? { verseFrom: 1, verseTo: 6 } : {}),
      versionCode: "latVUC",
      parallelGroup: spec.id,
    },
    ...(spec.id === "ps-22" ? { segments: psalm22Segments } : {}),
    learningGoals: spec.goals,
    tags: ["latin", "vulgate", "latVUC", ...spec.tags],
  }),
);

interface PrayerSpec {
  id: string;
  title: string;
  titleOriginal: string;
  subtitle: string;
  kind: "prayer" | "creed";
  difficulty: OriginalReaderSelection["difficulty"];
  pages: number;
  source?: OriginalReaderSource;
  scripture?: OriginalReaderSelection["scripture"];
  tags: string[];
}

const prayerSpecs: PrayerSpec[] = [
  { id: "nicene-creed", title: "尼西亞—君士坦丁堡信經", titleOriginal: "Symbolum Nicaenum-Constantinopolitanum", subtitle: "神學詞彙最密集的普世信經；含 consubstantialis、incarnatus 等核心詞。", kind: "creed", difficulty: 3, pages: 8, tags: ["creed", "trinity", "christology"] },
  { id: "apostles-creed", title: "宗徒信經", titleOriginal: "Symbolum Apostolorum", subtitle: "較短的信仰綱要，適合作為信經入門。", kind: "creed", difficulty: 2, pages: 4, tags: ["creed", "catechesis"] },
  { id: "athanasian-creed", title: "亞他拿修信經", titleOriginal: "Symbolum Quicumque", subtitle: "三位一體與基督二性的嚴密命題鏈。", kind: "creed", difficulty: 4, pages: 12, tags: ["creed", "trinity", "christology"] },
  { id: "pater-noster", title: "天主經／主禱文", titleOriginal: "Pater noster", subtitle: "七項祈求與虛擬語氣的基礎範本。", kind: "prayer", difficulty: 1, pages: 4, tags: ["daily-prayer", "lords-prayer"] },
  { id: "ave-maria", title: "聖母經", titleOriginal: "Ave Maria", subtitle: "問候、祝福與代禱的短篇核心祈禱。", kind: "prayer", difficulty: 1, pages: 3, tags: ["daily-prayer", "marian"] },
  { id: "gloria-patri", title: "榮福經", titleOriginal: "Gloria Patri", subtitle: "三一頌榮與 sicut erat 公式。", kind: "prayer", difficulty: 1, pages: 2, tags: ["doxology", "trinity"] },
  { id: "salve-regina", title: "又聖母經", titleOriginal: "Salve Regina", subtitle: "流亡、慈悲與轉求意象的中世紀聖母對經。", kind: "prayer", difficulty: 2, pages: 5, tags: ["marian", "antiphon"] },
  { id: "magnificat", title: "尊主頌／謝主曲", titleOriginal: "Magnificat", subtitle: "路加福音 1:46–55；社會翻轉與盟約記憶。", kind: "prayer", difficulty: 2, pages: 6, source: VULGATE_SOURCE, scripture: { bookCode: "LUK", chapter: 1, verseFrom: 46, verseTo: 55, versionCode: "latVUC", parallelGroup: "magnificat" }, tags: ["biblical-canticle", "marian"] },
  { id: "nunc-dimittis", title: "西面頌／遣散曲", titleOriginal: "Nunc dimittis", subtitle: "路加福音 2:29–32；安息、救恩、光與榮耀。", kind: "prayer", difficulty: 2, pages: 4, source: VULGATE_SOURCE, scripture: { bookCode: "LUK", chapter: 2, verseFrom: 29, verseTo: 32, versionCode: "latVUC", parallelGroup: "nunc-dimittis" }, tags: ["biblical-canticle", "compline"] },
  { id: "benedictus", title: "讚主曲", titleOriginal: "Benedictus Dominus Deus Israel", subtitle: "路加福音 1:68–79；盟約、救贖與預言。", kind: "prayer", difficulty: 3, pages: 7, source: VULGATE_SOURCE, scripture: { bookCode: "LUK", chapter: 1, verseFrom: 68, verseTo: 79, versionCode: "latVUC", parallelGroup: "benedictus" }, tags: ["biblical-canticle", "lauds"] },
  { id: "te-deum", title: "謝主頌", titleOriginal: "Te Deum", subtitle: "古老宏大的讚美詩與教會／諸聖意象。", kind: "prayer", difficulty: 3, pages: 8, tags: ["hymn", "thanksgiving"] },
  { id: "veni-creator", title: "懇求造物聖神降臨", titleOriginal: "Veni Creator Spiritus", subtitle: "聖神、恩寵、恩賜與光照詞彙。", kind: "prayer", difficulty: 3, pages: 6, tags: ["hymn", "holy-spirit"] },
  { id: "tantum-ergo", title: "皇皇聖體", titleOriginal: "Tantum ergo", subtitle: "阿奎那聖體詩節；感官、信德與新舊禮法。", kind: "prayer", difficulty: 3, pages: 4, tags: ["aquinas", "eucharist", "hymn"] },
  { id: "o-salutaris-hostia", title: "榮福聖體頌", titleOriginal: "O salutaris Hostia", subtitle: "阿奎那聖體詩節；祭獻、戰鬥與援助意象。", kind: "prayer", difficulty: 3, pages: 3, tags: ["aquinas", "eucharist", "hymn"] },
  { id: "panis-angelicus", title: "至聖華筵", titleOriginal: "Panis angelicus", subtitle: "阿奎那聖體詩節；天使之糧與謙卑對比。", kind: "prayer", difficulty: 3, pages: 4, tags: ["aquinas", "eucharist", "hymn"] },
  { id: "dies-irae", title: "末日經", titleOriginal: "Dies irae", subtitle: "審判、號角、灰燼與哀求的末世詩歌。", kind: "prayer", difficulty: 4, pages: 10, tags: ["sequence", "eschatology", "requiem"] },
  { id: "requiem-aeternam", title: "安魂彌撒進堂詠", titleOriginal: "Requiem aeternam", subtitle: "永恆安息、長明之光與垂聽祈禱。", kind: "prayer", difficulty: 2, pages: 4, tags: ["introit", "requiem"] },
  { id: "stabat-mater", title: "痛苦聖母", titleOriginal: "Stabat Mater", subtitle: "十字架下的悲傷、共苦與祈求。", kind: "prayer", difficulty: 4, pages: 10, tags: ["sequence", "marian", "passion"] },
  { id: "exsultet", title: "逾越節宣告", titleOriginal: "Praeconium Paschale (Exsultet)", subtitle: "復活夜的光、黑暗、出谷與基督逾越奧蹟。", kind: "prayer", difficulty: 4, pages: 16, source: PRIVATE_MISSAL_SOURCE, tags: ["easter-vigil", "proclamation", "rights-controlled"] },
  { id: "angelus", title: "三鐘經", titleOriginal: "Angelus Domini", subtitle: "報喜、道成肉身與代禱的對答式祈禱。", kind: "prayer", difficulty: 2, pages: 5, tags: ["daily-prayer", "incarnation", "marian"] },
];

const prayerSelections: SelectionSeed[] = prayerSpecs.map(
  (spec): SelectionSeed => ({
    id: `la-prayer-${spec.id}`,
    partId: "la-prayers-creeds",
    kind: spec.kind,
    title: spec.title,
    titleOriginal: spec.titleOriginal,
    subtitle: spec.subtitle,
    difficulty: spec.difficulty,
    track: spec.difficulty === 4 ? "advanced" : "core",
    estimatedPages: spec.pages,
    status: "planned",
    source: spec.source ?? HISTORICAL_PRAYER_SOURCE,
    ...(spec.scripture ? { scripture: spec.scripture } : {}),
    learningGoals: ["準確朗讀並背誦完整拉丁文本。", "辨認本篇的格位、動詞與核心神學詞彙。", "能說明文本在祈禱、信經或禮儀中的功能。"],
    tags: ["latin", "prayer-creed-canon", ...spec.tags],
  }),
);

interface OrdoSpec {
  id: string;
  title: string;
  titleOriginal: string;
  subtitle: string;
  difficulty: OriginalReaderSelection["difficulty"];
  pages: number;
  track?: OriginalReaderSelection["track"];
  tags: string[];
}

const ordoSpecs: OrdoSpec[] = [
  { id: "scope", title: "彌撒次序、角色與可變經文插入點", titleOriginal: "Ordo, ministeria et loci textuum variabilium", subtitle: "完整流程地圖；明確區分固定經文、可選公式與專用／可變經文。", difficulty: 1, pages: 6, track: "reference", tags: ["orientation", "structure"] },
  { id: "signum-crucis", title: "十字聖號", titleOriginal: "Signum Crucis", subtitle: "開端公式與會眾 Amen。", difficulty: 1, pages: 2, tags: ["ritus-initiales"] },
  { id: "salutatio", title: "致候辭：全部現行固定選式", titleOriginal: "Salutatio populi", subtitle: "主祭致候的現行選式與會眾答句；按授權底本完整收錄。", difficulty: 1, pages: 4, tags: ["ritus-initiales", "dialogue", "options"] },
  { id: "actus-paenitentialis-a", title: "懺悔禮甲式：懺悔詞", titleOriginal: "Actus paenitentialis, formula A: Confiteor", subtitle: "邀請、靜默、Confiteor 與共同祈求。", difficulty: 2, pages: 5, tags: ["ritus-initiales", "penitential-act"] },
  { id: "actus-paenitentialis-b", title: "懺悔禮乙式", titleOriginal: "Actus paenitentialis, formula B", subtitle: "主祭呼句與會眾答句的完整固定選式。", difficulty: 2, pages: 3, tags: ["ritus-initiales", "penitential-act", "options"] },
  { id: "actus-paenitentialis-c", title: "懺悔禮丙式：呼求架構", titleOriginal: "Actus paenitentialis, formula C", subtitle: "保存固定回應與結構；季節性／自選 tropes 標為可變，不以未授權文字補齊。", difficulty: 2, pages: 4, tags: ["ritus-initiales", "penitential-act", "options"] },
  { id: "absolutio-kyrie", title: "赦罪祈禱與求主垂憐", titleOriginal: "Absolutio et Kyrie, eleison", subtitle: "非告解聖事之赦罪祈禱，以及保留希臘文的 Kyrie 對答。", difficulty: 1, pages: 4, tags: ["ritus-initiales", "kyrie", "greek-in-latin-liturgy"] },
  { id: "gloria", title: "光榮頌", titleOriginal: "Gloria in excelsis Deo", subtitle: "主日與慶節所用完整固定讚歌。", difficulty: 3, pages: 7, tags: ["ritus-initiales", "hymn"] },
  { id: "collecta-frame", title: "集禱經框架", titleOriginal: "Invitatio ad collectam et Amen", subtitle: "收錄 Oremus、靜默與 Amen；當日 collecta 是可變專用經文，僅設插入點。", difficulty: 1, pages: 2, tags: ["ritus-initiales", "variable-slot"] },
  { id: "lectiones", title: "讀經宣讀與結語答句", titleOriginal: "Lectiones et acclamationes", subtitle: "Lectio 標題、Verbum Domini 與 Deo gratias；經文內容由當日讀經表插入。", difficulty: 1, pages: 3, tags: ["liturgia-verbi", "dialogue"] },
  { id: "evangelium-praeparatio", title: "福音前準備與祝福", titleOriginal: "Praeparatio et benedictio ante Evangelium", subtitle: "執事請降福、主祭祝福，以及無執事時主祭默禱。", difficulty: 2, pages: 4, tags: ["liturgia-verbi", "gospel", "ministerial-text"] },
  { id: "evangelium-dialogue", title: "福音宣讀對答與結語", titleOriginal: "Dialogus et acclamationes Evangelii", subtitle: "Dominus vobiscum、福音書名、Gloria tibi、Verbum Domini、Laus tibi 與親書默禱。", difficulty: 2, pages: 5, tags: ["liturgia-verbi", "gospel", "dialogue"] },
  { id: "homilia-silence", title: "講道與靜默的結構位置", titleOriginal: "Homilia et silentium", subtitle: "無固定拉丁經文；保留版面、角色與流程標記，避免誤當正文缺漏。", difficulty: 1, pages: 1, track: "reference", tags: ["liturgia-verbi", "structure", "no-fixed-text"] },
  { id: "professio-fidei", title: "信仰宣認：兩種信經選式", titleOriginal: "Professio fidei", subtitle: "交叉引用尼西亞—君士坦丁堡信經與准用時的宗徒信經，避免重複排正文。", difficulty: 3, pages: 2, tags: ["liturgia-verbi", "creed", "cross-reference"] },
  { id: "oratio-universalis", title: "信友禱詞結構", titleOriginal: "Oratio universalis", subtitle: "保存引言、意向、會眾答句與結禱的位置；具體意向為可變文本。", difficulty: 2, pages: 3, track: "reference", tags: ["liturgia-verbi", "variable-slot"] },
  { id: "oblatio-panis", title: "準備祭品：餅的祝福詞", titleOriginal: "Praeparatio donorum: oblatio panis", subtitle: "主祭固定祝福詞與會眾可聽見時的答句。", difficulty: 2, pages: 3, tags: ["liturgia-eucharistica", "offertory"] },
  { id: "aqua-vinum", title: "水酒混合默禱", titleOriginal: "Commixtio aquae et vini", subtitle: "執事或主祭注水時的固定默禱。", difficulty: 2, pages: 2, tags: ["liturgia-eucharistica", "offertory", "private-prayer"] },
  { id: "oblatio-vini", title: "準備祭品：酒的祝福詞", titleOriginal: "Praeparatio donorum: oblatio vini", subtitle: "主祭固定祝福詞與會眾可聽見時的答句。", difficulty: 2, pages: 3, tags: ["liturgia-eucharistica", "offertory"] },
  { id: "in-spiritu-humilitatis", title: "謙卑祈禱", titleOriginal: "In spiritu humilitatis", subtitle: "主祭俯身所念的固定默禱。", difficulty: 2, pages: 2, tags: ["liturgia-eucharistica", "offertory", "private-prayer"] },
  { id: "lavabo", title: "洗手默禱", titleOriginal: "Lavabo", subtitle: "主祭洗手時的固定祈禱。", difficulty: 2, pages: 2, tags: ["liturgia-eucharistica", "offertory", "private-prayer"] },
  { id: "orate-fratres", title: "請眾同禱與會眾答句", titleOriginal: "Orate, fratres", subtitle: "主祭邀請與 Suscipiat Dominus 完整答句。", difficulty: 2, pages: 4, tags: ["liturgia-eucharistica", "dialogue"] },
  { id: "super-oblata-frame", title: "獻禮經框架", titleOriginal: "Oratio super oblata et Amen", subtitle: "保留可變獻禮經插入點及會眾 Amen。", difficulty: 1, pages: 2, track: "reference", tags: ["liturgia-eucharistica", "variable-slot"] },
  { id: "praefatio-dialogue", title: "頌謝詞序言對答", titleOriginal: "Dialogus praefationis", subtitle: "Dominus vobiscum、Sursum corda、Gratias agamus 與固定答句。", difficulty: 1, pages: 4, tags: ["liturgia-eucharistica", "preface", "dialogue"] },
  { id: "praefatio-slot", title: "頌謝詞可變經文插入點", titleOriginal: "Praefatio variabilis", subtitle: "不宣稱有單一『常年期最簡單全文』；依當日／季節選擇授權頌謝詞。", difficulty: 3, pages: 2, track: "reference", tags: ["liturgia-eucharistica", "preface", "variable-slot"] },
  { id: "sanctus", title: "聖、聖、聖", titleOriginal: "Sanctus", subtitle: "完整固定歡呼歌。", difficulty: 1, pages: 3, tags: ["liturgia-eucharistica", "acclamation"] },
  { id: "prex-eucharistica-ii", title: "第二式感恩經：完整固定模板", titleOriginal: "Prex Eucharistica II", subtitle: "按授權底本收錄完整可選感恩經；姓名、共融紀念與當日專用插句以明確欄位標示。", difficulty: 4, pages: 14, track: "advanced", tags: ["liturgia-eucharistica", "eucharistic-prayer", "complete-template"] },
  { id: "mysterium-fidei", title: "信德的奧蹟與全部現行歡呼選式", titleOriginal: "Mysterium fidei et acclamationes", subtitle: "主祭呼句與會眾三個現行選式均納入，不混入地方性未核准變體。", difficulty: 2, pages: 5, tags: ["liturgia-eucharistica", "memorial-acclamation", "options"] },
  { id: "doxologia-finalis", title: "感恩經結尾頌榮與大阿們", titleOriginal: "Doxologia finalis et Amen", subtitle: "Per ipsum 頌榮與會眾 Amen。", difficulty: 2, pages: 3, tags: ["liturgia-eucharistica", "doxology"] },
  { id: "pater-noster", title: "天主經：引言與全文", titleOriginal: "Praeceptis salutaribus moniti et Pater noster", subtitle: "交叉引用核心禱文正文，同時保存彌撒中的引言與流程位置。", difficulty: 2, pages: 4, tags: ["ritus-communionis", "pater-noster", "cross-reference"] },
  { id: "embolismus", title: "天主經後續禱文與頌榮", titleOriginal: "Embolismus et doxologia", subtitle: "Libera nos、會眾 Quia tuum est 與銜接結構。", difficulty: 3, pages: 4, tags: ["ritus-communionis", "embolism"] },
  { id: "pax", title: "平安祈禱與對答", titleOriginal: "Ritus pacis", subtitle: "Domine Iesu Christe、Pax Domini 與會眾答句。", difficulty: 2, pages: 4, tags: ["ritus-communionis", "peace", "dialogue"] },
  { id: "offerte-pacem", title: "互祝平安的可選邀請", titleOriginal: "Offerte vobis pacem", subtitle: "保存可選固定邀請與 rubrical 狀態。", difficulty: 1, pages: 2, tags: ["ritus-communionis", "peace", "optional"] },
  { id: "fractio-agnus", title: "分餅、合酒與羔羊讚", titleOriginal: "Fractio panis, commixtio et Agnus Dei", subtitle: "合酒默禱、Agnus Dei 重複結構與終句。", difficulty: 2, pages: 5, tags: ["ritus-communionis", "agnus-dei", "private-prayer"] },
  { id: "praeparatio-communionis", title: "主祭領聖體前默禱：兩個選式", titleOriginal: "Praeparatio sacerdotis ad Communionem", subtitle: "完整收錄兩個固定可選默禱。", difficulty: 3, pages: 5, tags: ["ritus-communionis", "private-prayer", "options"] },
  { id: "ecce-agnus", title: "請看天主的羔羊與會眾答句", titleOriginal: "Ecce Agnus Dei et Domine, non sum dignus", subtitle: "領聖體前展示、邀請及全體答句。", difficulty: 2, pages: 4, tags: ["ritus-communionis", "dialogue"] },
  { id: "communio-sacerdotis", title: "主祭領受聖體聖血公式", titleOriginal: "Communio sacerdotis", subtitle: "Corpus Christi、Sanguis Christi 及相關固定默禱。", difficulty: 2, pages: 3, tags: ["ritus-communionis", "ministerial-text"] },
  { id: "communio-fidelium", title: "分送聖體公式", titleOriginal: "Communio fidelium", subtitle: "施領者固定公式與領受者 Amen。", difficulty: 1, pages: 2, tags: ["ritus-communionis", "dialogue"] },
  { id: "purificatio", title: "潔淨聖器默禱", titleOriginal: "Purificatio vasorum sacrorum", subtitle: "潔淨時的固定默禱。", difficulty: 2, pages: 2, tags: ["ritus-communionis", "private-prayer"] },
  { id: "postcommunio-frame", title: "領聖體後經框架", titleOriginal: "Oratio post Communionem et Amen", subtitle: "保留 Oremus、可變經文插入點與會眾 Amen。", difficulty: 1, pages: 2, track: "reference", tags: ["ritus-communionis", "variable-slot"] },
  { id: "salutatio-finalis", title: "禮成前致候", titleOriginal: "Salutatio ante benedictionem", subtitle: "Dominus vobiscum 與會眾固定答句。", difficulty: 1, pages: 2, tags: ["ritus-conclusionis", "dialogue"] },
  { id: "benedictio-simplex", title: "普通降福", titleOriginal: "Benedictio simplex", subtitle: "全能天主降福公式與會眾 Amen。", difficulty: 1, pages: 3, tags: ["ritus-conclusionis", "blessing"] },
  { id: "benedictio-solemnis-frame", title: "隆重降福與為民祈禱框架", titleOriginal: "Benedictio sollemnis et oratio super populum", subtitle: "保存執事邀請、答句與結構；季節／節日祝福正文為可變插入項。", difficulty: 2, pages: 3, track: "reference", tags: ["ritus-conclusionis", "variable-slot", "blessing"] },
  { id: "dimissio", title: "遣散：全部現行選式", titleOriginal: "Dimissio", subtitle: "Ite, missa est 及現行准用選式，連同 Deo gratias；不得只保留單一常見式。", difficulty: 1, pages: 4, tags: ["ritus-conclusionis", "dismissal", "options"] },
];

const ordoSelections: SelectionSeed[] = ordoSpecs.map(
  (spec): SelectionSeed => ({
    id: `la-ordo-${spec.id}`,
    partId: "la-ordo-missae",
    kind: spec.id === "scope" ? "orientation" : "liturgy",
    title: spec.title,
    titleOriginal: spec.titleOriginal,
    subtitle: spec.subtitle,
    difficulty: spec.difficulty,
    track: spec.track ?? (spec.difficulty === 4 ? "advanced" : "core"),
    estimatedPages: spec.pages,
    status: "planned",
    source: PRIVATE_MISSAL_SOURCE,
    learningGoals: ["依彌撒流程說出本段之前與之後的段落。", "分辨主祭、執事、會眾及默禱的角色。", "準確朗讀固定經文，並辨認可選或可變插入項。"],
    tags: ["latin", "roman-missal", "ordo-missae", "private-authorized", ...spec.tags],
  }),
);

interface PatristicSpec {
  id: string;
  title: string;
  titleOriginal: string;
  citation: string;
  subtitle: string;
  difficulty: OriginalReaderSelection["difficulty"];
  pages: number;
  track: "core" | "advanced";
  authorTag: string;
}

const patristicSpecs: PatristicSpec[] = [
  { id: "cyprian-dominica-8-12", title: "西彼廉｜主禱文論 8–12", titleOriginal: "Cyprianus, De dominica oratione 8–12", citation: "Cyprianus, De dominica oratione 8–12", subtitle: "主禱文、共同祈禱與基督徒群體。", difficulty: 3, pages: 10, track: "core", authorTag: "cyprian" },
  { id: "ambrose-mysteriis-47-54", title: "盎博羅削｜論奧蹟 47–54", titleOriginal: "Ambrosius, De mysteriis 47–54", citation: "Ambrosius, De mysteriis 47–54", subtitle: "聖體奧蹟、祝聖語言與聖經預像。", difficulty: 3, pages: 10, track: "core", authorTag: "ambrose" },
  { id: "jerome-ep-22-30", title: "熱羅尼莫｜書信 22.30", titleOriginal: "Hieronymus, Epistula 22.30", citation: "Hieronymus, Epistula 22.30", subtitle: "夢境、自我審判與『西塞羅派／基督徒』張力。", difficulty: 3, pages: 8, track: "core", authorTag: "jerome" },
  { id: "augustine-conf-1-1-5", title: "奧古斯丁｜懺悔錄 I.1–5", titleOriginal: "Augustinus, Confessiones I.1–5", citation: "Augustinus, Confessiones I.1–5", subtitle: "不安之心、讚美、認識與呼求。", difficulty: 3, pages: 14, track: "core", authorTag: "augustine" },
  { id: "augustine-conf-8-12", title: "奧古斯丁｜懺悔錄 VIII.12.28–30", titleOriginal: "Augustinus, Confessiones VIII.12.28–30", citation: "Augustinus, Confessiones VIII.12.28–30", subtitle: "花園皈依、tolle lege 與羅馬書。", difficulty: 3, pages: 10, track: "core", authorTag: "augustine" },
  { id: "augustine-sermo-272", title: "奧古斯丁｜講道 272", titleOriginal: "Augustinus, Sermo 272", citation: "Augustinus, Sermo 272", subtitle: "『成為你們所領受的』：教會與聖體。", difficulty: 3, pages: 8, track: "core", authorTag: "augustine" },
  { id: "vincent-commonitorium-2", title: "萊蘭的文森｜備忘錄 2.3–6", titleOriginal: "Vincentius Lerinensis, Commonitorium 2.3–6", citation: "Vincentius Lerinensis, Commonitorium 2.3–6", subtitle: "普遍、恆常、共同持守的信仰準則。", difficulty: 3, pages: 10, track: "core", authorTag: "vincent-of-lerins" },
  { id: "leo-sermo-21", title: "良一世｜講道 21.1–3", titleOriginal: "Leo Magnus, Sermo 21.1–3", citation: "Leo Magnus, Sermo 21.1–3", subtitle: "聖誕、兩性與基督徒尊嚴。", difficulty: 3, pages: 12, track: "core", authorTag: "leo-the-great" },
  { id: "benedict-prologue-1-22", title: "聖本篤會規｜序言 1–22", titleOriginal: "Regula Benedicti, Prologus 1–22", citation: "Regula Benedicti, Prologus 1–22", subtitle: "聆聽、服從與修道學校的開端。", difficulty: 2, pages: 12, track: "core", authorTag: "benedictine-rule" },
  { id: "benedict-72", title: "聖本篤會規｜第 72 章", titleOriginal: "Regula Benedicti 72", citation: "Regula Benedicti, caput 72", subtitle: "良善熱忱、彼此尊敬與共同奔向永生。", difficulty: 2, pages: 6, track: "core", authorTag: "benedictine-rule" },
  { id: "gregory-regula-1-1", title: "大額我略｜牧靈規則 I.1", titleOriginal: "Gregorius Magnus, Regula pastoralis I.1", citation: "Gregorius Magnus, Regula pastoralis I.1", subtitle: "治理之責與不合格領導者的危險。", difficulty: 4, pages: 10, track: "core", authorTag: "gregory-the-great" },
  { id: "cassian-conlationes-1-5-7", title: "卡西安｜會談錄 I.5–7", titleOriginal: "Ioannes Cassianus, Conlationes I.5–7", citation: "Ioannes Cassianus, Conlationes I.5–7", subtitle: "修道生活的目的、目標與心靈純潔。", difficulty: 4, pages: 14, track: "core", authorTag: "john-cassian" },
  { id: "tertullian-apologeticum-39", title: "戴爾都良｜護教篇 39.1–9", titleOriginal: "Tertullianus, Apologeticum 39.1–9", citation: "Tertullianus, Apologeticum 39.1–9", subtitle: "基督徒集會、祈禱、紀律與愛筵。", difficulty: 4, pages: 14, track: "advanced", authorTag: "tertullian" },
  { id: "tertullian-praescriptione-7", title: "戴爾都良｜反異端規條 7.9–13", titleOriginal: "Tertullianus, De praescriptione haereticorum 7.9–13", citation: "Tertullianus, De praescriptione haereticorum 7.9–13", subtitle: "雅典與耶路撒冷、學院與教會之問。", difficulty: 4, pages: 8, track: "advanced", authorTag: "tertullian" },
  { id: "hilary-trinitate-1-1-5", title: "普瓦捷的依拉略｜論三位一體 I.1–5", titleOriginal: "Hilarius Pictaviensis, De Trinitate I.1–5", citation: "Hilarius Pictaviensis, De Trinitate I.1–5", subtitle: "人生目的、哲學追問與天主啟示。", difficulty: 4, pages: 16, track: "advanced", authorTag: "hilary-of-poitiers" },
  { id: "ambrose-officiis-1-132-136", title: "盎博羅削｜論職責 I.132–136", titleOriginal: "Ambrosius, De officiis I.132–136", citation: "Ambrosius, De officiis I.132–136", subtitle: "德行、職責與基督徒倫理修辭。", difficulty: 4, pages: 10, track: "advanced", authorTag: "ambrose" },
  { id: "jerome-prologus-galeatus", title: "熱羅尼莫｜戴盔序言", titleOriginal: "Hieronymus, Prologus Galeatus", citation: "Hieronymus, Prologus Galeatus", subtitle: "希伯來正典、譯本與拉丁聖經序言。", difficulty: 4, pages: 12, track: "advanced", authorTag: "jerome" },
  { id: "augustine-doctrina-1-35-36", title: "奧古斯丁｜論基督教教義 I.35–36", titleOriginal: "Augustinus, De doctrina christiana I.35–36", citation: "Augustinus, De doctrina christiana I.35–36", subtitle: "愛、詮釋目的與善意誤讀的界線。", difficulty: 4, pages: 10, track: "advanced", authorTag: "augustine" },
  { id: "augustine-civitate-19-17", title: "奧古斯丁｜天主之城 XIX.17", titleOriginal: "Augustinus, De civitate Dei XIX.17", citation: "Augustinus, De civitate Dei XIX.17", subtitle: "兩城、現世和平與共同生活秩序。", difficulty: 4, pages: 12, track: "advanced", authorTag: "augustine" },
  { id: "caesarius-sermo-13", title: "阿爾勒的凱撒略｜講道 13.2–5", titleOriginal: "Caesarius Arelatensis, Sermo 13.2–5", citation: "Caesarius Arelatensis, Sermo 13.2–5", subtitle: "平民講道、倫理勸勉與晚期口語化拉丁文。", difficulty: 4, pages: 10, track: "advanced", authorTag: "caesarius-of-arles" },
];

const patristicSelections: SelectionSeed[] = patristicSpecs.map(
  (spec): SelectionSeed => ({
    id: `la-patristic-${spec.id}`,
    partId: spec.track === "core" ? "la-patristic-core" : "la-patristic-advanced",
    kind: "patristic",
    title: spec.title,
    titleOriginal: spec.titleOriginal,
    subtitle: spec.subtitle,
    difficulty: spec.difficulty,
    track: spec.track,
    estimatedPages: spec.pages,
    status: "planned",
    source: PATRISTIC_SOURCE(spec.citation),
    learningGoals: ["逐句分析教父拉丁文的主幹、分詞與從句。", "辨識本篇的歷史語域與核心神學術語。", "能把原文論證與繁中翻譯逐段對照。"],
    tags: ["latin", "patristic", spec.track, spec.authorTag],
  }),
);

const bridgeSelections: SelectionSeed[] = [
  {
    id: "la-bridge-anselm-proslogion-2-3",
    partId: "la-bridge-texts",
    kind: "bridge_text",
    title: "安瑟莫｜《Proslogion》2–3",
    titleOriginal: "Anselmus Cantuariensis, Proslogion 2–3",
    subtitle: "『無可設想有比祂更大者』與本體論論證的拉丁句法。",
    difficulty: 4,
    track: "advanced",
    estimatedPages: 12,
    status: "planned",
    source: SCHOLASTIC_SOURCE("Anselmus Cantuariensis, Proslogion 2–3"),
    learningGoals: ["拆解比較級、關係子句與思想中／實在中的對比。", "用拉丁原文重述論證步驟。"],
    tags: ["latin", "scholastic", "anselm", "philosophy-of-religion"],
  },
  {
    id: "la-bridge-aquinas-st-1-1-1",
    partId: "la-bridge-texts",
    kind: "bridge_text",
    title: "多瑪斯．阿奎那｜神學大全 I，問題 1，條目 1",
    titleOriginal: "Thomas Aquinas, Summa theologiae I, q. 1, a. 1",
    subtitle: "除哲學學科之外，是否還需要另一種教導。",
    difficulty: 4,
    track: "advanced",
    estimatedPages: 12,
    status: "planned",
    source: SCHOLASTIC_SOURCE("Thomas Aquinas, Summa theologiae I, q. 1, a. 1"),
    learningGoals: ["辨認 quaestio、obiectio、sed contra、respondeo 與 ad 結構。", "追蹤自然理性與啟示知識的論證。"],
    tags: ["latin", "scholastic", "aquinas", "sacred-doctrine"],
  },
  {
    id: "la-bridge-aquinas-st-1-2-3",
    partId: "la-bridge-texts",
    kind: "bridge_text",
    title: "多瑪斯．阿奎那｜神學大全 I，問題 2，條目 3",
    titleOriginal: "Thomas Aquinas, Summa theologiae I, q. 2, a. 3",
    subtitle: "天主是否存在：五路論證。",
    difficulty: 4,
    track: "advanced",
    estimatedPages: 18,
    status: "planned",
    source: SCHOLASTIC_SOURCE("Thomas Aquinas, Summa theologiae I, q. 2, a. 3"),
    learningGoals: ["辨認因果、可能／必然、程度與目的論詞彙。", "逐路標出前提、推論與結論。"],
    tags: ["latin", "scholastic", "aquinas", "five-ways"],
  },
  {
    id: "la-bridge-bonaventure-itinerarium-prol-1-3",
    partId: "la-bridge-texts",
    kind: "bridge_text",
    title: "文德｜心靈邁向天主的旅程，序言 1–3",
    titleOriginal: "Bonaventura, Itinerarium mentis in Deum, Prologus 1–3",
    subtitle: "和平、熾愛者方濟與神祕上升的經院—靈修語域。",
    difficulty: 4,
    track: "advanced",
    estimatedPages: 14,
    status: "planned",
    source: SCHOLASTIC_SOURCE("Bonaventura, Itinerarium mentis in Deum, Prologus 1–3"),
    learningGoals: ["辨識經院分析與靈修修辭的交疊。", "追蹤旅程、光照、和平與欲望的意象鏈。"],
    tags: ["latin", "scholastic", "bonaventure", "mysticism"],
  },
];

const appendixSelections: SelectionSeed[] = [
  {
    id: "la-appendix-sacrosanctum-concilium-1-10-14",
    partId: "la-appendices",
    kind: "appendix",
    title: "現代橋接附錄｜禮儀憲章 1、10、14",
    titleOriginal: "Sacrosanctum Concilium 1, 10, 14",
    subtitle: "大公會議目的、禮儀作為高峰與泉源、以及完整主動參與；現代受保護文本。",
    difficulty: 4,
    track: "advanced",
    estimatedPages: 10,
    status: "planned",
    source: SACROSANCTUM_CONCILIUM_SOURCE,
    learningGoals: ["閱讀現代教會公文的長句與制度性語彙。", "比較 patristic、scholastic 與 conciliar Latin 的語域差異。"],
    tags: ["latin", "vatican-ii", "liturgy", "modern-latin", "rights-controlled"],
  },
  {
    id: "la-appendix-source-rights-manifest",
    partId: "la-appendices",
    kind: "appendix",
    title: "版本、授權與校驗清單",
    titleOriginal: "Index editionum, licentiarum et summorum verificatorum",
    subtitle: "每篇的版本、來源 URL、授權、翻譯權、音訊權、checksum 與異文記錄。",
    difficulty: 1,
    track: "reference",
    estimatedPages: 12,
    status: "planned",
    source: EDITORIAL_SOURCE,
    learningGoals: ["能追溯每一頁原文、翻譯與音訊的來源。", "在輸出前辨識 license unknown、NC、版本未凍結等阻斷條件。"],
    tags: ["latin", "provenance", "licensing", "checksum", "production-gate"],
  },
  {
    id: "la-appendix-audio-index",
    partId: "la-appendices",
    kind: "appendix",
    title: "對齊音訊與 QR 索引",
    titleOriginal: "Index auditionum congruentium",
    subtitle: "只連結與固定文本 checksum 相符、且已取得分段與公開播放權的錄音。",
    difficulty: 1,
    track: "reference",
    estimatedPages: 10,
    status: "planned",
    source: EDITORIAL_SOURCE,
    learningGoals: ["用 passage ID 與 checksum 核對紙本、網站及音訊。", "區分教會式、古典式與詠唱式發音軌。"],
    tags: ["latin", "audio", "alignment", "qr", "production-gate"],
  },
];

const orderedSelections: SelectionSeed[] = [
  ...vocabularySelections,
  ...referenceSelections,
  ...memorySelections,
  ...scriptureSelections,
  ...prayerSelections,
  ...ordoSelections,
  ...patristicSelections.filter((selection) => selection.track === "core"),
  ...patristicSelections.filter((selection) => selection.track === "advanced"),
  ...bridgeSelections,
  ...appendixSelections,
];

const selections: OriginalReaderSelection[] = orderedSelections.map((selection, index) => ({
  ...selection,
  ordinal: index + 1,
}));

export const latinOriginalReaderVolume: OriginalReaderVolume = {
  id: "original-reader-la",
  slug: "la",
  language: "la",
  title: "教會拉丁文原文讀本",
  subtitle: "一千詞彙、百句記憶、武加大、祈禱與信經、羅馬彌撒、拉丁教父及經院橋接文本",
  privateUse: true,
  rtl: false,
  print: JIS_B5_READER_PROFILE,
  pronunciationProfiles: [
    {
      id: "la-ecclesiastical-roman",
      label: "羅馬式教會拉丁文",
      description: "紙本與主音軌的預設發音；依現代羅馬天主教常用教會式讀法，重音與連音另行校訂。",
    },
    {
      id: "la-restored-classical",
      label: "古典重建發音",
      description: "比較音軌，用於辨識古典音值與後期演變；不得與主音軌在同一朗讀內混用。",
    },
    {
      id: "la-liturgical-chant",
      label: "禮儀詠唱",
      description: "僅在旋律、編曲、表演與錄音權均已清理後加入；未授權前只保留製作槽位。",
    },
  ],
  textPolicy: {
    scriptStandard: "依各 selection 指定版本校訂的完整教會拉丁文正文",
    requiredMarks: [
      "保留底本的標點、段落、大小寫與可影響讀音或句法的記號",
      "若版本未印 macron 或重音符號，不得由系統臆加；若教學層補入，須與底本文字分層標記",
      "版本、正字與標點差異須在 textualNotes 中留下可追溯記錄",
    ],
    prohibitedSubstitutions: [
      "不得以中文翻譯、現代語改寫或 transliteration 取代拉丁正文",
      "不得因只分析部分 tokens 而截斷、重建或取代完整 sourceText",
      "不得在未註明時混用 restored classical 與 ecclesiastical 拼讀規約",
    ],
    notes:
      "sourceText 永遠完整顯示；tokens 僅另列已校驗的關鍵詞。古典／中世紀／禮儀正字差異不應被靜默正規化，主音軌採羅馬式教會拉丁文。",
  },
  parts: [
    { id: "la-vocabulary-reference", ordinal: 1, title: "第一部｜一千詞彙與語法參考", description: "二十組、每組五十個詞元，另附發音、屈折、句法、查典與授權工作流程。" },
    { id: "la-memory-units", ordinal: 2, title: "第二部｜一百個記憶單元", description: "一百個獨立生產槽；每單元配置原句、直譯、詞形、朗讀與複習。" },
    { id: "la-vulgate", ordinal: 3, title: "第三部｜武加大十五章精讀", description: "固定採 Clementine Vulgate 公版底本；詠篇 22 提供六節已核對樣章。" },
    { id: "la-prayers-creeds", ordinal: 4, title: "第四部｜二十篇禱文、信經與頌歌", description: "按已議定清單收錄三篇信經、日常祈禱、聖經頌歌、聖體詩、末世與節慶文本。" },
    { id: "la-ordo-missae", ordinal: 5, title: "第五部｜現行羅馬彌撒固定經文", description: "完整生產目錄含全部選式、默禱、角色與可變插入點；正文須來自私下獲授權的精確版本。" },
    { id: "la-patristic-core", ordinal: 6, title: "第六部｜拉丁教父核心十二篇", description: "從西彼廉至卡西安的核心選文，建立教父敘事、講道、靈修、教義與牧靈語域。" },
    { id: "la-patristic-advanced", ordinal: 7, title: "第七部｜拉丁教父進階八篇", description: "戴爾都良、依拉略、盎博羅削、熱羅尼莫、奧古斯丁與凱撒略的高階論證文本。" },
    { id: "la-bridge-texts", ordinal: 8, title: "第八部｜四篇經院橋接文本", description: "安瑟莫、多瑪斯與文德，從教父拉丁文過渡到經院論證及神祕神學。" },
    { id: "la-appendices", ordinal: 9, title: "第九部｜現代橋接與生產附錄", description: "含《禮儀憲章》選段、版本授權清單及對齊音訊索引。" },
  ],
  selections,
};

export const latinOriginalReader = latinOriginalReaderVolume;
export const LATIN_ORIGINAL_READER = latinOriginalReaderVolume;

export default latinOriginalReaderVolume;
