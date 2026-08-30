import { describe, expect, it } from "vitest";

import {
  ORIGINAL_READER_VOLUMES,
  getOriginalReaderVolume,
} from "../data/originalReaders/index";
import {
  getHebrewFullHaggadah,
  getHebrewFullLesson,
  getHebrewFullReaderOverview,
  getHebrewReferenceTables,
} from "../data/originalReaders/hebrew-full-reader";
import type {
  OriginalReaderSelection,
  OriginalReaderToken,
  OriginalReaderVolume,
} from "../data/originalReaders/types";
import {
  findUnpointedHebrewWords,
  isFullyPointedHebrewWord,
} from "../server/utils/original-reader-materialize";

function requireVolume(slug: "hbo" | "grc" | "la"): OriginalReaderVolume {
  const volume = getOriginalReaderVolume(slug);
  expect(volume, `missing ${slug} reader manifest`).toBeDefined();
  return volume!;
}

function selectionsInPart(
  volume: OriginalReaderVolume,
  partId: string,
): OriginalReaderSelection[] {
  return volume.selections.filter((selection) => selection.partId === partId);
}

function expectCoreAdvancedSplit(selections: OriginalReaderSelection[]) {
  expect(selections).toHaveLength(20);
  expect(selections.filter((selection) => selection.track === "core")).toHaveLength(12);
  expect(selections.filter((selection) => selection.track === "advanced")).toHaveLength(8);
}

describe("original-reader manifest invariants", () => {
  it("has exactly one private B5 volume for each language", () => {
    expect(ORIGINAL_READER_VOLUMES.map((volume) => volume.slug)).toEqual([
      "hbo",
      "grc",
      "la",
    ]);

    for (const volume of ORIGINAL_READER_VOLUMES) {
      expect(volume.privateUse).toBe(true);
      expect(volume.print).toMatchObject({
        trim: "JIS_B5",
        widthMm: 182,
        heightMm: 257,
        marginTopMm: 18,
        marginBottomMm: 20,
        marginInsideMm: 24,
        marginOutsideMm: 17,
        mirroredMargins: true,
      });
    }
  });

  it("keeps volume, part, and selection IDs unique and ordinals stable", () => {
    const volumeIds = ORIGINAL_READER_VOLUMES.map((volume) => volume.id);
    const allSelectionIds = ORIGINAL_READER_VOLUMES.flatMap((volume) =>
      volume.selections.map((selection) => selection.id),
    );

    expect(new Set(volumeIds).size).toBe(volumeIds.length);
    expect(new Set(allSelectionIds).size).toBe(allSelectionIds.length);

    for (const volume of ORIGINAL_READER_VOLUMES) {
      const partIds = volume.parts.map((part) => part.id);
      expect(new Set(partIds).size).toBe(partIds.length);
      expect(volume.parts.map((part) => part.ordinal)).toEqual(
        Array.from({ length: volume.parts.length }, (_, index) => index + 1),
      );
      expect(volume.selections.map((selection) => selection.ordinal)).toEqual(
        Array.from(
          { length: volume.selections.length },
          (_, index) => index + 1,
        ),
      );

      for (const selection of volume.selections) {
        expect(partIds, `${volume.slug}/${selection.id} has an unknown part`).toContain(
          selection.partId,
        );
        expect(selection.source.authorization).toBe("private-authorized");
      }
    }
  });
});

