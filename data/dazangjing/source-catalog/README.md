# Dazangjing Source Catalog

這裡放「來源館藏先行」的候選總書目。這一層不是正式入藏資料，而是供後續逐筆去重、查核、斷代、分類，再寫入 `data/dazangjing/{ancient,medieval,early-modern,modern}.ts`。

## Current Seed

- `seed-records.json`
  - 產生腳本：`python scripts/dazangjing_source_catalog.py --limit 3 --sleep 0.1`
  - 初版結果：140 candidate records
  - 已自動查詢來源：
    - Library of Congress (`loc`)：57
    - Deutsche Nationalbibliothek (`dnb`)：26
    - Bibliotheque nationale de France (`bnf`)：57
  - timeout/error：1（LoC: `Corpus iuris canonici`）

## Source Status

Automated in first pass:

- `loc` — Library of Congress JSON API for digitized/public loc.gov book records.
- `dnb` — Deutsche Nationalbibliothek SRU.
- `bnf` — Bibliotheque nationale de France SRU.

Manual queue until stable machine endpoint is confirmed:

- `bl` — British Library.
- `rsl` — Russian State Library.
- `nlr` — National Library of Russia.
- `vatican_library` — Biblioteca Apostolica Vaticana.
- `vatican_archive` — Archivio Apostolico Vaticano.
- `constantinople` — Ecumenical Patriarchate of Constantinople.
- `alexandria_patriarchate` — Greek Orthodox Patriarchate of Alexandria and All Africa.

Tradition-specific sources that must be checked when national-library coverage is thin:

- `hmml` — Hill Museum & Manuscript Library Reading Room; especially Armenian, Coptic, Ge'ez/Ethiopic, Syriac manuscript witnesses.
- `betamasaheft` — Beta masaheft: Manuscripts of Ethiopia and Eritrea; primary source layer for Ge'ez/Ethiopian/Eritrean Christian manuscripts.
- `syriaca` — Syriaca.org; authority layer for Syriac authors, saints, hagiography, bibliography, and work identification.
- `matenadaran` — Mesrop Mashtots Institute of Ancient Manuscripts; primary Armenian manuscript repository.
- `georgian_manuscripts` — Korneli Kekelidze Georgian National Centre of Manuscripts; primary Georgian manuscript repository and related Caucasus materials.
- `coptic_encyclopedia` — Claremont Coptic Encyclopedia; reference layer for Coptic authors, works, institutions, and traditions.
- `bho` — Bibliotheca Hagiographica Orientalis; Oriental Christian hagiographic authority list covering Arabic, Coptic, Syriac, Armenian, and Ethiopic materials.
- `ldab` — Leuven Database of Ancient Books / Trismegistos; ancient literary manuscript witnesses, including Coptic and Syriac.

Rule: if a Coptic, Armenian, Ethiopic, Syriac, or Georgian work is not visible in LoC/DNB/BnF/BL/Russian/Vatican searches, it still remains in scope and must be checked through these tradition-specific repositories before being dropped.

## Curation Rule

每筆候選至少要補：

- `title_orig`
- `title_zh`
- `author`
- `era`
- `place`
- `language`
- source URL or shelf/catalog identifier
- `eraKey`: `pre` / `ancient` / `medieval` / `early-modern` / `modern`
- `collectionKey`: `jing` / `lu` / `lun` / `xuandao` / `shuxin` / `liyi` / `shiwen` / `yijiao` / `shizhuan` / `leishu`
- `canon`: `zheng` / `wai`

不得直接 auto-merge。先對整個 Dazangjing corpus 做 `title_zh` + `title_orig` 語義去重，再人工判斷是否入庫。

## Local AI Loop

Classifier:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\dazangjing_catalog_loop.ps1 once -MaxRecords 5
```

Background loop:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\dazangjing_catalog_loop.ps1 start -IntervalSeconds 1800 -MaxRecords 25
powershell -ExecutionPolicy Bypass -File scripts\dazangjing_catalog_loop.ps1 health
powershell -ExecutionPolicy Bypass -File scripts\dazangjing_catalog_loop.ps1 stop
```

Engine order:

1. Local Ollama (`OLLAMA_BASE`, default `http://localhost:11434`; model `DAZANGJING_OLLAMA_MODEL`, default `qwen2.5:7b`)
2. Gemini (`GEMINI_API_KEY*` / `GOOGLE_API_KEY*`; model `DAZANGJING_GEMINI_MODEL`, default `gemini-2.5-flash`)
3. NVIDIA (`NVIDIA_API_KEY*`; model `DAZANGJING_NVIDIA_MODEL`, default `deepseek-ai/deepseek-v4-flash`)

Local Ollama results are not blindly trusted. If local classification succeeds, the script asks Gemini to review it; if Gemini fails, NVIDIA reviews it. If local output is malformed or low-confidence without review, the script falls through to Gemini/NVIDIA. Output is appended to `classified-records.jsonl`; heartbeat and loop status are written to `catalog-loop-heartbeat.json`, `catalog-loop.pid`, and `catalog-loop.log`.

Current loop snapshot (2026-06-24): background process restarted on `seed-records-expanded.json` with `IntervalSeconds=1800`, `MaxRecords=10`; ledger total reached `181`. Blank-title records are now handled by a rule-based `needs_manual_review` path instead of spending AI calls.
