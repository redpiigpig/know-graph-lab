# Supabase 電子書數據執行指南

## 概述

所有 92 本電子書的 SQL 插入語句已生成完畢，並保存在版本控制中。本指南提供多種執行方式。

## 文件位置

- **SQL 批次**: `ebook_complete_insert.sql`
- **元數據目錄**: `ebook_complete_catalog.json`
- **執行報告**: `ebook_complete_report.json`

## 方式 1: Supabase Dashboard SQL Editor (推薦)

**最簡單、最安全的方式**

步驟:
1. 前往 https://supabase.com/dashboard/project/vloqgautkahgmqcwgfuo
2. 進入 **SQL Editor** 標籤
3. 點擊 **New Query**
4. 打開文件: `ebook_complete_insert.sql`
5. 複製全部內容到編輯框
6. 點擊 **Run** 按鈕

預期結果:
```
NOTICE: 92 插入語句已執行
```

驗證查詢:
```sql
SELECT COUNT(*) as total,
       COUNT(CASE WHEN category='歷史學' THEN 1 END) as history,
       COUNT(CASE WHEN category='社會政治學' THEN 1 END) as politics,
       COUNT(CASE WHEN category='心理學' THEN 1 END) as psychology,
       COUNT(CASE WHEN category='自然科學' THEN 1 END) as science,
       COUNT(CASE WHEN category='文學' THEN 1 END) as literature
FROM ebooks;
```

## 方式 2: 命令行工具執行

### 2a. 使用 supabase-cli

```bash
supabase db push < ebook_complete_insert.sql
```

### 2b. 使用 psql

```bash
# 設置連接變數
export PGPASSWORD="your_supabase_password"

psql -h vloqgautkahgmqcwgfuo.supabase.co \
     -U postgres \
     -d postgres \
     -f ebook_complete_insert.sql
```

## 方式 3: 自動化 Python 執行

運行自動化腳本 (需要網絡連接):

```bash
python3 /c/tmp/supabase_psycopg2_insert.py
```

或使用 REST API:

```bash
python3 /c/tmp/supabase_rest_api_insert.py
```

## SQL 結構說明

### 批次格式

```sql
-- Batch 1 (92 books)
BEGIN;
INSERT INTO ebooks (...) VALUES (...) ON CONFLICT (title) DO NOTHING;
INSERT INTO ebooks (...) VALUES (...) ON CONFLICT (title) DO NOTHING;
...
COMMIT;
```

### 去重機制

- 使用 `ON CONFLICT (title) DO NOTHING` 自動跳過重複的書籍
- 不會覆蓋現有記錄
- 安全的冪等操作 (可重複執行)

### 數據映射

| 欄位 | 來源 | 說明 |
|------|------|------|
| title | 檔名解析 | 去除作者信息和後綴後的書名 |
| author | 檔名解析 | 使用 "，" 或 " by " 分隔符提取 |
| file_type | 原始副檔名 | pdf, epub, azw3, mobi 等 |
| category | 文件夾名稱 | 9 個主分類之一 |
| subcategory | 預留 | 子分類 (暫未使用) |

## 預期效果

執行完成後，數據庫應包含:

| 分類 | 新增書籍數 |
|------|-----------|
| 歷史學 | 11 |
| 社會政治學 | 12 |
| 心理學 | 21 |
| 自然科學 | 27 |
| 文學 | 25 |
| **總計** | **92** |

加上原有的 107 本，總計 **199 本書籍**

## 故障排除

### 問題 1: "table ebooks does not exist"

**解決方案**: 確認 Supabase 數據庫中已創建 ebooks 表

```sql
CREATE TABLE IF NOT EXISTS public.ebooks (
    id BIGSERIAL PRIMARY KEY,
    title TEXT NOT NULL UNIQUE,
    author TEXT,
    file_type TEXT,
    category TEXT,
    subcategory TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);
```

### 問題 2: 連接超時

**原因**: 防火牆或網絡限制  
**解決方案**: 使用 Supabase Dashboard SQL Editor (Web 界面)

### 問題 3: 編碼錯誤

**原因**: 中文字符編碼不匹配  
**解決方案**: 確保使用 UTF-8 編碼執行 SQL

## 驗證清單

執行後確認:

- [ ] SQL 執行沒有錯誤
- [ ] 92 條新記錄已插入
- [ ] 所有分類都有相應的書籍
- [ ] 作者信息正確解析
- [ ] 沒有重複的書籍

## Git 提交記錄

相關的提交:
```
8fe7ee0 feat: complete ebook catalog automation pipeline - 92 books scanned
7ee4b25 docs: update ebook catalog automation status - Phase 1 completion
03efcc2 docs: add comprehensive ebook automation completion report
```

## 後續步驟

執行成功後:

1. ✅ 數據庫插入完成
2. 📊 可選: 分析書籍統計
3. 🔄 可選: Google Drive 檔案同步和重命名
4. 📚 完成電子書目錄自動化系統

## 支援信息

- Supabase 專案 ID: `vloqgautkahgmqcwgfuo`
- 資料庫: PostgreSQL
- 表名: `ebooks`
- SQL 檔案大小: ~14KB
- 總 INSERT 語句: 104 條

---

**最後更新**: 2026-05-02  
**狀態**: ✅ 準備就緒，等待執行
