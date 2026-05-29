"""CapCut draft builder built from a real working sample as canonical template.

We load the user's actual draft_content.json (committed at
tests/fixtures/sample_capcut/minimal/draft_content.json — known to work on
their CapCut Desktop 8.5.0) and surgically swap in our own segments,
materials, and durations while preserving every other field exactly as
CapCut wrote it. This sidesteps schema reverse-engineering entirely.

Approach:
  1. Deepcopy the template
  2. Use its first video material + segment + each aux material as cookie
     cutters for our own clips (one set per clip)
  3. Clear the rest of the segments / primary materials
  4. Rewrite duration to match our timeline
  5. Generate fresh UUIDs everywhere so IDs don't collide with the original
"""
from __future__ import annotations

import copy
import json
import time
import uuid
from pathlib import Path

from ..types import EditPlan

_TEMPLATE_PATH = Path(__file__).parent / "_template.json"
_IMAGE_EXT = {".jpg", ".jpeg", ".png", ".bmp", ".webp", ".gif"}


def _uid() -> str:
    return str(uuid.uuid4()).upper()


def _us(seconds: float) -> int:
    return int(round(seconds * 1_000_000))


def _load_template() -> dict:
    return json.loads(_TEMPLATE_PATH.read_text(encoding="utf-8"))


def _first_with_aux(template: dict) -> tuple[dict, dict, dict]:
    """Return (first_video_material, first_video_segment, aux_refs_by_section)
    from the template — used as cookie cutters."""
    vm = template["materials"]["videos"][0]
    seg = template["tracks"][0]["segments"][0]
    aux_by_section: dict[str, dict] = {}
    by_id = {m["id"]: (section, m) for section, items in template["materials"].items()
             if isinstance(items, list) for m in items if isinstance(m, dict) and "id" in m}
    for ref_id in seg["extra_material_refs"]:
        section, m = by_id[ref_id]
        aux_by_section[section] = m
    return vm, seg, aux_by_section


