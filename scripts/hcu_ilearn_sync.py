"""抓玄奘大學 I-Learn（Moodle）我修的每一門課的課程大綱與教材檔案。

用法:
    python scripts/hcu_ilearn_sync.py            # 只寫大綱 md
    python scripts/hcu_ilearn_sync.py --files    # 連教材檔案一起下載

帳密讀 .env 的 HCU_ILEARN_USER / HCU_ILEARN_PASS。
成品寫到 Drive: G:/我的雲端硬碟/玄奘/博一上/上課/<課名>/
"""
import argparse
import html
import json
import os
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path

BASE = "https://ilearn.hcu.edu.tw"
REST = BASE + "/webservice/rest/server.php"
OUT_ROOT = Path("G:/我的雲端硬碟/玄奘/博一上/上課")


def load_env(path=".env"):
    env = {}
    p = Path(path)
    if p.exists():
        for line in p.read_text(encoding="utf-8", errors="replace").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip().strip('"').strip("'")
    return env


def post(url, data):
    body = urllib.parse.urlencode(data).encode("utf-8")
    req = urllib.request.Request(url, data=body, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=90) as r:
        return json.loads(r.read().decode("utf-8"))


def get_token(user, pw):
    d = post(BASE + "/login/token.php",
             {"username": user, "password": pw, "service": "moodle_mobile_app"})
    if "token" not in d:
        sys.exit("登入失敗: " + json.dumps(d, ensure_ascii=False))
    return d["token"]


def ws(token, fn, **params):
    p = {"wstoken": token, "wsfunction": fn, "moodlewsrestformat": "json"}
    p.update(params)
    return post(REST, p)


TAG_BREAKS = re.compile(r"</(p|div|li|tr|h[1-6])>|<br\s*/?>", re.I)


def to_text(s):
    """把 Moodle 的 HTML 摘要轉成保留換行的純文字。"""
    if not s:
        return ""
    s = TAG_BREAKS.sub("\n", s)
    s = re.sub(r"<[^>]+>", "", s)
    s = html.unescape(s)
    s = re.sub(r"[ \t\u00a0]+", " ", s)
    s = re.sub(r"\n{3,}", "\n\n", s)
    return "\n".join(ln.strip() for ln in s.split("\n")).strip()


try:
    import opencc
    _CC = opencc.OpenCC("s2tw")
except Exception:
    _CC = None


def to_trad(s):
    """站上教材偶有簡體（例如康德譯文），依專案規則一律寫成繁體。"""
    return _CC.convert(s) if (_CC and s) else s


SAFE = re.compile(r'[<>:"/\\|?*]')


def safe_name(s):
    return SAFE.sub("_", s).strip().rstrip(".")[:120]


def course_title(c):
    """課程 fullname 在本站是「班級 | 課號 - 課名」重複兩次，取乾淨的課名。"""
    full = c.get("fullname", "")
    part = full.split("|")[1] if "|" in full else full
    part = part.strip()
    m = re.match(r"^(\S+)\s*-\s*(.+)$", part)
    return (m.group(1), m.group(2).strip()) if m else ("", part)


def render(course, sections):
    code, name = course_title(course)
    out = [f"# {name}", ""]
    out.append(f"- 課號：{code}")
    out.append(f"- 班級：{course.get('fullname','').split('|')[0].strip()}")
    out.append(f"- I-Learn：{BASE}/course/view.php?id={course['id']}")
    out.append("")
    for s in sections:
        title = (s.get("name") or "").strip()
        mods = s.get("modules", [])
        summary = to_text(s.get("summary"))
        if not summary and not mods and re.match(r"^(Topic \d+|新單元)$", title):
            continue  # 空的佔位單元不列
        out.append(f"## {title}")
        out.append("")
        if summary:
            out.append(summary)
            out.append("")
        for m in mods:
            label = m.get("name", "")
            url = m.get("url") or ""
            kind = m.get("modname", "")
            if kind == "url":
                # 外部連結：真正的網址藏在 contents
                ext = [c.get("fileurl") for c in m.get("contents", []) if c.get("fileurl")]
                url = ext[0] if ext else url
            out.append(f"- （{kind}）{label}" + (f" — {url}" if url else ""))
            desc = to_text(m.get("description"))
            if desc:
                out.append(f"  - {desc}")
        out.append("")
    return "\n".join(out).rstrip() + "\n"


def download_files(token, sections, dest):
    n = 0
    for s in sections:
        for m in s.get("modules", []):
            if m.get("modname") not in ("resource", "folder"):
                continue
            for c in m.get("contents", []):
                fu = c.get("fileurl")
                if not fu or c.get("type") != "file":
                    continue
                sep = "&" if "?" in fu else "?"
                url = f"{fu}{sep}token={token}"
                fname = safe_name(c.get("filename") or "file")
                target = dest / fname
                if target.exists() and target.stat().st_size == (c.get("filesize") or -1):
                    continue
                req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
                try:
                    with urllib.request.urlopen(req, timeout=180) as r:
                        target.write_bytes(r.read())
                    n += 1
                    print(f"    ↓ {fname}")
                except Exception as e:
                    print(f"    ✗ {fname}: {e}")
    return n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--files", action="store_true", help="連教材檔案一起下載")
    ap.add_argument("--out", default=str(OUT_ROOT))
    args = ap.parse_args()

    env = load_env()
    user = env.get("HCU_ILEARN_USER") or os.environ.get("HCU_ILEARN_USER")
    pw = env.get("HCU_ILEARN_PASS") or os.environ.get("HCU_ILEARN_PASS")
    if not user or not pw:
        sys.exit(".env 缺 HCU_ILEARN_USER / HCU_ILEARN_PASS")

    token = get_token(user, pw)
    info = ws(token, "core_webservice_get_site_info")
    uid = info["userid"]
    print(f"登入成功：{info.get('fullname')} (uid={uid})")

    courses = ws(token, "core_enrol_get_users_courses", userid=uid)
    root = Path(args.out)
    root.mkdir(parents=True, exist_ok=True)

    for c in courses:
        code, name = course_title(c)
        sections = ws(token, "core_course_get_contents", courseid=c["id"])
        if not isinstance(sections, list):
            print(f"  ! {name}: {sections}")
            continue
        dest = root / safe_name(name)
        dest.mkdir(parents=True, exist_ok=True)
        md = dest / "課程大綱.md"
        md.write_text(to_trad(render(c, sections)), encoding="utf-8")
        print(f"  ✓ {name} → {md}")
        if args.files:
            n = download_files(token, sections, dest)
            print(f"    教材 {n} 檔")


if __name__ == "__main__":
    main()
