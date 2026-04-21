/** Normalize journal rows so list/detail can merge duplicates from import. */
export function normJournalPart(s: string | null | undefined): string {
  return (s ?? "").replace(/\s+/g, " ").trim().toLowerCase();
}

export function journalArticleMergeKey(r: {
  title: string | null;
  venue: string | null;
  author: string | null;
  issue_label: string | null;
}): string {
  return `${normJournalPart(r.title)}|${normJournalPart(r.venue)}|${normJournalPart(r.author)}|${normJournalPart(r.issue_label)}`;
}
