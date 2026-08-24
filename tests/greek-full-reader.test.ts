import { describe, expect, it } from "vitest";

import {
  getGreekLesson,
  getGreekLiturgy,
  getGreekReaderOverview,
  listGreekLessons,
  listGreekVolumes,
  parseGreekLessonKey,
} from "../data/originalReaders/greek-full-reader";

describe("complete two-volume Koine Greek private reader", () => {
  const overview = getGreekReaderOverview();
  const volumes = listGreekVolumes();
  const volumeOne = volumes.find((volume) => volume.volume === 1)!;
  const volumeTwo = volumes.find((volume) => volume.volume === 2)!;

  it("carries the frozen release counts", () => {
    expect(overview.counts.volumes).toBe(2);
    expect(overview.counts.lessons).toBe(100);
    expect(overview.counts.vocabulary).toBe(2000);
    expect(overview.counts.memoryUnits).toBe(200);
    expect(overview.counts.scriptureChapters).toBe(50);
    expect(overview.counts.patristicReadings).toBe(50);
  });

  it("cuts both volumes into fifty lessons of exactly twenty words", () => {
    for (const volume of volumes) {
      expect(volume.lessons, `volume ${volume.volume}`).toHaveLength(50);
      expect(volume.counts.vocabulary).toBe(1000);
      for (const lesson of volume.lessons) {
        expect(
          lesson.vocabularyCount,
          `volume ${volume.volume} lesson ${lesson.lesson}`,
        ).toBe(20);
      }
    }
  });

  it("gives 上冊 a chapter and 下冊 a reading in every lesson", () => {
    expect(volumeOne.lessons.every((lesson) => lesson.reading.kind === "scripture_chapter")).toBe(true);
    expect(volumeTwo.lessons.every((lesson) => lesson.reading.kind === "patristic_reading")).toBe(true);
  });

  it("keeps each volume's halves on their own corpus", () => {
    const first = volumeOne.lessons.slice(0, 25).map((lesson) => lesson.reading.label);
    expect(new Set(first)).toEqual(new Set(["新約"]));
    const second = new Set(volumeOne.lessons.slice(25).map((lesson) => lesson.reading.label));
    expect(second).toContain("七十士譯本（正典）");
    expect(second).toContain("次經");
    expect(second).toContain("偽經");
    expect(second).not.toContain("新約");

    const patristic = new Set(volumeTwo.lessons.slice(0, 25).map((lesson) => lesson.reading.label));
    expect(patristic).toEqual(new Set(["使徒教父", "希臘教父"]));
    const documents = new Set(volumeTwo.lessons.slice(25).map((lesson) => lesson.reading.label));
    expect(documents).toContain("教規彙編");
    expect(documents).toContain("禮儀文本與頌歌");
  });

  it("gives every lesson exactly two memory units of its volume's kind", () => {
    for (const volume of volumes) {
      for (const summary of volume.lessons) {
        const lesson = getGreekLesson(volume.volume, summary.lesson);
        expect(lesson, `volume ${volume.volume} lesson ${summary.lesson} missing`).toBeTruthy();
        expect(lesson!.memoryUnits).toHaveLength(2);
        expect(new Set(lesson!.memoryUnits.map((unit) => unit.ref)).size).toBe(2);
        expect(lesson!.memoryUnits.every((unit) => unit.kind === volume.memoryUnitKind)).toBe(true);
      }
    }
  });

  it("never labels an excerpt as a complete work", () => {
    for (const summary of listGreekLessons()) {
      const reading = getGreekLesson(summary.volume, summary.lesson)!.reading;
      if (reading.completeness === "excerpt") {
        expect(reading.extent, `${reading.titleZh} excerpt without extent`).toBeTruthy();
        expect(reading.extent).not.toBe("全篇");
      }
    }
  });

  it("ships no empty reading segment", () => {
    for (const summary of listGreekLessons()) {
      const reading = getGreekLesson(summary.volume, summary.lesson)!.reading;
      const segments = reading.verses || reading.segments || [];
      expect(segments.length, `${reading.titleZh} has no segments`).toBeGreaterThan(0);
      for (const segment of segments) {
        const text = segment.displayText || segment.sourceText || "";
        expect(text.trim(), `${reading.titleZh} ${segment.ref} is empty`).not.toBe("");
      }
    }
  });

  it("pairs Chinese with every Scripture verse that has a Chinese counterpart", () => {
    for (const summary of volumeOne.lessons) {
      const reading = getGreekLesson(1, summary.lesson)!.reading;
      if (reading.corpusLabel === "偽經") continue;
      for (const verse of reading.verses || []) {
        if (verse.translationNote) continue;
        expect(
          (verse.translationZh || "").trim(),
          `${reading.ref} ${verse.ref} has no Chinese`,
        ).not.toBe("");
      }
    }
  });

  it("states the release status honestly while a layer is incomplete", () => {
    if (overview.glossProgress.complete) {
      expect(overview.releaseStatus).not.toBe("source_frozen");
    } else {
      expect(overview.releaseStatus).toBe("source_frozen");
      expect(overview.glossProgress.glossed).toBeLessThan(overview.glossProgress.target);
    }
  });

  it("declares no recorded audio until real tracks exist", () => {
    expect(overview.audioStatus.status).toBe("not_recorded");
    expect(overview.audioStatus.recordedTrackCount).toBe(0);
  });

  it("carries the five appendix tables outside the lesson count", () => {
    expect(overview.appendices).toHaveLength(5);
    expect(overview.appendices.map((table) => table.title)).toContain("人名、地名與國族");
    expect(overview.counts.appendixEntries).toBeGreaterThan(600);
  });

  it("carries the whole liturgy in celebration order, in 下冊 only", () => {
    expect(volumeOne.appendices).toHaveLength(0);
    expect(volumeTwo.appendices.map((item) => item.key)).toContain("divine-liturgy-chrysostom");

    const liturgy = getGreekLiturgy();
    expect(liturgy.summary.stepCount).toBeGreaterThan(300);
    expect(liturgy.sections.length).toBeGreaterThanOrEqual(20);

    const keys = liturgy.sections.map((section) => section.key);
    for (const required of ["great-litany", "trisagion", "creed", "anaphora", "lords-prayer", "dismissal"]) {
      expect(keys, `liturgy missing ${required}`).toContain(required);
    }
    expect(keys.indexOf("creed")).toBeLessThan(keys.indexOf("anaphora"));
    expect(keys.indexOf("anaphora")).toBeLessThan(keys.indexOf("lords-prayer"));
    expect(keys[keys.length - 1]).toBe("dismissal");

    const ordinals = liturgy.steps.map((step) => step.ordinal);
    expect(ordinals).toEqual([...ordinals].sort((a, b) => a - b));
    expect(liturgy.steps.every((step) => step.displayText.trim())).toBe(true);
  });

  it("resolves a lesson key from either form and rejects anything else", () => {
    expect(parseGreekLessonKey("v2-37")).toEqual({ volume: 2, lesson: 37 });
    // A bare number is what links written before the second volume existed say.
    expect(parseGreekLessonKey("12")).toEqual({ volume: 1, lesson: 12 });
    expect(parseGreekLessonKey("v3-1")).toEqual({ volume: 3, lesson: 1 });
    expect(parseGreekLessonKey("liturgy")).toBeNull();
    expect(parseGreekLessonKey("v2-")).toBeNull();

    expect(getGreekLesson(1, 0)).toBeNull();
    expect(getGreekLesson(1, 51)).toBeNull();
    expect(getGreekLesson(3, 1)).toBeNull();
  });
});
