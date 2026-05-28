"""Generate a self-contained CapCut test draft for opening in CapCut Desktop.

Output: tests/fixtures/sample_capcut/test_output/draft_content.json

We reference an image we know exists on the target machine (the one
captured in the user's earlier root_meta_info upload). If that file is
missing CapCut will still load the project with red placeholder tiles,
which is enough to confirm the schema is accepted.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from shoppingshorts.capcut.builder import export_capcut_draft
from shoppingshorts.types import EditPlan, TimelineClip

ASSET_PATH = "C:/Users/sub/Downloads/0512(1)-복사.png"

plan = EditPlan(
    width=1080,
    height=1920,
    fps=30.0,
    narration_audio=None,
    clips=[
        TimelineClip(
            sentence_index=i,
            asset_path=ASSET_PATH,
            audio_start=i * 3.0,
            audio_end=(i + 1) * 3.0,
            asset_in=0.0,
            asset_out=3.0,
            text=text,
        )
        for i, text in enumerate(["테스트 1", "테스트 2", "테스트 3"])
    ],
)

work = ROOT / ".work"
work.mkdir(exist_ok=True)
plan_path = work / "test_plan.json"
plan_path.write_text(plan.model_dump_json(indent=2), encoding="utf-8")

out = ROOT / "tests" / "fixtures" / "sample_capcut" / "test_output" / "draft_content.json"
export_capcut_draft(plan_path=plan_path, out_path=out)
print(f"wrote {out}")
print(f"  duration: {plan.clips[-1].audio_end}s, {len(plan.clips)} clips")
