# 🧹 Haiku Text Cleanup: Simplified → Traditional + Format Cleaning

## Overview

This tool uses **Claude Haiku 4.5** to clean ebook text:
1. **Simplified → Traditional Chinese conversion** (简体转繁体)
2. **Format cleanup**: Fix spacing, remove OCR artifacts, normalize paragraph breaks
3. **Encoding fixes**: Handle mojibake and mixed encodings

**Why?** Your 750+ books have poor text quality: inconsistent formatting, mixed simplified/traditional characters, OCR artifacts, and spacing issues. Haiku can fix these at scale with low cost.

---

## Setup

### 1. Install dependencies
```bash
pip install anthropic requests
```

### 2. Set API key
```bash
export ANTHROPIC_API_KEY=your-key-here
```

---

## Usage

### Check status
```bash
python scripts/clean_with_haiku.py status
```

Shows:
- Number of books pending cleanup (751)
- Number of available JSONL chunks (901)
- First 5 books to process

### Dry run (preview what would be processed)
```bash
python scripts/clean_with_haiku.py run --limit 5 --dry-run
```

### Run cleanup on books
```bash
# Process first 10 books
python scripts/clean_with_haiku.py run --limit 10

# Process all books
python scripts/clean_with_haiku.py run
```

---

## How It Works

1. **Fetch books** from Supabase (751 books with chunk_count > 0)
2. **Load JSONL chunks** from `G:/我的雲端硬碟/資料/電子書/_chunks/{book_id}.jsonl`
3. **Send to Haiku 4.5** with prompt: convert simplified→traditional, clean formatting
4. **Write cleaned JSONL** back to disk with improved text
5. **Update tracker** (optional: can add `cleaned_at` timestamp to DB)

### Text processing
- Processes up to **30KB of text per API call** (Haiku budget)
- Splits large books into batches
- Preserves structure: combines chunks with `---CHUNK BREAK---` marker
- Returns cleaned text with marker preserved

### Cost estimate
- **Haiku 4.5**: $0.80/$4 per 1M tokens (input/output)
- Typical book: 50-100K chars ≈ 12-25K tokens input → ~5-10K output
- **~700 books × 20K tokens ≈ 14M tokens → ~$11 total** (very cheap!)

---

## Example

**Before:**
```
图字：01-2018-7665号

图书在版编目（CIP）数据

古希腊人：在希腊大陆之外/（英）菲利普·马特扎克著；戚悦译.--北京：中国社会科学出版社，2019.9

ISBN 978-7-5203-4375-6

Ⅰ.①古… Ⅱ.①菲…②戚… Ⅲ.①文化史-古希腊-通俗读物
```

**After (expected):**
```
圖字：01-2018-7665號

圖書在版編目（CIP）數據

古希臘人：在希臘大陸之外 / （英）菲利普·馬特扎克著；戚悅譯. — 北京：中國社會科學出版社，2019.9

ISBN 978-7-5203-4375-6

I. 古… II. 菲…戚… III. 文化史-古希臘-通俗讀物
```

Changes:
- ✅ `图` → `圖`, `古希腊` → `古希臘`, `著` preserved
- ✅ Removed OCR artifacts: `Ⅰ.①` → `I.`, `……` → `…`
- ✅ Fixed spacing and punctuation formatting
- ✅ Normalized line breaks for better readability

---

## Integration with Reader

Once cleanup is done:
1. Reader automatically loads cleaned JSONL from disk or R2
2. Users see properly formatted traditional Chinese text
3. Search works better with consistent text quality
4. Annotations work on clean text

---

## Future Improvements

- Add `cleaned_at` timestamp column to `ebooks` table
- Track cleanup progress per book (num chunks cleaned)
- A/B test Haiku vs other models for quality
- Optionally re-embed cleaned text for vector search

---

## Troubleshooting

### "No chunks found"
- Check that JSONL files exist in `G:/我的雲端硬碟/資料/電子書/_chunks/`
- Run: `ls -lh G:/我的雲端硬碟/資料/電子書/_chunks/ | wc -l`

### "API key not found"
```bash
export ANTHROPIC_API_KEY=sk_...
```

### "Bad Request from Supabase"
- Ensure `chunk_count` column exists and is populated
- Check: `SELECT id, chunk_count FROM ebooks LIMIT 5;`

---

## Timeline

- **Now**: Run cleanup on first 50-100 books as pilot
- **Next**: Monitor quality, adjust prompt if needed
- **Final**: Run full batch on all 750 books
