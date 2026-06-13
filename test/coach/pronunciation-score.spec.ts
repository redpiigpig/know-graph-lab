import { describe, it, expect } from "vitest";
import { scorePronunciation, similarity, displayTokens } from "~/composables/usePronunciationScore";

describe("similarity", () => {
  it("identical = 1, disjoint = 0", () => {
    expect(similarity("logos", "logos")).toBe(1);
    expect(similarity("abc", "xyz")).toBe(0);
  });
  it("close words score high", () => {
    expect(similarity("beginning", "begining")).toBeGreaterThan(0.8);
  });
});

describe("displayTokens", () => {
  it("splits words and punctuation, drops spaces", () => {
    expect(displayTokens("In the beginning, God.")).toEqual(["In", "the", "beginning", ",", "God", "."]);
  });
});

describe("scorePronunciation", () => {
  it("perfect read = 100, all hit", () => {
    const r = scorePronunciation("In the beginning", "in the beginning");
    expect(r.score).toBe(100);
    expect(r.hits).toBe(3);
    expect(r.miss).toBe(0);
    expect(r.tokens.filter((t) => t.isWord).every((t) => t.status === "hit")).toBe(true);
  });

  it("empty heard = 0, all words miss", () => {
    const r = scorePronunciation("In the beginning", "");
    expect(r.score).toBe(0);
    expect(r.total).toBe(3);
    expect(r.miss).toBe(3);
  });

  it("a missed word is marked miss, others hit", () => {
    const r = scorePronunciation("In the beginning God", "in the God");
    const words = r.tokens.filter((t) => t.isWord);
    expect(words.find((w) => w.text === "beginning")!.status).toBe("miss");
    expect(words.find((w) => w.text === "God")!.status).toBe("hit");
    expect(r.hits).toBe(3);
    expect(r.miss).toBe(1);
    expect(r.score).toBe(75);
  });

  it("a near-miss is flagged near with heardAs + half credit", () => {
    const r = scorePronunciation("beginning", "begining");
    const w = r.tokens.find((t) => t.isWord)!;
    expect(w.status).toBe("near");
    expect(w.heardAs).toBe("begining");
    expect(r.near).toBe(1);
    expect(r.score).toBe(50);
  });

  it("punctuation is not scored", () => {
    const r = scorePronunciation("Hello, world!", "hello world");
    expect(r.total).toBe(2);
    expect(r.score).toBe(100);
    expect(r.tokens.some((t) => !t.isWord && /[,!]/.test(t.text))).toBe(true);
  });

  it("extra heard words (insertions) do not penalise target", () => {
    const r = scorePronunciation("the word", "um the the word you know");
    expect(r.score).toBe(100);
    expect(r.hits).toBe(2);
  });

  it("works on non-Latin script (Greek)", () => {
    const r = scorePronunciation("ἐν ἀρχῇ", "ἐν ἀρχῇ");
    expect(r.score).toBe(100);
    expect(r.total).toBe(2);
  });
});
