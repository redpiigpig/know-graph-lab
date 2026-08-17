import { describe, expect, it } from "vitest";

import {
  ORIGINAL_READER_VOLUMES,
  getOriginalReaderVolume,
} from "../data/originalReaders/index";
import {
  getHebrewFullHaggadah,
  getHebrewFullLesson,
  getHebrewFullReaderOverview,
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

  it("reserves 50 consecutive BBH lessons sized by the textbook's own chapters", () => {
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
    expect(vocabularyTokens.filter((token) => token.sourceType === "bbh2_order")).toHaveLength(552);
    expect(vocabularyTokens.filter((token) => token.sourceType === "reader_frequency_extension")).toHaveLength(448);
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

    for (const strong of ["H3389", "H4872", "H1732", "H1168", "H1390"]) {
      expect(tokens.find((token) => token.strong === strong)?.isProperName, strong).toBe(true);
    }
    expect(tokens.find((token) => token.strong === "H7586")?.properNameTypes).toEqual(["person"]);
    expect(tokens.find((token) => token.strong === "H1390")?.properNameTypes).toEqual(["place"]);
    expect(tokens.find((token) => token.strong === "H3063")?.properNameTypes).toEqual([
      "person",
      "place",
      "people_or_nation",
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
      expect(lesson?.vocabulary.length).toBeGreaterThan(0);
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
