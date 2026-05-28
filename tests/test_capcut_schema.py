import json
from pathlib import Path

from shoppingshorts.capcut.builder import export_capcut_draft
from shoppingshorts.plan.planner import build_plan
from shoppingshorts.types import (
    EditPlan,
    ReferenceAnalysis,
    Script,
    ScriptSentence,
    TimelineClip,
)

FIXTURE = Path(__file__).parent / "fixtures" / "sample_capcut" / "minimal" / "draft_content.json"


def _sample_plan() -> EditPlan:
    return EditPlan(
        width=1080,
        height=1920,
        fps=30.0,
        narration_audio="/tmp/narration.wav",
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


def test_top_level_matches_fixture(tmp_path: Path):
    p = _write_plan(tmp_path)
    out = tmp_path / "draft_content.json"
    export_capcut_draft(plan_path=p, out_path=out)

    fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
    produced = json.loads(out.read_text(encoding="utf-8"))

    missing = set(fixture.keys()) - set(produced.keys())
    assert not missing, f"missing top-level keys vs CapCut sample: {sorted(missing)}"


def test_materials_buckets_match_fixture(tmp_path: Path):
    p = _write_plan(tmp_path)
    out = tmp_path / "draft_content.json"
    export_capcut_draft(plan_path=p, out_path=out)

    fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
    produced = json.loads(out.read_text(encoding="utf-8"))

    missing = set(fixture["materials"].keys()) - set(produced["materials"].keys())
    assert not missing, f"missing material buckets: {sorted(missing)}"


def test_segment_refs_resolve_to_materials(tmp_path: Path):
    p = _write_plan(tmp_path)
    out = tmp_path / "draft_content.json"
    export_capcut_draft(plan_path=p, out_path=out)

    produced = json.loads(out.read_text(encoding="utf-8"))
    all_ids: set[str] = set()
    for items in produced["materials"].values():
        for m in items:
            if isinstance(m, dict) and "id" in m:
                all_ids.add(m["id"])

    for track in produced["tracks"]:
        for seg in track["segments"]:
            assert seg["material_id"] in all_ids, f"segment material_id {seg['material_id']} not in materials"
            for ref in seg["extra_material_refs"]:
                assert ref in all_ids, f"extra_material_ref {ref} not in materials"


def test_durations_are_microseconds(tmp_path: Path):
    p = _write_plan(tmp_path)
    out = tmp_path / "draft_content.json"
    export_capcut_draft(plan_path=p, out_path=out)

    produced = json.loads(out.read_text(encoding="utf-8"))
    # plan total: 5.0s -> 5_000_000 us
    assert produced["duration"] == 5_000_000
    # first video segment: 2.0s -> 2_000_000 us
    first = produced["tracks"][0]["segments"][0]
    assert first["target_timerange"]["duration"] == 2_000_000


def test_text_content_is_valid_json_string(tmp_path: Path):
    p = _write_plan(tmp_path)
    out = tmp_path / "draft_content.json"
    export_capcut_draft(plan_path=p, out_path=out)

    produced = json.loads(out.read_text(encoding="utf-8"))
    for tm in produced["materials"]["texts"]:
        parsed = json.loads(tm["content"])
        assert "text" in parsed
        assert "styles" in parsed and len(parsed["styles"]) > 0
