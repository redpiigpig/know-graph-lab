// Pure markdown → HTML render helpers for the chunk readers.
//
// Extracted verbatim from pages/ebook/[id].vue so the shared library reader
// and the dedicated /fathers reader render identical HTML (footnotes, page
// markers, parallel-column alignment) without drifting. These are all pure
// functions — no reactive/DOM deps — so both pages wrap them in their own
// computeds. Highlight/annotation injection stays page-side (DOM-based).

import { zipParallel } from "~/lib/multilang-sources";

// ── Inline formatters ──
export function escapeHtml(s: string): string {
  return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

// Inline markdown formatter. `chunkIdx` (when provided) mints per-chunk
// footnote ref anchors so each `[^N]` becomes a clickable sup linked to the
// chunk's footnote section, with a back-link from the footnote body to here.
export function inlineFmt(s: string, chunkIdx: number | null = null): string {
  let out = s.replace(/\*\*([^*\n]+)\*\*/g, "<strong>$1</strong>")
          // *italic* — Latin-containing → Georgia italic (English/Latin book
          // titles & foreign terms); pure CJK → plain <em>.
          .replace(/(^|[^*])\*([^*\n]+)\*(?!\*)/g, (_, lead, inner) =>
            /[A-Za-z]/.test(inner)
              ? `${lead}<em class="book-title-en">${inner}</em>`
              : `${lead}<em>${inner}</em>`
          )
          // <u>X</u> survives escapeHtml as &lt;u&gt;…&lt;/u&gt; — restore it.
          .replace(/&lt;u&gt;([^<]+?)&lt;\/u&gt;/g, "<u>$1</u>")
          // English book titles 《Some Title》 → italic Latin serif.
          .replace(/《([^《》]*[A-Za-z][^《》]*)》/g, "<em class=\"book-title-en\">《$1》</em>");

  // Footnote refs `[^N]` → clickable superscript with bidirectional anchor.
  if (chunkIdx !== null) {
    out = out.replace(/\[\^(\d+)\]/g, (_, n) =>
      `<sup class="footnote-ref" id="fnref-${chunkIdx}-${n}">` +
      `<a href="#fn-${chunkIdx}-${n}" title="跳到註 ${n}">${n}</a></sup>`
    );
  }
  // Print page markers `{{p:N}}` → tiny inline pill (原書頁碼).
  out = out.replace(/\{\{p:(\d+)\}\}/g, (_, n) =>
    `<span class="page-marker" data-page="${n}" title="原書頁碼 ${n}">[頁${n}]</span>`
  );
  return out;
}

// ── Block markdown render ──
export function renderMarkdown(md: string, chunkIndex: number | null = null): string {
  const blocks = md.split(/\n{2,}/);
  const bodyOut: string[] = [];
  const footnoteItems: string[] = [];
  let subSeq = 0;
  let inFootnotes = false;
  for (let block of blocks) {
    block = block.trim();
    if (!block) continue;
    // Footnote-section TOGGLE separator (15+ dashes on their own line).
    if (/^[—－\-]{15,}$/.test(block)) {
      inFootnotes = !inFootnotes;
      continue;
    }
    if (/^-{3,}$/.test(block)) {
      if (!inFootnotes) bodyOut.push("<hr>");
      continue;
    }
    const escaped = escapeHtml(block);
    let h: RegExpMatchArray | null;
    // Headings always belong to body — flip mode back if seen mid-footnotes.
    const isHeading = /^#{1,4}\s/.test(escaped);
    if (isHeading && inFootnotes) inFootnotes = false;

    if (inFootnotes) {
      const fnMatch = escaped.match(/^\((\d+)\)\s*(.*)$/s);
      if (fnMatch && chunkIndex !== null) {
        const num = fnMatch[1];
        const rest = inlineFmt(fnMatch[2], chunkIndex).replace(/\n/g, " ");
        footnoteItems.push(
          `<p class="footnote-item" id="fn-${chunkIndex}-${num}">` +
          `<a href="#fnref-${chunkIndex}-${num}" class="footnote-num" title="回到正文">(${num})</a> ` +
          `${rest} ` +
          `<a href="#fnref-${chunkIndex}-${num}" class="footnote-back" title="回到正文">↩</a></p>`
        );
      } else {
        const cont = `<p class="footnote-continuation">${inlineFmt(escaped, chunkIndex).replace(/\n/g, " ")}</p>`;
        if (footnoteItems.length) {
          footnoteItems.push(cont);
        } else {
          bodyOut.push(`<p>${inlineFmt(escaped, chunkIndex).replace(/\n/g, " ").replace(/  +/g, " ")}</p>`);
        }
      }
      continue;
    }

    if ((h = escaped.match(/^####\s+([\s\S]+)$/))) {
      const id = chunkIndex !== null ? ` id="sec-${chunkIndex}-${subSeq}"` : "";
      subSeq++;
      const joined = h[1].replace(/\n+/g, " ").replace(/\s+/g, " ").trim();
      bodyOut.push(`<h4${id}>${inlineFmt(joined, chunkIndex)}</h4>`);
    }
    else if ((h = escaped.match(/^###\s+([\s\S]+)$/))) {
      const id = chunkIndex !== null ? ` id="sec-${chunkIndex}-${subSeq}"` : "";
      subSeq++;
      const joined = h[1].replace(/\n+/g, " ").replace(/\s+/g, " ").trim();
      bodyOut.push(`<h3${id}>${inlineFmt(joined, chunkIndex)}</h3>`);
    }
    else if ((h = escaped.match(/^##\s+([\s\S]+)$/))) {
      const joined = h[1].replace(/\n+/g, " ").replace(/\s+/g, " ").trim();
      if (joined === "註釋" || joined === "註　釋") {
        bodyOut.push(`<h2 class="section-notes-divider">註　釋</h2>`);
      } else {
        bodyOut.push(`<h2>${inlineFmt(joined, chunkIndex)}</h2>`);
      }
    }
    else if ((h = escaped.match(/^#\s+([\s\S]+)$/))) {
      const joined = h[1].replace(/\n+/g, " ").replace(/\s+/g, " ").trim();
      bodyOut.push(`<h1>${inlineFmt(joined, chunkIndex)}</h1>`);
    }
    else if (/^&gt;\s/.test(escaped)) {
      const lines = escaped.split(/\n/).map(ln => ln.replace(/^&gt;\s?/, "")).join("<br>");
      bodyOut.push(`<blockquote>${inlineFmt(lines, chunkIndex)}</blockquote>`);
    } else {
      // Collapse single \n to a space so the browser reflows naturally.
      bodyOut.push(`<p>${inlineFmt(escaped, chunkIndex).replace(/\n/g, " ").replace(/  +/g, " ")}</p>`);
    }
  }
  if (footnoteItems.length) {
    bodyOut.push('<section class="footnotes" aria-label="註釋">');
    bodyOut.push('<div class="footnotes-label">註　釋</div>');
    bodyOut.push(...footnoteItems);
    bodyOut.push("</section>");
  }
  return bodyOut.join("\n");
}

// ── 目錄 (table-of-contents) page render ──
export function normChapterKey(s: string): string {
  return s.replace(/\[\^\d+\]/g, "").replace(/\s+/g, "").trim();
}

// Render the 目錄 chunk content as an indented + hyperlinked list.
// `chapterIndexByTitle` maps normalized chapter title → chunk_index (0-based)
// so each `**第N章 …**` line resolves to `?page=N+1`.
export function renderTocPage(md: string, chapterIndexByTitle: Map<string, number>): string {
  const lines = md.split(/\n+/).map(l => l.trim()).filter(Boolean);
  const out: string[] = [];
  for (const raw of lines) {
    const line = raw;
    let m = line.match(/^##\s+(?:<u>)?目[　 ]*錄(?:<\/u>)?$/);
    if (m) { out.push('<h2 class="toc-page-title">目　錄</h2>'); continue; }
    m = line.match(/^\*\*(第[一二三四五六七八九十百千]+[卷編冊集篇部])\*\*$/);
    if (m) { out.push(`<div class="toc-volume">${m[1]}</div>`); continue; }
    m = line.match(/^\*\*(第[一二三四五六七八九十百千]+章)([　 ]+)(.+?)\*\*$/);
    if (m) {
      const chNum = m[1];
      const title = m[3].trim();
      const cleanTitle = title.replace(/\[\^\d+\]/g, "").trim();
      const fullKey = normChapterKey(`${chNum}${title}`);
      const idx = chapterIndexByTitle.get(fullKey);
      if (idx !== undefined) {
        out.push(
          `<div class="toc-chapter"><a href="?page=${idx + 1}" data-toc-chapter="${idx + 1}">` +
          `<span class="toc-ch-num">${chNum}</span>` +
          `<span class="toc-ch-title">${escapeHtml(cleanTitle)}</span>` +
          `</a></div>`
        );
      } else {
        out.push(`<div class="toc-chapter toc-chapter-orphan">${escapeHtml(chNum)} ${escapeHtml(cleanTitle)}</div>`);
      }
      continue;
    }
    m = line.match(/^\*\*(.+?)\*\*$/);
    if (m) {
      const title = m[1].trim();
      const idx = chapterIndexByTitle.get(normChapterKey(title));
      if (idx !== undefined) {
        out.push(
          `<div class="toc-chapter"><a href="?page=${idx + 1}" data-toc-chapter="${idx + 1}">` +
          `<span class="toc-ch-title toc-ch-title-solo">${escapeHtml(title)}</span>` +
          `</a></div>`
        );
      } else {
        out.push(`<div class="toc-chapter toc-chapter-orphan">${escapeHtml(title)}</div>`);
      }
      continue;
    }
    out.push(`<div class="toc-section">${escapeHtml(line)}</div>`);
  }
  return out.join("\n");
}

// ── Parallel (對照) column builder ──
const FOOTNOTE_SEP_RE = /^[—－\-]{15,}$/;
const HEADING_RE = /^#{1,4}\s/;

function splitParagraphs(md: string): string[] {
  return md.split(/\n{2,}/).map(p => p.trim()).filter(Boolean);
}

// Split a chunk's paragraphs into body[] and footnotes[], tracking the
// body↔footnotes mode via separator toggles (headings restart body context).
function splitBodyAndFootnotes(md: string): { body: string[]; footnotes: string[] } {
  const paras = splitParagraphs(md);
  const body: string[] = [];
  const footnotes: string[] = [];
  let inFootnotes = false;
  for (const p of paras) {
    if (FOOTNOTE_SEP_RE.test(p)) { inFootnotes = !inFootnotes; continue; }
    if (HEADING_RE.test(p)) { inFootnotes = false; body.push(p); continue; }
    (inFootnotes ? footnotes : body).push(p);
  }
  return { body, footnotes };
}

function parseFootnoteItem(p: string): { num: number; text: string } | null {
  const m = p.match(/^\((\d+)\)\s*([\s\S]*)$/);
  if (!m) return null;
  return { num: parseInt(m[1], 10), text: m[2] };
}

function renderFootnoteItem(num: number, text: string, chunkIdx: number): string {
  const inner = inlineFmt(escapeHtml(text), chunkIdx).replace(/\n/g, " ");
  return (
    `<p class="footnote-item" id="fn-${chunkIdx}-${num}">` +
    `<a href="#fnref-${chunkIdx}-${num}" class="footnote-num" title="回到正文">(${num})</a> ` +
    `${inner} ` +
    `<a href="#fnref-${chunkIdx}-${num}" class="footnote-back" title="回到正文">↩</a></p>`
  );
}

function parseFootnoteColumn(paras: string[], chunkIdx: number): Map<number, string> {
  const out = new Map<number, string>();
  let lastNum: number | null = null;
  for (const p of paras) {
    if (FOOTNOTE_SEP_RE.test(p)) continue;
    const item = parseFootnoteItem(p);
    if (item) {
      out.set(item.num, renderFootnoteItem(item.num, item.text, chunkIdx));
      lastNum = item.num;
    } else if (lastNum !== null) {
      const html = `<p class="footnote-continuation">${inlineFmt(escapeHtml(p), chunkIdx)}</p>`;
      out.set(lastNum, (out.get(lastNum) ?? "") + html);
    }
  }
  return out;
}

export interface ParallelFootnote { num: number; zh: string; cols: Record<string, string> }
export interface ParallelColumns {
  langs: string[];
  rows: { zh: string; cols: Record<string, string> }[];
  footnotes: ParallelFootnote[];
}

// Generalized 對照 rendering: 中 + every source language. Body paragraphs are
// zipped by index; footnotes aligned by NUMBER across all columns. Each column
// renders in its own footnote-id namespace (100000*(col+1)) so refs never
// collide. `zhChunkIdx` is the current 0-based chunk index.
export function buildParallelColumns(
  zhMd: string,
  sources: Record<string, string>,
  langs: string[],
  zhChunkIdx: number
): ParallelColumns {
  if (!langs.length || !zhMd) return { langs: [], rows: [], footnotes: [] };

  const zhSplit = splitBodyAndFootnotes(zhMd);
  const zhBody = zhSplit.body.map(p => renderMarkdown(p, zhChunkIdx));
  const bodyByLang: Record<string, string[]> = {};
  const fnByLang: Record<string, Map<number, string>> = {};
  langs.forEach((lang, li) => {
    const ns = zhChunkIdx + 100000 * (li + 1);
    const split = splitBodyAndFootnotes(sources[lang] ?? "");
    bodyByLang[lang] = split.body.map(p => renderMarkdown(p, ns));
    fnByLang[lang] = parseFootnoteColumn(split.footnotes, ns);
  });
  const rows = zipParallel(zhBody, bodyByLang, langs);

  const zhFn = parseFootnoteColumn(zhSplit.footnotes, zhChunkIdx);
  const nums = [...new Set([
    ...zhFn.keys(),
    ...langs.flatMap(l => [...fnByLang[l].keys()]),
  ])].sort((a, b) => a - b);
  const footnotes = nums.map(n => ({
    num: n,
    zh: zhFn.get(n) ?? "",
    cols: Object.fromEntries(langs.map(l => [l, fnByLang[l].get(n) ?? ""])),
  }));

  return { langs, rows, footnotes };
}

// Per-source single-column render (「德」「英」… view modes), each in its own
// footnote namespace so refs don't collide with the 中 column.
export function renderSourceHtmlByLang(
  sources: Record<string, string>,
  langs: string[],
  zhChunkIdx: number
): Record<string, string> {
  const out: Record<string, string> = {};
  langs.forEach((lang, li) => {
    out[lang] = renderMarkdown(sources[lang] ?? "", zhChunkIdx + 100000 * (li + 1));
  });
  return out;
}