describe("Hebrew reader curriculum", () => {
  const hebrew = requireVolume("hbo");

  it("reserves 50 consecutive BBH lessons of twenty words each", () => {
    const lessons = hebrew.selections.filter((selection) =>
      /^hbo-vocab-\d{2}$/.test(selection.id),
    );
    expect(lessons).toHaveLength(50);

    const coveredSlots: number[] = [];
    const vocabularyTokens: OriginalReaderToken[] = [];
    lessons.forEach((lesson, index) => {
      expect(lesson.id).toBe(`hbo-vocab-${String(index + 1).padStart(2, "0")}`);
      expect(`${lesson.title} ${lesson.subtitle}`).toMatch(/\d+ (字|詞)/);
      expect(lesson.source.edition).toContain("Basics of Biblical Hebrew Grammar");

      const rangeTag = lesson.tags?.find((tag) => tag.startsWith("slots:"));
      expect(rangeTag, `${lesson.id} has no slots range`).toBeDefined();
      const match = /^slots:(\d+)-(\d+)$/.exec(rangeTag!);
      expect(match, `${lesson.id} has a malformed slots range`).not.toBeNull();
      const start = Number(match![1]);
      const end = Number(match![2]);
      expect(end).toBeGreaterThanOrEqual(start);
      coveredSlots.push(
        ...Array.from({ length: end - start + 1 }, (_, offset) => start + offset),
      );

      expect(lesson.learningGoals?.join(" ")).toMatch(/niqqud|pointed/i);
      expect(lesson.status).toBe("source_ready");
      expect(lesson.segments).toHaveLength(1);
      expect(lesson.segments?.[0].tokens?.length).toBe(end - start + 1);
      expect(findUnpointedHebrewWords(lesson.segments?.[0].sourceText || "")).toEqual([]);
      vocabularyTokens.push(...(lesson.segments?.[0].tokens || []));
    });

    expect(coveredSlots).toEqual(
      Array.from({ length: 1000 }, (_, index) => index + 1),
    );
    expect(vocabularyTokens).toHaveLength(1000);
    expect(new Set(vocabularyTokens.map((token) => token.id)).size).toBe(1000);
    // The BBH2 run is shorter than the textbook's 552 because its person, place
    // and nation names moved to the appendix; the frequency extension reaches
    // further down the corpus by the same amount to keep the total at 1,000.
    expect(vocabularyTokens.filter((token) => token.sourceType === "bbh2_order")).toHaveLength(546);
    expect(vocabularyTokens.filter((token) => token.sourceType === "reader_frequency_extension")).toHaveLength(454);
    expect(vocabularyTokens.filter((token) => (token.sourceOrders?.length || 0) > 1)).toHaveLength(2);
    expect(hebrew.vocabularyCurriculum?.exactOrderingStatus).toBe("verified");

    for (const token of vocabularyTokens) {
      expect(findUnpointedHebrewWords(token.surface), token.id).toEqual([]);
      expect(token.lemmaPointed, token.id).toBe(token.surface);
      expect(token.lemmaUnpointed, token.id).toBeTruthy();
      expect(token.textbookTransliteration, token.id).toBeTruthy();
      expect(typeof token.glossEn, token.id).toBe("string");
      expect(typeof token.isProperName, token.id).toBe("boolean");
      expect(token.verification, token.id).toBeTruthy();
    }
  });

  it("states a Masoretic/Biblical pointed-text policy and never substitutes modern Hebrew", () => {
    const pronunciationPolicy = hebrew.pronunciationProfiles
      .map((profile) => `${profile.label} ${profile.description}`)
      .join(" ");

    expect(hebrew.rtl).toBe(true);
    expect(pronunciationPolicy).toMatch(/馬所拉|Masoretic/i);
    expect(pronunciationPolicy).toMatch(/niqqud/i);
    expect(pronunciationPolicy).toMatch(/不是\s*modern Israeli/i);

    const nonEmptySegments = hebrew.selections.flatMap(
      (selection) => selection.segments?.filter((segment) => segment.sourceText.trim()) ?? [],
    );
    expect(nonEmptySegments.length).toBeGreaterThan(0);

    for (const segment of nonEmptySegments) {
      const HebrewWords = segment.sourceText
        .split(/[\s\u05BE]+/u)
        .filter((word) => /[\u05D0-\u05EA]/u.test(word));
      expect(HebrewWords.length, `${segment.id} has no Hebrew words`).toBeGreaterThan(0);
      expect(
        findUnpointedHebrewWords(segment.sourceText),
        `${segment.id} contains a wholly or partly unpointed Hebrew word`,
      ).toEqual([]);
    }
  });

  it("accepts shureq, matres, closed finals, and YHWH but rejects partial pointing", () => {
    for (const word of ["סוּס", "הוּא", "תּוֹרָה", "בֵּית", "מֶלֶךְ", "יְהוָה"]) {
      expect(isFullyPointedHebrewWord(word), word).toBe(true);
    }
    for (const word of ["דָבר", "שָלם", "דּבר", "שׁ֙מר"]) {
      expect(isFullyPointedHebrewWord(word), word).toBe(false);
    }
    expect(findUnpointedHebrewWords("סוּס יְהוָה דָבר שָלם")).toEqual([
      "דָבר",
      "שָלם",
    ]);
  });

  it("pins BBH homographs, aleph transliteration, POS metadata, and required names", () => {
    const tokens = hebrew.selections
      .filter((selection) => /^hbo-vocab-\d{2}$/.test(selection.id))
      .flatMap((selection) => selection.segments?.[0].tokens || []);
    const bySourceOrder = new Map(
      tokens
        .filter((token) => token.sourceOrder)
        .map((token) => [token.sourceOrder!, token]),
    );

    const expectedStrongBySourceOrder: Record<number, string> = {
      5: "H410",
      109: "H2205",
      283: "H2204",
      111: "H2896",
      360: "H2895",
      229: "H4193",
      301: "H4191",
      538: "H1847",
    };
    for (const [sourceOrder, strong] of Object.entries(expectedStrongBySourceOrder)) {
      expect(bySourceOrder.get(Number(sourceOrder))?.strong, `BBH order ${sourceOrder}`).toBe(strong);
    }

    const expectedTransliterations: Record<string, string> = {
      H7218: "rōʾš",
      H6629: "ṣōʾn",
      H3808: "lōʾ",
      H935: "bôʾ",
      H4672: "māṣāʾ",
      H7121: "qārāʾ",
      H2930: "ṭāmēʾ",
      H1254: "bārāʾ",
    };
    for (const [strong, transliteration] of Object.entries(expectedTransliterations)) {
      expect(
        tokens.find((token) => token.strong === strong)?.textbookTransliteration,
        strong,
      ).toBe(transliteration);
    }

    // Jerusalem, Moses, David and Gibeah are appendix entries now; only divine
    // names and titles still carry a name flag inside the lessons.
    for (const strong of ["H3389", "H4872", "H1732", "H1390", "H7586", "H3063"]) {
      expect(tokens.find((token) => token.strong === strong), strong).toBeUndefined();
    }
    for (const strong of ["H3068", "H430", "H1168", "H7706"]) {
      expect(tokens.find((token) => token.strong === strong)?.isProperName, strong).toBe(true);
    }
    expect(tokens.find((token) => token.strong === "H3068")?.properNameTypes).toEqual([
      "divine_name_or_title",
    ]);
    expect(tokens.filter((token) => !token.partOfSpeech)).toEqual([]);
    expect(tokens.filter((token) => !token.isProperName && token.properNameTypes?.length)).toEqual([]);
  });

  it("contains 15 Tanakh chapters, 20 prayers, the 15-step Haggadah, and 20 rabbinic readings", () => {
    expect(selectionsInPart(hebrew, "hbo-part-tanakh")).toHaveLength(15);
    expect(selectionsInPart(hebrew, "hbo-part-prayers")).toHaveLength(20);
    expect(selectionsInPart(hebrew, "hbo-part-haggadah")).toHaveLength(15);

    const rabbinic = hebrew.selections.filter(
      (selection) => selection.kind === "rabbinic",
    );
    expectCoreAdvancedSplit(rabbinic);
  });
});

