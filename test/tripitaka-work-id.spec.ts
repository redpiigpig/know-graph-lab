import { describe, expect, it } from "vitest";
import { isValidWorkId } from "../server/utils/tripitaka";

// 🚨 這個函式一度只放行 T 與 N，卍續藏那 1,230 部（X0001…）全部打不開，
//    而首頁照樣列得出部數與字數，只有點進去才壞。四種藏經各鎖一筆。
describe("isValidWorkId", () => {
  it("四種藏經的代號都放行", () => {
    for (const id of [
      "T0262", "T0220a", "T1005A", "T0150A",   // 大正藏，含大小寫分卷
      "X0001", "X0088",                         // 卍新纂續藏
      "N01n0001", "N70n0043",                   // 漢譯南傳
      "DKtoh0001", "DKtoh0113", "DKtoh0539a",   // 德格版甘珠爾，含後綴本
      "DKkarchag",                              // 甘珠爾目錄冊，無 Toh 號
    ]) {
      expect(isValidWorkId(id), id).toBe(true);
    }
  });

  it("擋掉路徑注入與亂寫的代號", () => {
    // 代號會直接拼成檔名去讀 Drive／R2，這裡是唯一一道防線
    for (const id of [
      "", "T262", "T02620", "Y0001", "DKtoh1", "DKtoh0113A",
      "../../etc/passwd", "T0262/../../x", "T0262.jsonl", "T0262%2F..",
      "DK", "DKkarchag2", "N1n0001", "T0262 ", " T0262",
    ]) {
      expect(isValidWorkId(id), id).toBe(false);
    }
  });
});
