from pathlib import Path

from ..types import EditPlan, Narration, ReferenceAnalysis, Script, TimelineClip


_ASSET_EXT = {".mp4", ".mov", ".m4v", ".webm", ".jpg", ".jpeg", ".png"}


def build_plan(
    *,
    analysis_path: Path,
    script_path: Path,
    narration_path: Path | None,
    assets_dir: Path,
) -> EditPlan:
    analysis = ReferenceAnalysis.model_validate_json(analysis_path.read_text(encoding="utf-8"))
    script = Script.model_validate_json(script_path.read_text(encoding="utf-8"))

    durations: dict[int, float] = {}
    narration_audio: str | None = None
    if narration_path and narration_path.exists():
        narration = Narration.model_validate_json(narration_path.read_text(encoding="utf-8"))
        for c in narration.clips:
            durations[c.sentence_index] = c.duration
        narration_audio = narration.full_audio_path

    assets = sorted(
        [p for p in assets_dir.iterdir() if p.suffix.lower() in _ASSET_EXT],
    )
    if not assets:
        raise ValueError(f"no assets found in {assets_dir}")

    clips: list[TimelineClip] = []
    cursor = 0.0
    for s in script.sentences:
        dur = durations.get(s.index, analysis.avg_cut_seconds)
        if dur <= 0:
            dur = analysis.avg_cut_seconds
        asset = assets[s.index % len(assets)]
        clips.append(
            TimelineClip(
                sentence_index=s.index,
                asset_path=str(asset),
                audio_start=cursor,
                audio_end=cursor + dur,
                asset_in=0.0,
                asset_out=dur,
                text=s.text,
            )
        )
        cursor += dur

    return EditPlan(
        width=analysis.width,
        height=analysis.height,
        fps=analysis.fps,
        clips=clips,
        narration_audio=narration_audio,
    )
