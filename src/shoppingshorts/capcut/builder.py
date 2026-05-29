"""CapCut PC draft builder per the documented v5.x minimal schema.

Targets schema version 360000 / new_version 93.0.0 / app_id 359 / app_version 5.1.0.
This is a much simpler shape than the 171.x version we'd been chasing — each
segment carries only a canvas reference in extra_material_refs and segments
omit hdr_settings / responsive_layout / enable_video_mask and friends entirely.
"""
from __future__ import annotations

import json
import shutil
import time
import uuid
from pathlib import Path

from ..types import EditPlan

_IMAGE_EXT = {".jpg", ".jpeg", ".png", ".bmp", ".webp", ".gif"}
_VIDEO_EXT = {".mp4", ".mov", ".m4v", ".webm", ".mkv"}


def _uid() -> str:
    return str(uuid.uuid4()).upper()


def _us(seconds: float) -> int:
    return int(round(seconds * 1_000_000))


def _win_path(p: str | Path) -> str:
    return str(p).replace("/", "\\")


def _video_material(path: str, width: int, height: int,
                    duration_us: int, has_audio: bool) -> dict:
    p = Path(path)
    is_image = p.suffix.lower() in _IMAGE_EXT
    return {
        "id": _uid(),
        "type": "photo" if is_image else "video",
        "path": _win_path(p),
        "material_name": p.name,
        "duration": duration_us,
        "width": width,
        "height": height,
        "has_audio": has_audio,
        "has_sound_separated": False,
        "crop": {
            "lower_left_x": 0.0, "lower_left_y": 1.0,
            "lower_right_x": 1.0, "lower_right_y": 1.0,
            "upper_left_x": 0.0, "upper_left_y": 0.0,
            "upper_right_x": 1.0, "upper_right_y": 0.0,
        },
        "crop_ratio": "free",
        "crop_scale": 1.0,
        "category_id": "",
        "category_name": "local",
        "extra_type_option": 0,
        "check_flag": 63487,
        "local_material_id": _uid(),
        "source_platform": 0,
        "stable": {
            "matrix_path": "",
            "stable_level": 0,
            "time_range": {"duration": 0, "start": 0},
        },
        "team_id": "",
        "type_specific_id": "",
    }


def _audio_material(path: str, duration_us: int) -> dict:
    p = Path(path)
    return {
        "id": _uid(),
        "type": "extract_music",
        "path": _win_path(p),
        "name": p.name,
        "duration": duration_us,
        "category_id": "",
        "category_name": "local",
        "check_flag": 1,
        "local_material_id": _uid(),
        "music_id": "",
        "source_platform": 0,
        "team_id": "",
        "wave_points": [],
    }


def _text_material(text: str) -> dict:
    content = {
        "text": text,
        "styles": [{
            "fill": {"content": {"render_type": "solid", "solid": {"color": [1.0, 1.0, 1.0]}}},
            "font": {"path": "", "id": ""},
            "strokes": [{
                "content": {"render_type": "solid", "solid": {"color": [0.0, 0.0, 0.0]}},
                "width": 0.08, "mode": 0,
            }],
            "size": 15,
            "useLetterColor": True,
            "range": [0, len(text)],
        }],
    }
    return {
        "id": _uid(),
        "type": "subtitle",
        "content": json.dumps(content, ensure_ascii=False),
        "text": text,
        "font_name": "",
        "font_path": "",
        "font_size": 15.0,
        "text_color": "#FFFFFF",
        "text_alpha": 1.0,
        "border_color": "#000000",
        "border_width": 0.08,
        "border_alpha": 1.0,
        "has_shadow": False,
        "shadow_color": "#000000",
        "shadow_alpha": 0.0,
        "alignment": 1,
        "background_color": "",
        "background_alpha": 0.0,
        "letter_spacing": 0.0,
        "line_spacing": 0.0,
        "italic_degree": 0,
        "bold_width": 0.0,
        "underline": False,
        "style_name": "",
    }


def _canvas_material() -> dict:
    return {
        "id": _uid(),
        "type": "canvas_color",
        "color": "",
        "blur": 0.0,
        "image": "",
        "album_image": "",
        "source_platform": 0,
        "team_id": "",
    }


def _video_segment(*, material_id: str, canvas_id: str,
                   source_start_us: int, source_dur_us: int,
                   target_start_us: int, target_dur_us: int,
                   volume: float = 1.0) -> dict:
    return {
        "id": _uid(),
        "material_id": material_id,
        "source_timerange": {"start": source_start_us, "duration": source_dur_us},
        "target_timerange": {"start": target_start_us, "duration": target_dur_us},
        "extra_material_refs": [canvas_id],
        "speed": 1.0,
        "volume": volume,
        "visible": True,
        "clip": {
            "alpha": 1.0,
            "flip": {"horizontal": False, "vertical": False},
            "rotation": 0.0,
            "scale": {"x": 1.0, "y": 1.0},
            "transform": {"x": 0.0, "y": 0.0},
        },
        "enable_adjust": True,
        "enable_color_curves": True,
        "enable_color_wheels": True,
        "enable_lut": True,
        "enable_smart_color_adjust": False,
        "last_nonzero_volume": 1.0,
        "reverse": False,
        "track_attribute": 0,
        "track_render_index": 0,
        "uniform_scale": {"on": True, "value": 1.0},
    }


