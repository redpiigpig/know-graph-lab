"""Regression tests for the manifest-driven, fail-closed photo renamer."""

import datetime as dt
import json
from pathlib import Path

import pytest

import rename_photos as rp


def metadata(**values):
    return values


def make_library(tmp_path, year=2024, month=7):
    root = tmp_path / "library"
    year_dir = root / f"{year}相片"
    month_dir = year_dir / f"{year}.{month:02d}"
    event_dir = month_dir / "event"
    event_dir.mkdir(parents=True)
    (year_dir / f"{year}下載").mkdir()
    (year_dir / f"{year}截圖").mkdir()
    return root, year_dir, month_dir, event_dir


def install_metadata(monkeypatch, values_by_name):
    monkeypatch.setattr(
        rp,
        "read_metadata",
        lambda path: values_by_name.get(path.name, {}),
    )


def trusted_iphone(value="2024:07:02 08:30:00", **extra):
    return metadata(
        Make="Apple",
        Model="iPhone 11",
        DateTimeOriginal=value,
        **extra,
    )


def test_unprefixed_month_files_require_physical_device_and_original_date(
    tmp_path, monkeypatch,
):
    root, _year, month, _event = make_library(tmp_path)
    names = (
        "2024-07-01(9).jpg",
        "trusted.jpg",
        "datetime-only.jpg",
        "app-make.jpg",
        "software-foodie.jpg",
    )
    for name in names:
        (month / name).write_bytes(name.encode())
    install_metadata(monkeypatch, {
        "trusted.jpg": trusted_iphone(),
        "datetime-only.jpg": metadata(
            Make="Apple", Model="iPhone 11", DateTime="2024:07:03 09:00:00",
        ),
        "app-make.jpg": metadata(
            Make="Snowcorp", Model="Foodie", DateTimeOriginal="2024:07:04 09:00:00",
        ),
        # Export/edit software alone must not erase real device + DTO evidence.
        "software-foodie.jpg": trusted_iphone(
            "2024:07:05 10:00:00", Software="Foodie",
        ),
    })

    operations, _folders, _leftovers = rp.collect_plan(photos_root=root)
    by_name = {Path(item["src"]).name: item for item in operations}

    assert by_name["2024-07-01(9).jpg"]["action"] == "blocked"
    assert by_name["datetime-only.jpg"]["action"] == "blocked"
    assert by_name["app-make.jpg"]["action"] == "blocked"
    assert by_name["trusted.jpg"]["capture_verified"] is True
    assert by_name["trusted.jpg"]["date_source"] == "DateTimeOriginal"
    assert by_name["trusted.jpg"]["date"] == "2024-07-02"
    assert by_name["software-foodie.jpg"]["capture_verified"] is True


def test_filename_date_and_mtime_never_supply_unprefixed_capture(tmp_path, monkeypatch):
    root, _year, _month, event = make_library(tmp_path)
    source = event / "IMG_20240709_123456.jpg"
    source.write_bytes(b"no exif")
    timestamp = dt.datetime(2024, 7, 10, 11, 12, 13).timestamp()
    source.touch()
    import os
    os.utime(source, (timestamp, timestamp))
    install_metadata(monkeypatch, {})

    operation = rp.collect_plan(photos_root=root)[0][0]

    assert operation["action"] == "blocked"
    assert operation["date_source"] is None
    assert "lacks_trusted_physical" in operation["block_reasons"][0]