describe("complete 50-lesson Hebrew private reader", () => {
  it("assembles all requested content without placeholders", () => {
    const overview = getHebrewFullReaderOverview();
    expect(overview.privateUse).toBe(true);
    expect(overview.chineseBible).toMatchObject({
      versionCode: "cuv2010",
      titleZh: "和合本修訂版（2010）",
      variant: "RCUV2（上帝版）",
    });
    expect(overview.counts).toMatchObject({
      lessons: 50,
      vocabulary: 1000,
      memoryVerses: 100,
      scriptureChapters: 25,
      prayersArticles: 25,
      haggadahSteps: 15,
      haggadahSegments: 199,
    });
    expect(overview.audioStatus).toMatchObject({
      status: "not_recorded",
      recordedTrackCount: 0,
    });

    const refs = new Set<string>();
    for (let lessonNumber = 1; lessonNumber <= 50; lessonNumber += 1) {
      const lesson = getHebrewFullLesson(lessonNumber);
      expect(lesson, `missing full lesson ${lessonNumber}`).not.toBeNull();
      expect(lesson?.vocabulary).toHaveLength(20);
      expect(lesson?.vocabulary).toHaveLength(lesson!.vocabularyCount);
      expect(lesson?.memoryVerses).toHaveLength(2);
      expect(lesson?.reading.segments.length).toBeGreaterThan(0);
      expect(lesson?.vocabulary.every((word) => word.glossZh.trim())).toBe(true);
      expect(lesson?.vocabulary.every((word) => word.textbookTransliteration.trim())).toBe(true);
      expect(lesson?.vocabulary.every((word) => findUnpointedHebrewWords(word.pointed).length === 0)).toBe(true);
      expect(lesson?.reading.segments.every((segment) => segment.text.trim())).toBe(true);
      expect(lesson?.memoryVerses.every((verse) => verse.translationZh.trim())).toBe(true);
      expect(lesson?.chineseBible).toMatchObject({
        versionCode: "cuv2010",
        variant: "RCUV2（上帝版）",
      });
      lesson?.memoryVerses.forEach((verse) => refs.add(verse.ref));

      if (lessonNumber <= 25) {
        expect(lesson?.track).toBe("scripture");
        expect(lesson?.reading.kind).toBe("scripture_chapter");
        expect(lesson?.reading.segments.every((segment) => segment.translationZh.trim())).toBe(true);
      } else {
        expect(lesson?.track).toBe("prayer_article");
        expect(lesson?.reading.kind).toBe("prayer_article");
      }
    }
    expect(refs.size).toBe(100);

    const psalm136 = getHebrewFullLesson(1);
    const combinedPsalm136 = psalm136?.reading.segments.filter(
      (segment) => segment.translationCrosswalk?.translationRange === "11-12",
    );
    expect(combinedPsalm136).toHaveLength(2);
    expect(combinedPsalm136?.map((segment) => segment.translationContinuation)).toEqual([
      false,
      true,
    ]);
    const psalm23 = getHebrewFullLesson(2);
    expect(
      psalm23?.reading.segments.find((segment) => segment.ref === "Ps.23.1")?.translationZh,
    ).toBe("（大衛的詩。）耶和華是我的牧者，我必不致缺乏。");

    const haggadah = getHebrewFullHaggadah();
    expect(haggadah.steps).toHaveLength(15);
    expect(haggadah.steps.flatMap((step) => step.segments)).toHaveLength(199);
    expect(haggadah.steps.flatMap((step) => step.segments).every((segment) => segment.text.trim())).toBe(true);
  });

  it("keeps person, place and nation names out of the lesson vocabulary", () => {
    // The names live in their own appendix table now, so printing them inside a
    // lesson would repeat the same word in two places.  The exceptions are the
    // handful that read as ordinary vocabulary — אָדָם alone occurs 552 times —
    // and each of those carries a written reason in the data.
    const lifted = new Set(["person", "place", "people_or_nation"]);
    for (let lessonNumber = 1; lessonNumber <= 50; lessonNumber += 1) {
      const duplicated = (getHebrewFullLesson(lessonNumber)?.vocabulary || []).filter(
        (word) => (word.properNameTypes || []).some((type) => lifted.has(type)) && !word.keptInLessons,
      );
      expect(duplicated.map((word) => word.pointed), `第 ${lessonNumber} 課仍有專名`).toEqual([]);
    }

    const kept = Array.from({ length: 50 }, (_, index) => getHebrewFullLesson(index + 1))
      .flatMap((lesson) => lesson?.vocabulary || [])
      .filter((word) => word.keptInLessons);
    expect(kept.map((word) => word.pointed).sort()).toEqual(
      ["אָדָם", "יְאֹר", "נֶ֫גֶב", "שְׁאוֹל"].sort(),
    );
    expect(kept.every((word) => (word.keptInLessons || "").trim())).toBe(true);
  });

  it("publishes the numeral, kinship, calendar and proper-name tables", () => {
    const payload = getHebrewReferenceTables();
    expect(payload.tables.map((table) => table.id)).toEqual([
      "hbo-appendix-numerals",
      "hbo-appendix-kinship",
      "hbo-appendix-calendar",
      "hbo-appendix-proper-names",
    ]);

    payload.tables.forEach((table) => {
      expect(table.intro.trim(), `${table.id} 缺凡例`).not.toBe("");
      expect(table.groups.length).toBeGreaterThan(0);
      table.groups.forEach((group) => {
        expect(group.entries.length, `${group.id} 是空的`).toBeGreaterThan(0);
        group.entries.forEach((entry) => {
          expect(entry.glossZh.trim(), `${group.id} 有空白繁中義`).not.toBe("");
          // Split on maqqef: compound names such as בֶּן־הֲדַד are two pointed
          // words joined by it, not one unpointed word.
          const pointed = entry.pointed || entry.masculine?.pointed || "";
          expect(findUnpointedHebrewWords(pointed), `${pointed} 未完全標母音`).toEqual([]);
        });
      });
    });

    // The five Babylonian months that never appear in the Masoretic Text must
    // stay labelled as such rather than passing as biblical words.
    const calendar = payload.tables.find((table) => table.id === "hbo-appendix-calendar");
    const post = calendar?.groups.find((group) => group.id === "babylonian-months-post");
    expect(post?.entries).toHaveLength(5);
    expect(post?.entries.every((entry) => entry.attestation === "post_biblical")).toBe(true);
    expect(post?.source).toBeTruthy();

    // The proper-name table is split nine ways rather than five: a single
    // 「人名」 section swallowed most of the table, so looking up 保羅 and
    // looking up 大衛 meant reading the same heap.  The order is the print
    // order in scripts/proper_name_categories.py -- geography, then divine
    // names, then people from specific to general, with 待歸類 last.
    const names = payload.tables.find((table) => table.id === "hbo-appendix-proper-names");
    // 2026-08-29 使用者重定人名分類：「族長與先知」拆成「先祖與族長」與「先知」，
    // 節期歸曆法表（安息日本來在兩張表各一張卡）。一個名字只出現在一節裡，
    // 所以節名就是卡上那一個標籤。
    expect(names?.groups.map((group) => group.id)).toEqual([
      "民族與國名",
      "地名",
      "神名與稱號",
      "君王",
      "其他人名",
      "先祖與族長",
      "先知",
    ]);
    // 一個名字只能出現在一節裡：跨節重複就是同一個詞印兩張卡。
    const everyName = names!.groups.flatMap((group) =>
      group.entries.map((entry) => entry.glossZh),
    );
    expect(new Set(everyName).size).toBe(everyName.length);
    // Divine names stay in the lessons, so their rows carry a lesson number.
    const divine = names?.groups.find((group) => group.id === "神名與稱號");
    expect(divine?.entries.every((entry) => typeof entry.lesson === "number")).toBe(true);
  });
});

