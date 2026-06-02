import { defineVitestConfig } from '@nuxt/test-utils/config'

// Genealogy spine-tree component tests run in the Nuxt environment so that
// Nuxt auto-imports (computed/ref/watch + composables) resolve inside the SFCs.
export default defineVitestConfig({
  test: {
    environment: 'nuxt',
    include: ['test/**/*.spec.ts'],
  },
})