def test_download_dates_are_structural_and_follow_safe_priority(tmp_path, monkeypatch):
    root, year, _month, _event = make_library(tmp_path)
    downloads = year / "2024下載"
    for name in (
        "D2024-07-03(9).JPG",
        "embedded.jpg",
        "download_2024-08-02.png",
        "no-date.jpg",
    ):
        (downloads / name).write_bytes(name.encode())
    install_metadata(monkeypatch, {
        "embedded.jpg": metadata(DateTimeOriginal="2024:09:04 12:00:00"),
    })

    operations, _folders, _leftovers = rp.collect_plan(photos_root=root)
    by_name = {Path(item["src"]).name: item for item in operations}

    assert by_name["D2024-07-03(9).JPG"]["date_source"] == "existing_legal_name"
    assert by_name["D2024-07-03(9).JPG"]["date"] == "2024-07-03"
    assert by_name["embedded.jpg"]["date_source"] == "embedded_DateTimeOriginal"
    assert by_name["embedded.jpg"]["date"] == "2024-09-04"
    assert by_name["download_2024-08-02.png"]["date_source"] == "filename_date"
    assert by_name["download_2024-08-02.png"]["date"] == "2024-08-02"
    assert by_name["no-date.jpg"]["date_source"] == "bucket_year_01_01_anchor"
    assert by_name["no-date.jpg"]["date"] == "2024-01-01"
    assert all(item["not_capture"] is True for item in by_name.values())
    assert all(item["date_semantics"] == "not_capture" for item in by_name.values())


def test_wrong_year_screenshot_name_falls_back_to_bucket_anchor(tmp_path, monkeypatch):
    root, year, _month, _event = make_library(tmp_path)
    screenshots = year / "2024截圖"
    source = screenshots / "S2023-12-31(1).png"
    source.write_bytes(b"screenshot")
    install_metadata(monkeypatch, {})

    operation = rp.collect_plan(photos_root=root)[0][0]

    assert operation["prefix"] == "S"
    assert operation["date"] == "2024-01-01"
    assert operation["date_source"] == "bucket_year_01_01_anchor"
    assert operation["not_capture"] is True


def test_same_stem_image_video_share_one_atomic_basename(tmp_path, monkeypatch):
    root, _year, _month, event = make_library(tmp_path)
    still = event / "IMG_0001.JPG"
    video = event / "IMG_0001.MOV"
    still.write_bytes(b"still")
    video.write_bytes(b"video")
    install_metadata(monkeypatch, {still.name: trusted_iphone()})

    operations, folders, leftovers = rp.collect_plan(photos_root=root)
    pair = [item for item in operations if item["pair_candidate"]]
    manifest = rp.build_manifest(
        operations,
        photos_root=root,
        folders_scanned=folders,
        leftover_tmp_files=leftovers,
    )

    assert len(pair) == 2
    assert len({item["unit_id"] for item in pair}) == 1
    assert len({Path(item["target"]).stem for item in pair}) == 1
    assert {Path(item["target"]).suffix for item in pair} == {".jpg", ".mov"}
    assert next(item for item in pair if Path(item["src"]).suffix == ".MOV")[
        "capture_inherited_by_video"
    ] is True
    assert manifest["status"] == "ready_for_review"
    rp.validate_manifest(manifest)


def test_untrusted_same_stem_pair_blocks_whole_manifest(tmp_path, monkeypatch):
    root, _year, _month, event = make_library(tmp_path)
    (event / "IMG_0001.JPG").write_bytes(b"still")
    (event / "IMG_0001.MOV").write_bytes(b"video")
    install_metadata(monkeypatch, {})

    operations, folders, leftovers = rp.collect_plan(photos_root=root)
    manifest = rp.build_manifest(
        operations,
        photos_root=root,
        folders_scanned=folders,
        leftover_tmp_files=leftovers,
    )

    assert {item["action"] for item in operations} == {"blocked"}
    assert manifest["status"] == "blocked"
    with pytest.raises(ValueError, match="not executable"):
        rp.validate_manifest(manifest)


def test_normalized_extension_collision_blocks_entire_pair(tmp_path, monkeypatch):
    root, _year, _month, event = make_library(tmp_path)
    for name in ("IMG_0001.jpg", "IMG_0001.jpeg", "IMG_0001.mov"):
        (event / name).write_bytes(name.encode())
    install_metadata(monkeypatch, {
        "IMG_0001.jpg": trusted_iphone(),
        "IMG_0001.jpeg": trusted_iphone(),
    })

    operations, _folders, _leftovers = rp.collect_plan(photos_root=root)

    assert {item["action"] for item in operations} == {"blocked"}
    assert all("batch_target_collision" in item["block_reasons"] for item in operations)


