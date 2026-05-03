"""
建立 writing_projects + video_transcripts 資料表，並插入千面上帝計畫。
使用 Supabase Management API（需要 SUPABASE_ACCESS_TOKEN）。
"""
import os, sys, requests
from pathlib import Path

# 從 .env 讀取設定
env_path = Path(__file__).parent.parent / ".env"
cfg = {}
for line in env_path.read_text(encoding="utf-8").splitlines():
    if "=" in line and not line.startswith("#"):
        k, _, v = line.partition("=")
        cfg[k.strip()] = v.strip().strip('"')

SUPABASE_URL        = cfg["SUPABASE_URL"]               # https://xxx.supabase.co
ACCESS_TOKEN        = cfg["SUPABASE_ACCESS_TOKEN"]       # sbp_...
SERVICE_ROLE_KEY    = cfg["SUPABASE_SERVICE_ROLE_KEY"]

# 專案 ref = URL 中的子域名
PROJECT_REF = SUPABASE_URL.replace("https://", "").split(".")[0]

SQL = """
CREATE TABLE IF NOT EXISTS writing_projects (
  id          UUID        DEFAULT gen_random_uuid() PRIMARY KEY,
  slug        TEXT        UNIQUE NOT NULL,
  title       TEXT        NOT NULL,
  description TEXT,
  emoji       TEXT        DEFAULT '📝',
  created_at  TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS video_transcripts (
  id           UUID        DEFAULT gen_random_uuid() PRIMARY KEY,
  project_slug TEXT        NOT NULL REFERENCES writing_projects(slug) ON DELETE CASCADE,
  episode      INTEGER     NOT NULL,
  title        TEXT        NOT NULL,
  content      TEXT        NOT NULL,
  video_date   TEXT,
  youtube_id   TEXT,
  created_at   TIMESTAMPTZ DEFAULT now(),
  UNIQUE(project_slug, episode)
);

ALTER TABLE writing_projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE video_transcripts ENABLE ROW LEVEL SECURITY;

DO $$ BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename='writing_projects' AND policyname='authenticated read writing_projects') THEN
    CREATE POLICY "authenticated read writing_projects" ON writing_projects FOR SELECT TO authenticated USING (true);
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename='video_transcripts' AND policyname='authenticated read video_transcripts') THEN
    CREATE POLICY "authenticated read video_transcripts" ON video_transcripts FOR SELECT TO authenticated USING (true);
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename='writing_projects' AND policyname='service insert writing_projects') THEN
    CREATE POLICY "service insert writing_projects" ON writing_projects FOR INSERT TO service_role WITH CHECK (true);
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename='video_transcripts' AND policyname='service insert video_transcripts') THEN
    CREATE POLICY "service insert video_transcripts" ON video_transcripts FOR INSERT TO service_role WITH CHECK (true);
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename='video_transcripts' AND policyname='service upsert video_transcripts') THEN
    CREATE POLICY "service upsert video_transcripts" ON video_transcripts FOR UPDATE TO service_role USING (true);
  END IF;
END $$;

INSERT INTO writing_projects (slug, title, description, emoji)
VALUES ('qiangmian', '千面上帝', '探討世界宗教中神明概念的多元面貌，橫跨印度教、佛教、基督宗教、伊斯蘭教等傳統', '🌐')
ON CONFLICT (slug) DO NOTHING;
"""

def run_sql(sql: str):
    url = f"https://api.supabase.com/v1/projects/{PROJECT_REF}/database/query"
    resp = requests.post(url, json={"query": sql}, headers={
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json",
    })
    if resp.status_code in (200, 201):
        print(f"OK: SQL executed ({resp.status_code})")
    else:
        print(f"FAIL {resp.status_code}: {resp.text}")
        sys.exit(1)

def insert_transcript(episode: int, title: str, content: str, video_date: str = None, youtube_id: str = None):
    url = f"{SUPABASE_URL}/rest/v1/video_transcripts"
    data = {
        "project_slug": "qiangmian",
        "episode": episode,
        "title": title,
        "content": content,
    }
    if video_date:
        data["video_date"] = video_date
    if youtube_id:
        data["youtube_id"] = youtube_id

    resp = requests.post(url, json=data, headers={
        "apikey": SERVICE_ROLE_KEY,
        "Authorization": f"Bearer {SERVICE_ROLE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates",
    })
    if resp.status_code in (200, 201):
        return True
    else:
        print(f"  FAIL ep{episode}: {resp.status_code} {resp.text}")
        return False

if __name__ == "__main__":
    print("1. 建立資料表...")
    run_sql(SQL)

    print("2. 上傳現有逐字稿 txt 檔...")
    txt_dir = Path(__file__).parent.parent / "public" / "content" / "qiangmian-readings"
    txts = sorted(txt_dir.glob("*.txt"))
    if not txts:
        print("  （無 txt 檔，跳過）")
    for txt in txts:
        name = txt.stem  # e.g. "01 第一章、被拋入世界的萬物之靈"
        parts = name.split(" ", 1)
        try:
            ep = int(parts[0])
        except ValueError:
            ep = 0
        title = parts[1] if len(parts) > 1 else name
        content = txt.read_text(encoding="utf-8")
        print(f"  上傳 ep{ep:02d} {title}...")
        if insert_transcript(ep, title, content):
            print(f"  OK")

    print("\n全部完成！")
