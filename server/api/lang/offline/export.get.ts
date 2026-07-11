/**
 * GET /api/lang/offline/export?language=la&kind=pack|progress → .docx 下載（零 AI，純讀 DB）
 *
 * kind=pack：FSI 離線練習包 — 拿去 NotebookLM / Gemini 練習用。
 *   內含：學習者檔案（程度/弱項）＋本課素材（到期複習字、建議新字、今日主題）
 *   ＋「教官指令」（FSI 聽說教學法 drill 循環，華語母語者視角）＋成果報告模板。
 * kind=progress：學習進度報告 — 給自己或外部 AI 看的完整近況。
 *
 * FSI 的 Category I–IV 時數分類以英語母語者為基準，對華語母語者不適用，
 * 故只採 FSI 的「方法」（drill 循環、先練後講）與 ILR 量表，難度註記改用華語視角。
 */
import { AlignmentType, Document, Packer, Paragraph, TextRun, convertMillimetersToTwip } from "docx";
import { getCoach } from "~/server/utils/lang-coaches";
import { reportTemplate } from "~/utils/offlineReport";

const EN = "Times New Roman";
const CJK = "新細明體";

const ILR_BY_LEVEL: Record<string, string> = {
  A1: "ILR 0+", A2: "ILR 1", B1: "ILR 1+", B2: "ILR 2", C1: "ILR 3", C2: "ILR 4",
  N5: "ILR 0+", N4: "ILR 1", N3: "ILR 1+", N2: "ILR 2", N1: "ILR 2+～3",
  入門: "ILR R-0+（閱讀）", 初級: "ILR R-1（閱讀）", 中級: "ILR R-2（閱讀）", 進階: "ILR R-3（閱讀）",
};

/** 華語母語者視角的難度／策略註記（取代美國中心的 FSI Category 時數表） */
const ZH_L1_NOTES: Record<string, string> = {
  en: "印歐語、無漢字紅利；華語者最大障礙＝冠詞、時態一致、關係子句，這三項要反覆 drill。",
  ja: "漢字共通是華語者的巨大優勢（FSI 把日語列為對英語母語者最難的第四類，對華語者不成立）；重點在假名熟練度、敬語與 SOV 語序。",
  de: "四格變化與可分離動詞為華語所無，需 drill 到反射；名詞一律連冠詞（性別）一起背。",
  fr: "動詞變位與陰陽性為華語所無；發音（鼻母音、連誦 liaison）優先 drill。",
  es: "變位規則但量大；華語者無同源詞可借，詞彙靠間隔複習累積。",
  la: "目標是閱讀教會文獻（ILR 閱讀量表）；變格變位用替換／轉換練習最有效，無口說壓力。",
  grc: "目標是閱讀新約／七十士譯本；冠詞系統與分詞是 drill 重點。",
  hbo: "目標是閱讀希伯來聖經；三子音字根與 binyanim 動詞幹最適合轉換練習。",
  lzh: "華語者的母語古層；重點在虛詞、句讀與訓詁，用精讀而非外語 drill。",
};

interface RunOpts { size?: number; bold?: boolean; color?: string; mono?: boolean }
const run = (text: string, o: RunOpts = {}) =>
  new TextRun({
    text, bold: o.bold, size: o.size ?? 22, color: o.color ?? "000000",
    font: o.mono
      ? { ascii: "Consolas", hAnsi: "Consolas", cs: "Consolas", eastAsia: CJK }
      : { ascii: EN, hAnsi: EN, cs: EN, eastAsia: CJK },
  });
const p = (text: string, o: RunOpts & { after?: number; indent?: boolean } = {}) =>
  new Paragraph({
    spacing: { after: o.after ?? 80, line: 300, lineRule: "auto" as any },
    indent: o.indent ? { left: 360 } : undefined,
    children: [run(text, o)],
  });
const h1 = (text: string) =>
  new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { before: 120, after: 200, line: 320, lineRule: "auto" as any },
    children: [run(text, { size: 34, bold: true })],
  });
const h2 = (text: string) =>
  new Paragraph({
    spacing: { before: 260, after: 120, line: 320, lineRule: "auto" as any },
    children: [run(text, { size: 27, bold: true, color: "1F3864" })],
  });
