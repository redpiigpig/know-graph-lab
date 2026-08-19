"""Safety regressions for the fail-closed Chenwei photo classifier."""

import json
from pathlib import Path

import pytest

import classify_photos as cp


def exif(**values):
    return values


@pytest.mark.parametrize(
    ("name", "metadata", "expected_kind"),
    [
        (
            "anything.jpg",
            exif(Make="Apple", Model="iPhone 11", DateTimeOriginal="2024:07:01 12:34:56"),
            "phone",
        ),
        (
            "anything.jpg",
            exif(Make="SONY", Model="DSC-HX99", DateTimeDigitized="2024:07:01 12:34:56"),
            "camera",
        ),
        (
            "anything.jpg",
            exif(Make="Canon", Model="EOS R6", DateTime="2024:07:01 12:34:56"),
            "download",
        ),
        (
            "anything.jpg",
            exif(Make="Apple", Model="", DateTimeOriginal="2024:07:01 12:34:56"),
            "download",
        ),
        (
            "anything.jpg",
            exif(Make="Apple", Model="iPhone 11", DateTimeOriginal="not a date"),
            "download",
        ),
        (
            "anything.jpg",
            exif(Make="Snowcorp", Model="Foodie", DateTimeOriginal="2024:07:01 12:34:56"),
            "download",
        ),
        (
            "anything.jpg",
            exif(Make="Apple", Model="Foodie", DateTimeOriginal="2024:07:01 12:34:56"),
            "download",
        ),
        (
            "anything.jpg",
            exif(
                Make="Apple",
                Model="iPhone 11",
                Software="Foodie",
                DateTimeOriginal="2024:07:01 12:34:56",
            ),
            "phone",
        ),
        (
            "anything.jpg",
            exif(
                Make="Apple",
                Model="iPhone 11",
                Software="Instagram",
                DateTimeDigitized="2024:07:01 12:34:56",
            ),
            "phone",
        ),
        (
            "anything.jpg",
            exif(Make="Unknown Software", Model="Filter 2", DateTimeOriginal="2024:07:01 12:34:56"),
            "download",
        ),
    ],
)
def test_month_requires_trusted_make_model_and_original_or_digitized_date(
    name, metadata, expected_kind,
):
    result = cp.classify_from_exif(Path(name), metadata)
    assert result["kind"] == expected_kind
    assert result["photo_qualified"] is (expected_kind in {"phone", "camera"})


@pytest.mark.parametrize(
    "name",
    [
        "IMG_20240701_123456.HEIC",
        "2024-07-01(1).jpg",
        "D2024-07-01(1).jpg",
        "S2024-07-01(1).png",
    ],
)
def test_extension_img_prefix_filename_date_and_canonical_name_do_not_prove_photo(name):
    result = cp.classify_from_exif(Path(name), {})
    assert result["kind"] == "download"
    assert result["photo_qualified"] is False


def test_dimensions_and_mtime_do_not_prove_photo(tmp_path, monkeypatch):
    source = tmp_path / "IMG_20240701_123456.PNG"
    source.write_bytes(b"not actually an image")
    source.touch()
    monkeypatch.setattr(cp, "read_exif", lambda _path: ({}, 1170, 2532, "PNG"))

    result = cp.classify(source)

    assert result["kind"] == "download"
    assert result["photo_qualified"] is False


@pytest.mark.parametrize(
    ("name", "metadata", "expected_kind"),
    [
        ("Screenshot_2024-07-01.png", {}, "screenshot"),
        ("螢幕截圖 2024-07-01.png", {}, "screenshot"),
        ("ordinary.png", {"UserComment": b"ASCII\x00\x00\x00Screenshot"}, "screenshot"),
        (
            "ordinary.jpg",
            {
                "Make": "Apple",
                "Model": "iPhone 11",
                "DateTimeOriginal": "2024:07:01 12:34:56",
                "UserComment": "Screenshot",
            },
            "screenshot",
        ),
        ("S2024-07-01(1).png", {}, "download"),
        ("ordinary.png", {}, "download"),
    ],
)
def test_only_explicit_screenshot_evidence_routes_to_screenshot(
    name, metadata, expected_kind,
):
    assert cp.classify_from_exif(Path(name), metadata)["kind"] == expected_kind