def _ready_manifest(tmp_path, monkeypatch, names=("first.jpg", "second.jpg")):
    root, _year, _month, event = make_library(tmp_path)
    values = {}
    for index, name in enumerate(names, start=1):
        (event / name).write_bytes(f"source-{index}".encode())
        values[name] = trusted_iphone(f"2024:07:02 08:30:{index:02d}")
    install_metadata(monkeypatch, values)
    operations, folders, leftovers = rp.collect_plan(photos_root=root)
    manifest = rp.build_manifest(
        operations,
        photos_root=root,
        folders_scanned=folders,
        leftover_tmp_files=leftovers,
    )
    assert manifest["status"] == "ready_for_review"
    return root, event, manifest


def test_manifest_digest_detects_plan_edits(tmp_path, monkeypatch):
    _root, _event, manifest = _ready_manifest(tmp_path, monkeypatch, ("one.jpg",))
    rp.validate_manifest(manifest)
    edited = json.loads(json.dumps(manifest))
    edited["operations"][0]["target_name"] = "tampered.jpg"

    with pytest.raises(ValueError, match="plan_sha256 mismatch"):
        rp.validate_manifest(edited)


def test_execute_requires_explicit_manifest_checkpoint_and_digest():
    parser = rp.build_parser()
    with pytest.raises(SystemExit):
        parser.parse_args(["execute"])
    with pytest.raises(SystemExit):
        parser.parse_args(["auto", "chenwei"])
    parsed = parser.parse_args([
        "execute",
        "--manifest", "reviewed.json",
        "--checkpoint", "rename.checkpoint.json",
        "--confirm-plan-sha256", "abc",
    ])
    assert parsed.manifest == Path("reviewed.json")
    assert parsed.checkpoint == Path("rename.checkpoint.json")
    assert parsed.confirm_plan_sha256 == "abc"


def test_legacy_folder_api_cannot_bypass_reviewed_manifest(tmp_path):
    _root, _year, month, _event = make_library(tmp_path)
    (month / "old-caller.jpg").write_bytes(b"fixture")

    with pytest.raises(RuntimeError, match="legacy.*disabled"):
        rp.collect_folder_plan(month, "")


def test_no_arguments_default_to_plan_only(monkeypatch):
    called = {}

    def fake_plan(**kwargs):
        called.update(kwargs)
        return {}

    monkeypatch.setattr(rp, "cmd_plan", fake_plan)
    assert rp.main([]) == 0
    assert called == {
        "library": "chenwei",
        "photos_root": None,
        "manifest_path": None,
    }


def test_two_phase_execute_checkpoint_resume_and_explicit_rollback(
    tmp_path, monkeypatch,
):
    _root, event, manifest = _ready_manifest(tmp_path, monkeypatch)
    manifest_path = tmp_path / "reviewed.json"
    checkpoint_path = tmp_path / "rename.checkpoint.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False), encoding="utf-8")
    monkeypatch.setattr(rp, "LOG_PATH", tmp_path / "rename.log.jsonl")

    result = rp.cmd_execute(
        manifest_path=manifest_path,
        checkpoint_path=checkpoint_path,
        confirm_plan_sha256=manifest["plan_sha256"],
    )
    assert result["renamed"] == 2
    assert sorted(path.name for path in event.iterdir()) == [
        "2024-07-02(1).jpg", "2024-07-02(2).jpg",
    ]
    checkpoint = json.loads(checkpoint_path.read_text(encoding="utf-8"))
    assert checkpoint["status"] == "complete"

    rollback = rp.cmd_rollback(
        manifest_path=manifest_path,
        checkpoint_path=checkpoint_path,
        confirm_plan_sha256=manifest["plan_sha256"],
    )
    assert rollback == {"restored": 2, "errors": 0}
    assert sorted(path.name for path in event.iterdir()) == ["first.jpg", "second.jpg"]

    resumed = rp.cmd_execute(
        manifest_path=manifest_path,
        checkpoint_path=checkpoint_path,
        confirm_plan_sha256=manifest["plan_sha256"],
    )
    assert resumed["committed_now"] == 2
    assert sorted(path.name for path in event.iterdir()) == [
        "2024-07-02(1).jpg", "2024-07-02(2).jpg",
    ]


