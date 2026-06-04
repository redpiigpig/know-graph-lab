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
    // 日文＝假名鍵盤；希臘文＝希臘鍵盤
    expect(getCoach("ja")!.keyboard).toBe("kana");
    // 拉丁文＝教會拉丁（非古典），用拉丁字母不需轉寫鍵盤
    const la = getCoach("la")!;
    expect(la.accent).toContain("教會拉丁");
    expect(la.systemPrompt).toContain("不是古典");
    expect(la.keyboard).toBeUndefined();
    // 希伯來文＝舊約聖經希伯來文（非現代），希伯來鍵盤、voiceless
    const hbo = getCoach("hbo")!;
    expect(hbo.langLabel).toBe("聖經希伯來文");
    expect(hbo.systemPrompt).toContain("不是現代");
    expect(hbo.keyboard).toBe("hebrew");
    expect(hbo.voiceless).toBe(true);
  });

  it("en/ja 啟用；古語言 voiceless", () => {
    expect(getCoach("en")!.enabled).toBe(true);
    expect(getCoach("ja")!.enabled).toBe(true);
    expect(getCoach("la")!.voiceless).toBe(true);
    expect(getCoach("grc")!.voiceless).toBe(true);
  });

  it("德/法已啟用：A1 初學、CEFR、有 STT/TTS（非 voiceless），題材重單字/文法/輸入", () => {
    const de = getCoach("de")!;
    expect(de.enabled).toBe(true);
    expect(de.name).toBe("Lukas");
    expect(de.langLabel).toBe("德文");
    expect(de.levelScale).toEqual(["A1", "A2", "B1", "B2", "C1", "C2"]);
    expect(de.defaultLevel).toBe("A1");
    expect(de.voiceless).toBeFalsy(); // 活語言、有語音
    expect(de.keyboard).toBeUndefined(); // 拉丁字母直打
    expect(de.systemPrompt).toContain("A1");
    expect(de.systemPrompt).toContain("Hochdeutsch");
    expect(de.personas!.length).toBeGreaterThan(0);
    expect(de.smalltalkTopics!.length).toBeGreaterThan(0);
    expect(de.qaTopics!.length).toBeGreaterThan(0);

    const fr = getCoach("fr")!;
    expect(fr.enabled).toBe(true);
    expect(fr.name).toBe("Camille");
    expect(fr.langLabel).toBe("法文");
    expect(fr.defaultLevel).toBe("A1");
    expect(fr.voiceless).toBeFalsy();
    expect(fr.keyboard).toBeUndefined();
    expect(fr.systemPrompt).toContain("A1");
    expect(fr.systemPrompt).toContain("français");
    expect(fr.personas!.length).toBeGreaterThan(0);
    expect(fr.scenarios!.length).toBeGreaterThan(0);
  });

  it("pickPersona 依 seed 穩定輪替；無 personas 回 null", () => {
    const en = getCoach("en")!;
    const n = en.personas!.length;
    expect(pickPersona(en, 0)).toBe(en.personas![0]);
    expect(pickPersona(en, n)).toBe(en.personas![0]); // 繞回
    expect(pickPersona(en, 1)).toBe(en.personas![1 % n]);
    expect(pickPersona(getCoach("de")!, 0)).toBe(getCoach("de")!.personas![0]); // de 已啟用、有 personas
    expect(pickPersona({ personas: [] } as any, 0)).toBeNull(); // 空 personas 回 null
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