describe("Greek reader curriculum", () => {
  const greek = requireVolume("grc");

  it("keeps Mounce as the verified vocabulary order and Graded Reader as a non-ordering reading path", () => {
    const primary = greek.selections.find(
      (selection) => selection.id === "grc-vocab-curriculum-mounce",
    );
    const supplement = greek.selections.find(
      (selection) => selection.id === "grc-vocab-curriculum-graded-reader",
    );
    const capacityGroups = greek.selections.filter((selection) =>
      /^grc-vocab-\d{2}$/.test(selection.id),
    );

    expect(primary?.title).toMatch(/孟恩思|Mounce/i);
    expect(primary?.subtitle).toContain("2017");
    expect(supplement?.title).toContain("A Graded Reader of Biblical Greek");
    expect(`${supplement?.subtitle} ${supplement?.learningGoals?.join(" ")}`).toMatch(/不.*詞序|沒有.*詞序/);
    expect(capacityGroups).toHaveLength(20);
    const vocabularyTokens: OriginalReaderToken[] = [];
    for (const group of capacityGroups) {
      const policy = `${group.source.edition} ${group.learningGoals?.join(" ")}`;
      expect(policy).toMatch(/Mounce|孟恩思/i);
      expect(group.status).toBe("source_ready");
      expect(group.segments).toHaveLength(1);
      expect(group.segments?.[0].tokens).toHaveLength(50);
      vocabularyTokens.push(...(group.segments?.[0].tokens || []));
    }

    expect(vocabularyTokens).toHaveLength(1000);
    expect(new Set(vocabularyTokens.map((token) => token.id)).size).toBe(1000);
    expect(vocabularyTokens.filter((token) => token.sourceType === "mounce_bbg_chapter_order")).toHaveLength(340);
    expect(vocabularyTokens.filter((token) => token.sourceType === "mounce_official_frequency_extension")).toHaveLength(660);
    expect(greek.vocabularyCurriculum?.exactOrderingStatus).toBe("verified");

    for (const token of vocabularyTokens) {
      expect(token.surface, token.id).toBeTruthy();
      expect(token.printedEntry, token.id).toBeTruthy();
      expect(token.textbookTransliteration, token.id).toBeTruthy();
      expect(token.transliterationSystem, token.id).toMatch(/Mounce/i);
      expect(typeof token.glossEn, token.id).toBe("string");
      expect(typeof token.isProperName, token.id).toBe("boolean");
      expect(token.sourcePage, token.id).toBeGreaterThan(0);
      expect(token.verification, token.id).toBeTruthy();
    }
  });

  it("pins Mounce accent collisions, textbook transliteration, and name types", () => {
    const tokens = greek.selections
      .filter((selection) => /^grc-vocab-\d{2}$/.test(selection.id))
      .flatMap((selection) => selection.segments?.[0].tokens || []);
    const byOrdinal = new Map(
      tokens.map((token) => [token.sourceOrder!, token]),
    );
    const expectedStrongByOrdinal: Record<number, string> = {
      44: "G1519",
      93: "G1487",
      105: "G5101",
      148: "G2228",
      212: "G2590",
      284: "G3757",
      341: "G686",
      489: "G4218",
      689: "G3376",
      698: "G4735",
      811: "G4458",
    };
    for (const [ordinal, strong] of Object.entries(expectedStrongByOrdinal)) {
      expect(byOrdinal.get(Number(ordinal))?.strong, `Mounce ordinal ${ordinal}`).toBe(strong);
    }

    const expectedTransliterations: Record<number, string> = {
      1: "angelos",
      4: "apostolos",
      47: "Iēsous",
      142: "huper",
    };
    for (const [ordinal, transliteration] of Object.entries(expectedTransliterations)) {
      expect(byOrdinal.get(Number(ordinal))?.textbookTransliteration).toBe(transliteration);
    }

    expect(byOrdinal.get(47)?.properNameTypes).toEqual([
      "person",
      "divine_name_or_title",
    ]);
    expect(byOrdinal.get(65)?.properNameTypes).toEqual(["person"]);
    expect(byOrdinal.get(211)?.properNameTypes).toEqual([
      "person",
      "people_or_nation",
    ]);
    expect(byOrdinal.get(570)?.properNameTypes).toEqual(["person"]);
    expect(tokens.filter((token) => token.isProperName)).toHaveLength(56);
    expect(tokens.filter((token) => !token.isProperName && token.properNameTypes?.length)).toEqual([]);
  });

  it("contains 15 NT chapters, 15 LXX/deuterocanonical chapters, 20 prayers, and 20 patristic readings", () => {
    expect(selectionsInPart(greek, "new-testament")).toHaveLength(15);
    expect(selectionsInPart(greek, "septuagint")).toHaveLength(15);
    expect(selectionsInPart(greek, "prayers")).toHaveLength(20);

    const patristic = greek.selections.filter(
      (selection) => selection.kind === "patristic",
    );
    expectCoreAdvancedSplit(patristic);
  });
});

describe("Latin reader curriculum", () => {
  const latin = requireVolume("la");

  it("contains 15 Vulgate chapters, 20 prayers/creeds, and 20 patristic readings", () => {
    expect(selectionsInPart(latin, "la-vulgate")).toHaveLength(15);
    expect(selectionsInPart(latin, "la-prayers-creeds")).toHaveLength(20);

    const patristic = latin.selections.filter(
      (selection) => selection.kind === "patristic",
    );
    expectCoreAdvancedSplit(patristic);
  });
});
