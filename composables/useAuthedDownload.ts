import { authedFetch } from "~/composables/useAuthedFetch";

/**
 * 帶驗證下載檔案。
 *
 * 🚨 為什麼不能用 `<a href="/api/...&download=1">`：那是瀏覽器自己發的請求，
 *    **帶不了 Authorization header**，端點一旦加上 requireAdmin 就會 401。
 *    所以改成用 authedFetch 取回 blob，再用一個暫時的 object URL 觸發下載。
 */
export async function authedDownload(url: string, filename: string) {
  const blob = await authedFetch<Blob>(url, { responseType: "blob" });
  const href = URL.createObjectURL(blob as Blob);
  const a = document.createElement("a");
  a.href = href;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  // 立刻 revoke 會讓某些瀏覽器來不及開始下載，延後釋放
  setTimeout(() => URL.revokeObjectURL(href), 10_000);
}
