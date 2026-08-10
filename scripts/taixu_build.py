"""《太虛大師全書》私人研究版匯入器。

來源是 CBETA TX 系列 TEI P5 XML（TX00–TX32，40 個 XML；20 編加編纂說明）。
本工具把同一編跨冊的 XML 合併成一個 reader ebook，保留章節樹、韻文、清單、
對話與表格，再輸出單語繁中 JSONL。使用者已聲明取得權利方授權；部署仍限於
有登入保護的私人研究站，來源與 CBETA 版本說明不可移除。

常用命令：

  python -X utf8 scripts/taixu_build.py --all
  python -X utf8 scripts/taixu_build.py --work TX0001 --inspect
  python -X utf8 scripts/taixu_build.py --all --upload
  python -X utf8 scripts/taixu_build.py --fetch --all
"""
from __future__ import annotations

import argparse
import datetime as dt
import gzip
import hashlib
import io
import json
import os
import re
import sys
from pathlib import Path
from xml.etree import ElementTree as ET

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(SCRIPT_DIR))

ENV_PATH = ROOT / ".env"
if ENV_PATH.exists():
    for line in ENV_PATH.read_text(encoding="utf-8").splitlines():
        if "=" in line and not line.strip().startswith("#"):
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))

TEI = "http://www.tei-c.org/ns/1.0"
XML = "http://www.w3.org/XML/1998/namespace"
REGISTRY_PATH = ROOT / ".claude/skills/ebook-collected-works/taixu_registry.json"
DEFAULT_SOURCE_DIR = ROOT / ".cache/taixu-tx-xml"
DEFAULT_OUTPUT_DIR = ROOT / ".cache/taixu-chunks"
RAW_URL = "https://raw.githubusercontent.com/cbeta-org/xml-p5/master/TX/{volume}/{stem}.xml"
MAX_CHARS = 12_000

BLOCK_TAGS = {
    "p", "byline", "lg", "list", "table", "sp", "dialog", "quote", "ab", "formula"
}
SKIP_TAGS = {"note", "back", "anchor", "pb"}


def _local(tag: str) -> str:
    return tag.split("}")[-1]


def load_registry() -> dict[str, dict]:
    return json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))


def _clean_prose(text: str) -> str:
    text = re.sub(r"[ \t]*\n[ \t\n]*", "", text)
    return re.sub(r"[ \t]+", " ", text).strip()


def _clean_line(text: str) -> str:
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r" *\n *", "\n", text)
    return text.strip()


def _char_map(root: ET.Element) -> dict[str, str]:
    result: dict[str, str] = {}
    for char in root.findall(f".//{{{TEI}}}char"):
        char_id = char.get(f"{{{XML}}}id")
        if not char_id:
            continue
        value = ""
        for mapping in char.findall(f"{{{TEI}}}mapping"):
            if mapping.get("type") == "unicode" and (mapping.text or "").startswith("U+"):
                try:
                    value = chr(int((mapping.text or "")[2:], 16))
                except ValueError:
                    pass
                if value:
                    break
        if not value:
            for prop in char.findall(f"{{{TEI}}}charProp"):
                local_name = prop.find(f"{{{TEI}}}localName")
                prop_value = prop.find(f"{{{TEI}}}value")
                if local_name is not None and local_name.text == "composition" and prop_value is not None:
                    value = prop_value.text or ""
                    break
        result[char_id] = value
    return result


def extract_text(
    element: ET.Element,
    *,
    char_map: dict[str, str] | None = None,
    preserve_breaks: bool = False,
) -> str:
    """Extract one TEI subtree without apparatus duplication or editorial notes."""
    char_map = char_map or {}
    tag = _local(element.tag)
    if tag in SKIP_TAGS or tag == "lb":
        return "\n" if tag == "lb" and preserve_breaks else ""
    if tag == "caesura":
        return "　"
    if tag == "g":
        ref = (element.get("ref") or "").lstrip("#")
        return element.text or char_map.get(ref, "□")
    if tag == "app":
        chosen = next((c for c in element if _local(c.tag) == "lem"), None)
        if chosen is None:
            chosen = next((c for c in element if _local(c.tag) == "rdg"), None)
        return extract_text(chosen, char_map=char_map, preserve_breaks=preserve_breaks) if chosen is not None else ""

    pieces = [element.text or ""]
    for child in element:
        pieces.append(extract_text(child, char_map=char_map, preserve_breaks=preserve_breaks))
        pieces.append(child.tail or "")
    return "".join(pieces)


