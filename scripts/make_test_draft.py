"""Generate a self-contained CapCut test project (draft_content + draft_meta_info).

Output: tests/fixtures/sample_capcut/test_output/shoppingshorts_test/
  - draft_content.json
  - draft_meta_info.json

To test in CapCut:
  1. Create an empty folder C:\\Users\\sub\\Downloads\\CapCut Drafts\\shoppingshorts_test\\
  2. Download both files from the test_output/shoppingshorts_test/ folder on GitHub
  3. Drop them into the folder
  4. Open CapCut - the project should appear in drafts
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from shoppingshorts.capcut.builder import export_capcut_project
from shoppingshorts.types import EditPlan, TimelineClip

# Reference an asset known to exist on the target machine (Windows username 'sub').
ASSET_PATH = "C:/Users/sub/Downloads/0512(1)-복사.png"
PROJECT_NAME = "shoppingshorts_test"
WINDOWS_ROOT = "C:/Users/sub/Downloads/CapCut Drafts"

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

out_dir = ROOT / "tests" / "fixtures" / "sample_capcut" / "test_output" / PROJECT_NAME
export_capcut_project(plan_path=plan_path, project_dir=out_dir, windows_root=WINDOWS_ROOT)
print(f"wrote project to {out_dir}")
for f in sorted(out_dir.iterdir()):
    print(f"  {f.name}: {f.stat().st_size} bytes")
