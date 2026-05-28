from __future__ import annotations

import json
import uuid
from pathlib import Path

from ..types import EditPlan


# SKELETON CapCut Desktop (Global) draft_content.json builder.
# The exact schema must be verified against a real sample exported from
# CapCut Desktop Global. Keys here follow the publicly-known shape and will
# be adjusted once tests/fixtures/sample_capcut/draft_content.json is added.

_VIDEO_EXT = {".mp4", ".mov", ".m4v", ".webm"}
_IMAGE_EXT = {".jpg", ".jpeg", ".png"}


def _uid() -> str:
    return str(uuid.uuid4()).upper()


def _us(seconds: float) -> int:
    return int(round(seconds * 1_000_000))


def _video_material(path: Path, duration_us: int) -> dict:
    is_image = path.suffix.lower() in _IMAGE_EXT
    return {
        "id": _uid(),
        "type": "photo" if is_image else "video",
        "path": str(path.resolve()),
        "material_name": path.name,
        "duration": duration_us,
        "width": 1080,
        "height": 1920,
        "has_audio": False,
        "extra_material_refs": [],
    }


def _audio_material(path: Path, duration_us: int) -> dict:
    return {
        "id": _uid(),
        "type": "extract_music",
        "path": str(path.resolve()),
        "name": path.name,
        "duration": duration_us,
        "extra_material_refs": [],
    }


def _text_material(text: str) -> dict:
    return {
        "id": _uid(),
        "type": "text",
        "content": json.dumps({"text": text}, ensure_ascii=False),
        "font_size": 12,
    }


def _segment(material_id: str, source_us: int, target_start_us: int, target_dur_us: int) -> dict:
    return {
        "id": _uid(),
        "material_id": material_id,
        "source_timerange": {"start": 0, "duration": source_us},
        "target_timerange": {"start": target_start_us, "duration": target_dur_us},
        "speed": 1.0,
        "volume": 1.0,
        "visible": True,
    }


def export_capcut_draft(*, plan_path: Path, out_path: Path) -> None:
    plan = EditPlan.model_validate_json(plan_path.read_text(encoding="utf-8"))

    materials = {"videos": [], "audios": [], "texts": []}
    video_segs: list[dict] = []
    text_segs: list[dict] = []
    audio_segs: list[dict] = []

    for clip in plan.clips:
        dur_us = _us(clip.audio_end - clip.audio_start)
        start_us = _us(clip.audio_start)

        vm = _video_material(Path(clip.asset_path), dur_us)
        materials["videos"].append(vm)
        video_segs.append(_segment(vm["id"], dur_us, start_us, dur_us))

        if clip.text:
            tm = _text_material(clip.text)
            materials["texts"].append(tm)
            text_segs.append(_segment(tm["id"], dur_us, start_us, dur_us))

    if plan.narration_audio:
        total_us = _us(plan.clips[-1].audio_end) if plan.clips else 0
        am = _audio_material(Path(plan.narration_audio), total_us)
        materials["audios"].append(am)
        audio_segs.append(_segment(am["id"], total_us, 0, total_us))

    total_us = _us(plan.clips[-1].audio_end) if plan.clips else 0

    draft = {
        "canvas_config": {
            "width": plan.width,
            "height": plan.height,
            "ratio": f"{plan.width}:{plan.height}",
        },
        "duration": total_us,
        "fps": plan.fps,
        "materials": materials,
        "tracks": [
            {"id": _uid(), "type": "video", "segments": video_segs},
            {"id": _uid(), "type": "audio", "segments": audio_segs},
            {"id": _uid(), "type": "text", "segments": text_segs},
        ],
    }

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(draft, ensure_ascii=False, indent=2), encoding="utf-8")
