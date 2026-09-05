"""quality_sweep.fetch_chunks 的分頁。兩次真實事故各釘一條。

事故一（2026-09-04）：用 `limit=10000` 分頁，但 PostgREST 有 max-rows 硬上限
（本專案是 1000），於是伺服器永遠只回 1000 列，而終止條件 `len(c) < step` 在
第一頁就成立 —— 全館 255,951 個 chunk 只掃到前 1000 個。其餘每一本都變成
n==0，被 harvest_signals 判成 blank/no_toc/tiny 全 100%，一律 15 分並掛
BLANK_BODY+NO_TOC+OVER_FRAGMENTED。sweep 正常結束、寫回分數、exit 0，只是
分數全錯。→ 終止條件必須跟伺服器上限脫鉤，只有「這一頁回 0 列」才算掃完。

事故二（2026-09-05）：改用 OFFSET 分頁之後，重分段把 chunk 從 25.6 萬變成
45.2 萬，翻到 offset=272000 就開始回 500 Internal Server Error。OFFSET 在
Postgres 是「先數過前 N 列再丟掉」，深度越深越慢，那是伺服器端逾時，重試再多
次都一樣。→ 必須用 keyset（id > 上一頁最後一筆），每頁都走索引。
"""
import quality_sweep


class FakeResponse:
    def __init__(self, rows):
        self._rows = rows

    def raise_for_status(self):
        pass

    def json(self):
        return self._rows


def make_fake_get(total_rows, server_cap, calls):
    """模擬 PostgREST：只認 keyset 游標，且不管你要多少最多給 server_cap 列。

    刻意**不支援 offset** —— 用 offset 就會 KeyError，等於把「別再退回 OFFSET
    分頁」這件事變成測試失敗而不是線上 500。
    """
    rows = [{"id": f"{i:08d}-0000-4000-8000-000000000000",
             "ebook_id": f"book-{i // 10}", "char_count": 500,
             "chapter_path": "第一章", "chunk_type": "chapter",
             "content": "x", "source_lang": None} for i in range(total_rows)]

    def fake_get(url, **kwargs):
        assert "offset=" not in url, "不可以用 OFFSET 分頁（深度一深就伺服器逾時）"
        limit = int(url.split("limit=")[1].split("&")[0])
        if "id=gt." in url:
            cursor = url.split("id=gt.")[1].split("&")[0]
            # 游標走到最後一筆之後就沒有下一頁了 —— 回空陣列，不是拋例外
            start = next((i for i, r in enumerate(rows) if r["id"] > cursor), len(rows))
        else:
            start, cursor = 0, None
        calls.append((cursor, limit))
        return FakeResponse(rows[start:start + min(limit, server_cap)])

    return fake_get


def test_pages_past_the_server_row_cap(monkeypatch):
    # 2500 列、伺服器每次最多給 1000：必須全部拿到，不能第一頁就停。
    calls = []
    monkeypatch.setattr(quality_sweep.requests, "get",
                        make_fake_get(2500, 1000, calls))
    ids = {f"book-{i}" for i in range(250)}
    buckets = quality_sweep.fetch_chunks(
        {"SUPABASE_URL": "http://x", "SUPABASE_SERVICE_ROLE_KEY": "k"},
        ids, use_rest=True)
    assert sum(len(v) for v in buckets.values()) == 2500
    assert len(calls) >= 3, f"只發了 {len(calls)} 次請求，第一頁就停了"


def test_uses_keyset_not_offset(monkeypatch):
    """游標必須是前一頁的最後一個 id，而且第一頁不帶游標。"""
    calls = []
    monkeypatch.setattr(quality_sweep.requests, "get",
                        make_fake_get(2500, 1000, calls))
    quality_sweep.fetch_chunks(
        {"SUPABASE_URL": "http://x", "SUPABASE_SERVICE_ROLE_KEY": "k"},
        {f"book-{i}" for i in range(250)}, use_rest=True)
    assert calls[0][0] is None, "第一頁不該帶游標"
    cursors = [c for c, _ in calls[1:] if c]
    assert cursors == sorted(cursors), "游標必須單調遞增"
    assert cursors[0] == "00000999-0000-4000-8000-000000000000"


def test_stops_on_empty_page(monkeypatch):
    # 掃完就該停，不可以無限打下去。
    calls = []
    monkeypatch.setattr(quality_sweep.requests, "get",
                        make_fake_get(1000, 1000, calls))
    buckets = quality_sweep.fetch_chunks(
        {"SUPABASE_URL": "http://x", "SUPABASE_SERVICE_ROLE_KEY": "k"},
        {"book-0"}, use_rest=True)
    assert len(buckets["book-0"]) == 10
    assert len(calls) == 2, "應該是「滿的一頁 + 空的一頁」就收工"


def test_empty_bucket_still_means_no_content():
    # 修好分頁之後，n==0 就真的代表這本沒 chunk，該扣的還是要扣。
    s = quality_sweep.harvest_signals({"standardized_at": "2026-01-01"}, [])
    assert s.n_chunks == 0
    assert s.blank_rate == 1.0
