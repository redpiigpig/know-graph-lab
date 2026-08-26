#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Translate selected foreign-language dadaodao transcripts to zh-TW.

Source: ``dadaodao-fulltext/<relative material path>.txt``
Output: ``dadaodao-fulltext/<relative material path>.zh.txt``

Each segment is atomically checkpointed under scripts/state before the next
model call.  The public .zh.txt object is uploaded only after every segment
passes validation, so material-text.get.ts can never expose a partial book.

Examples:
  python -X utf8 scripts/dadaodao_translate.py --discover
  python -X utf8 scripts/dadaodao_translate.py --engine nvidia --limit-files 1
  python -X utf8 scripts/dadaodao_translate.py --engine nvidia
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import time
from pathlib import Path

import boto3
import requests


ROOT = Path(__file__).resolve().parents[1]
STATE_DIR = ROOT / "scripts" / "state" / "dadaodao_translate"
TEXT_PREFIX = "dadaodao-fulltext/"
NVIDIA_URL = "https://integrate.api.nvidia.com/v1/chat/completions"
NVIDIA_MODEL = "nvidia/nemotron-3-super-120b-a12b"
GEMINI_MODEL = "gemini-2.5-flash"
SONNET_MODEL = "claude-sonnet-4-6"

# Deliberately narrow first batch requested for this project.  Matching is by
# case-insensitive basename substring, while --key can select another object.
PRIORITY_NAMES = (
    "Buddhist_Nuns_Ordination_in_the_Mulasarv",
    "Taiwan’s Buddhist nuns Ch6",
    "Taiwan's Buddhist nuns Ch6",
    "Gender_and_Buddhism_in_Taiwan",
    "Master Yinshun and the Pure Land Thought",
    "Writing History of Buddhist Thought in the Twentieth Century",
    "太虛大師對越南佛教的影響",
    "台灣人間佛教的保環注意",
    "Buddhist Modernism and Animal Welfare",
)

PROMPT = """你是臺灣佛教研究的學術翻譯者。請把下列外文原文完整翻成臺灣繁體中文。

規則：
1. 不摘要、不刪節、不評論，不補寫原文沒有的內容。
2. 使用繁體中文及臺灣學術用語；Buddhism=佛教、bhikṣuṇī=比丘尼、Vinaya=律／律藏、ordination=受戒、Humanistic Buddhism=人間佛教、Yinshun=印順、Taixu=太虛。
3. 保留標題層級、段落、頁碼、引文、註腳號、網址與書目資訊。人名第一次出現可保留外文於括號。
4. 僅輸出譯文，不要 markdown 圍欄或前言。

原文：
{source}
"""


def load_env() -> dict[str, str]:
    env = dict(os.environ)
    for line in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
        if line and not line.lstrip().startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            env.setdefault(k.strip(), v.strip().strip('"').strip("'"))
    return env


ENV = load_env()
s3 = boto3.client(
    "s3", region_name="auto", endpoint_url=ENV["R2_ENDPOINT"],
    aws_access_key_id=ENV["R2_ACCESS_KEY"],
    aws_secret_access_key=ENV["R2_SECRET_KEY"],
)
BUCKET = ENV["R2_BUCKET"]


def keys_for(prefix: str = TEXT_PREFIX) -> list[str]:
    out: list[str] = []
    token = None
    while True:
        kw = {"Bucket": BUCKET, "Prefix": prefix}
        if token:
            kw["ContinuationToken"] = token
        page = s3.list_objects_v2(**kw)
        out.extend(x["Key"] for x in page.get("Contents", []))
        if not page.get("IsTruncated"):
            return out
        token = page["NextContinuationToken"]


def priority_source_keys() -> list[str]:
    needles = tuple(x.casefold() for x in PRIORITY_NAMES)
    return sorted(k for k in keys_for() if k.endswith(".txt")
                  and not k.endswith(".zh.txt")
                  and any(n in Path(k).name.casefold() for n in needles))


def get_text(key: str) -> str:
    body = s3.get_object(Bucket=BUCKET, Key=key)["Body"].read()
    return body.decode("utf-8-sig").strip()


def exists(key: str) -> bool:
    try:
        s3.head_object(Bucket=BUCKET, Key=key)
        return True
    except Exception:
        return False


