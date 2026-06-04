// @vitest-environment node
import { describe, it, expect } from "vitest";
import { getCoach, listCoaches, publicCoaches, pickPersona, OUTPUT_CONTRACT } from "~/server/utils/lang-coaches";

describe("教練設定 lang-coaches", () => {
  it("getCoach 命中 / 未命中", () => {
    expect(getCoach("en")?.name).toBe("Emily");
    expect(getCoach("ja")?.name).toBe("櫻子");
    expect(getCoach("zz")).toBeUndefined();
  });

  it("每位教練都有必填欄位且 defaultLevel 在量表內", () => {
    for (const c of listCoaches()) {
      expect(c.language, `${c.language} language`).toBeTruthy();
      expect(c.name, `${c.language} name`).toBeTruthy();
      expect(c.langLabel).toBeTruthy();
      expect(c.bcp47).toBeTruthy();
      expect(c.ttsLang).toBeTruthy();
      expect(c.systemPrompt.length).toBeGreaterThan(20);
      expect(Array.isArray(c.levelScale)).toBe(true);
      expect(c.levelScale.length).toBeGreaterThan(0);
      expect(c.levelScale, `${c.language} defaultLevel∈scale`).toContain(c.defaultLevel);
    }
  });

  it("英文=CEFR/B2、日文=JLPT/N5", () => {
    expect(getCoach("en")!.levelScale).toEqual(["A1", "A2", "B1", "B2", "C1", "C2"]);
    expect(getCoach("en")!.defaultLevel).toBe("B2");
    expect(getCoach("ja")!.levelScale).toEqual(["N5", "N4", "N3", "N2", "N1"]);
    expect(getCoach("ja")!.defaultLevel).toBe("N5");
  });

  it("人設定向正確（使用者宗教研究需求）", () => {
    // 日文＝關東標準語（prompt 會明說「京都弁は使いません」故含 京都 二字，但不可「京都出身」）
    const ja = getCoach("ja")!;
    expect(ja.accent).toContain("關東");
    expect(ja.accent).not.toContain("京都");
    expect(ja.systemPrompt).toContain("東京出身");
    expect(ja.systemPrompt).toContain("標準語");
    expect(ja.systemPrompt).not.toContain("京都出身");
    // 希臘文＝神學院通用希臘文（Koine，非古典 Attic）
    const grc = getCoach("grc")!;
    expect(grc.langLabel).toBe("通用希臘文");
    expect(grc.accent).toContain("Koine");
    expect(grc.systemPrompt).toContain("Koine");
    expect(grc.systemPrompt).toContain("不是古典"); // 明示非古典 Attic
    expect(grc.keyboard).toBe("greek"); // 打英文轉希臘字母的鍵盤
    // 拉丁文＝教會拉丁
    expect(getCoach("la")!.accent).toContain("教會拉丁");
  });

  it("en/ja 啟用；古語言 voiceless", () => {
    expect(getCoach("en")!.enabled).toBe(true);
    expect(getCoach("ja")!.enabled).toBe(true);
    expect(getCoach("la")!.voiceless).toBe(true);
    expect(getCoach("grc")!.voiceless).toBe(true);
  });

  it("pickPersona 依 seed 穩定輪替；無 personas 回 null", () => {
    const en = getCoach("en")!;
    const n = en.personas!.length;
    expect(pickPersona(en, 0)).toBe(en.personas![0]);
    expect(pickPersona(en, n)).toBe(en.personas![0]); // 繞回
    expect(pickPersona(en, 1)).toBe(en.personas![1 % n]);
    expect(pickPersona(getCoach("de")!, 0)).toBeNull(); // de 無 personas
  });

  it("publicCoaches 去掉 systemPrompt 但保留 levelScale/personas/scenarios", () => {
    const pub = publicCoaches();
    const en = pub.find((c: any) => c.language === "en")!;
    expect((en as any).systemPrompt).toBeUndefined();
    expect(en.levelScale).toBeTruthy();
    expect((en as any).personas?.length).toBeGreaterThan(0);
    expect((en as any).scenarios?.length).toBeGreaterThan(0);
  });

  it("OUTPUT_CONTRACT 含結構化欄位", () => {
    for (const k of ["reply", "translation", "corrections", "new_vocab", "homework"]) {
      expect(OUTPUT_CONTRACT).toContain(k);
    }
    expect(OUTPUT_CONTRACT).toContain("繁體");
  });
});
