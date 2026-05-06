import type { RouterConfig } from "@nuxt/schema";

/**
 * Custom router scroll behavior — primarily so that "browser back" from a
 * book detail page returns the user to the exact scroll position they were
 * at on /ebook (instead of snapping to the top).
 *
 * - savedPosition: present when the navigation is back/forward → restore
 * - hash: jump to anchor element
 * - same path, different query (e.g. switching categories on /ebook): keep
 *   current scroll position so the user doesn't lose context when they
 *   filter
 * - everything else: top of page
 */
export default <RouterConfig>{
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) return savedPosition;
    if (to.hash) return { el: to.hash, behavior: "smooth" };
    if (from && to.path === from.path) return false; // query-only navigation
    return { top: 0 };
  },
};