def _audio_segment(*, material_id: str,
                   source_start_us: int, source_dur_us: int,
                   target_start_us: int, target_dur_us: int,
                   volume: float = 1.0) -> dict:
    return {
        "id": _uid(),
        "material_id": material_id,
        "source_timerange": {"start": source_start_us, "duration": source_dur_us},
        "target_timerange": {"start": target_start_us, "duration": target_dur_us},
        "extra_material_refs": [],
        "speed": 1.0,
        "volume": volume,
        "visible": True,
        "clip": None,
        "last_nonzero_volume": 1.0,
        "reverse": False,
        "track_attribute": 0,
        "track_render_index": 0,
    }


def _text_segment(*, material_id: str, target_start_us: int, target_dur_us: int,
                  render_index: int = 14000) -> dict:
    return {
        "id": _uid(),
        "material_id": material_id,
        "source_timerange": None,
        "target_timerange": {"start": target_start_us, "duration": target_dur_us},
        "extra_material_refs": [],
        "speed": 1.0,
        "volume": 1.0,
        "visible": True,
        "clip": {
            "alpha": 1.0,
            "flip": {"horizontal": False, "vertical": False},
            "rotation": 0.0,
            "scale": {"x": 1.0, "y": 1.0},
            "transform": {"x": 0.0, "y": 0.0},
        },
        "render_index": render_index,
        "track_render_index": 1,
    }


_EMPTY_MATERIAL_BUCKETS = (
    "effects", "stickers", "transitions", "audio_effects", "audio_fades",
    "beats", "speeds", "masks", "placeholder_infos", "sound_channel_mappings",
    "video_effects", "loudnesses",
)


def _build_draft_content(plan: EditPlan, resources_paths: dict[str, str] | None = None) -> dict:
    materials: dict[str, list] = {
        "videos": [], "audios": [], "texts": [], "canvases": [],
    }
    for k in _EMPTY_MATERIAL_BUCKETS:
        materials[k] = []

    video_segs: list[dict] = []
    text_segs: list[dict] = []
    audio_segs: list[dict] = []

    for i, clip in enumerate(plan.clips):
        target_start = _us(clip.audio_start)
        target_dur = _us(clip.audio_end - clip.audio_start)
        source_start = _us(clip.asset_in)
        clip_dur = (clip.asset_out or (clip.audio_end - clip.audio_start)) - clip.asset_in
        source_dur = _us(clip_dur)

        asset_path = resources_paths.get(clip.asset_path, clip.asset_path) if resources_paths else clip.asset_path
        asset = Path(asset_path)
        is_image = asset.suffix.lower() in _IMAGE_EXT
        # Photos get a huge nominal duration; videos use the cut length
        mat_duration = 10_800_000_000 if is_image else max(source_dur, target_dur)

        vm = _video_material(asset_path, plan.width, plan.height,
                             duration_us=mat_duration, has_audio=not is_image)
        materials["videos"].append(vm)

        canvas = _canvas_material()
        materials["canvases"].append(canvas)

        video_segs.append(_video_segment(
            material_id=vm["id"], canvas_id=canvas["id"],
            source_start_us=source_start, source_dur_us=source_dur,
            target_start_us=target_start, target_dur_us=target_dur,
            volume=0.0 if is_image else 1.0,
        ))

        if clip.text:
            tm = _text_material(clip.text)
            materials["texts"].append(tm)
            text_segs.append(_text_segment(
                material_id=tm["id"],
                target_start_us=target_start, target_dur_us=target_dur,
                render_index=14000 + i,
            ))

    total_us = _us(plan.clips[-1].audio_end) if plan.clips else 0

    if plan.narration_audio:
        audio_path = (resources_paths.get(plan.narration_audio, plan.narration_audio)
                      if resources_paths else plan.narration_audio)
        am = _audio_material(audio_path, total_us)
        materials["audios"].append(am)
        audio_segs.append(_audio_segment(
            material_id=am["id"],
            source_start_us=0, source_dur_us=total_us,
            target_start_us=0, target_dur_us=total_us,
        ))

    tracks: list[dict] = []
    if video_segs:
        tracks.append({"id": _uid(), "type": "video", "attribute": 0, "flag": 0,
                       "is_default_name": True, "name": "", "segments": video_segs})
    if audio_segs:
        tracks.append({"id": _uid(), "type": "audio", "attribute": 0, "flag": 0,
                       "is_default_name": True, "name": "", "segments": audio_segs})
    if text_segs:
        tracks.append({"id": _uid(), "type": "text", "attribute": 0, "flag": 0,
                       "is_default_name": True, "name": "", "segments": text_segs})

    return {
        "id": _uid(),
        "version": 360000,
        "new_version": "93.0.0",
        "fps": int(round(plan.fps)),
        "duration": total_us,
        "canvas_config": {"width": plan.width, "height": plan.height, "ratio": "9:16"},
        "color_space": 0,
        "config": {
            "video_mute": False,
            "record_audio_last_index": 1,
            "extract_audio_last_index": 1,
            "original_sound_last_index": 1,
            "subtitle_recognition_id": "",
            "subtitle_taskinfo": [],
            "lyrics_recognition_id": "",
            "adjust_max_index": 1,
            "lyrics_taskinfo": [],
        },
        "keyframes": {"videos": [], "audios": [], "texts": [], "stickers": [],
                      "filters": [], "adjusts": [], "handwrites": [], "effects": []},
        "materials": materials,
        "tracks": tracks,
        "platform": {
            "app_id": 359,
            "app_source": "cc",
            "app_version": "5.1.0",
            "os": "windows",
            "os_version": "10",
            "device_id": "",
            "hard_disk_id": "",
            "mac_address": "",
        },
        "create_time": 0,
        "update_time": 0,
        "name": "",
        "path": "",
        "relationships": [],
        "static_cover_image_path": "",
        "extra_info": None,
        "mutable_config": None,
    }