def _list_block(element: ET.Element, char_map: dict[str, str]) -> str:
    rows: list[str] = []
    for item in element.iter():
        if _local(item.tag) != "item":
            continue
        text = _clean_prose(extract_text(item, char_map=char_map))
        if text:
            rows.append(f"- {text}")
    return "\n".join(rows)


def _table_block(element: ET.Element, char_map: dict[str, str]) -> str:
    rows: list[str] = []
    for row in element.iter():
        if _local(row.tag) != "row":
            continue
        cells = [
            _clean_prose(extract_text(cell, char_map=char_map))
            for cell in row
            if _local(cell.tag) == "cell"
        ]
        cells = [cell for cell in cells if cell]
        if cells:
            rows.append("　│　".join(cells))
    return "\n".join(rows)


def _verse_block(element: ET.Element, char_map: dict[str, str]) -> str:
    lines: list[str] = []
    for line in element.iter():
        if _local(line.tag) != "l":
            continue
        text = _clean_line(extract_text(line, char_map=char_map, preserve_breaks=True))
        if text:
            lines.append(text)
    if lines:
        return "\n".join(lines)
    return _clean_line(extract_text(element, char_map=char_map, preserve_breaks=True))


def _speech_block(element: ET.Element, char_map: dict[str, str]) -> str:
    speaker = ""
    parts: list[str] = []
    for child in element:
        tag = _local(child.tag)
        if tag == "speaker":
            speaker = _clean_prose(extract_text(child, char_map=char_map))
        elif tag in BLOCK_TAGS:
            text = render_block(child, char_map)
            if text:
                parts.append(text)
    body = "\n\n".join(parts) or _clean_prose(extract_text(element, char_map=char_map))
    return f"〔{speaker}〕{body}" if speaker else body


def render_block(element: ET.Element, char_map: dict[str, str]) -> str:
    tag = _local(element.tag)
    if tag == "lg":
        return _verse_block(element, char_map)
    if tag == "list":
        return _list_block(element, char_map)
    if tag == "table":
        return _table_block(element, char_map)
    if tag == "sp":
        return _speech_block(element, char_map)
    if tag == "dialog":
        speeches = [_speech_block(child, char_map) for child in element if _local(child.tag) == "sp"]
        return "\n\n".join(s for s in speeches if s)
    return _clean_prose(extract_text(element, char_map=char_map))


def div_head(element: ET.Element, char_map: dict[str, str]) -> str:
    for wanted in ("head", "mulu"):
        for child in element:
            if _local(child.tag) == wanted:
                text = _clean_prose(extract_text(child, char_map=char_map))
                if text:
                    return text
    return ""


def _split_long(text: str, limit: int) -> list[str]:
    if len(text) <= limit:
        return [text]
    pieces = re.split(r"(\n\n|\n)", text)
    units: list[str] = []
    pending = ""
    for piece in pieces:
        if not piece:
            continue
        if len(pending) + len(piece) <= limit:
            pending += piece
            continue
        if pending.strip():
            units.append(pending.strip())
        pending = piece
        while len(pending) > limit:
            cut = pending.rfind("。", 0, limit)
            cut = cut + 1 if cut > limit // 3 else limit
            units.append(pending[:cut].strip())
            pending = pending[cut:]
    if pending.strip():
        units.append(pending.strip())
    return units


def _split_blocks(blocks: list[str], limit: int = MAX_CHARS) -> list[str]:
    normalized: list[str] = []
    for block in blocks:
        normalized.extend(_split_long(block, limit))
    groups: list[str] = []
    current: list[str] = []
    size = 0
    for block in normalized:
        extra = len(block) + (2 if current else 0)
        if current and size + extra > limit:
            groups.append("\n\n".join(current))
            current = []
            size = 0
        current.append(block)
        size += len(block) + (2 if len(current) > 1 else 0)
    if current:
        groups.append("\n\n".join(current))
    return groups