def _make_year_tree(tmp_path):
    root = tmp_path / "library"
    year = root / "2024相片"
    month = year / "2024.07"
    for folder in (month, year / "2024.06", year / "2024下載", year / "2024截圖"):
        folder.mkdir(parents=True, exist_ok=True)
    return root, year, month


def test_month_scan_requalifies_every_file_and_fails_closed(tmp_path, monkeypatch):
    root, _year, month = _make_year_tree(tmp_path)
    for name in (
        "2024-07-01(1).jpg",
        "S2024-07-01(2).png",
        "Screenshot_2024-07-01.png",
        "camera.jpg",
        "wrong-month.jpg",
    ):
        (month / name).write_bytes(b"fixture")

    original_classify = cp.classify

    def fake_classify(path):
        if path.name == "camera.jpg":
            return cp.classify_from_exif(path, exif(
                Make="Apple",
                Model="iPhone 11",
                DateTimeOriginal="2024:07:02 08:00:00",
            ))
        if path.name == "wrong-month.jpg":
            return cp.classify_from_exif(path, exif(
                Make="Canon",
                Model="EOS R6",
                DateTimeDigitized="2024:06:30 23:59:59",
            ))
        return original_classify(path)

    monkeypatch.setattr(cp, "classify", fake_classify)
    plan = cp.collect_plan(photos_root=root)
    items = {Path(item["src"]).name: item for item in plan}

    assert len(items) == 5
    assert items["2024-07-01(1).jpg"]["bucket"] == "download"
    assert items["2024-07-01(1).jpg"]["action"] == "move"
    assert items["S2024-07-01(2).png"]["bucket"] == "download"
    assert items["Screenshot_2024-07-01.png"]["bucket"] == "screenshot"
    assert items["camera.jpg"]["bucket"] == "photo"
    assert items["camera.jpg"]["action"] == "keep"
    assert items["wrong-month.jpg"]["bucket"] == "photo"
    assert Path(items["wrong-month.jpg"]["tgt_dir"]).name == "2024.06"
    assert items["wrong-month.jpg"]["action"] == "move"


def test_same_stem_image_video_candidates_block_the_whole_plan_unit(tmp_path):
    root, year, _month = _make_year_tree(tmp_path)
    (year / "IMG_0001.JPG").write_bytes(b"still")
    (year / "IMG_0001.MOV").write_bytes(b"video")

    plan = cp.collect_plan(photos_root=root)
    pair = [item for item in plan if Path(item["src"]).stem == "IMG_0001"]

    assert len(pair) == 2
    assert {item["action"] for item in pair} == {"blocked"}
    assert len({item["logical_unit"] for item in pair}) == 1
    assert all(
        "same_stem_image_video_candidate_requires_atomic_review"
        in item["block_reasons"]
        for item in pair
    )
    manifest = cp.build_manifest(plan, photos_root=root)
    assert manifest["status"] == "blocked"
    with pytest.raises(ValueError, match="not executable"):
        cp.validate_manifest(manifest)


def test_nested_event_download_is_found_and_moved_out_of_month(tmp_path):
    root = tmp_path / "library"
    year = root / "2025相片"
    trip = year / "2025.08" / "環島"
    trip.mkdir(parents=True)
    (year / "2025下載").mkdir()
    (year / "2025截圖").mkdir()
    source = trip / "D2025-08-03(1).jpg"
    source.write_bytes(b"no trusted device metadata")

    plan = cp.collect_plan(photos_root=root)
    item = next(item for item in plan if Path(item["src"]).name == source.name)

    assert item["source"] == "month/2025.08/環島"
    assert item["bucket"] == "download"
    assert item["action"] == "move"
    assert Path(item["tgt_dir"]).name == "2025下載"


def test_nested_qualified_photo_keeps_matching_event_structure(tmp_path, monkeypatch):
    root = tmp_path / "library"
    year = root / "2025相片"
    trip = year / "2025.08" / "環島"
    trip.mkdir(parents=True)
    (year / "2025下載").mkdir()
    (year / "2025截圖").mkdir()
    source = trip / "camera.jpg"
    source.write_bytes(b"trusted photo")
    monkeypatch.setattr(cp, "classify", lambda path: cp.classify_from_exif(path, exif(
        Make="Apple",
        Model="iPad Pro (11-inch)",
        DateTimeOriginal="2025:08:14 09:30:00",
    )))

    plan = cp.collect_plan(photos_root=root)
    item = next(item for item in plan if Path(item["src"]).name == source.name)

    assert item["photo_qualified"] is True
    assert item["bucket"] == "photo"
    assert item["action"] == "keep"
    assert Path(item["tgt_dir"]) == trip.resolve()
    assert Path(item["tgt"]) == source.resolve()


