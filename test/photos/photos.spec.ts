// @vitest-environment nuxt
import { describe, it, expect } from 'vitest'
import { mockNuxtImport } from '@nuxt/test-utils/runtime'
import { existsSync, readFileSync } from 'node:fs'
import { resolve } from 'node:path'

// photos.ts 用 Nuxt auto-import 取 useRuntimeConfig（getPhotosRoot 拿 photosRoot、簽章拿
// encryptionKey）。給 deterministic 設定讓 path / 簽章可預期、不依賴本機 Drive。
// ⚠️ 必須帶 app.baseURL，否則 nuxt env 的 router plugin 初始化會炸（覆蓋了全域 useRuntimeConfig）。
mockNuxtImport('useRuntimeConfig', () => {
  return () => ({
    app: { baseURL: '/', buildAssetsDir: '/_nuxt/', cdnURL: '' },
    photosRoot: '/srv/photos/辰瑋相片',
    encryptionKey: 'test-secret',
    supabaseServiceRoleKey: 'test-secret',
    public: {},
  })
})

import {
  LIBRARIES,
  isLibrarySlug,
  classify,
  sourceForSegment,
  bucketDir,
  contentTypeFor,
  resolveLibFolder,
  signFileUrl,
  verifyFileSig,
  signLibFileUrl,
  verifyLibFileSig,
  summarizeLibraryFromIndex,
  listYearsFromIndex,
  getYearMonthsFromIndex,
  getMonthEventsFromIndex,
  listFilesFromIndex,
  listLibraryFolderFromIndex,
  r2ThumbKey,
  r2IndexKey,
} from '~/server/utils/photos'
import { thumbCacheKey } from '~/server/utils/photo-thumbs'
import { createHash } from 'node:crypto'

// ---- 合成 index fixture（涵蓋 chenwei year-month + training/hongshi folders 兩種 layout）----
const file = (name: string, kind: 'image' | 'video' = 'image', ext = '.jpg') => ({
  name, kind, ext, size: 1234, mtime: 1_700_000_000_000,
})

const idx = {
  version: 1,
  generatedAt: '2026-06-02T00:00:00.000Z',
  libraries: {
    chenwei: {
      totalFiles: 9,
      topFolders: 13,
      layout: 'year-month' as const,
      years: {
        '2024': {
          monthCounts: { '01': 2, '03': 1, '07': 0 },
          monthEvents: { '03': [{ name: '03.19旅遊', count: 2 }] },
          screenshots: 3,
          downloads: 1,
          events: [{ name: '畢業典禮', count: 4 }],
          buckets: {
            '01': [file('2024-01-01(1).jpg'), file('2024-01-02(1).jpg')],
            '03': [file('2024-03-09(1).jpg')],
            '03/03.19旅遊': [file('2024-03-19(1).jpg'), file('2024-03-19(2).jpg')],
            screenshots: [file('S2024-01-05(1).png', 'image', '.png'), file('S2024-01-06(1).png', 'image', '.png'), file('S2024-01-07(1).png', 'image', '.png')],
            downloads: [file('D2024-02-02(1).webp', 'image', '.webp')],
            畢業典禮: [file('a.jpg'), file('b.jpg'), file('c.mp4', 'video', '.mp4'), file('d.jpg')],
          },
        },
        '2023': {
          monthCounts: { '05': 1 },
          screenshots: 0,
          downloads: 0,
          events: [],
          buckets: { '05': [file('2023-05-18(1).jpg')] },
        },
      },
    },
    training: {
      totalFiles: 5,
      topFolders: 2,
      layout: 'folders' as const,
      folders: {
        '': {
          folders: [
            { name: '2024.09.01 忠烈祠 宋修傳', fileCount: 3, subfolderCount: 0 },
            { name: '2023', fileCount: 0, subfolderCount: 1 },
          ],
          files: [],
        },
        '2024.09.01 忠烈祠 宋修傳': {
          folders: [],
          files: [file('2024-09-01(1).jpg'), file('2024-09-01(2).jpg'), file('2024-09-01(3).jpg')],
        },
        '2023': { folders: [{ name: '某活動', fileCount: 2, subfolderCount: 0 }], files: [] },
        '2023/某活動': { folders: [], files: [file('x.jpg'), file('y.jpg')] },
      },
    },
    hongshi: { totalFiles: 7, topFolders: 4, layout: 'folders' as const, folders: { '': { folders: [], files: [] } } },
  },
}

