// 給 scripts/ 底下的稽核腳本用的最小 vite 設定：只補 `~` 別名。
// 正式測試走 vitest.config.ts（Nuxt 環境），那邊的別名由 @nuxt/test-utils 提供；
// vite-node 直接跑腳本時沒有那一層，所以要自己補，否則 `~/lib/...` 解不開。
import { resolve } from "node:path";
export default { resolve: { alias: { "~": resolve(import.meta.dirname, "..") } } };