def source_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def split_segments(text: str, max_chars: int = 6000) -> list[str]:
    """Pack paragraph/line blocks without losing or reordering source text."""
    blocks = re.split(r"(\n\s*\n)", text)
    units: list[str] = []
    for block in blocks:
        if not block:
            continue
        if len(block) <= max_chars:
            units.append(block)
        else:
            # PDF extraction sometimes has no blank lines. Split on line
            # boundaries, then as a final fallback at a character boundary.
            lines = block.splitlines(keepends=True) or [block]
            for line in lines:
                rest = line
                while len(rest) > max_chars:
                    # Prefer a linguistic boundary so neither source words nor
                    # hyphen-less PDF tokens are cut across model calls.
                    cut = max(rest.rfind("\n", 0, max_chars + 1),
                              rest.rfind(". ", 0, max_chars + 1),
                              rest.rfind("。", 0, max_chars + 1),
                              rest.rfind(" ", 0, max_chars + 1))
                    if cut < max_chars // 2:
                        cut = max_chars
                    elif rest[cut:cut + 2] == ". ":
                        cut += 1
                    units.append(rest[:cut])
                    rest = rest[cut:].lstrip()
                if rest:
                    units.append(rest)
    packed: list[str] = []
    cur = ""
    for unit in units:
        if cur and len(cur) + len(unit) > max_chars:
            packed.append(cur.strip())
            cur = unit
        else:
            cur += unit
    if cur.strip():
        packed.append(cur.strip())
    return packed


def checkpoint_path(key: str) -> Path:
    digest = hashlib.sha256(key.encode("utf-8")).hexdigest()[:16]
    return STATE_DIR / f"{digest}.json"


def load_checkpoint(key: str, text: str, segments: list[str]) -> dict:
    path = checkpoint_path(key)
    expected = source_hash(text)
    try:
        state = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        state = {}
    if state.get("key") != key or state.get("source_sha256") != expected \
            or state.get("segment_count") != len(segments):
        state = {
            "version": 1, "key": key, "source_sha256": expected,
            "source_chars": len(text), "segment_count": len(segments),
            "translations": {}, "engines": {}, "complete": False,
        }
    return state


def save_checkpoint(state: dict) -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    path = checkpoint_path(state["key"])
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(tmp, path)


def nvidia_keys() -> list[str]:
    vals = []
    for i in range(1, 11):
        v = ENV.get(f"NVIDIA_API_Key_{i}") or ENV.get(f"NVIDIA_API_KEY_{i}")
        if v:
            vals.append(v)
    return vals


def gemini_keys() -> list[str]:
    vals = []
    for i in range(1, 11):
        v = ENV.get(f"Gemini_API_Key_{i}") or ENV.get(f"GEMINI_API_KEY_{i}")
        if v:
            vals.append(v)
    return vals


def translate_nvidia(source: str, slot: int) -> str:
    keys = nvidia_keys()
    if slot < 1 or slot > len(keys):
        raise RuntimeError(f"NVIDIA slot {slot} unavailable ({len(keys)} keys)")
    r = requests.post(
        NVIDIA_URL,
        headers={"Authorization": f"Bearer {keys[slot - 1]}",
                 "Content-Type": "application/json"},
        json={"model": NVIDIA_MODEL, "messages": [
            {"role": "user", "content": PROMPT.format(source=source)}],
              "temperature": 0.1, "max_tokens": 16384, "stream": False},
        timeout=600,
    )
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"].strip()


def translate_gemini(source: str, slot: int) -> str:
    keys = gemini_keys()
    if slot < 1 or slot > len(keys):
        raise RuntimeError(f"Gemini slot {slot} unavailable ({len(keys)} keys)")
    from google import genai
    # Keep a strong reference for the duration of the request. Constructing the
    # client inline lets its finalizer close the underlying httpx session while
    # generate_content is still running in some google-genai SDK versions.
    client = genai.Client(api_key=keys[slot - 1])
    response = client.models.generate_content(
        model=GEMINI_MODEL, contents=PROMPT.format(source=source))
    return (response.text or "").strip()


def translate_sonnet(source: str) -> str:
    # Reuse the project's OAuth refresh/client implementation instead of
    # duplicating credential mutation in two long-running processes.
    from dadaodao_fulltext import anthropic_client
    response = anthropic_client().messages.create(
        model=SONNET_MODEL, max_tokens=16000,
        messages=[{"role": "user", "content": PROMPT.format(source=source)}],
    )
    return "".join(block.text for block in response.content
                   if getattr(block, "type", "") == "text").strip()


