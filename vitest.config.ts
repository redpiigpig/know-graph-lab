import { defineVitestConfig } from '@nuxt/test-utils/config'

// Genealogy spine-tree component tests run in the Nuxt environment so that
// Nuxt auto-imports (computed/ref/watch + composables) resolve inside the SFCs.
export default defineVitestConfig({
  test: {
    environment: 'nuxt',
    include: ['test/**/*.spec.ts'],
    // Each spec spins up its own Nuxt environment; running many concurrently races
    // on @nuxt/test-utils setup (entry.mjs) and intermittently aborts a file
    // (e.g. multilang-sources skipping all 27). Serialize files for stability —
    // transform is cached so the wall-clock cost is small.
    fileParallelism: false,
  },
})