def test_nested_qualified_photo_crossing_month_moves_to_trusted_month(
    tmp_path, monkeypatch,
):
    root = tmp_path / "library"
    year = root / "2025相片"
    trip = year / "2025.08" / "環島"
    trip.mkdir(parents=True)
    (year / "2025.07").mkdir()
    (year / "2025下載").mkdir()
    (year / "2025截圖").mkdir()
    source = trip / "camera.jpg"
    source.write_bytes(b"trusted photo")
    monkeypatch.setattr(cp, "classify", lambda path: cp.classify_from_exif(path, exif(
        Make="SONY",
        Model="DSC-HX99",
        DateTimeDigitized="2025:07:31 23:59:59",
    )))

    item = cp.collect_plan(photos_root=root)[0]

    assert item["bucket"] == "photo"
    assert item["action"] == "move"
    assert Path(item["tgt_dir"]).name == "2025.07"


def test_manifest_digest_detects_edits(tmp_path, monkeypatch):
    root, _year, month = _make_year_tree(tmp_path)
    source = month / "camera.jpg"
    source.write_bytes(b"camera")
    monkeypatch.setattr(cp, "classify", lambda path: cp.classify_from_exif(path, exif(
        Make="NIKON CORPORATION",
        Model="NIKON Z 6",
        DateTimeOriginal="2024:07:02 08:00:00",
    )))
    manifest = cp.build_manifest(cp.collect_plan(photos_root=root), photos_root=root)
    assert manifest["status"] == "ready_for_review"
    cp.validate_manifest(manifest)

    edited = json.loads(json.dumps(manifest))
    edited["plan"][0]["bucket"] = "download"
    with pytest.raises(ValueError, match="plan_sha256 mismatch"):
        cp.validate_manifest(edited)


def test_no_argument_defaults_to_plan_without_execute(tmp_path, monkeypatch):
    called = {}

    def fake_plan(*, manifest_path, photos_root):
        called["manifest"] = manifest_path
        called["root"] = photos_root
        return {}

    monkeypatch.setattr(cp, "cmd_plan", fake_plan)
    assert cp.main([]) == 0
    assert called == {"manifest": cp.REPORT_PATH, "root": cp.PHOTOS_ROOT}


def test_execute_cli_requires_explicit_manifest_checkpoint_and_digest():
    parser = cp.build_parser()
    with pytest.raises(SystemExit):
        parser.parse_args(["execute"])
    parsed = parser.parse_args([
        "execute",
        "--manifest", "reviewed.json",
        "--checkpoint", "run.checkpoint.json",
        "--confirm-plan-sha256", "abc123",
    ])
    assert parsed.manifest == Path("reviewed.json")
    assert parsed.checkpoint == Path("run.checkpoint.json")
    assert parsed.confirm_plan_sha256 == "abc123"


def test_execute_uses_explicit_checkpoint_and_can_resume(tmp_path, monkeypatch):
    root, year, _month = _make_year_tree(tmp_path)
    source = year / "loose.jpg"
    source.write_bytes(b"download fixture")
    manifest = cp.build_manifest(cp.collect_plan(photos_root=root), photos_root=root)
    assert manifest["status"] == "ready_for_review"

    manifest_path = tmp_path / "reviewed-manifest.json"
    checkpoint_path = tmp_path / "explicit-checkpoint.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False), encoding="utf-8")
    monkeypatch.setattr(cp, "MOVE_LOG_PATH", tmp_path / "move-log.jsonl")

    first = cp.cmd_execute(
        manifest_path=manifest_path,
        checkpoint_path=checkpoint_path,
        confirm_plan_sha256=manifest["plan_sha256"],
    )
    assert first == {"moved": 1, "checkpoint_skipped": 0, "errors": 0}
    target = year / "2024下載" / "loose.jpg"
    assert not source.exists()
    assert target.is_file()

    second = cp.cmd_execute(
        manifest_path=manifest_path,
        checkpoint_path=checkpoint_path,
        confirm_plan_sha256=manifest["plan_sha256"],
    )
    assert second == {"moved": 0, "checkpoint_skipped": 1, "errors": 0}
