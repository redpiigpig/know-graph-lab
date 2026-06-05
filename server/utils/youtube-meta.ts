// ============================================================================
// YouTube 影片中繼資料抓取（標題 + 時長），不需 YouTube Data API key。
//  - 標題：oEmbed（穩定、官方端點）
//  - 時長：抓 watch 頁原始 HTML 內的 "lengthSeconds":"NNN"（無 key 可得）
// 用於「只記錄觀看」的輕量路徑：貼上網址即可記下影片與時長，
// 不必跑 Gemini 多模態分析（純 fetch，本機 dev 無 AI key 也能用）。
// ============================================================================

export interface YoutubeMeta {
  videoId: string | null;
  title: string | null;
  author: string | null;
  durationSeconds: number | null; // 抓不到則 null（交由前端要求手動輸入）
}

// 從各種 YouTube 網址形式取出 11 碼 video id
export function extractYoutubeId(raw: string): string | null {
  const url = (raw || "").trim();
  if (!url) return null;
  // 直接就是 11 碼 id
  if (/^[a-zA-Z0-9_-]{11}$/.test(url)) return url;
  const patterns = [
    /[?&]v=([a-zA-Z0-9_-]{11})/,        // watch?v=ID
    /youtu\.be\/([a-zA-Z0-9_-]{11})/,    // youtu.be/ID
    /\/embed\/([a-zA-Z0-9_-]{11})/,      // /embed/ID
    /\/shorts\/([a-zA-Z0-9_-]{11})/,     // /shorts/ID
    /\/live\/([a-zA-Z0-9_-]{11})/,       // /live/ID
  ];
  for (const p of patterns) {
    const m = url.match(p);
    if (m) return m[1];
  }
  return null;
}

async function fetchTitle(videoId: string): Promise<{ title: string | null; author: string | null }> {
  try {
    const res = await fetch(
      `https://www.youtube.com/oembed?url=${encodeURIComponent("https://www.youtube.com/watch?v=" + videoId)}&format=json`,
      { headers: { "User-Agent": "Mozilla/5.0" } }
    );
    if (!res.ok) return { title: null, author: null };
    const j = (await res.json()) as { title?: string; author_name?: string };
    return { title: j.title ?? null, author: j.author_name ?? null };
  } catch {
    return { title: null, author: null };
  }
}

async function fetchDurationSeconds(videoId: string): Promise<number | null> {
  try {
    const res = await fetch(`https://www.youtube.com/watch?v=${videoId}`, {
      headers: {
        // 桌機 UA + 英文，讓回傳的是含 ytInitialPlayerResponse 的完整頁
        "User-Agent":
          "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
      },
    });
    if (!res.ok) return null;
    const html = await res.text();
    // 主要：playerResponse 內的 lengthSeconds
    const m1 = html.match(/"lengthSeconds":"(\d+)"/);
    if (m1) return Number(m1[1]);
    // 備援：approxDurationMs（毫秒）
    const m2 = html.match(/"approxDurationMs":"(\d+)"/);
    if (m2) return Math.round(Number(m2[1]) / 1000);
    return null;
  } catch {
    return null;
  }
}

// 抓 YouTube 影片標題 + 時長（皆盡力而為，抓不到回 null）
export async function fetchYoutubeMeta(url: string): Promise<YoutubeMeta> {
  const videoId = extractYoutubeId(url);
  if (!videoId) return { videoId: null, title: null, author: null, durationSeconds: null };
  const [{ title, author }, durationSeconds] = await Promise.all([
    fetchTitle(videoId),
    fetchDurationSeconds(videoId),
  ]);
  return { videoId, title, author, durationSeconds };
}
