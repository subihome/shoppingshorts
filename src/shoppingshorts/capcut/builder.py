from __future__ import annotations

import json
import time
from pathlib import Path

from ..types import EditPlan
from . import templates as T


def _build_draft_content(plan: EditPlan) -> dict:
    materials = T.empty_materials()
    video_segs: list[dict] = []
    text_segs: list[dict] = []
    audio_segs: list[dict] = []

    for i, clip in enumerate(plan.clips):
        target_start = T.us(clip.audio_start)
        target_dur = T.us(clip.audio_end - clip.audio_start)

        source_dur_us = T.us((clip.asset_out or (clip.audio_end - clip.audio_start)) - clip.asset_in)
        vm = T.video_material(Path(clip.asset_path), plan.width, plan.height,
                              used_duration_us=source_dur_us)
        materials["videos"].append(vm)

        speed = T.speed_material()
        ph = T.placeholder_info_material()
        canvas = T.canvas_material()
        anim = T.sticker_animation_material()
        scm = T.sound_channel_mapping_material()
        mc = T.material_color_material()
        loud = T.loudness_material()
        vs = T.vocal_separation_material()
        materials["speeds"].append(speed)
        materials["placeholder_infos"].append(ph)
        materials["canvases"].append(canvas)
        materials["material_animations"].append(anim)
        materials["sound_channel_mappings"].append(scm)
        materials["material_colors"].append(mc)
        materials["loudnesses"].append(loud)
        materials["vocal_separations"].append(vs)

        source_start = T.us(clip.asset_in)

        is_photo = vm["type"] == "photo"
        video_segs.append(T.video_segment(
            material_id=vm["id"],
            target_start_us=target_start, target_dur_us=target_dur,
            source_start_us=source_start, source_dur_us=source_dur_us,
            extra_refs=[speed["id"], ph["id"], canvas["id"], anim["id"],
                        scm["id"], mc["id"], loud["id"], vs["id"]],
            volume=0.0 if is_photo else 1.0,
        ))

        if clip.text:
            tm = T.text_material(clip.text)
            t_anim = T.sticker_animation_material()
            materials["texts"].append(tm)
            materials["material_animations"].append(t_anim)
            text_segs.append(T.text_segment(
                material_id=tm["id"],
                target_start_us=target_start, target_dur_us=target_dur,
                extra_refs=[t_anim["id"]],
                render_index=14000 + i,
            ))

    total_us = T.us(plan.clips[-1].audio_end) if plan.clips else 0

    if plan.narration_audio:
        am = T.audio_material(Path(plan.narration_audio), total_us)
        a_speed = T.speed_material()
        a_ph = T.placeholder_info_material()
        a_beats = T.beats_material()
        a_scm = T.sound_channel_mapping_material()
        a_vs = T.vocal_separation_material()
        materials["audios"].append(am)
        materials["speeds"].append(a_speed)
        materials["placeholder_infos"].append(a_ph)
        materials["beats"].append(a_beats)
        materials["sound_channel_mappings"].append(a_scm)
        materials["vocal_separations"].append(a_vs)
        audio_segs.append(T.audio_segment(
            material_id=am["id"],
            target_start_us=0, target_dur_us=total_us,
            source_start_us=0, source_dur_us=total_us,
            extra_refs=[a_speed["id"], a_ph["id"], a_beats["id"], a_scm["id"], a_vs["id"]],
        ))

    tracks: list[dict] = []
    if video_segs:
        tracks.append({"id": T.uid(), "type": "video", "attribute": 1, "flag": 0, "name": "", "segments": video_segs})
    if text_segs:
        text_track_idx = len(tracks)
        for s in text_segs:
            s["track_render_index"] = text_track_idx
        tracks.append({"id": T.uid(), "type": "text", "attribute": 0, "flag": 0, "name": "", "segments": text_segs})
    if audio_segs:
        audio_track_idx = len(tracks)
        for s in audio_segs:
            s["track_render_index"] = audio_track_idx
        tracks.append({"id": T.uid(), "type": "audio", "attribute": 0, "flag": 0, "name": "", "segments": audio_segs})

    draft = T.root_scaffold(width=plan.width, height=plan.height, fps=plan.fps,
                            total_duration_us=total_us)
    draft["materials"] = materials
    draft["tracks"] = tracks
    return draft


def export_capcut_draft(*, plan_path: Path, out_path: Path) -> None:
    plan = EditPlan.model_validate_json(plan_path.read_text(encoding="utf-8"))
    draft = _build_draft_content(plan)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(draft, ensure_ascii=False, indent=2), encoding="utf-8")


def export_capcut_project(*, plan_path: Path, project_dir: Path,
                          windows_root: str = "C:/Users/sub/Downloads/CapCut Drafts") -> None:
    """Emit both draft_content.json and draft_meta_info.json into project_dir.

    project_dir's basename becomes draft_name. windows_root sets draft_root_path
    in the meta — must match where CapCut expects projects on the target machine
    (the user's CapCut Drafts root, NOT the local Linux path).
    """
    plan = EditPlan.model_validate_json(plan_path.read_text(encoding="utf-8"))
    draft = _build_draft_content(plan)

    project_dir.mkdir(parents=True, exist_ok=True)
    name = project_dir.name
    folder_path = f"{windows_root.rstrip('/')}/{name}"
    now_us = int(time.time() * 1_000_000)

    meta = T.meta_scaffold(
        draft_id=T.uid(),
        name=name,
        folder_path=folder_path,
        root_path=windows_root.rstrip("/"),
        total_duration_us=draft["duration"],
        create_us=now_us,
        modified_us=now_us,
    )

    (project_dir / "draft_content.json").write_text(
        json.dumps(draft, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (project_dir / "draft_meta_info.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
    )
