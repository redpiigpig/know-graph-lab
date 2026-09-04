import { describe, it, expect } from 'vitest';
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { PRESS_GROUPS } from '../data/press';

const repo = resolve(__dirname, '..');
const ALL = PRESS_GROUPS.flatMap(g => g.items);

/** press_airiti.py 的 JOURNALS 字典：slug → (publicationID, 刊名) */
function harvesterSlugs(): Set<string> {
  const py = readFileSync(resolve(repo, 'scripts/press_airiti.py'), 'utf-8');
  const block = py.slice(py.indexOf('JOURNALS = {'), py.indexOf('\n}\n', py.indexOf('JOURNALS = {')));
  return new Set([...block.matchAll(/^\s*"([a-z0-9-]+)":\s*\(/gm)].map(m => m[1]));
}

describe('期刊與報紙 × 華藝篇目', () => {
  it('slug 全站唯一', () => {
    const seen = new Map<string, number>();
    for (const p of ALL) seen.set(p.slug, (seen.get(p.slug) ?? 0) + 1);
    expect([...seen].filter(([, n]) => n > 1)).toEqual([]);
  });

  // 這條是本檔的重點：slug 打錯不會爆，只會渲染出一個「尚未收錄篇目」的空頁——
  // 看起來完全正常的失敗。所以在測試裡把兩邊的名單對起來。
  it('標了 airiti 的刊，slug 都在 press_airiti.py 的 JOURNALS 裡', () => {
    const harvested = harvesterSlugs();
    expect(harvested.size).toBeGreaterThan(20);
    const missing = ALL.filter(p => p.airiti && !harvested.has(p.slug)).map(p => p.slug);
    expect(missing).toEqual([]);
  });

  it('沒標 airiti 的刊，不會指到 /research-data/press/<slug>', () => {
    const bad = ALL.filter(p => !p.airiti && p.to?.startsWith('/research-data/press/'));
    expect(bad.map(p => p.slug)).toEqual([]);
  });

  it('華藝收錄斷限與創刊年分開記，不互相冒充', () => {
    // coverage 是資料庫斷限、start 是創刊；兩欄若寫成同一個值多半是誤填
    const conflated = ALL.filter(p => p.coverage && p.start && p.coverage === p.start);
    expect(conflated.map(p => p.slug)).toEqual([]);
  });
});