def _build_draft_content(plan: EditPlan) -> dict:
    tpl = _load_template()

    # -- Cookie cutters from template's first video segment + its aux refs
    src_video_mat, src_video_seg, video_aux = _first_with_aux(tpl)

    # First text material + segment + its aux refs (from text track)
    text_track = next(t for t in tpl["tracks"] if t["type"] == "text")
    src_text_seg = text_track["segments"][0]
    src_text_mat = next(m for m in tpl["materials"]["texts"] if m["id"] == src_text_seg["material_id"])
    text_aux: dict[str, dict] = {}
    by_id = {m["id"]: (section, m) for section, items in tpl["materials"].items()
             if isinstance(items, list) for m in items if isinstance(m, dict) and "id" in m}
    for ref_id in src_text_seg["extra_material_refs"]:
        section, m = by_id[ref_id]
        text_aux[section] = m

    # Audio (template has audio segments — use first as cookie cutter)
    audio_track = next((t for t in tpl["tracks"] if t["type"] == "audio"), None)
    src_audio_seg = audio_track["segments"][0] if audio_track and audio_track["segments"] else None
    src_audio_mat = None
    audio_aux: dict[str, dict] = {}
    if src_audio_seg:
        src_audio_mat = next(m for m in tpl["materials"]["audios"]
                             if m["id"] == src_audio_seg["material_id"])
        for ref_id in src_audio_seg["extra_material_refs"]:
            section, m = by_id[ref_id]
            audio_aux[section] = m

    # -- Start fresh: keep all material buckets but clear primary lists.
    out = copy.deepcopy(tpl)
    out["id"] = _uid()
    out["materials"]["videos"] = []
    out["materials"]["audios"] = []
    out["materials"]["texts"] = []
    for section in list(video_aux.keys()) + list(text_aux.keys()) + list(audio_aux.keys()):
        out["materials"][section] = []

    # Keep only the video + text tracks the template has at positions 0 and 2;
    # drop everything else (PIP video, extra text/sticker, all audio tracks).
    keep_video = next(t for t in tpl["tracks"] if t["type"] == "video" and t.get("flag") == 0)
    keep_text = text_track
    keep_audio = audio_track  # we'll empty its segments

    video_track = copy.deepcopy(keep_video)
    video_track["id"] = _uid()
    video_track["segments"] = []
    text_track_out = copy.deepcopy(keep_text)
    text_track_out["id"] = _uid()
    text_track_out["segments"] = []
    audio_track_out = copy.deepcopy(keep_audio) if keep_audio else None
    if audio_track_out:
        audio_track_out["id"] = _uid()
        audio_track_out["segments"] = []

    # -- Materialize our clips.
    for i, clip in enumerate(plan.clips):
        target_start = _us(clip.audio_start)
        target_dur = _us(clip.audio_end - clip.audio_start)
        asset_dur = _us((clip.asset_out or (clip.audio_end - clip.audio_start)) - clip.asset_in)
        source_start = _us(clip.asset_in)

        # ---- Video material
        vm = copy.deepcopy(src_video_mat)
        vm["id"] = _uid()
        asset = Path(clip.asset_path)
        vm["path"] = str(asset).replace("\\", "/")
        vm["material_name"] = asset.name
        vm["width"] = plan.width
        vm["height"] = plan.height
        if asset.suffix.lower() in _IMAGE_EXT:
            vm["type"] = "photo"
            vm["duration"] = 10_800_000_000
        else:
            vm["type"] = "video"
            vm["duration"] = max(asset_dur, target_dur)
        if "video_algorithm" in vm and isinstance(vm["video_algorithm"], dict):
            vm["video_algorithm"].setdefault("time_range", {"start": 0, "duration": 0})
            vm["video_algorithm"]["time_range"] = {"start": 0, "duration": asset_dur}
        out["materials"]["videos"].append(vm)

        # ---- Per-segment aux materials (cloned from template's aux pool)
        new_video_aux_refs: list[str] = []
        for section, src_m in video_aux.items():
            m = copy.deepcopy(src_m)
            m["id"] = _uid()
            out["materials"][section].append(m)
            new_video_aux_refs.append(m["id"])

        # ---- Video segment
        seg = copy.deepcopy(src_video_seg)
        seg["id"] = _uid()
        seg["material_id"] = vm["id"]
        seg["extra_material_refs"] = new_video_aux_refs
        seg["source_timerange"] = {"start": source_start, "duration": asset_dur}
        seg["target_timerange"] = {"start": target_start, "duration": target_dur}
        video_track["segments"].append(seg)

        # ---- Text material + segment
        if clip.text:
            tm = copy.deepcopy(src_text_mat)
            tm["id"] = _uid()
            # Content is a JSON-encoded string; rewrite the text + range.
            content_obj = json.loads(tm["content"])
            content_obj["text"] = clip.text
            if content_obj.get("styles"):
                content_obj["styles"][0]["range"] = [0, len(clip.text)]
            tm["content"] = json.dumps(content_obj, ensure_ascii=False)
            out["materials"]["texts"].append(tm)

            new_text_aux_refs: list[str] = []
            for section, src_m in text_aux.items():
                m = copy.deepcopy(src_m)
                m["id"] = _uid()
                out["materials"][section].append(m)
                new_text_aux_refs.append(m["id"])

            tseg = copy.deepcopy(src_text_seg)
            tseg["id"] = _uid()
            tseg["material_id"] = tm["id"]
            tseg["extra_material_refs"] = new_text_aux_refs
            tseg["target_timerange"] = {"start": target_start, "duration": target_dur}
            # render_index increments per text segment in the template; keep that.
            tseg["render_index"] = src_text_seg["render_index"] + i
            text_track_out["segments"].append(tseg)

    # ---- Narration audio (single segment spanning the timeline)
    total_us = _us(plan.clips[-1].audio_end) if plan.clips else 0
    if plan.narration_audio and src_audio_seg and audio_track_out is not None:
        am = copy.deepcopy(src_audio_mat)
        am["id"] = _uid()
        am["path"] = plan.narration_audio.replace("\\", "/")
        am["name"] = Path(plan.narration_audio).name
        am["duration"] = total_us
        out["materials"]["audios"].append(am)

        new_audio_aux_refs: list[str] = []
        for section, src_m in audio_aux.items():
            m = copy.deepcopy(src_m)
            m["id"] = _uid()
            out["materials"][section].append(m)
            new_audio_aux_refs.append(m["id"])

        aseg = copy.deepcopy(src_audio_seg)
        aseg["id"] = _uid()
        aseg["material_id"] = am["id"]
        aseg["extra_material_refs"] = new_audio_aux_refs
        aseg["source_timerange"] = {"start": 0, "duration": total_us}
        aseg["target_timerange"] = {"start": 0, "duration": total_us}
        audio_track_out["segments"].append(aseg)

    # -- Assemble tracks (preserve template order: video, text, audio).
    out["tracks"] = [video_track, text_track_out]
    if audio_track_out and audio_track_out["segments"]:
        out["tracks"].append(audio_track_out)

    out["duration"] = total_us
    out["canvas_config"]["width"] = plan.width
    out["canvas_config"]["height"] = plan.height
    out["fps"] = plan.fps

    return out


def export_capcut_draft(*, plan_path: Path, out_path: Path) -> None:
    plan = EditPlan.model_validate_json(plan_path.read_text(encoding="utf-8"))
    draft = _build_draft_content(plan)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(draft, ensure_ascii=False, indent=2), encoding="utf-8")


def export_capcut_project(*, plan_path: Path, project_dir: Path,
                          windows_root: str = "C:/Users/sub/Downloads/CapCut Drafts") -> None:
    plan = EditPlan.model_validate_json(plan_path.read_text(encoding="utf-8"))
    draft = _build_draft_content(plan)

    project_dir.mkdir(parents=True, exist_ok=True)
    name = project_dir.name
    folder_path = f"{windows_root.rstrip('/')}/{name}"
    now_us = int(time.time() * 1_000_000)

    (project_dir / "draft_content.json").write_text(
        json.dumps(draft, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    meta = _meta_scaffold(
        draft_id=_uid(),
        name=name,
        folder_path=folder_path,
        root_path=windows_root.rstrip("/"),
        total_duration_us=draft["duration"],
        create_us=now_us,
        modified_us=now_us,
    )
    (project_dir / "draft_meta_info.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def _meta_scaffold(*, draft_id, name, folder_path, root_path,
                   total_duration_us, create_us, modified_us) -> dict:
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