const bullet = (text: string) => p(`•  ${text}`, { indent: true });

/** 台北日期種子的簡單輪替（同天穩定、隔天換），與首頁「今日推薦」精神一致 */
function rotateDaily<T>(arr: T[] | undefined, day: string, n: number): T[] {
  if (!arr?.length) return [];
  let seed = 0;
  for (const ch of day) seed = (seed * 31 + ch.charCodeAt(0)) % 997;
  const out: T[] = [];
  for (let i = 0; i < Math.min(n, arr.length); i++) out.push(arr[(seed + i) % arr.length]);
  return out;
}

const wordLine = (w: any) =>
  [w.word, w.reading || "－", w.meaning || "", w.example || "－"].join("｜");

export default defineEventHandler(async (event) => {
  const user = await requireAuth(event);
  const supabase = getAdminClient();
  const q = getQuery(event);
  const language = (q.language as string) || "en";
  const kind = (q.kind as string) === "progress" ? "progress" : "pack";
  const coach = getCoach(language);
  if (!coach) throw createError({ statusCode: 400, message: "不支援的語言" });

  const today = tzToday();
  const [{ data: prog }, { data: mem }] = await Promise.all([
    supabase.from("lang_progress").select("level, streak_days, total_minutes").eq("user_id", user.id).eq("language", language).single(),
    supabase.from("lang_memory").select("memory, highlights").eq("user_id", user.id).eq("language", language).single(),
  ]);
  const level = prog?.level || coach.defaultLevel;
  const ilr = ILR_BY_LEVEL[level] ? `${level}（約 ${ILR_BY_LEVEL[level]}）` : level;
  const hl = (mem?.highlights ?? {}) as { strengths?: string[]; weaknesses?: string[]; topics?: string[] };

  const children: Paragraph[] = [];
  let title: string;

  if (kind === "pack") {
    // ── 素材：到期複習字 + 建議新字 + 今日主題 ─────────────────────────
    const [{ data: due }, bankR] = await Promise.all([
      supabase
        .from("lang_vocab")
        .select("word, reading, meaning, example")
        .eq("user_id", user.id).eq("language", language)
        .lte("next_review", today)
        .order("next_review", { ascending: true })
        .limit(40),
      supabase.rpc("pick_vocab_bank", { p_language: language, p_category: null, p_user: user.id, p_limit: 15 }),
    ]);
    const newWords = (bankR.data ?? []) as any[];
    const topics = [
      ...rotateDaily(coach.smalltalkTopics, today, 3).map((t) => `聊天主題：${t}`),
      ...rotateDaily(coach.scenarios, today, 2).map((t) => `情境角色：${t}`),
      ...rotateDaily(coach.qaTopics, today, 2).map((t) => `知識問答：${t}`),
    ];

    title = `FSI 練習包-${coach.langLabel}-${today}`;
    children.push(
      h1(`FSI 離線練習包 · ${coach.langLabel}`),
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { after: 240 },
        children: [run(`產生日期 ${today}｜教練 ${coach.name}｜目前程度 ${ilr}`, { size: 20, color: "666666" })],
      }),

      h2("一、使用方式"),
      p("1. 把這份 Word 上傳到 NotebookLM 或 Gemini（或直接貼上內文）。"),
      p("2. 對 AI 說：「請依這份練習包的〈教官指令〉帶我練習」。"),
      p("3. 練習結束時，請 AI 依〈成果報告格式〉輸出報告，整段複製。"),
      p(`4. 回到語言教練網站的「離線練習」頁貼上報告，練習時間、單字、改錯就會自動入庫。`),

      h2("二、教官指令（請 AI 扮演 FSI 教官）"),
      p(`你是採用 FSI（美國國務院外交學院）聽說教學法的${coach.langLabel}教官。學生的母語是臺灣華語（繁體中文），目前程度 ${ilr}。所有解說一律用繁體中文；教學時多做「華語 ↔ ${coach.langLabel}」對比，凡是華語所沒有的概念（冠詞、格變化、時態一致、變位等）要特別放慢、多輪 drill。`, { after: 120 }),
      p(`學生的題材偏好：宗教、神話、宗教學為主軸，輔以人文。`, { after: 120 }),
      ...(ZH_L1_NOTES[language] ? [p(`本語言對華語母語者的重點：${ZH_L1_NOTES[language]}`, { after: 120 })] : []),
      p("每課訓練循環（FSI 原則：先練後講、精熟優先於進度）：", { bold: true }),
      bullet("① 基礎對話 Basic Dialogue：寫一段 6–10 輪的情境對話（題材從〈本課素材〉的主題挑，盡量用到複習單字），先讓學生整段看懂，再用 backward build-up（從句尾往前逐段加長）帶學生逐句背誦。"),
      bullet("② 替換練習 Substitution drill：取本課句型，每次給一個替換詞（cue），學生把句子換槽位重說整句；一次一題，答完才給正解。至少 8 題。"),
      bullet("③ 轉換練習 Transformation drill：肯定↔否定、直述↔疑問、換時態／換人稱（依本語言文法特性挑 2–3 種轉換規則）。至少 8 題。"),
      bullet("④ 擴展練習 Expansion drill：從單詞出發逐步擴成完整句。3–5 組。"),
      bullet("⑤ 問答應答 Response drill：用本課句型快問快答，學生須立即回答。至少 6 題。"),
      bullet("⑥ 文法短講：drill 全部做完後，才用繁體中文講解剛才練的文法點（先練後講是 FSI 原則），並與華語對比。"),
      bullet("⑦ 引導式會話 Guided conversation：與學生做只限用本課句型的半自由對話 6–10 輪，學生每說錯一句就記下來（進報告的「改錯紀錄」）。"),
      bullet("⑧ 寫作應用：請學生用本課句型寫 3–5 句短文，逐句批改。"),
      ...(coach.voiceless
        ? [p(`※ ${coach.langLabel}是古典語言、以閱讀為目標：不要求口說，把上述 drill 改成「朗讀＋筆譯＋詞形判析」形式（背誦改為抄寫與默寫，會話改為問答式筆談），成果報告的技能時間以閱讀／寫作為主。`, { after: 120 })]
        : []),
      p("節奏原則：一次只出一題，等學生回答後再對答案；學生答錯先讓他再試一次，仍錯才給正解並要求複誦；精熟優先於進度，寧可課程沒跑完也不要跳過沒練熟的句型。", { after: 120 }),
      p("練習結束時：務必依〈四、成果報告格式〉原樣輸出報告（標題與欄位名照抄、內容如實填寫），讓學生帶回網站入庫。", { bold: true }),

      h2("三、本課素材"),
      ...(hl.weaknesses?.length
        ? [p("學生目前的弱項（drill 選材優先攻這些）：", { bold: true }), ...hl.weaknesses.map(bullet)]
        : []),
      ...(hl.strengths?.length ? [p("學生的強項：", { bold: true }), ...hl.strengths.map(bullet)] : []),
      p(`到期複習單字（${(due ?? []).length} 個，格式：單字｜讀音｜釋義｜例句）——請在對話與 drill 中盡量用到，並在「複習結果」回報對錯：`, { bold: true }),
      ...(due ?? []).map((w: any) => p(wordLine(w), { size: 20, indent: true, after: 40 })),
      ...(!due?.length ? [p("（目前沒有到期單字）", { color: "888888", indent: true })] : []),
      p(`建議新字（${newWords.length} 個）——可挑入本課教學，學生學會的列進報告「新學單字」：`, { bold: true }),
      ...newWords.map((w: any) => p(wordLine(w), { size: 20, indent: true, after: 40 })),
      ...(!newWords.length ? [p("（字庫暫無建議新字，由教官自行依程度挑選）", { color: "888888", indent: true })] : []),
      ...(topics.length ? [p("今日建議主題（擇一或混用）：", { bold: true }), ...topics.map(bullet)] : []),

      h2("四、成果報告格式（練習結束時由 AI 原樣填寫）"),
      p("請把下列模板原樣複製、如實填寫（欄位名不可改、單字行用「｜」分隔）；「新學單字」只列這次真正教過且學生答對過的字。", { after: 120 }),
      ...reportTemplate(coach.langLabel).split("\n").map((line) => p(line, { mono: true, size: 20, after: 20 }))
    );
  } else {
    // ── kind=progress：學習進度報告 ───────────────────────────────────
    const from30 = tzDaysAgo(29);
    const [{ data: acts }, { data: journals }, { data: levels }, vocabAllR, vocabDueR] = await Promise.all([
      supabase.from("lang_activity").select("activity_date, skill, minutes").eq("user_id", user.id).eq("language", language).gte("activity_date", from30),
      supabase.from("lang_journal").select("journal_date, summary, direction, minutes").eq("user_id", user.id).eq("language", language).order("journal_date", { ascending: false }).limit(14),
      supabase.from("lang_level_history").select("level, assessed_at, method").eq("user_id", user.id).eq("language", language).order("assessed_at", { ascending: true }),
      supabase.from("lang_vocab").select("mastery_level", { count: "exact" }).eq("user_id", user.id).eq("language", language),
      supabase.from("lang_vocab").select("id", { count: "exact", head: true }).eq("user_id", user.id).eq("language", language).lte("next_review", today),
    ]);

    const bySkill: Record<string, number> = {};
    for (const a of acts ?? []) bySkill[a.skill] = (bySkill[a.skill] || 0) + Number(a.minutes);
    const skillZh: Record<string, string> = { listening: "聽力", speaking: "口說", reading: "閱讀", writing: "寫作" };
    const mastered = (vocabAllR.data ?? []).filter((v: any) => (v.mastery_level || 0) >= 3).length;

    title = `學習進度報告-${coach.langLabel}-${today}`;
    children.push(
      h1(`學習進度報告 · ${coach.langLabel}`),
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { after: 240 },
        children: [run(`產生日期 ${today}｜教練 ${coach.name}`, { size: 20, color: "666666" })],
      }),
      h2("一、總覽"),
      bullet(`目前程度：${ilr}`),
      bullet(`連續學習：${prog?.streak_days ?? 0} 天｜累計 ${Math.round(prog?.total_minutes ?? 0)} 分鐘`),
      bullet(`單字庫：${vocabAllR.count ?? 0} 字（已精熟 ${mastered}）｜今日待複習 ${vocabDueR.count ?? 0} 字`),
      h2("二、近 30 天技能時間"),
      ...Object.entries(bySkill).map(([k, v]) => bullet(`${skillZh[k] ?? k}：${Math.round(v)} 分鐘`)),
      ...(!Object.keys(bySkill).length ? [p("（近 30 天沒有練習紀錄）", { color: "888888" })] : []),
      ...(levels?.length ? [h2("三、等級歷史"), ...levels.map((l: any) => bullet(`${String(l.assessed_at).slice(0, 10)}：${l.level}（${l.method ?? "評估"}）`))] : []),
      h2("四、教練的長期了解"),
      p(mem?.memory || "（尚未建立長期記憶）"),
      ...(hl.strengths?.length ? [p("強項：", { bold: true }), ...hl.strengths.map(bullet)] : []),
      ...(hl.weaknesses?.length ? [p("弱項：", { bold: true }), ...hl.weaknesses.map(bullet)] : []),
      ...(journals?.length
        ? [h2("五、近期教練日誌"), ...(journals ?? []).flatMap((j: any) => [
            p(`${j.journal_date}（${Math.round(j.minutes || 0)} 分）`, { bold: true, after: 40 }),
            p(`${j.summary}${j.direction ? `　→ ${j.direction}` : ""}`, { size: 20, indent: true }),
          ])]
        : [])
    );
  }

  const doc = new Document({
    creator: "AI 語言教練",
    title,
    styles: { default: { document: { run: { font: { name: EN, eastAsia: CJK }, size: 22 } } } },
    sections: [{
      properties: {
        page: {
          size: { width: convertMillimetersToTwip(210), height: convertMillimetersToTwip(297) },
          margin: {
            top: convertMillimetersToTwip(22), bottom: convertMillimetersToTwip(22),
            left: convertMillimetersToTwip(22), right: convertMillimetersToTwip(22),
          },
        },
      },
      children,
    }],
  });

  const buffer = await Packer.toBuffer(doc);
  setHeader(event, "Content-Type", "application/vnd.openxmlformats-officedocument.wordprocessingml.document");
  setHeader(event, "Content-Disposition", `attachment; filename*=UTF-8''${encodeURIComponent(`${title}.docx`)}`);
  setHeader(event, "Cache-Control", "no-store");
  return buffer;
});