describe('LIBRARIES registry', () => {
  it('registers chenwei / training / hongshi with the expected layouts', () => {
    expect(Object.keys(LIBRARIES).sort()).toEqual(['chenwei', 'hongshi', 'training'])
    expect(LIBRARIES.chenwei.layout).toBe('year-month')
    expect(LIBRARIES.training.layout).toBe('folders')
    expect(LIBRARIES.hongshi.layout).toBe('folders')
  })

  it('isLibrarySlug accepts the three slugs and rejects others', () => {
    expect(isLibrarySlug('training')).toBe(true)
    expect(isLibrarySlug('hongshi')).toBe(true)
    expect(isLibrarySlug('chenwei')).toBe(true)
    expect(isLibrarySlug('nope')).toBe(false)
    expect(isLibrarySlug('')).toBe(false)
  })
})

describe('classify', () => {
  it('recognises image / video extensions case-insensitively', () => {
    expect(classify('IMG_0001.JPG')).toEqual({ kind: 'image', ext: '.jpg' })
    expect(classify('clip.MOV')).toEqual({ kind: 'video', ext: '.mov' })
    expect(classify('shot.heic')).toEqual({ kind: 'image', ext: '.heic' })
  })
  it('returns null for non-media (e.g. .AAE sidecar / desktop.ini)', () => {
    expect(classify('IMG_0001.AAE')).toBeNull()
    expect(classify('desktop.ini')).toBeNull()
  })
})

describe('sourceForSegment', () => {
  it('maps segment → source', () => {
    expect(sourceForSegment('01')).toBe('photo')
    expect(sourceForSegment('12')).toBe('photo')
    expect(sourceForSegment('screenshots')).toBe('screenshot')
    expect(sourceForSegment('downloads')).toBe('download')
    expect(sourceForSegment('畢業典禮')).toBe('event')
  })
})

describe('bucketDir', () => {
  it('resolves month / screenshot / download / event folders', () => {
    expect(bucketDir('2024', '03')).toContain('2024.03')
    expect(bucketDir('2024', '03')).toContain('2024相片')
    expect(bucketDir('2024', 'screenshots')).toContain('2024截圖')
    expect(bucketDir('2024', 'downloads')).toContain('2024下載')
    expect(bucketDir('2024', '畢業典禮')).toContain('畢業典禮')
  })
  it('rejects bad year and path-traversal segments', () => {
    expect(() => bucketDir('20XX', '01')).toThrow()
    expect(() => bucketDir('2024', '../etc')).toThrow()
    expect(() => bucketDir('2024', 'a/b')).toThrow()
    expect(() => bucketDir('2024', '.hidden')).toThrow()
  })
})

describe('resolveLibFolder path-traversal guard', () => {
  it('keeps a valid subpath under the library root', () => {
    const p = resolveLibFolder('training', '2023/某活動')
    expect(p).toContain('訓練相片')
    expect(p).toContain('某活動')
  })
  it('throws when a segment escapes the root', () => {
    expect(() => resolveLibFolder('training', '../../secret')).toThrow()
    expect(() => resolveLibFolder('training', '..')).toThrow()
  })
})

describe('contentTypeFor', () => {
  it('maps known extensions and falls back to octet-stream', () => {
    expect(contentTypeFor('.jpg')).toBe('image/jpeg')
    expect(contentTypeFor('.mp4')).toBe('video/mp4')
    expect(contentTypeFor('.heic')).toBe('image/heic')
    expect(contentTypeFor('.xyz')).toBe('application/octet-stream')
  })
})

describe('signed URLs round-trip', () => {
  it('signFileUrl → verifyFileSig accepts, tamper rejects', () => {
    const url = signFileUrl('2024', '01', 'a.jpg')
    const q = new URLSearchParams(url.split('?')[1])
    expect(verifyFileSig('2024', '01', 'a.jpg', q.get('exp')!, q.get('sig')!)).toBe(true)
    // 換檔名 / 換簽章都該失敗
    expect(verifyFileSig('2024', '01', 'b.jpg', q.get('exp')!, q.get('sig')!)).toBe(false)
    expect(verifyFileSig('2024', '01', 'a.jpg', q.get('exp')!, 'deadbeef')).toBe(false)
  })
  it('signLibFileUrl → verifyLibFileSig accepts, tamper rejects', () => {
    const url = signLibFileUrl('training', '2024.09.01 忠烈祠 宋修傳', '2024-09-01(1).jpg')
    const q = new URLSearchParams(url.split('?')[1])
    expect(
      verifyLibFileSig('training', '2024.09.01 忠烈祠 宋修傳', '2024-09-01(1).jpg', q.get('exp')!, q.get('sig')!),
    ).toBe(true)
    expect(
      verifyLibFileSig('hongshi', '2024.09.01 忠烈祠 宋修傳', '2024-09-01(1).jpg', q.get('exp')!, q.get('sig')!),
    ).toBe(false)
  })
})

