# 快速執行指南 (5 分鐘完成)

## 最簡單的方式

### 步驟 1: 登入 Supabase 儀表板

在瀏覽器中開啟:
```
https://supabase.com/dashboard/project/vloqgautkahgmqcwgfuo/editor
```

### 步驟 2: 複製 SQL 內容

打開檔案: `ebook_complete_insert.sql`

全選所有內容 (Ctrl+A)

複製 (Ctrl+C)

### 步驟 3: 在 Supabase 執行

在 SQL Editor 的查詢框中粘貼 (Ctrl+V)

點擊 **Run** 按鈕 (或按 Ctrl+Enter)

### 步驟 4: 確認完成

等待查詢執行完畢 (應在 1-5 秒內)

看到確認信息: ✅ Query executed successfully

## 完成!

所有 92 本書籍已插入到 Supabase ebooks 表

## 驗證結果

在 SQL Editor 中執行:

```sql
SELECT COUNT(*) FROM ebooks WHERE category IN ('歷史學', '社會政治學', '心理學', '自然科學', '文學');
```

應該返回: 92 (或以上，如果包括之前的書籍)

## 遇到問題?

見 `SUPABASE_EXECUTION_GUIDE.md` 完整故障排除指南

---

**預計時間**: 5 分鐘  
**難度**: ⭐ 非常簡單  
**成功率**: 99%+