def test_target_appearing_after_plan_is_never_overwritten(tmp_path, monkeypatch):
    _root, event, manifest = _ready_manifest(tmp_path, monkeypatch, ("source.jpg",))
    operation = manifest["operations"][0]
    target = Path(operation["target"])
    target.write_bytes(b"unrelated occupant")
    manifest_path = tmp_path / "reviewed.json"
    checkpoint_path = tmp_path / "rename.checkpoint.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False), encoding="utf-8")
    monkeypatch.setattr(rp, "LOG_PATH", tmp_path / "rename.log.jsonl")

    with pytest.raises(FileExistsError, match="overwritten"):
        rp.cmd_execute(
            manifest_path=manifest_path,
            checkpoint_path=checkpoint_path,
            confirm_plan_sha256=manifest["plan_sha256"],
        )

    assert (event / "source.jpg").read_bytes() == b"source-1"
    assert target.read_bytes() == b"unrelated occupant"
    assert not checkpoint_path.exists()


def test_phase2_failure_rolls_back_whole_batch(tmp_path, monkeypatch):
    _root, event, manifest = _ready_manifest(tmp_path, monkeypatch)
    manifest_path = tmp_path / "reviewed.json"
    checkpoint_path = tmp_path / "rename.checkpoint.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False), encoding="utf-8")
    monkeypatch.setattr(rp, "LOG_PATH", tmp_path / "rename.log.jsonl")
    original_rename = rp._rename_no_overwrite
    calls = {"count": 0}

    def fail_once_on_second_phase2(source, target):
        calls["count"] += 1
        if calls["count"] == 4:
            raise OSError("injected phase2 failure")
        return original_rename(source, target)

    monkeypatch.setattr(rp, "_rename_no_overwrite", fail_once_on_second_phase2)

    with pytest.raises(RuntimeError, match="was rolled back"):
        rp.cmd_execute(
            manifest_path=manifest_path,
            checkpoint_path=checkpoint_path,
            confirm_plan_sha256=manifest["plan_sha256"],
        )

    assert sorted(path.name for path in event.iterdir()) == ["first.jpg", "second.jpg"]
    checkpoint = json.loads(checkpoint_path.read_text(encoding="utf-8"))
    assert checkpoint["status"] == "rolled_back"
    assert set(checkpoint["op_states"].values()) == {"planned"}


def test_resume_reconciles_source_to_temp_write_ahead_intent(tmp_path, monkeypatch):
    _root, _event, manifest = _ready_manifest(tmp_path, monkeypatch, ("one.jpg",))
    manifest_path = tmp_path / "reviewed.json"
    checkpoint_path = tmp_path / "rename.checkpoint.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False), encoding="utf-8")
    monkeypatch.setattr(rp, "LOG_PATH", tmp_path / "rename.log.jsonl")
    operation = manifest["operations"][0]
    checkpoint = rp._checkpoint_template(manifest_path, manifest)
    checkpoint["status"] = "phase1"
    checkpoint["intent"] = {
        "op_id": operation["op_id"],
        "transition": "source_to_temp",
        "from": operation["src"],
        "to": operation["temp"],
    }
    rp._atomic_write_json(checkpoint_path, checkpoint)
    Path(operation["src"]).rename(Path(operation["temp"]))

    result = rp.cmd_execute(
        manifest_path=manifest_path,
        checkpoint_path=checkpoint_path,
        confirm_plan_sha256=manifest["plan_sha256"],
    )

    assert result["staged_now"] == 0
    assert result["committed_now"] == 1
    assert Path(operation["target"]).is_file()