describe('summarizeLibraryFromIndex', () => {
  it('returns totals per library and null for an absent library', () => {
    expect(summarizeLibraryFromIndex(idx as any, 'training')).toEqual({ totalFiles: 5, topFolders: 2 })
    expect(summarizeLibraryFromIndex(idx as any, 'chenwei')).toEqual({ totalFiles: 9, topFolders: 13 })
    expect(summarizeLibraryFromIndex({ ...idx, libraries: {} } as any, 'training')).toBeNull()
  })
})

describe('listYearsFromIndex (chenwei)', () => {
  it('sums months + screenshots + downloads + events, sorts newest first', () => {
    const years = listYearsFromIndex(idx as any)!
    expect(years.map((y) => y.year)).toEqual(['2024', '2023']) // desc
    const y2024 = years.find((y) => y.year === '2024')!
    expect(y2024.total).toBe(13) // (2+1+0) + 3ss + 1dl + 4event + 2 month-event(03.19旅遊)
    expect(y2024.monthsWithPhotos).toBe(2) // 01, 03 (07 is empty; 03 already active)
    expect(years.find((y) => y.year === '2023')!.total).toBe(1)
  })
})

describe('getYearMonthsFromIndex (chenwei)', () => {
  it('returns sorted months + segment counts', () => {
    const r = getYearMonthsFromIndex(idx as any, '2024')!
    expect(r.months).toEqual([
      { month: '01', count: 2, eventCount: 0 },
      { month: '03', count: 1, eventCount: 1 }, // 03 底下有 1 個事件夾
      { month: '07', count: 0, eventCount: 0 },
    ])
    expect(r.screenshots).toBe(3)
    expect(r.downloads).toBe(1)
    expect(r.events).toEqual([{ name: '畢業典禮', count: 4 }])
  })
  it('returns an empty shell for an unknown year', () => {
    expect(getYearMonthsFromIndex(idx as any, '1999')).toEqual({
      months: [], screenshots: 0, downloads: 0, events: [],
    })
  })
})

// ---- 月內事件夾（year → month → event 三層巢狀）----
describe('month-nested events (chenwei)', () => {
  it('getMonthEventsFromIndex lists a month\'s event folders', () => {
    expect(getMonthEventsFromIndex(idx as any, '2024', '03')).toEqual([{ name: '03.19旅遊', count: 2 }])
    expect(getMonthEventsFromIndex(idx as any, '2024', '01')).toEqual([]) // 無事件夾
    expect(getMonthEventsFromIndex(idx as any, '1999', '03')).toEqual([]) // 未知年
  })
  it('listFilesFromIndex resolves an "MM/event" segment, tagged event + signed', () => {
    const r = listFilesFromIndex(idx as any, '2024', '03/03.19旅遊')!
    expect(r.map((f) => f.name)).toEqual(['2024-03-19(1).jpg', '2024-03-19(2).jpg'])
    expect(r.every((f) => f.source === 'event')).toBe(true)
    // 簽章 URL 內含編碼後的 m=03/03.19旅遊
    expect(r[0]!.url).toContain(encodeURIComponent('03/03.19旅遊'))
  })
  it('bucketDir maps "MM/event" to {year}.{MM}/{event} on disk', () => {
    const d = bucketDir('2024', '03/03.19旅遊')
    expect(d).toContain('2024.03')
    expect(d).toContain('03.19旅遊')
  })
  it('bucketDir rejects a nested path with traversal / bad month', () => {
    expect(() => bucketDir('2024', '03/../etc')).toThrow()
    expect(() => bucketDir('2024', '13/x')).toThrow() // 13 非合法月份 → 落到年層事件檢查 → 含 / 被擋
  })
  it('thumbCacheKey for a nested segment matches the sync-script parts', () => {
    const parts = ['chenwei', '2024', '03/03.19旅遊', '2024-03-19(1).jpg']
    const expected = createHash('sha256').update(parts.join('|')).digest('hex').slice(0, 32)
    expect(thumbCacheKey(parts)).toBe(expected)
  })
})

