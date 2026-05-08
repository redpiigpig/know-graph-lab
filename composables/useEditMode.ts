// Global edit-mode toggle, shared across all pages that use AppHeader.
// SSR-safe via useState (Nuxt's built-in state container).
export function useEditMode() {
  return useState<boolean>("edit-mode", () => false);
}