def parse_tei_chunks(
    xml_text: str,
    *,
    volume: str,
    parent_volume: str,
    book_prefix: str = "",
    source_stem: str = "",
) -> tuple[str, list[dict]]:
    """Parse one TX XML file into bounded, single-language reader chunks."""
    root = ET.fromstring(xml_text)
    chars = _char_map(root)
    book = ""
    for title in root.findall(f".//{{{TEI}}}titleStmt/{{{TEI}}}title"):
        if title.get("level") == "m":
            book = _clean_prose(extract_text(title, char_map=chars))
            break
    body = root.find(f".//{{{TEI}}}body")
    if body is None:
        return book, []

    chunks: list[dict] = []
    root_label = book_prefix or volume or book

    def walk(element: ET.Element, path: list[str]) -> None:
        blocks: list[str] = []
        for child in element:
            tag = _local(child.tag)
            if tag in BLOCK_TAGS:
                text = render_block(child, chars)
                if text:
                    blocks.append(text)
        parts = _split_blocks(blocks)
        for part, content in enumerate(parts, start=1):
            leaf_path = [root_label, *path]
            if len(parts) > 1:
                leaf_path.append(f"續 {part}")
            chunks.append({
                "chunk_type": "chapter",
                "chapter_path": " · ".join(p for p in leaf_path if p),
                "volume": volume,
                "parent_volume": parent_volume,
                "format": "markdown",
                "content": content,
                "source_id": source_stem,
            })
        for child in element:
            if _local(child.tag) != "div":
                continue
            heading = div_head(child, chars)
            walk(child, path + [heading] if heading else path)

    walk(body, [])
    for index, chunk in enumerate(chunks, start=1):
        chunk["chunk_index"] = index
        chunk["page_number"] = index
    return book, chunks


def _source_path(source_dir: Path, stem: str) -> Path:
    return source_dir / f"{stem}.xml"


def fetch_missing(registry: dict[str, dict], source_dir: Path) -> None:
    import requests

    source_dir.mkdir(parents=True, exist_ok=True)
    session = requests.Session()
    headers = {"User-Agent": "know-graph-lab-private-taixu-research/1.0"}
    for meta in registry.values():
        for stem in meta["sources"]:
            destination = _source_path(source_dir, stem)
            if destination.exists() and destination.stat().st_size > 1000:
                continue
            volume = "TX00" if stem == "TX00na001" else stem[:4]
            url = RAW_URL.format(volume=volume, stem=stem)
            response = session.get(url, headers=headers, timeout=60)
            if response.status_code in (403, 429):
                raise RuntimeError(f"provider stop {response.status_code}: {url}")
            response.raise_for_status()
            temp = destination.with_suffix(".xml.part")
            temp.write_bytes(response.content)
            ET.parse(temp)
            temp.replace(destination)
            print(f"  fetched {stem}", flush=True)


def build_work(code: str, meta: dict, source_dir: Path) -> list[dict]:
    body_chunks: list[dict] = []
    xml_versions: set[str] = set()
    for stem in meta["sources"]:
        source = _source_path(source_dir, stem)
        if not source.exists():
            raise FileNotFoundError(f"missing {source}; run --fetch first")
        xml_text = source.read_text(encoding="utf-8")
        root = ET.fromstring(xml_text)
        pub_date = root.find(f".//{{{TEI}}}publicationStmt/{{{TEI}}}date")
        if pub_date is not None and (pub_date.text or "").strip():
            xml_versions.add((pub_date.text or "").strip())
        _, chunks = parse_tei_chunks(
            xml_text,
            volume=meta["title"],
            parent_volume=meta["parent_volume"],
            book_prefix=meta["title"],
            source_stem=stem,
        )
        body_chunks.extend(chunks)

    notice = (
        f"# {meta['title']}\n\n"
        "《太虛大師全書》私人研究授權版。來源：CBETA TX 系列 TEI P5 XML；"
        "底本由印順文教基金會提供。限非商業私人研究與密碼保護環境使用，"
        "不得移除來源、版本及授權說明，亦不得未經許可對外再散布。"
    )
    cover = {
        "chunk_index": 0,
        "chunk_type": "chapter",
        "page_number": 0,
        "chapter_path": meta["title"],
        "volume": meta["title"],
        "parent_volume": meta["parent_volume"],
        "format": "markdown",
        "content": notice,
        "source_id": code,
        "source_versions": sorted(xml_versions),
    }
    for index, chunk in enumerate(body_chunks, start=1):
        chunk["chunk_index"] = index
        chunk["page_number"] = index
    result = [cover, *body_chunks]
    _validate_chunks(code, result)
    return result


