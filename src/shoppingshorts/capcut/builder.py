"""CapCut draft builder backed by pyJianYingDraft.

We use pyJianYingDraft to emit the CapCut/JianYing draft schema. The library
validates media paths against the local filesystem on construction; when we're
building on a remote machine for a user's Windows paths the file isn't there,
so we provide *_unchecked helpers that bypass validation and fill in metadata
explicitly.
"""
from __future__ import annotations

import json
import time
import uuid
from pathlib import Path

import pyJianYingDraft as pyd
from pyJianYingDraft import (
    AudioMaterial,
    AudioSegment,
    ScriptFile,
    TextSegment,
    Timerange,
    TrackType,
    VideoMaterial,
    VideoSegment,
)
from pyJianYingDraft.local_materials import CropSettings

from ..types import EditPlan

_IMAGE_EXT = {".jpg", ".jpeg", ".png", ".bmp", ".webp", ".gif"}


def _video_material_unchecked(path: str, width: int, height: int) -> VideoMaterial:
    """Construct a VideoMaterial without touching the filesystem."""
    p = Path(path)
    vm = VideoMaterial.__new__(VideoMaterial)
    vm.material_name = p.name
    vm.material_id = uuid.uuid4().hex
    vm.path = str(p).replace("\\", "/")
    vm.crop_settings = CropSettings()
    vm.local_material_id = ""
    if p.suffix.lower() in _IMAGE_EXT:
        vm.material_type = "photo"
    else:
        vm.material_type = "video"
    # Without media probing, give a long virtual duration so any segment
    # source_timerange we hand the library passes its bounds check.
    vm.duration = 10_800_000_000
    vm.width = width
    vm.height = height
    return vm


def _audio_material_unchecked(path: str, duration_us: int) -> AudioMaterial:
    p = Path(path)
    am = AudioMaterial.__new__(AudioMaterial)
    am.material_name = p.name
    am.material_id = uuid.uuid4().hex
    am.path = str(p).replace("\\", "/")
    am.duration = duration_us
    return am


def _build_script(plan: EditPlan) -> ScriptFile:
    script = ScriptFile(width=plan.width, height=plan.height, fps=int(plan.fps),
                        maintrack_adsorb=False)
    script.add_track(TrackType.video, track_name="video_main")
    script.add_track(TrackType.text, track_name="captions")
    if plan.narration_audio:
        script.add_track(TrackType.audio, track_name="narration")

    for clip in plan.clips:
        target = Timerange(
            start=int(round(clip.audio_start * 1_000_000)),
            duration=int(round((clip.audio_end - clip.audio_start) * 1_000_000)),
        )
        source = Timerange(
            start=int(round(clip.asset_in * 1_000_000)),
            duration=int(round(((clip.asset_out or (clip.audio_end - clip.audio_start)) - clip.asset_in) * 1_000_000)),
        )
        vm = _video_material_unchecked(clip.asset_path, plan.width, plan.height)
        seg = VideoSegment(material=vm, target_timerange=target, source_timerange=source)
        script.add_segment(seg, track_name="video_main")

        if clip.text:
            tseg = TextSegment(text=clip.text, timerange=target)
            script.add_segment(tseg, track_name="captions")

    if plan.narration_audio and plan.clips:
        total_us = int(round(plan.clips[-1].audio_end * 1_000_000))
        am = _audio_material_unchecked(plan.narration_audio, total_us)
        aseg = AudioSegment(material=am,
                            target_timerange=Timerange(start=0, duration=total_us),
                            source_timerange=Timerange(start=0, duration=total_us))
        script.add_segment(aseg, track_name="narration")

    return script


def export_capcut_draft(*, plan_path: Path, out_path: Path) -> None:
    plan = EditPlan.model_validate_json(plan_path.read_text(encoding="utf-8"))
    script = _build_script(plan)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    script.dump(str(out_path))


def export_capcut_project(*, plan_path: Path, project_dir: Path,
                          windows_root: str = "C:/Users/sub/Downloads/CapCut Drafts") -> None:
    """Emit draft_content.json + draft_meta_info.json into project_dir."""
    plan = EditPlan.model_validate_json(plan_path.read_text(encoding="utf-8"))
    script = _build_script(plan)

    project_dir.mkdir(parents=True, exist_ok=True)
    name = project_dir.name
    folder_path = f"{windows_root.rstrip('/')}/{name}"
    now_us = int(time.time() * 1_000_000)
    total_us = int(round(plan.clips[-1].audio_end * 1_000_000)) if plan.clips else 0

    script.dump(str(project_dir / "draft_content.json"))

    meta = _meta_scaffold(
        draft_id=str(uuid.uuid4()).upper(),
        name=name,
        folder_path=folder_path,
        root_path=windows_root.rstrip("/"),
        total_duration_us=total_us,
        create_us=now_us,
        modified_us=now_us,
    )
    (project_dir / "draft_meta_info.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def _meta_scaffold(*, draft_id: str, name: str, folder_path: str, root_path: str,
                   total_duration_us: int, create_us: int, modified_us: int) -> dict:
    return {
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
        "draft_cover": "draft_cover.jpg",
        "draft_deeplink_url": "",
        "draft_enterprise_info": {
            "draft_enterprise_extra": "",
            "draft_enterprise_id": "",
            "draft_enterprise_name": "",
            "enterprise_material": [],
        },
        "draft_fold_path": folder_path,
        "draft_id": draft_id,
        "draft_is_ae_produce": False,
        "draft_is_ai_packaging_used": False,
        "draft_is_ai_shorts": False,
        "draft_is_ai_translate": False,
        "draft_is_article_video_draft": False,
        "draft_is_cloud_temp_draft": False,
        "draft_is_from_deeplink": "false",
        "draft_is_invisible": False,
        "draft_is_pippit_draft": False,
        "draft_is_web_article_video": False,
        "draft_materials": [{"type": t, "value": []} for t in (0, 1, 2, 3, 6, 7, 8, 18)],
        "draft_materials_copied_info": [],
        "draft_name": name,
        "draft_need_rename_folder": False,
        "draft_new_version": "",
        "draft_removable_storage_device": "",
        "draft_root_path": root_path,
        "draft_segment_extra_info": [],
        "draft_timeline_materials_size_": 0,
        "draft_type": "",
        "draft_web_article_video_enter_from": "",
        "tm_draft_cloud_completed": 0,
        "tm_draft_cloud_entry_id": 0,
        "tm_draft_cloud_modified": 0,
        "tm_draft_cloud_parent_entry_id": -1,
        "tm_draft_cloud_space_id": 0,
        "tm_draft_cloud_user_id": 0,
        "tm_draft_create": create_us,
        "tm_draft_modified": modified_us,
        "tm_draft_removed": 0,
        "tm_duration": total_duration_us,
    }