def export_capcut_draft(*, plan_path: Path, out_path: Path) -> None:
    plan = EditPlan.model_validate_json(plan_path.read_text(encoding="utf-8"))
    draft = _build_draft_content(plan)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(draft, ensure_ascii=False, indent=2), encoding="utf-8")


def export_capcut_project(*, plan_path: Path, project_dir: Path,
                          windows_root: str = "C:\\Users\\sub\\Downloads\\CapCut Drafts",
                          copy_resources: bool = False) -> None:
    """Emit draft_content.json + draft_meta_info.json into project_dir.

    If copy_resources=True and the asset files exist locally, copies them
    into project_dir/Resources/ and rewrites paths to point at the copies.
    """
    plan = EditPlan.model_validate_json(plan_path.read_text(encoding="utf-8"))

    project_dir.mkdir(parents=True, exist_ok=True)
    name = project_dir.name
    win_root = windows_root.rstrip("\\").rstrip("/").replace("/", "\\")
    folder_path = f"{win_root}\\{name}"

    resources_paths: dict[str, str] | None = None
    if copy_resources:
        res_dir = project_dir / "Resources"
        res_dir.mkdir(exist_ok=True)
        resources_paths = {}
        for clip in plan.clips:
            src = Path(clip.asset_path)
            if src.exists():
                dst = res_dir / src.name
                shutil.copy2(src, dst)
                resources_paths[clip.asset_path] = f"{folder_path}\\Resources\\{src.name}"
        if plan.narration_audio:
            src = Path(plan.narration_audio)
            if src.exists():
                dst = res_dir / src.name
                shutil.copy2(src, dst)
                resources_paths[plan.narration_audio] = f"{folder_path}\\Resources\\{src.name}"

    draft = _build_draft_content(plan, resources_paths=resources_paths)

    now_us = int(time.time() * 1_000_000)
    meta = _meta_scaffold(
        draft_id=_uid(),
        name=name,
        folder_path=folder_path,
        root_path=win_root,
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


def _meta_scaffold(*, draft_id, name, folder_path, root_path,
                   total_duration_us, create_us, modified_us) -> dict:
    return {
        "draft_id": draft_id,
        "draft_name": name,
        "draft_cover": "draft_cover.jpg",
        "draft_fold_path": folder_path,
        "draft_root_path": root_path,
        "draft_removable_storage_device": "",
        "tm_draft_create": create_us,
        "tm_draft_modified": modified_us,
        "tm_draft_removed": 0,
        "tm_duration": total_duration_us,
        "draft_materials": [{"type": 0, "value": []}],
        "draft_enterprise_info": {
            "draft_enterprise_extra": "",
            "draft_enterprise_id": "",
            "draft_enterprise_name": "",
            "enterprise_material": [],
        },
        "draft_deeplink_url": "",
        "draft_is_ai_shorts": False,
        "draft_is_invisible": False,
        "draft_materials_copied_info": [],
        "draft_new_version": "",
        "draft_segment_extra_info": [],
        "draft_timeline_materials_size_": 0,
        "draft_type": "",
        "draft_is_ae_produce": False,
        "draft_is_article_video_draft": False,
        "draft_is_cloud_temp_draft": False,
        "draft_is_from_deeplink": "false",
        "draft_is_pippit_draft": False,
        "draft_is_web_article_video": False,
        "draft_need_rename_folder": False,
        "draft_web_article_video_enter_from": "",
        "cloud_draft_cover": False,
        "cloud_draft_sync": False,
        "cloud_package_completed_time": "",
        "draft_cloud_capcut_purchase_info": "",
        "draft_cloud_last_action_download": False,
        "draft_cloud_package_type": "",
        "draft_cloud_purchase_info": "",
        "draft_cloud_template_id": "",
        "draft_cloud_tutorial_info": "",
        "draft_cloud_videocut_purchase_info": "",
        "tm_draft_cloud_completed": 0,
        "tm_draft_cloud_entry_id": 0,
        "tm_draft_cloud_modified": 0,
        "tm_draft_cloud_parent_entry_id": -1,
        "tm_draft_cloud_space_id": 0,
        "tm_draft_cloud_user_id": 0,
    }
