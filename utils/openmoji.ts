// OpenMoji 彩色 SVG（CC BY-SA 4.0）走 jsDelivr CDN。hex 為 OpenMoji 檔名碼點。
export function emojiUrl(hex?: string | null): string {
  return hex ? `https://cdn.jsdelivr.net/gh/hfg-gmuend/openmoji@master/color/svg/${hex}.svg` : "";
}
