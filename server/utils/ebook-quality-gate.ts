// 電子圖書館的上架品質閘門 —— 門檻只寫在這裡一次。
//
// 為什麼要有這道閘門：全館 4,600 冊裡只有約三分之一轉錄完成，其餘是還沒 OCR 的
// 掃描檔或只有書目的空殼。空殼書出現在書架上比不出現更糟 —— 點進去是一片空白，
// 而使用者無從分辨「這本壞了」和「這本還沒做」。所以預設只上架把關過的書，
// 未過關的留給策展模式（?quality=all）。
//
// 分數來自 scripts/quality_sweep.py（純規則、零 LLM），tier 定義：
//   >= 80  GOOD          ← 目前的上架門檻
//   60–79  FAIR，結構有瑕疵但讀得下去
//   1–59   結構壞掉，需要重做 standardize 或重拆卷
//   0      NEEDS_OCR，還沒被讀過
//   null   還沒評分（多半是還沒 parse）
//
// 想放寬到「可用」等級就把這個數字改成 60，兩支 API 會一起生效
// （2026-09-04 實測：80 → 1,164 冊上架；60 → 1,451 冊）。
export const EBOOK_QUALITY_PASS = 80;

/** 這本書可以上架閱讀嗎？全集（collection 非 null）是人工策展的，不受此閘門限制。 */
export function ebookPassesGate(b: {
  collection?: string | null;
  quality_score?: number | null;
  chunk_count?: number | null;
} | null | undefined): boolean {
  if (!b) return false;
  if (b.collection != null) return true;
  return (b.quality_score ?? 0) >= EBOOK_QUALITY_PASS && (b.chunk_count ?? 0) > 0;
}