def test_resume_reconciles_temp_to_target_write_ahead_intent(tmp_path, monkeypatch):
    _root, _event, manifest = _ready_manifest(tmp_path, monkeypatch, ("one.jpg",))
    manifest_path = tmp_path / "reviewed.json"
    checkpoint_path = tmp_path / "rename.checkpoint.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False), encoding="utf-8")
    monkeypatch.setattr(rp, "LOG_PATH", tmp_path / "rename.log.jsonl")
    operation = manifest["operations"][0]
    checkpoint = rp._checkpoint_template(manifest_path, manifest)
    checkpoint["status"] = "phase2"
    checkpoint["op_states"][operation["op_id"]] = "staged"
    checkpoint["intent"] = {
        "op_id": operation["op_id"],
        "transition": "temp_to_target",
        "from": operation["temp"],
        "to": operation["target"],
    }
    rp._atomic_write_json(checkpoint_path, checkpoint)
    Path(operation["src"]).rename(Path(operation["temp"]))
    Path(operation["temp"]).rename(Path(operation["target"]))

    result = rp.cmd_execute(
        manifest_path=manifest_path,
        checkpoint_path=checkpoint_path,
        confirm_plan_sha256=manifest["plan_sha256"],
    )

    assert result["staged_now"] == 0
    assert result["committed_now"] == 0
    saved = json.loads(checkpoint_path.read_text(encoding="utf-8"))
    assert saved["status"] == "complete"
    assert saved["intent"] is None


def test_content_fingerprint_detects_same_size_same_mtime_replacement(
    tmp_path, monkeypatch,
):
    _root, _event, manifest = _ready_manifest(tmp_path, monkeypatch, ("one.jpg",))
    operation = manifest["operations"][0]
    source = Path(operation["src"])
    assert source.stat().st_size == len(b"source-1")
    source.write_bytes(b"evil-001")
    import os
    os.utime(source, ns=(operation["source_mtime_ns"], operation["source_mtime_ns"]))
    manifest_path = tmp_path / "reviewed.json"
    checkpoint_path = tmp_path / "rename.checkpoint.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False), encoding="utf-8")
    monkeypatch.setattr(rp, "LOG_PATH", tmp_path / "rename.log.jsonl")

    with pytest.raises(ValueError, match="content changed"):
        rp.cmd_execute(
            manifest_path=manifest_path,
            checkpoint_path=checkpoint_path,
            confirm_plan_sha256=manifest["plan_sha256"],
        )

    assert source.read_bytes() == b"evil-001"
    assert not checkpoint_path.exists()


def test_replan_after_rename_is_idempotent_even_for_equal_capture_times(
    tmp_path, monkeypatch,
):
    root, _year, _month, event = make_library(tmp_path)
    (event / "zeta.jpg").write_bytes(b"zeta")
    (event / "alpha.jpg").write_bytes(b"alpha")
    monkeypatch.setattr(rp, "read_metadata", lambda _path: trusted_iphone())
    operations, folders, leftovers = rp.collect_plan(photos_root=root)
    manifest = rp.build_manifest(
        operations,
        photos_root=root,
        folders_scanned=folders,
        leftover_tmp_files=leftovers,
    )
    manifest_path = tmp_path / "reviewed.json"
    checkpoint_path = tmp_path / "rename.checkpoint.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False), encoding="utf-8")
    monkeypatch.setattr(rp, "LOG_PATH", tmp_path / "rename.log.jsonl")
    rp.cmd_execute(
        manifest_path=manifest_path,
        checkpoint_path=checkpoint_path,
        confirm_plan_sha256=manifest["plan_sha256"],
    )

    replanned, _folders, _leftovers = rp.collect_plan(photos_root=root)

    assert sorted(path.name for path in event.iterdir()) == [
        "2024-07-02(1).jpg", "2024-07-02(2).jpg",
    ]
    assert {item["action"] for item in replanned} == {"keep"}