def validate_translation(source: str, translated: str) -> None:
    if not translated or len(translated) < max(30, len(source) * 0.12):
        raise ValueError("translation is empty or suspiciously short")
    if translated.startswith("```") or "我無法" in translated[:100]:
        raise ValueError("model returned wrapper/refusal instead of translation")
    cjk = len(re.findall(r"[\u3400-\u9fff]", translated))
    if len(source) > 300 and cjk < 30:
        raise ValueError("translation does not contain enough Chinese text")
    # A high concentration of simplified-only forms usually means the model
    # ignored zh-TW. A handful can legitimately occur in quoted names.
    simp = len(re.findall(r"[这为与从东丝两严丧个丰临义乌乐乔习乡书买乱争于亏云亚产亩亲亿仅仆仓仪们价众优会伞伟传伤伦伪体余佣侠侣侥侧侦儿党关兴养兽冈册写军农冲决况冻净凉减凤凭凯击划刘则刚创删别剂劳势区医华协单卖卢卫却厅历厉压厌县叁发变叙叶号叹吗吕听启员呐呕咏咸响哑哟团园围国图圆圣场坏块坚坛坝坞坟坠垄垅垒垦垫尘墙壮声壶处备复够头夹夺奋奖奥妇妈妆孙宁宝实宠审宪宫宽宾寻导寿将层屉届属岁岂岗岛岭岳峡币帅师帐帘干并广庄庆庐库应庙庞废开异弃张弥弯弹强归当录彻径忆忧怀态总恋恒恳恶惊惧惨惯戏户执扩扫扬扰抚抛护报拟拢拣拥择挂挚挛换据掳掴掷掺揽搀携摄摆摇摊撑敌敛数斋斗断无旧时旷显晋晓暂术朴机杀杂权条来杨杰极构枪柜标栈栋栏树样档桥检楼欢欧歼残殴毁毕毙气汇汉汤沟没沧沪泞泪泻泽洁浅浆浇测济浑浓涛润涧涨渐渊渔温湾湿溃溅滚满滤滥滨滩潜澜灭灯灵灾灿炉炼烂点炼热爱爷牍状犹独狭狮奖玛环现电画畅疗疯痒皱盘着睁瞒矫矿码砖础硕确碍礼祷离秃种积称税稳窍窝窥竞笔笼签简粮紧纠红纤约级纪纬纯纲纳纵纷纸纹纺线练组细织终经结绕绘给络绝统绣继绩绪续罚罗罢羁羡翘耸聋职联聪肃肠肤肿胀胁胆胜胶脉脏脑脚脱脸腊腻腾舆舰舱艺节芜苇苏范茧荐药获莲莹营萧萨蓝虑虚虫虽虾蚁蚂蛮蜕补衬袄袭装裤见观规觉览触誉计订认讥讨让训议讯记讲许论讼设访证评识诈诉词译试诗诚话诞询该详语误说请诸诺谋谓谬谢谣贝负贡财责贤败账货质贩贪贫贯贵贷贸费贺贼贾赏赔赖赚赛赠赵赶趋跃践踪车轨轩转轮软轰轻载辆辈辉输辖辙边辽达迁过迈运还进远违连迟适选递逻遗邮邻郑释里鉴针钓钞钟钢钥钦钱钳钻铁铃铅铠铜铭银铺链销锁锅锋锐错锡锦键锻镇镜长门闪闭问闯闲间闷闸闹闻阁阅阐队阳阴阵阶际陆陈险随隐难雏雾静页顶项顺须顾顿颁颂预领颇颈颗题颜额风飞饥饭饮饲饼馆驱马驳驴驶驾骂骄验骑骗骤鱼鸟鸡鸣鸥鸭鸿鹏鹰麦黄齐齿龄龙龟]", translated))
    if cjk and simp > max(12, cjk * 0.025):
        raise ValueError(f"too many simplified-only characters ({simp}/{cjk})")


