import { describe, expect, it } from "vitest";
import { headwordForSpeech, toEcclesiasticalSpeech } from "../utils/ecclesiasticalLatin";

// 這層改寫只有一個目的：讓義大利語聲線把拉丁文念成羅馬式教會發音。
// 每個斷言都對應教會拉丁發音表的一條，改壞了會變成「聽起來像義大利文的拉丁文」。
describe("教會拉丁文朗讀拼寫", () => {
  it("ae/oe 是單母音 [e]，不可讀成兩個音節", () => {
    expect(toEcclesiasticalSpeech("caelum saeculum poena")).toBe("celum seculum pena");
  });

  it("ti + 母音讀 [tsi]，但 s/t/x 之後不變", () => {
    expect(toEcclesiasticalSpeech("gratia")).toBe("grazia");
    expect(toEcclesiasticalSpeech("sanctificatio")).toBe("sanctificazio");
    expect(toEcclesiasticalSpeech("hostia")).toBe("hostia");
    expect(toEcclesiasticalSpeech("mixtio")).toBe("mixtio");
  });

  it("j 是子音性 i，y 讀 [i]", () => {
    expect(toEcclesiasticalSpeech("justitia")).toBe("iustizia");
    expect(toEcclesiasticalSpeech("Kyrie")).toBe("kirie");
  });

  it("希臘借字的送氣塞音已失去送氣", () => {
    expect(toEcclesiasticalSpeech("philosophia")).toBe("filosofia");
    expect(toEcclesiasticalSpeech("catholica")).toBe("catolica");
  });

  it("ch 一律 [k]：e/i 前保留義大利語拼法，其餘改成 c", () => {
    expect(toEcclesiasticalSpeech("Christus")).toBe("cristus");
    expect(toEcclesiasticalSpeech("charitas")).toBe("caritas");
  });

  it("x 在 e/i 前是 [kʃ]", () => {
    expect(toEcclesiasticalSpeech("excelsis")).toBe("ecscelsis");
  });

  it("mihi 與 nihil 用中世紀既有的 ch 拼法", () => {
    expect(toEcclesiasticalSpeech("mihi nihil")).toBe("michi nichil");
  });

  it("長音符號、體例記號與大寫都要清掉", () => {
    expect(toEcclesiasticalSpeech("ōrāre")).toBe("orare");
    expect(toEcclesiasticalSpeech("R. Et cum spiritu tuo.")).toBe("et cum spiritu tuo.");
    expect(toEcclesiasticalSpeech("† Ego DEMETRIUS")).toBe("ego demetrius");
    expect(toEcclesiasticalSpeech("[誦讀者往誦讀台] Verbum Domini")).toBe("verbum domini");
  });

  it("行首節號是版面，不可以唸成義大利文數字", () => {
    expect(toEcclesiasticalSpeech("1　Attendite ne justitiam")).toBe("attendite ne iustiziam");
    expect(toEcclesiasticalSpeech("12. Deus caritas est")).toBe("deus caritas est");
    // 句中的數字是經文的一部分，要留著
    expect(toEcclesiasticalSpeech("annos 40 in deserto")).toBe("annos 40 in deserto");
  });

  it("義大利語天生就對的部分不可以動", () => {
    // c/g 在 e/i 前、gn、sc 在 e/i 前、qu、h 不發音
    expect(toEcclesiasticalSpeech("Ecclesia agnus ascendit qui homo")).toBe(
      "ecclesia agnus ascendit qui homo",
    );
  });

  it("朗讀單字只念字典形的第一個形式", () => {
    expect(headwordForSpeech("ōrō, ōrāre, ōrāvī, ōrātus")).toBe("oro");
    expect(headwordForSpeech("lūmināre, lūmināris, lūminārium, n.")).toBe("luminare");
  });

  it("空字串與純記號不會炸", () => {
    expect(toEcclesiasticalSpeech("")).toBe("");
    expect(toEcclesiasticalSpeech("†")).toBe("");
  });
});
