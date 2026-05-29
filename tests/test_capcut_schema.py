"""Smoke tests for the pyJianYingDraft-backed builder."""
import json
from pathlib import Path

from shoppingshorts.capcut.builder import export_capcut_draft, export_capcut_project
from shoppingshorts.types import EditPlan, TimelineClip


def _sample_plan() -> EditPlan:
    return EditPlan(
        width=1080,
        height=1920,
        fps=30.0,
        narration_audio=None,
        clips=[
            TimelineClip(
                sentence_index=0, asset_path="/tmp/a.mp4",
                audio_start=0.0, audio_end=2.0, asset_in=0.0, asset_out=2.0,
                text="여러분",
            ),
            TimelineClip(
                sentence_index=1, asset_path="/tmp/b.jpg",
                audio_start=2.0, audio_end=5.0, asset_in=0.0, asset_out=3.0,
                text="대박",
            ),
        ],
    )


def _write_plan(tmp: Path) -> Path:
    p = tmp / "plan.json"
    p.write_text(_sample_plan().model_dump_json(indent=2), encoding="utf-8")
    return p


def test_export_draft_emits_valid_json(tmp_path: Path):
    p = _write_plan(tmp_path)
    out = tmp_path / "draft_content.json"
    export_capcut_draft(plan_path=p, out_path=out)
    d = json.loads(out.read_text(encoding="utf-8"))
    assert d["canvas_config"]["width"] == 1080
    assert d["canvas_config"]["height"] == 1920
    assert d["duration"] == 5_000_000
    assert len(d["materials"]["videos"]) == 2
    assert len(d["materials"]["texts"]) == 2
    video_segs = [t for t in d["tracks"] if t["type"] == "video"][0]["segments"]
    text_segs = [t for t in d["tracks"] if t["type"] == "text"][0]["segments"]
    assert len(video_segs) == 2
    assert len(text_segs) == 2


def test_segment_material_ids_resolve(tmp_path: Path):
    p = _write_plan(tmp_path)
    out = tmp_path / "draft_content.json"
    export_capcut_draft(plan_path=p, out_path=out)
    d = json.loads(out.read_text(encoding="utf-8"))
    all_ids = {m["id"] for bucket in d["materials"].values() if isinstance(bucket, list)
               for m in bucket if isinstance(m, dict) and "id" in m}
    for track in d["tracks"]:
        for seg in track["segments"]:
            assert seg["material_id"] in all_ids


def test_project_export_emits_both_files_with_matching_duration(tmp_path: Path):
    p = _write_plan(tmp_path)
    proj = tmp_path / "myproj"
    export_capcut_project(plan_path=p, project_dir=proj, windows_root="C:/CapCut Drafts")

    assert (proj / "draft_content.json").exists()
    assert (proj / "draft_meta_info.json").exists()
    content = json.loads((proj / "draft_content.json").read_text(encoding="utf-8"))
    meta = json.loads((proj / "draft_meta_info.json").read_text(encoding="utf-8"))
    assert content["duration"] == meta["tm_duration"]
    assert meta["draft_name"] == "myproj"
    assert meta["draft_fold_path"] == "C:\\CapCut Drafts\\myproj"
