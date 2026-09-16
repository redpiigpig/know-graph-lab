import { describe, it, expect } from 'vitest';
// @ts-expect-error — 純 JS 模組，沒有型別宣告
import { sizeMB, rank } from '../scripts/zlib_fetch.mjs';

/** 一筆看得上眼的中譯 epub；各測試只改它的 filesize。 */
const hit = (filesize: string, extra: Record<string, string> = {}) => ({
  title: '心靈的黑夜',
  author: '十字若望',
  language: 'Chinese (Traditional)',
  extension: 'epub',
  filesize,
  ...extra,
});

describe('z-lib 挑版本：檔案大小', () => {
  // 🚨 這是本檔的重點。站方給的是帶單位的字串，原本用 parseFloat 讀 "661 KB"
  //    會得到 661 並當成 661 MB——於是最小的那批檔反而拿不到小檔加分。
  //    帳本裡實測 129/1,103 筆是 KB 級的，全都中了這個坑。
  it('KB 要換算成 MB，不可以照數字讀', () => {
    expect(sizeMB('661 KB')).toBeCloseTo(661 / 1024, 4);
    expect(sizeMB('661 KB')).toBeLessThan(1);
  });

  it('MB 與 GB 都解得開，解不開的回 0', () => {
    expect(sizeMB('11.02 MB')).toBeCloseTo(11.02, 4);
    expect(sizeMB('1.5 GB')).toBeCloseTo(1536, 1);
    expect(sizeMB('')).toBe(0);
    expect(sizeMB(undefined)).toBe(0);
    expect(sizeMB('不知道多大')).toBe(0);
  });

  it('小檔勝出：KB 級 > 20MB > 45MB > 200MB', () => {
    const score = (fs: string) => rank(hit(fs), '', '', '', '', '', '', '');
    const kb = score('661 KB');
    const small = score('20.00 MB');
    const mid = score('45.00 MB');
    const big = score('200.00 MB');
    expect(kb).toBeGreaterThan(small);
    expect(small).toBeGreaterThan(mid);
    expect(mid).toBeGreaterThan(big);
  });

  it('30MB 以內算首選，30–60 次之', () => {
    const score = (fs: string) => rank(hit(fs), '', '', '', '', '', '', '');
    expect(score('29.00 MB') - score('31.00 MB')).toBeGreaterThan(3);
  });

  // 🚨 大小只准影響排序，不准把候選打成負分。rank() 的呼叫端是
  //    `scored.filter(([r]) => r > 0)`，扣成負的就等於把「站上有貨但檔案大」
  //    記成 probe-miss，而那在帳本裡是半永久的。
  it('再大的檔也不會被扣成負分而變成「查無此書」', () => {
    for (const fs of ['200.00 MB', '530.00 MB', '2.00 GB']) {
      expect(rank(hit(fs), '', '', '', '', '', '', '')).toBeGreaterThan(0);
    }
  });

  it('大小壓不過語言與格式的差距', () => {
    // 小的簡體 pdf 不該贏過大的繁體 epub
    const tradBig = rank(hit('50.00 MB'), '', '', '', '', '', '', '');
    const simpSmall = rank(
      hit('1.00 MB', { language: 'Chinese', extension: 'pdf' }), '', '', '', '', '', '', '');
    expect(tradBig).toBeGreaterThan(simpSmall);
  });
});