def test_two_phase_swap_and_rollback_preserve_both_sources(tmp_path, monkeypatch):
    root, _year, month, _event = make_library(tmp_path)
    july2 = month / "2024-07-02(1).jpg"
    july3 = month / "2024-07-03(1).jpg"
    july2.write_bytes(b"original-two")
    july3.write_bytes(b"original-three")
    install_metadata(monkeypatch, {
        july2.name: trusted_iphone("2024:07:03 08:00:00"),
        july3.name: trusted_iphone("2024:07:02 08:00:00"),
    })
    operations, folders, leftovers = rp.collect_plan(photos_root=root)
    manifest = rp.build_manifest(
        operations,
        photos_root=root,
        folders_scanned=folders,
        leftover_tmp_files=leftovers,
    )
    assert manifest["status"] == "ready_for_review"
    manifest_path = tmp_path / "swap.json"
    checkpoint_path = tmp_path / "swap.checkpoint.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False), encoding="utf-8")
    monkeypatch.setattr(rp, "LOG_PATH", tmp_path / "rename.log.jsonl")

    rp.cmd_execute(
        manifest_path=manifest_path,
        checkpoint_path=checkpoint_path,
        confirm_plan_sha256=manifest["plan_sha256"],
    )
    assert july2.read_bytes() == b"original-three"
    assert july3.read_bytes() == b"original-two"

    rp.cmd_rollback(
        manifest_path=manifest_path,
        checkpoint_path=checkpoint_path,
        confirm_plan_sha256=manifest["plan_sha256"],
    )
    assert july2.read_bytes() == b"original-two"
    assert july3.read_bytes() == b"original-three"


def test_checkpoint_rollback_handles_swap_with_identical_content(tmp_path, monkeypatch):
    root, _year, month, _event = make_library(tmp_path)
    july2 = month / "2024-07-02(1).jpg"
    july3 = month / "2024-07-03(1).jpg"
    july2.write_bytes(b"identical")
    july3.write_bytes(b"identical")
    install_metadata(monkeypatch, {
        july2.name: trusted_iphone("2024:07:03 08:00:00"),
        july3.name: trusted_iphone("2024:07:02 08:00:00"),
    })
    operations, folders, leftovers = rp.collect_plan(photos_root=root)
    manifest = rp.build_manifest(
        operations,
        photos_root=root,
        folders_scanned=folders,
        leftover_tmp_files=leftovers,
    )
    manifest_path = tmp_path / "identical-swap.json"
    checkpoint_path = tmp_path / "identical-swap.checkpoint.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False), encoding="utf-8")
    monkeypatch.setattr(rp, "LOG_PATH", tmp_path / "rename.log.jsonl")

    rp.cmd_execute(
        manifest_path=manifest_path,
        checkpoint_path=checkpoint_path,
        confirm_plan_sha256=manifest["plan_sha256"],
    )
    rp.cmd_rollback(
        manifest_path=manifest_path,
        checkpoint_path=checkpoint_path,
        confirm_plan_sha256=manifest["plan_sha256"],
    )

    assert july2.read_bytes() == b"identical"
    assert july3.read_bytes() == b"identical"
    checkpoint = json.loads(checkpoint_path.read_text(encoding="utf-8"))
    assert checkpoint["status"] == "rolled_back"


def test_script_change_blocks_execute_but_does_not_strand_rollback(tmp_path, monkeypatch):
    _root, event, manifest = _ready_manifest(tmp_path, monkeypatch, ("one.jpg",))
    manifest_path = tmp_path / "reviewed.json"
    checkpoint_path = tmp_path / "rename.checkpoint.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False), encoding="utf-8")
    monkeypatch.setattr(rp, "LOG_PATH", tmp_path / "rename.log.jsonl")
    rp.cmd_execute(
        manifest_path=manifest_path,
        checkpoint_path=checkpoint_path,
        confirm_plan_sha256=manifest["plan_sha256"],
    )
    monkeypatch.setattr(rp, "current_script_sha256", lambda: "changed-script-hash")

    rollback = rp.cmd_rollback(
        manifest_path=manifest_path,
        checkpoint_path=checkpoint_path,
        confirm_plan_sha256=manifest["plan_sha256"],
    )

    assert rollback == {"restored": 1, "errors": 0}
    assert (event / "one.jpg").is_file()
    with pytest.raises(ValueError, match="different renamer script"):
        rp.cmd_execute(
            manifest_path=manifest_path,
            checkpoint_path=checkpoint_path,
            confirm_plan_sha256=manifest["plan_sha256"],
        )
