// @vitest-environment node
import { describe, it, expect } from "vitest";
import { sm2 } from "~/server/utils/srs";

describe("SM-2 間隔複習", () => {
  it("新卡答『good(4)』→ 第一次 interval=1、reps=1", () => {
    const r = sm2({ ease_factor: 2.5, interval_days: 0, repetitions: 0 }, 4);
    expect(r.repetitions).toBe(1);
    expect(r.interval_days).toBe(1);
    expect(r.mastery_level).toBe(1);
  });

  it("第二次 good → interval=6", () => {
    const r = sm2({ ease_factor: 2.5, interval_days: 1, repetitions: 1 }, 4);
    expect(r.repetitions).toBe(2);
    expect(r.interval_days).toBe(6);
  });

  it("第三次 good → interval = round(interval*ease)", () => {
    const r = sm2({ ease_factor: 2.5, interval_days: 6, repetitions: 2 }, 4);
    expect(r.repetitions).toBe(3);
    expect(r.interval_days).toBeGreaterThanOrEqual(13); // 6*~2.5
  });

  it("答錯（q<3）→ reps 歸 0、interval=1（排回複習）", () => {
    const r = sm2({ ease_factor: 2.5, interval_days: 30, repetitions: 5 }, 2);
    expect(r.repetitions).toBe(0);
    expect(r.interval_days).toBe(1);
  });

  it("ease factor 下限 1.3", () => {
    let s = { ease_factor: 1.3, interval_days: 1, repetitions: 1 };
    for (let i = 0; i < 5; i++) {
      const r = sm2(s, 3); // 反覆 hard 會壓低 ease
      s = { ease_factor: r.ease_factor, interval_days: r.interval_days, repetitions: r.repetitions };
    }
    expect(s.ease_factor).toBeGreaterThanOrEqual(1.3);
  });

  it("next_review 是 YYYY-MM-DD 且為未來日", () => {
    const r = sm2({ ease_factor: 2.5, interval_days: 0, repetitions: 0 }, 5);
    expect(r.next_review).toMatch(/^\d{4}-\d{2}-\d{2}$/);
    expect(new Date(r.next_review).getTime()).toBeGreaterThan(Date.now() - 86400000);
  });

  it("mastery 上限 5", () => {
    let s = { ease_factor: 2.5, interval_days: 1, repetitions: 8 };
    const r = sm2(s, 5);
    expect(r.mastery_level).toBeLessThanOrEqual(5);
  });
});