def _validate_chunks(code: str, chunks: list[dict]) -> None:
    if len(chunks) < 2:
        raise ValueError(f"{code}: no body chunks")
    indices = [chunk["chunk_index"] for chunk in chunks]
    if indices != list(range(len(chunks))):
        raise ValueError(f"{code}: non-contiguous chunk indices")
    for chunk in chunks:
        content = chunk.get("content", "")
        if not content.strip():
            raise ValueError(f"{code}: empty chunk {chunk['chunk_index']}")
        if len(content) > MAX_CHARS:
            raise ValueError(f"{code}: oversized chunk {chunk['chunk_index']} ({len(content)})")
        if re.search(r"</?(?:cb:)?(?:div|p|lb|note)\b", content):
            raise ValueError(f"{code}: XML leaked into chunk {chunk['chunk_index']}")


def write_jsonl(chunks: list[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for chunk in chunks:
            handle.write(json.dumps(chunk, ensure_ascii=False) + "\n")


def _r2_state(ebook_id: str, local_path: Path) -> tuple[bool | None, str | None]:
    """Return (exact_match, sha256); None means the object does not exist."""
    import boto3
    from botocore.config import Config
    from botocore.exceptions import ClientError
    import translate_ebook_to_zh as te

    r2 = boto3.client(
        "s3",
        region_name="auto",
        endpoint_url=te.se.ENV["R2_ENDPOINT"],
        aws_access_key_id=te.se.ENV["R2_ACCESS_KEY"],
        aws_secret_access_key=te.se.ENV["R2_SECRET_KEY"],
        config=Config(
            retries={"total_max_attempts": 1, "mode": "standard"},
            connect_timeout=30,
            read_timeout=300,
        ),
    )
    try:
        result = r2.get_object(
            Bucket=te.se.ENV["R2_BUCKET"],
            Key=f"ebook-chunks/{ebook_id}.jsonl.gz",
        )
    except ClientError as exc:
        response = exc.response or {}
        status = response.get("ResponseMetadata", {}).get("HTTPStatusCode")
        code = str(response.get("Error", {}).get("Code") or "")
        if status in (403, 429) or code in {"AccessDenied", "SlowDown", "429"}:
            raise RuntimeError(f"provider stop {status or code}: R2 verify") from exc
        if status == 404 or code in {"NoSuchKey", "NotFound", "404"}:
            return None, None
        raise
    remote_raw = gzip.decompress(result["Body"].read())
    local_raw = local_path.read_bytes()
    digest = hashlib.sha256(remote_raw).hexdigest()
    return hashlib.sha256(remote_raw).digest() == hashlib.sha256(local_raw).digest(), digest


def upload(meta: dict, chunks: list[dict]) -> Path:
    import boto3
    import requests
    from botocore.config import Config
    import translate_ebook_to_zh as te

    ebook_id = meta["ebook_id"]
    output = te.CHUNKS_DIR / f"{ebook_id}.jsonl"
    write_jsonl(chunks, output)
    raw = output.read_bytes()
    compressed = io.BytesIO()
    with gzip.GzipFile(fileobj=compressed, mode="wb", compresslevel=6) as handle:
        handle.write(raw)
    r2_match, r2_digest = _r2_state(ebook_id, output)
    if r2_match is True:
        print(f"  R2 already exact: {r2_digest[:16]}", flush=True)
    else:
        r2 = boto3.client(
            "s3",
            region_name="auto",
            endpoint_url=te.se.ENV["R2_ENDPOINT"],
            aws_access_key_id=te.se.ENV["R2_ACCESS_KEY"],
            aws_secret_access_key=te.se.ENV["R2_SECRET_KEY"],
            config=Config(
                retries={"total_max_attempts": 1, "mode": "standard"},
                connect_timeout=30,
                read_timeout=300,
            ),
        )
        try:
            r2.put_object(
                Bucket=te.se.ENV["R2_BUCKET"],
                Key=f"ebook-chunks/{ebook_id}.jsonl.gz",
                Body=compressed.getvalue(),
                ContentType="application/x-ndjson",
                ContentEncoding="gzip",
            )
        except Exception:
            # A write timeout is ambiguous: the server may have committed the
            # entire object before the connection closed.  This is a readback,
            # not a retry; continue only when the bytes are already exact.
            after_match, after_digest = _r2_state(ebook_id, output)
            if after_match is not True:
                raise
            print(f"  R2 timeout but exact on readback: {after_digest[:16]}", flush=True)

    now = dt.datetime.now(dt.timezone.utc).isoformat()
    total_chars = sum(len(chunk["content"]) for chunk in chunks)
    row = {
        "id": ebook_id,
        "title": meta["title"],
        "author": "太虛大師",
        "author_en": "Taixu",
        "original_title": meta["title"],
        # The ebooks table constrains file_type to the reader's supported
        # source classes.  The normalized TEI corpus is served as JSONL, but
        # behaves like the other text-first collected-works EPUB entries.
        "file_type": "epub",
        "file_path": f"太虛大師全書/{meta['parent_volume']}/{meta['title']}",
        "category": "世界宗教",
        "subcategory": "佛教",
        "display_mode": "standard",
        "collection": "collected-works",
        "translator": None,
        "publication_year": 1948,
        "chunk_count": len(chunks),
        "total_pages": len(chunks),
        "total_chars": total_chars,
        "parsed_at": now,
        "standardized_at": now,
    }
    upsert_headers = {**te.H_JSON, "Prefer": "resolution=merge-duplicates,return=representation"}
    response = requests.post(
        f"{te.URL}/rest/v1/ebooks?on_conflict=id",
        headers=upsert_headers,
        json=row,
        timeout=60,
    )
    if response.status_code in (403, 429):
        raise RuntimeError(f"provider stop {response.status_code}: ebooks upsert")
    if not response.ok:
        raise RuntimeError(f"ebooks upsert {response.status_code}: {response.text[:1000]}")
    response = requests.delete(
        f"{te.URL}/rest/v1/ebook_chunks?ebook_id=eq.{ebook_id}",
        headers=te.H_GET,
        timeout=60,
    )
    if response.status_code in (403, 429):
        raise RuntimeError(f"provider stop {response.status_code}: ebook_chunks delete")
    if not response.ok:
        raise RuntimeError(f"ebook_chunks delete {response.status_code}: {response.text[:1000]}")
    previews = [
        {
            "ebook_id": ebook_id,
            "chunk_index": chunk["chunk_index"],
            "chunk_type": chunk["chunk_type"],
            "page_number": chunk["page_number"],
            "chapter_path": chunk["chapter_path"],
            "content": chunk["content"][:200],
            "char_count": len(chunk["content"]),
        }
        for chunk in chunks
    ]
    for start in range(0, len(previews), 100):
        response = requests.post(
            f"{te.URL}/rest/v1/ebook_chunks",
            headers=te.H_JSON,
            json=previews[start:start + 100],
            timeout=60,
        )
        if response.status_code in (403, 429):
            raise RuntimeError(
                f"provider stop {response.status_code}: ebook_chunks batch {start // 100 + 1}"
            )
        if not response.ok:
            raise RuntimeError(
                f"ebook_chunks batch {start // 100 + 1} {response.status_code}: "
                f"{response.text[:1000]}"
            )
    return output


def verify_remote(meta: dict, chunks: list[dict], local_path: Path) -> None:
    """Read DB previews and the private R2 object back and compare exactly."""
    import requests
    import translate_ebook_to_zh as te

    ebook_id = meta["ebook_id"]
    response = requests.get(
        f"{te.URL}/rest/v1/ebooks",
        headers=te.H_GET,
        params={
            "id": f"eq.{ebook_id}",
            "select": "id,title,author,file_type,chunk_count,total_pages,total_chars,collection",
        },
        timeout=60,
    )
    if response.status_code in (403, 429):
        raise RuntimeError(f"provider stop {response.status_code}: ebooks verify")
    if not response.ok:
        raise RuntimeError(f"ebooks verify {response.status_code}: {response.text[:1000]}")
    rows = response.json()
    expected_chars = sum(len(chunk["content"]) for chunk in chunks)
    if len(rows) != 1:
        raise ValueError(f"{ebook_id}: expected one ebooks row, got {len(rows)}")
    row = rows[0]
    expected_row = {
        "id": ebook_id,
        "title": meta["title"],
        "author": "太虛大師",
        "file_type": "epub",
        "chunk_count": len(chunks),
        "total_pages": len(chunks),
        "total_chars": expected_chars,
        "collection": "collected-works",
    }
    if row != expected_row:
        raise ValueError(f"{ebook_id}: ebooks row mismatch: {row!r}")

    previews: list[dict] = []
    page_size = 1000
    for offset in range(0, len(chunks), page_size):
        response = requests.get(
            f"{te.URL}/rest/v1/ebook_chunks",
            headers=te.H_GET,
            params={
                "ebook_id": f"eq.{ebook_id}",
                "select": "chunk_index,char_count",
                "order": "chunk_index.asc",
                "limit": page_size,
                "offset": offset,
            },
            timeout=60,
        )
        if response.status_code in (403, 429):
            raise RuntimeError(f"provider stop {response.status_code}: ebook_chunks verify")
        if not response.ok:
            raise RuntimeError(
                f"ebook_chunks verify {response.status_code}: {response.text[:1000]}"
            )
        previews.extend(response.json())
    expected_previews = [
        {"chunk_index": chunk["chunk_index"], "char_count": len(chunk["content"])}
        for chunk in chunks
    ]
    if previews != expected_previews:
        raise ValueError(
            f"{ebook_id}: preview mismatch ({len(previews)} remote / {len(chunks)} local)"
        )

    r2_match, r2_digest = _r2_state(ebook_id, local_path)
    if r2_match is not True or not r2_digest:
        raise ValueError(f"{ebook_id}: R2 JSONL checksum mismatch")
    print(
        f"  verified {ebook_id}: DB {len(previews)} previews; "
        f"R2 sha256 {r2_digest[:16]}",
        flush=True,
    )


def verify_r2_only(meta: dict, local_path: Path) -> None:
    match, digest = _r2_state(meta["ebook_id"], local_path)
    state = "missing" if match is None else ("exact" if match else "mismatch")
    print(f"  R2 {state}: {(digest or '-')[:16]}", flush=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--work", help="TXA001 or TX0001–TX0020")
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--from-work", help="with --all, start at this registry code")
    parser.add_argument("--fetch", action="store_true")
    parser.add_argument("--inspect", action="store_true")
    parser.add_argument("--upload", action="store_true")
    parser.add_argument("--verify", action="store_true")
    parser.add_argument("--verify-r2", action="store_true")
    parser.add_argument("--source-dir", type=Path, default=DEFAULT_SOURCE_DIR)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()

    registry = load_registry()
    if args.fetch:
        fetch_missing(registry, args.source_dir)
    targets = list(registry) if args.all else ([args.work] if args.work else [])
    if args.from_work:
        if not args.all:
            raise SystemExit("--from-work requires --all")
        if args.from_work not in targets:
            raise SystemExit(f"unknown start work: {args.from_work}")
        targets = targets[targets.index(args.from_work):]
    if not targets:
        raise SystemExit("choose --all or --work TX0001")

    summary: list[dict] = []
    for code in targets:
        if code not in registry:
            raise SystemExit(f"unknown work: {code}")
        meta = registry[code]
        chunks = build_work(code, meta, args.source_dir)
        local_path = args.output_dir / f"{meta['ebook_id']}.jsonl"
        write_jsonl(chunks, local_path)
        if args.upload:
            upload_path = upload(meta, chunks)
            print(f"  uploaded {code} -> {upload_path}", flush=True)
        if args.verify:
            verify_remote(meta, chunks, local_path)
        if args.verify_r2:
            verify_r2_only(meta, local_path)
        chars = sum(len(chunk["content"]) for chunk in chunks)
        summary.append({"code": code, "chunks": len(chunks), "chars": chars, "path": str(local_path)})
        print(f"{code} {meta['title']}: {len(chunks)} chunks / {chars:,} chars", flush=True)
        if args.inspect:
            for chunk in chunks[:12]:
                print(f"  [{chunk['chunk_index']:>4}] {chunk['chapter_path']} ({len(chunk['content'])})")

    manifest = args.output_dir / "manifest.json"
    manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest.write_text(
        json.dumps(
            {
                "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
                "source": "CBETA TX TEI P5",
                "private_authorized_research": True,
                "works": summary,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"manifest: {manifest}", flush=True)


if __name__ == "__main__":
    main()
