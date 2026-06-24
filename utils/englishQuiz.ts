// 從課程資料產生測驗題目（單元測驗 + 段考 + 總複習共用）。
type Word = { en: string; zh: string; emoji?: string };
type Lesson = { no: number; title_zh: string; words: Word[]; exercises?: any[] };

export function shuffle<T>(a: T[]): T[] {
  const x = [...a];
  for (let i = x.length - 1; i > 0; i--) { const j = Math.floor(Math.random() * (i + 1)); [x[i], x[j]] = [x[j], x[i]]; }
  return x;
}
export const sample = <T>(a: T[], n: number): T[] => shuffle(a).slice(0, n);

export function vocabMCQ(words: Word[], n: number) {
  return sample(words, n).map((w) => {
    const distract = sample(words.filter((x) => x.en !== w.en), 3).map((x) => x.en);
    return { kind: "mcq", prompt: w.zh, emoji: w.emoji, options: shuffle([w.en, ...distract]), answer: w.en };
  });
}
export function listenMCQ(words: Word[], n: number) {
  return sample(words, n).map((w) => {
    const distract = sample(words.filter((x) => x.zh !== w.zh), 3).map((x) => x.zh);
    return { kind: "mcq", prompt: "聽到的英文是什麼意思？", audio: w.en, options: shuffle([w.zh, ...distract]), answer: w.zh };
  });
}
export function grammarMCQ(lessons: Lesson[], n: number) {
  const pool: any[] = [];
  for (const L of lessons) for (const ex of L.exercises || []) {
    if (ex.type === "fill_choice" || ex.type === "choice")
      for (const it of ex.items || []) pool.push({ kind: "mcq", prompt: it.q, options: shuffle(it.opts), answer: it.ans });
  }
  return sample(pool, Math.min(n, pool.length));
}
export function sentenceItems(lessons: Lesson[], n = 8) {
  const out: any[] = [];
  for (const L of lessons) for (const ex of L.exercises || []) {
    if (ex.type === "unscramble") for (const it of ex.items || []) out.push({ kind: "type", hint: "把單字排成正確的句子", prompt: it.q, answer: it.ans });
    if (ex.type === "translate") for (const it of ex.items || []) out.push({ kind: "type", hint: "把中文翻成英文", prompt: it.q, answer: it.ans });
  }
  return shuffle(out).slice(0, n);
}
export function speakItems(words: Word[], n: number) {
  return sample(words, n).map((w) => ({ kind: "speak", answer: w.en, zh: w.zh }));
}

// 單一單元測驗
export function buildUnitQuiz(lesson: Lesson, type: string) {
  const w = lesson.words;
  if (type === "vocab") return vocabMCQ(w, Math.min(10, w.length));
  if (type === "listening") return listenMCQ(w, Math.min(10, w.length));
  if (type === "speaking") return speakItems(w, Math.min(6, w.length));
  if (type === "sentence") return sentenceItems([lesson], 8);
  if (type === "comprehensive") return shuffle([...vocabMCQ(w, 4), ...listenMCQ(w, 3), ...grammarMCQ([lesson], 5)]);
  return [];
}

// 跨單元複習（段考 / 總複習）。total 題數依範圍大小。
export function buildReviewQuiz(lessons: Lesson[], total: number) {
  const words = lessons.flatMap((l) => l.words);
  const nVocab = Math.round(total * 0.5);
  const nListen = Math.round(total * 0.25);
  const nGrammar = total - nVocab - nListen;
  return shuffle([
    ...vocabMCQ(words, nVocab),
    ...listenMCQ(words, nListen),
    ...grammarMCQ(lessons, nGrammar),
  ]);
}
