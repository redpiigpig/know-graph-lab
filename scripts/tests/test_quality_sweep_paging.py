"""quality_sweep.fetch_chunks 的分頁終止條件。

這支測試存在的理由是一次真實事故：fetch_chunks 用 `limit=10000` 分頁，但
PostgREST 有 max-rows 硬上限（本專案是 1000），於是伺服器永遠只回 1000 列，
而終止條件 `len(c) < step` 在第一頁就成立 —— 全館 255,951 個 chunk 只掃到前
1000 個。其餘每一本書都變成 n==0，被 harvest_signals 判成 blank/no_toc/tiny
全 100%，一律 15 分並掛 BLANK_BODY+NO_TOC+OVER_FRAGMENTED。

這是「看起來像成功的失敗」：sweep 正常結束、寫回分數、exit 0，只是分數全錯。
所以終止條件必須跟伺服器上限脫鉤 —— 只有「這一頁回 0 列」才算掃完。
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
    """模擬一個「不管你要多少，最多只給 server_cap 列」的 PostgREST。"""
    rows = [{"ebook_id": f"book-{i // 10}", "char_count": 500,
             "chapter_path": "第一章", "chunk_type": "chapter",
             "content": "x", "source_lang": None} for i in range(total_rows)]

    def fake_get(url, **kwargs):
        off = int(url.split("offset=")[1].split("&")[0])
        limit = int(url.split("limit=")[1].split("&")[0])
        calls.append((off, limit))
        return FakeResponse(rows[off:off + min(limit, server_cap)])

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