def translate_document(key: str, engine: str, slot: int, max_chars: int,
                       pace: float, max_segments: int = 0,
                       attempts: int = 12) -> tuple[int, int, str]:
    output_key = key[:-4] + ".zh.txt"
    if exists(output_key):
        print(f"SKIP published: {output_key}", flush=True)
        return 0, 0, output_key
    text = get_text(key)
    segments = split_segments(text, max_chars)
    state = load_checkpoint(key, text, segments)
    completed_now = 0
    for i, source in enumerate(segments):
        skey = str(i)
        if state["translations"].get(skey):
            continue
        if max_segments and completed_now >= max_segments:
            break
        for attempt in range(1, attempts + 1):
            try:
                if engine == "nvidia":
                    translated = translate_nvidia(source, slot)
                elif engine == "gemini":
                    translated = translate_gemini(source, slot)
                else:
                    translated = translate_sonnet(source)
                validate_translation(source, translated)
                break
            except Exception as exc:
                message = str(exc).lower()
                # A per-day account quota cannot recover during a 20/40-second
                # retry loop. Fail fast so an operator can lease another lane;
                # checkpoints make that switch lossless.
                if "perday" in message or "requestsperday" in message \
                        or "generate_content_free_tier_requests" in message \
                        or "credits are depleted" in message:
                    save_checkpoint(state)
                    raise
                if attempt == attempts:
                    save_checkpoint(state)
                    raise
                wait = min(60, 15 * attempt)
                print(f"  retry {attempt}/{attempts} in {wait}s: {type(exc).__name__}: {exc}", flush=True)
                time.sleep(wait)
        state["translations"][skey] = translated
        state["engines"][skey] = f"{engine}-{slot}"
        state["updated_at"] = time.strftime("%Y-%m-%dT%H:%M:%S%z")
        save_checkpoint(state)
        completed_now += 1
        print(f"  segment {i + 1}/{len(segments)}: {len(source)} -> {len(translated)} chars", flush=True)
        time.sleep(pace)
    if len(state["translations"]) != len(segments):
        return completed_now, len(segments), output_key
    final = "\n\n".join(state["translations"][str(i)].strip()
                          for i in range(len(segments))).strip() + "\n"
    validate_translation(text, final)
    s3.put_object(Bucket=BUCKET, Key=output_key, Body=final.encode("utf-8"),
                  ContentType="text/plain; charset=utf-8",
                  Metadata={"source-sha256": state["source_sha256"],
                            "translation-engine": f"{engine}-{slot}"})
    state.update({"complete": True, "output_key": output_key,
                  "translated_chars": len(final), "published_at":
                  time.strftime("%Y-%m-%dT%H:%M:%S%z")})
    save_checkpoint(state)
    print(f"PUBLISHED {output_key} ({len(final)} chars, {len(segments)} segments)", flush=True)
    return completed_now, len(segments), output_key


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--discover", action="store_true")
    ap.add_argument("--key", action="append", default=[],
                    help="exact dadaodao-fulltext/...txt key; repeatable")
    ap.add_argument("--engine", choices=("nvidia", "gemini", "sonnet"),
                    default="nvidia")
    ap.add_argument("--slot", type=int, default=4,
                    help="dedicated provider key slot (claim matching lane first)")
    ap.add_argument("--limit-files", type=int, default=0)
    ap.add_argument("--max-segments", type=int, default=0,
                    help="checkpoint smoke test; 0 means finish each file")
    ap.add_argument("--max-chars", type=int, default=6000)
    ap.add_argument("--pace", type=float, default=7.0)
    ap.add_argument("--attempts", type=int, default=12,
                    help="bounded retries per segment for transient 503/network errors")
    args = ap.parse_args()
    keys = args.key or priority_source_keys()
    if args.discover:
        for key in keys:
            print(key)
        print(f"TOTAL {len(keys)}")
        return
    if args.limit_files:
        keys = keys[:args.limit_files]
    if not keys:
        raise SystemExit("No matching source transcripts found")
    failed = 0
    for key in keys:
        try:
            print(f"\n=== {key} ===", flush=True)
            translate_document(key, args.engine, args.slot, args.max_chars,
                               args.pace, args.max_segments, args.attempts)
        except Exception as exc:
            failed += 1
            print(f"FAILED {key}: {type(exc).__name__}: {exc}", flush=True)
    if failed:
        raise SystemExit(f"{failed}/{len(keys)} files failed; checkpoints preserved")


if __name__ == "__main__":
    main()
