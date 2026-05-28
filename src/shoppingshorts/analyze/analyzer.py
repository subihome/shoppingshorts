from pathlib import Path

from ..types import ReferenceAnalysis, SceneSegment


# STUB: replace with ffprobe + PySceneDetect + faster-whisper (+ yt-dlp for URLs).
# Returns a placeholder analysis so the rest of the pipeline can run end-to-end.
def analyze_reference(url: str | None = None, file: Path | None = None) -> ReferenceAnalysis:
    if not url and not file:
        raise ValueError("provide url or file")
    source = url or str(file)
    return ReferenceAnalysis(
        source=source,
        duration=30.0,
        width=1080,
        height=1920,
        fps=30.0,
        scenes=[
            SceneSegment(start=0.0, end=3.0),
            SceneSegment(start=3.0, end=10.0),
            SceneSegment(start=10.0, end=20.0),
            SceneSegment(start=20.0, end=30.0),
        ],
        transcript=[],
        avg_cut_seconds=5.0,
        structure_notes="hook(0-3s) / body(3-25s) / cta(25-30s)",
    )
