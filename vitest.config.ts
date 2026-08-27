import { defineVitestConfig } from '@nuxt/test-utils/config'

// Genealogy spine-tree component tests run in the Nuxt environment so that
// Nuxt auto-imports (computed/ref/watch + composables) resolve inside the SFCs.
export default defineVitestConfig({
  test: {
    environment: 'nuxt',
    // 測試一律放 test/，副檔名一律 .spec.ts（2026-08-27 把原本並存的 tests/*.test.ts 併進來）
    include: ['test/**/*.spec.ts'],
    // Each spec spins up its own Nuxt environment; running many concurrently races
    // on @nuxt/test-utils setup (entry.mjs) and intermittently aborts a file
    // (e.g. multilang-sources skipping all 27). Serialize files for stability —
    // transform is cached so the wall-clock cost is small.
    fileParallelism: false,
    // Real-data episcopal mount is heavy (300+ branches / ~4800 bishops in happy-dom);
    // default 10s is too tight for the mount + Nuxt env hook. stores/collectedWorks.ts
    // has grown to 35k+ lines → cold vite transform alone is ~33s, so the Nuxt setup
    // hook needs headroom above that.
    testTimeout: 60000,
    hookTimeout: 60000,
  },
})
