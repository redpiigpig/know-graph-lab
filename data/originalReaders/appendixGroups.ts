// 附錄分節：三本讀本的網頁與紙本共用同一個次序。
//
// 這份次序的正本在 scripts/proper_name_categories.py 的 PRINT_ORDER，紙本附錄與
// 單字卡都讀那一份。網頁自己列一次是因為前端讀不到 Python，兩邊不一致就會出現
// 「翻書在〈使徒與門徒〉找得到、上網在別節」這種事，所以任一邊要改都得兩邊一起改。
export const APPENDIX_GROUP_ORDER = [
  "民族與國名",
  "地名",
  "神名與稱號",
  "族長與先知",
  "君王",
  "使徒與門徒",
  "教宗與主教",
  "教父與聖人",
  "其他人名",
  "節期與聖日",
  "待歸類",
];

export interface AppendixGroup<T> {
  title: string;
  entries: T[];
}

/**
 * 把一張附錄表切成印得出來的小節。
 *
 * 專名表用 `category`（九類），其餘各表用資料裡本來就有的 `group`；兩者都沒有的
 * 表整張當一節，不硬切。已知的類別照 PRINT_ORDER，其餘照首次出現接在後面。
 */
export function groupAppendixEntries<T extends Record<string, unknown>>(
  entries: T[],
): AppendixGroup<T>[] {
  const field = entries.some((entry) => entry.category) ? "category" : "group";
  const buckets = new Map<string, T[]>();
  for (const entry of entries) {
    const key = String(entry[field] ?? "").trim();
    const bucket = buckets.get(key);
    if (bucket) bucket.push(entry);
    else buckets.set(key, [entry]);
  }
  if (buckets.size <= 1) return [{ title: "", entries }];
  const known = APPENDIX_GROUP_ORDER.filter((name) => buckets.has(name));
  const rest = [...buckets.keys()].filter((name) => !known.includes(name));
  return [...known, ...rest].map((title) => ({ title, entries: buckets.get(title)! }));
}
