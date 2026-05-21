"""
Refactor 16 Vatican II ts files: eager `?raw` imports -> lazy textKey + loader.

Reason: 16 docs × 3 langs × avg ~50KB = ~9MB raw text eagerly imported by
data/creeds/index.ts caused Vite SSR IPC buffer overflow ("IPC connection closed").

After this refactor:
  - ts files keep only metadata; `text: ''` + `textKey: 'sc-latin'` etc.
  - Single _loaders.ts uses import.meta.glob({ eager: false }) -> lazy map
  - Detail page awaits loaders only when a version is actively displayed.
"""
import os
import re
import glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TS_DIR = os.path.join(ROOT, "data", "creeds", "ecumenical-councils")

LANG_MAP = {
    "latText": "latin",
    "enText": "english",
    "zhText": "chinese",
    "scLatin": "latin",
    "scEnglish": "english",
    "scChinese": "chinese",
}

files = sorted(glob.glob(os.path.join(TS_DIR, "vatican-ii-*.ts")))
print(f"Found {len(files)} ts files")

for path in files:
    base = os.path.basename(path)
    m = re.match(r"vatican-ii-(\d+)-(\w+)\.ts", base)
    if not m:
        print(f"  skip {base} (name pattern)")
        continue
    code_lc = m.group(2)

    with open(path, "r", encoding="utf-8") as f:
        src = f.read()

    # 1. Remove all raw text imports (with their // @ts-expect-error comments)
    src = re.sub(
        r"// @ts-expect-error[^\n]*\nimport \w+ from '\./vatican-ii/[^']+\?raw'\n",
        "",
        src,
    )

    # 2. Replace `text: <var> as string,` -> `text: '',\n      textKey: '{code}-{lang}',`
    def repl(match: re.Match) -> str:
        var = match.group(1)
        lang = LANG_MAP.get(var)
        if not lang:
            return match.group(0)
        return f"text: '',\n      textKey: '{code_lc}-{lang}',"

    new_src, n = re.subn(r"text:\s+(\w+)\s+as\s+string,", repl, src)
    print(f"  [{code_lc}] replaced {n} text refs")

    with open(path, "w", encoding="utf-8") as f:
        f.write(new_src)

print("Done.")