describe('listFilesFromIndex (chenwei)', () => {
  it('returns signed files tagged with the right source per segment', () => {
    const jan = listFilesFromIndex(idx as any, '2024', '01')!
    expect(jan.map((f) => f.name)).toEqual(['2024-01-01(1).jpg', '2024-01-02(1).jpg'])
    expect(jan.every((f) => f.source === 'photo')).toBe(true)
    expect(jan.every((f) => f.url.startsWith('/api/photos/file?'))).toBe(true)

    expect(listFilesFromIndex(idx as any, '2024', 'screenshots')!.every((f) => f.source === 'screenshot')).toBe(true)
    expect(listFilesFromIndex(idx as any, '2024', '畢業典禮')!.every((f) => f.source === 'event')).toBe(true)
  })
  it('returns [] for an unknown segment / year', () => {
    expect(listFilesFromIndex(idx as any, '2024', '99')).toEqual([])
    expect(listFilesFromIndex(idx as any, '1999', '01')).toEqual([])
  })
})

describe('listLibraryFolderFromIndex (training / hongshi folder browser)', () => {
  it('lists the training root folders — the page IS populated', () => {
    const root = listLibraryFolderFromIndex(idx as any, 'training', '')!
    expect(root.folders.map((f) => f.name)).toEqual(['2024.09.01 忠烈祠 宋修傳', '2023'])
    expect(root.files).toEqual([]) // 根層只有資料夾
  })
  it('lists files inside an event folder, signed + tagged event', () => {
    const r = listLibraryFolderFromIndex(idx as any, 'training', '2024.09.01 忠烈祠 宋修傳')!
    expect(r.files.map((f) => f.name)).toHaveLength(3)
    expect(r.files.every((f) => f.source === 'event')).toBe(true)
    expect(r.files.every((f) => f.url.startsWith('/api/photos/lib/training/file?'))).toBe(true)
  })
  it('returns an empty folder (not null) for an unknown subpath', () => {
    expect(listLibraryFolderFromIndex(idx as any, 'training', 'does/not/exist')).toEqual({ folders: [], files: [] })
  })
})

// ---- R2 hybrid key helpers（守「sync 腳本算出的 key ＝ thumb 端點要的 key」這條 invariant）----
describe('R2 hybrid keys (cloud /photos)', () => {
  it('r2IndexKey is fixed', () => {
    expect(r2IndexKey()).toBe('photos/index.json')
  })

  it('r2ThumbKey format = photos/thumb/{cacheKey}_{w}.webp', () => {
    const key = thumbCacheKey(['chenwei', '2015', '11', '2015-11-14(1).jpg'])
    expect(r2ThumbKey(key, 480)).toBe(`photos/thumb/${key}_480.webp`)
    expect(r2ThumbKey(key, 1600)).toBe(`photos/thumb/${key}_1600.webp`)
  })

  // sync_photos_to_r2.mjs 重算 thumbCacheKey = sha256(parts.join('|')).slice(0,32)。
  // 這裡用同演算法重算，確保端點的 thumbCacheKey 與腳本上傳的 key 對得起來。
  it('thumbCacheKey matches the sync script algorithm (sha256 first 32 hex)', () => {
    for (const parts of [
      ['chenwei', '2024', '03', 'x.jpg'],
      ['lib', 'training', '2017 忠烈祠', 'y.png'],
    ]) {
      const expected = createHash('sha256').update(parts.join('|')).digest('hex').slice(0, 32)
      expect(thumbCacheKey(parts)).toBe(expected)
    }
  })
})

// ---- 整合測試：用真實 scripts/photo_index.json 證明三個相簿（尤其訓練）有東西可顯示 ----
// CI / 沒跑過 build_photo_index 的環境會自動 skip，不會紅。
describe('real photo_index.json (integration)', () => {
  const p = resolve(process.cwd(), 'scripts', 'photo_index.json')
  const has = existsSync(p)
  const maybe = has ? it : it.skip
  const real: any = has ? JSON.parse(readFileSync(p, 'utf-8')) : null

  maybe('every library has files, and training resolves to a non-empty folder list', () => {
    for (const slug of ['chenwei', 'training', 'hongshi'] as const) {
      const s = summarizeLibraryFromIndex(real, slug)
      expect(s, `${slug} missing from index`).not.toBeNull()
      expect(s!.totalFiles, `${slug} has 0 files`).toBeGreaterThan(0)
    }
    const trainingRoot = listLibraryFolderFromIndex(real, 'training', '')
    expect(trainingRoot, 'training root not in index').not.toBeNull()
    expect(
      trainingRoot!.folders.length + trainingRoot!.files.length,
      'training root is empty → /photos/training would render 空',
    ).toBeGreaterThan(0)
  })
})
