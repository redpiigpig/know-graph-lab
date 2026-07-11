// @vitest-environment node
import { describe, it, expect } from "vitest";
import { parseOfflineReport, reportTemplate, reportHasData, REPORT_BEGIN, REPORT_END } from "~/utils/offlineReport";

const FULL = `以下是本次練習的成果：

${REPORT_BEGIN}
語言：拉丁文
日期：2026-07-11
練習內容：FSI 替換練習與引導會話（主禱文句型）
技能時間：口說 20 分、寫作 10 分、閱讀 15 分
整體評分：78
強項：
- 變格記得穩
待加強：
- 與格和奪格常混淆
新學單字：
- verbum｜－｜話語｜In principio erat Verbum
- gratia｜grá-ti-a｜恩典｜Ave Maria, gratia plena
複習結果：
- amor｜對
- fides｜錯
改錯紀錄：
- Ego amat te → Ego amo te
${REPORT_END}

謝謝教官！`;

describe("parseOfflineReport 成果報告解析（零 AI）", () => {
  it("完整報告：所有欄位正確解析", () => {
    const r = parseOfflineReport(FULL)!;
    expect(r).not.toBeNull();
    expect(r.date).toBe("2026-07-11");
    expect(r.content).toContain("替換練習");
    expect(r.skills).toEqual(
      expect.arrayContaining([
        { skill: "speaking", minutes: 20 },
        { skill: "writing", minutes: 10 },
        { skill: "reading", minutes: 15 },
      ])
    );
    expect(r.overall).toBe(78);
    expect(r.strengths).toEqual(["變格記得穩"]);
    expect(r.improvements).toEqual(["與格和奪格常混淆"]);
    expect(r.newWords).toHaveLength(2);
    expect(r.newWords[0]).toEqual({ word: "verbum", reading: null, meaning: "話語", example: "In principio erat Verbum" });
    expect(r.newWords[1].reading).toBe("grá-ti-a");
    expect(r.reviews).toEqual([
      { word: "amor", correct: true },
      { word: "fides", correct: false },
    ]);
    expect(r.corrections).toEqual([{ original: "Ego amat te", fixed: "Ego amo te" }]);
    expect(reportHasData(r)).toBe(true);
  });

  it("沒有報告標記 → null", () => {
    expect(parseOfflineReport("今天練了很多，很開心")).toBeNull();
  });

  it("缺 REPORT_END → 解析到文末仍成功", () => {
    const r = parseOfflineReport(`${REPORT_BEGIN}\n技能時間：口說 30 分\n複習結果:\n- amor|對`)!;
    expect(r.skills).toEqual([{ skill: "speaking", minutes: 30 }]);
    expect(r.reviews).toEqual([{ word: "amor", correct: true }]);
  });

  it("容忍變體：半形冒號/半形直線/=>、英文技能名、數字編號清單", () => {
    const r = parseOfflineReport(`${REPORT_BEGIN}
日期: 2026/07/10
技能時間: speaking 25 分鐘、listening 5 分
改錯:
1. Ich habe gegangen => Ich bin gegangen
新單字:
1. Gnade|恩典
${REPORT_END}`)!;
    expect(r.date).toBe("2026-07-10");
    expect(r.skills).toEqual(
      expect.arrayContaining([
        { skill: "speaking", minutes: 25 },
        { skill: "listening", minutes: 5 },
      ])
    );
    expect(r.corrections).toEqual([{ original: "Ich habe gegangen", fixed: "Ich bin gegangen" }]);
    expect(r.newWords).toEqual([{ word: "Gnade", reading: null, meaning: "恩典", example: null }]);
  });

  it("只有總時間沒拆技能 → 歸口說", () => {
    const r = parseOfflineReport(`${REPORT_BEGIN}\n總時間：45 分鐘`)!;
    expect(r.skills).toEqual([{ skill: "speaking", minutes: 45 }]);
  });

  it("三欄單字行：第二欄繁中＝釋義、否則＝讀音", () => {
    const r = parseOfflineReport(`${REPORT_BEGIN}
新學單字：
- λόγος｜道、話語｜ἐν ἀρχῇ ἦν ὁ λόγος
- λόγος｜lógos｜道、話語
${REPORT_END}`)!;
    expect(r.newWords[0]).toEqual({ word: "λόγος", reading: null, meaning: "道、話語", example: "ἐν ἀρχῇ ἦν ὁ λόγος" });
    expect(r.newWords[1]).toEqual({ word: "λόγος", reading: "lógos", meaning: "道、話語", example: null });
  });

  it("模板占位文字（全形括號）不入庫", () => {
    const r = parseOfflineReport(reportTemplate("拉丁文"))!;
    expect(r.strengths).toEqual([]);
    expect(r.improvements).toEqual([]);
    // 模板的示意單字行「單字｜讀音｜…」會被解析，但實務上 AI 會整段替換；
    // 這裡只驗證占位括號行被略過
  });

  it("模板本身可被解析器讀回（roundtrip 保險）", () => {
    const t = reportTemplate("德文");
    expect(t).toContain(REPORT_BEGIN);
    expect(t).toContain(REPORT_END);
    const r = parseOfflineReport(t)!;
    expect(r).not.toBeNull();
    expect(r.skills.length).toBeGreaterThan(0);
  });

  it("無效分鐘（0 分）不入列", () => {
    const r = parseOfflineReport(`${REPORT_BEGIN}\n技能時間：聽力 0 分、口說 10 分`)!;
    expect(r.skills).toEqual([{ skill: "speaking", minutes: 10 }]);
  });
});
