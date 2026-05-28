"""CapCut Desktop (Global) draft_content.json material templates.

Derived from a real sample exported by CapCut 8.5.0 / schema version 360000.
Each factory returns a dict shaped the way CapCut writes it; fields irrelevant
to our use case (matting, beauty presets, AI-gen state, etc.) get neutral
defaults so CapCut accepts the draft without complaining.
"""
from __future__ import annotations

import json
import uuid
from pathlib import Path


def uid() -> str:
    return str(uuid.uuid4()).upper()


def us(seconds: float) -> int:
    return int(round(seconds * 1_000_000))


# ---------- Auxiliary materials ----------

def speed_material() -> dict:
    return {"id": uid(), "type": "speed", "mode": 0, "speed": 1.0, "curve_speed": None}


def placeholder_info_material() -> dict:
    return {
        "id": uid(),
        "type": "placeholder_info",
        "meta_type": "none",
        "res_path": "",
        "res_text": "",
        "error_path": "",
        "error_text": "",
    }


def canvas_material() -> dict:
    return {
        "id": uid(),
        "type": "canvas_color",
        "color": "",
        "blur": 0.0,
        "image": "",
        "album_image": "",
        "image_id": "",
        "image_name": "",
        "source_platform": 0,
        "team_id": "",
    }


def sticker_animation_material() -> dict:
    return {"id": uid(), "type": "sticker_animation", "animations": [], "multi_language_current": "none"}


def sound_channel_mapping_material() -> dict:
    return {"id": uid(), "type": "none", "audio_channel_mapping": 0, "is_config_open": False}


def material_color_material() -> dict:
    return {
        "id": uid(),
        "is_color_clip": False,
        "is_gradient": False,
        "solid_color": "",
        "gradient_colors": [],
        "gradient_percents": [],
        "gradient_angle": 90.0,
        "width": 0.0,
        "height": 0.0,
    }


def loudness_material() -> dict:
    return {
        "id": uid(),
        "enable": False,
        "time_range": None,
        "file_id": "",
        "target_loudness": 0.0,
        "loudness_param": None,
    }


def vocal_separation_material() -> dict:
    return {
        "id": uid(),
        "type": "vocal_separation",
        "choice": 0,
        "removed_sounds": [],
        "time_range": None,
        "production_path": "",
        "final_algorithm": "",
        "enter_from": "",
    }


def beats_material() -> dict:
    return {
        "id": uid(),
        "type": "beats",
        "enable_ai_beats": False,
        "gear": 404,
        "gear_count": 0,
        "mode": 404,
        "user_beats": [],
        "user_delete_ai_beats": None,
        "ai_beats": {
            "melody_url": "",
            "melody_path": "",
            "beats_url": "",
            "beats_path": "",
            "melody_percents": [0.0],
            "beat_speed_infos": [],
        },
    }


# ---------- Primary materials ----------

_IMAGE_EXT = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def video_material(path: Path, width: int, height: int) -> dict:
    is_image = path.suffix.lower() in _IMAGE_EXT
    # Photos get a long virtual duration (CapCut convention: 3h in microseconds);
    # actual on-timeline length is set by the segment's source_timerange.
    duration = 10_800_000_000 if is_image else 0
    return {
        "id": uid(),
        "unique_id": "",
        "type": "photo" if is_image else "video",
        "duration": duration,
        "path": str(path).replace("\\", "/"),
        "media_path": "",
        "local_id": "",
        "has_audio": False,
        "reverse_path": "",
        "intensifies_path": "",
        "reverse_intensifies_path": "",
        "intensifies_audio_path": "",
        "cartoon_path": "",
        "width": width,
        "height": height,
        "category_id": "",
        "category_name": "local",
        "material_id": "",
        "material_name": path.name,
        "material_url": "",
        "crop": {
            "upper_left_x": 0.0, "upper_left_y": 0.0,
            "upper_right_x": 1.0, "upper_right_y": 0.0,
            "lower_left_x": 0.0, "lower_left_y": 1.0,
            "lower_right_x": 1.0, "lower_right_y": 1.0,
        },
        "crop_ratio": "free",
        "audio_fade": None,
        "crop_scale": 1.0,
        "extra_type_option": 0,
        "stable": {"stable_level": 0, "matrix_path": "", "time_range": {"start": 0, "duration": 0}},
        "matting": {
            "flag": 0, "path": "", "interactiveTime": [],
            "has_use_quick_brush": False, "strokes": [], "has_use_quick_eraser": False,
            "expansion": 0, "feather": 0, "reverse": False,
            "custom_matting_id": "", "enable_matting_stroke": False,
            "is_clould": False, "mask_video_path": "", "cloud_product_fps": 0.0,
        },
        "source": 0,
        "source_platform": 0,
        "formula_id": "",
        "check_flag": 62978047,
        "is_unified_beauty_mode": False,
        "is_set_beauty_mode": False,
        "object_locked": None,
        "smart_motion": None,
        "multi_camera_info": None,
        "freeze": None,
        "picture_from": "none",
        "picture_set_category_id": "",
        "picture_set_category_name": "",
        "team_id": "",
        "local_material_id": "",
        "origin_material_id": "",
        "request_id": "",
        "has_sound_separated": False,
        "is_text_edit_overdub": False,
        "is_ai_generate_content": False,
        "aigc_type": "none",
        "is_copyright": False,
        "aigc_history_id": "",
        "aigc_item_id": "",
        "local_material_from": "",
        "smart_match_info": None,
        "beauty_face_preset_infos": [],
        "beauty_body_preset_id": "",
        "beauty_face_auto_preset": {"preset_id": "", "name": "", "rate_map": "", "scene": ""},
        "beauty_face_auto_preset_infos": [],
        "beauty_body_auto_preset": None,
        "live_photo_timestamp": -1,
        "live_photo_cover_path": "",
        "content_feature_info": None,
        "corner_pin": None,
        "surface_trackings": [],
        "video_algorithm": {
            "algorithms": [], "time_range": {"start": 0, "duration": 0},
            "path": "", "gameplay_configs": [], "ai_in_painting_config": [],
            "complement_frame_config": None, "motion_blur_config": None,
            "deflicker": None, "noise_reduction": None, "quality_enhance": None,
            "super_resolution": None, "ai_background_configs": [],
            "smart_complement_frame": None, "aigc_generate": None,
            "aigc_generate_list": [], "mouth_shape_driver": None,
            "ai_expression_driven": None, "ai_motion_driven": None,
            "image_interpretation": None,
            "story_video_modify_video_config": {
                "task_id": "", "is_overwrite_last_video": False, "tracker_task_id": "",
            },
            "skip_algorithm_index": [],
        },
        "video_mask_stroke": {
            "resource_id": "", "path": "", "type": "", "color": "",
            "size": 0.0, "alpha": 0.0, "distance": 0.0, "texture": 0.0,
            "horizontal_shift": 0.0, "vertical_shift": 0.0,
        },
        "video_mask_shadow": {
            "resource_id": "", "path": "", "color": "",
            "alpha": 0.0, "blur": 0.0, "distance": 0.0, "angle": 0.0,
        },
    }


def audio_material(path: Path, duration_us: int) -> dict:
    return {
        "id": uid(),
        "type": "extract_music",
        "path": str(path).replace("\\", "/"),
        "name": path.name,
        "duration": duration_us,
        "category_id": "",
        "category_name": "local",
        "music_id": "",
        "music_source": "local",
        "source_platform": 0,
        "app_id": 0,
        "check_flag": 1,
        "copyright_limit_type": "none",
        "effect_id": "",
        "formula_id": "",
        "intensifies_path": "",
        "is_ai_clone_tone": False,
        "is_ai_clone_tone_post": False,
        "is_text_edit_overdub": False,
        "is_ugc": False,
        "local_material_id": "",
        "lyric_type": 0,
        "mock_tone_speaker": "",
        "moyin_emotion": "",
        "pgc_id": "",
        "pgc_name": "",
        "query": "",
        "request_id": "",
        "resource_id": "",
        "search_id": "",
        "similiar_music_info": None,
        "sound_separate_type": 0,
        "source_from": "",
        "team_id": "",
        "text_id": "",
        "third_resource_id": "",
        "tone_category_id": "",
        "tone_category_name": "",
        "tone_effect_id": "",
        "tone_effect_name": "",
        "tone_emotion_name_key": "",
        "tone_emotion_role": "",
        "tone_emotion_scale": 0.0,
        "tone_emotion_selection": "",
        "tone_emotion_style": "",
        "tone_platform": "",
        "tone_second_category_id": "",
        "tone_second_category_name": "",
        "tone_speaker": "",
        "tone_type": "",
        "tts_benefit_info": None,
        "tts_generate_scene": "",
        "tts_task_id": "",
        "unique_id": "",
        "video_id": "",
        "wave_points": [],
        "ai_music_enter_from": "",
        "ai_music_generate_scene": "",
        "ai_music_type": "",
        "aigc_history_id": "",
        "aigc_item_id": "",
        "cloned_model_type": 0,
    }


_DEFAULT_FONT_PATH = ""


def text_material(text: str, *, font_path: str = _DEFAULT_FONT_PATH, text_size: int = 30) -> dict:
    content = {
        "text": text,
        "styles": [
            {
                "fill": {"content": {"render_type": "solid", "solid": {"color": [1, 1, 1]}}},
                "font": {"path": font_path, "id": ""},
                "strokes": [{
                    "content": {"render_type": "solid", "solid": {"color": [0, 0, 0]}},
                    "width": 0.02, "mode": 0,
                }],
                "size": 12,
                "useLetterColor": True,
                "range": [0, len(text)],
            }
        ],
    }
    return {
        "id": uid(),
        "type": "subtitle",
        "content": json.dumps(content, ensure_ascii=False),
        "name": "",
        "recognize_text": "",
        "recognize_model": "",
        "recognize_task_id": "",
        "recognize_type": 0,
        "punc_model": "",
        "base_content": "",
        "words": {"start_time": [], "end_time": [], "text": []},
        "current_words": {"start_time": [], "end_time": [], "text": []},
        "global_alpha": 1.0,
        "combo_info": {"text_templates": []},
        "caption_template_info": {
            "resource_id": "", "third_resource_id": "", "resource_name": "",
            "category_id": "", "category_name": "", "effect_id": "",
            "request_id": "", "path": "", "is_new": False, "source_platform": 0,
        },
        "layer_weight": 1,
        "letter_spacing": 0.0,
        "text_curve": None,
        "text_loop_on_path": False,
        "offset_on_path": 0.0,
        "enable_path_typesetting": False,
        "text_exceeds_path_process_type": 0,
        "text_typesetting_paths": None,
        "text_typesetting_paths_file": "",
        "text_typesetting_path_index": 0,
        "line_spacing": 0.02,
        "has_shadow": False,
        "shadow_color": "#000000",
        "shadow_alpha": 0.0,
        "shadow_smoothing": 1.0,
        "shadow_distance": 5.0,
        "shadow_point": {"x": 0.0, "y": 0.0},
        "shadow_angle": -45.0,
        "shadow_thickness_projection_enable": False,
        "shadow_thickness_projection_angle": 0.0,
        "shadow_thickness_projection_distance": 0.0,
        "border_alpha": 1.0,
        "border_color": "#000000",
        "border_width": 0.02,
        "border_mode": 0,
        "style_name": "",
        "text_color": "#ffffff",
        "text_alpha": 1.0,
        "font_name": "",
        "font_title": "none",
        "font_size": 12.0,
        "font_path": font_path,
        "font_id": "",
        "font_resource_id": "",
        "initial_scale": 1.0,
        "font_url": "",
        "typesetting": 0,
        "alignment": 1,
        "line_feed": 1,
        "use_effect_default_color": True,
        "is_rich_text": False,
        "shape_clip_x": False,
        "shape_clip_y": False,
        "ktv_color": "",
        "text_to_audio_ids": [],
        "bold_width": 0.0,
        "italic_degree": 0,
        "underline": False,
        "underline_width": 0.05,
        "underline_offset": 0.22,
        "sub_type": 0,
        "check_flag": 47,
        "text_size": text_size,
        "font_category_name": "",
        "font_source_platform": 0,
        "font_third_resource_id": "",
        "font_category_id": "",
        "add_type": 2,
        "operation_type": 0,
        "fonts": [],
        "background_color": "#000000",
        "background_alpha": 0.0,
        "background_style": 0,
        "background_fill": 0,
        "background_height": 0.14,
        "background_horizontal_offset": 0.0,
        "background_vertical_offset": 0.0,
        "background_round_radius": 0.0,
        "background_width": 0.14,
        "fixed_height": -1.0,
        "fixed_width": -1.0,
        "force_apply_line_max_width": False,
        "line_max_width": 0.82,
        "preset_category": "",
        "preset_category_id": "",
        "preset_has_set_alignment": False,
        "preset_id": "",
        "preset_index": 0,
        "preset_name": "",
        "single_char_bg_alpha": 0.0,
        "single_char_bg_color": "#000000",
        "single_char_bg_enable": False,
        "single_char_bg_height": 0.14,
        "single_char_bg_horizontal_offset": 0.0,
        "single_char_bg_round_radius": 0.0,
        "single_char_bg_vertical_offset": 0.0,
        "single_char_bg_width": 0.14,
        "source_from": "",
        "ssml_content": "",
        "sub_template_id": "",
        "subtitle_keywords": None,
        "subtitle_keywords_config": None,
        "subtitle_template_original_fontsize": 0,
        "text_preset_resource_id": "",
        "translate_original_text": "",
        "tts_auto_update": False,
        "cutoff_postfix": "",
        "current_words_recognize_type": 0,
        "enable_text_motion_blur": False,
        "group_id": "",
        "initial_scale_x": 1.0,
        "initial_scale_y": 1.0,
        "is_batch_replace": False,
        "is_lyric_effect": False,
        "is_words_linear": False,
        "language": "",
        "lyric_group_id": "",
        "lyrics_template": None,
        "multi_language_current": "none",
        "oneline_cutoff": 0,
        "original_size": [0.0, 0.0],
        "relevance_segment": [],
    }


# ---------- Segments ----------

def video_segment(*, material_id: str, target_start_us: int, target_dur_us: int,
                  source_start_us: int, source_dur_us: int,
                  extra_refs: list[str], render_index: int = 0,
                  track_render_index: int = 0, volume: float = 1.0,
                  track_attribute: int = 1) -> dict:
    return {
        "id": uid(),
        "material_id": material_id,
        "source_timerange": {"start": source_start_us, "duration": source_dur_us},
        "target_timerange": {"start": target_start_us, "duration": target_dur_us},
        "render_timerange": {"start": 0, "duration": 0},
        "desc": "",
        "state": 0,
        "speed": 1.0,
        "is_loop": False,
        "is_tone_modify": False,
        "reverse": False,
        "intensifies_audio": False,
        "cartoon": False,
        "volume": volume,
        "last_nonzero_volume": 1.0,
        "clip": {
            "scale": {"x": 1.0, "y": 1.0},
            "rotation": 0.0,
            "transform": {"x": 0.0, "y": 0.0},
            "flip": {"vertical": False, "horizontal": False},
            "alpha": 1.0,
        },
        "uniform_scale": {"on": True, "value": 1.0},
        "extra_material_refs": extra_refs,
        "render_index": render_index,
        "keyframe_refs": [],
        "enable_lut": True,
        "enable_adjust": True,
        "enable_hsl": False,
        "visible": True,
        "group_id": "",
        "enable_color_curves": True,
        "enable_hsl_curves": True,
        "track_render_index": track_render_index,
        "hdr_settings": {"mode": 1, "intensity": 1.0, "nits": 1000},
        "enable_color_wheels": True,
        "track_attribute": track_attribute,
        "is_placeholder": False,
        "template_id": "",
        "enable_smart_color_adjust": False,
        "template_scene": "default",
        "common_keyframes": [],
        "caption_info": None,
        "responsive_layout": {
            "enable": False, "target_follow": "",
            "size_layout": 0, "horizontal_pos_layout": 0, "vertical_pos_layout": 0,
        },
        "enable_color_match_adjust": False,
        "enable_color_correct_adjust": False,
        "enable_adjust_mask": False,
        "raw_segment_id": "",
        "lyric_keyframes": None,
        "enable_video_mask": True,
        "digital_human_template_group_id": "",
        "color_correct_alg_result": "",
        "source": "segmentsourcenormal",
        "enable_mask_stroke": False,
        "enable_mask_shadow": False,
        "enable_color_adjust_pro": False,
    }


def audio_segment(*, material_id: str, target_start_us: int, target_dur_us: int,
                  source_start_us: int, source_dur_us: int,
                  extra_refs: list[str], volume: float = 1.0,
                  track_render_index: int = 0) -> dict:
    seg = video_segment(
        material_id=material_id,
        target_start_us=target_start_us, target_dur_us=target_dur_us,
        source_start_us=source_start_us, source_dur_us=source_dur_us,
        extra_refs=extra_refs,
        volume=volume,
        track_render_index=track_render_index,
        track_attribute=0,
    )
    seg["enable_video_mask"] = False
    return seg


def text_segment(*, material_id: str, target_start_us: int, target_dur_us: int,
                 extra_refs: list[str], render_index: int = 14000,
                 track_render_index: int = 0) -> dict:
    return {
        "id": uid(),
        "material_id": material_id,
        "source_timerange": None,
        "target_timerange": {"start": target_start_us, "duration": target_dur_us},
        "render_timerange": {"start": 0, "duration": 0},
        "desc": "",
        "state": 0,
        "speed": 1.0,
        "is_loop": False,
        "is_tone_modify": False,
        "reverse": False,
        "intensifies_audio": False,
        "cartoon": False,
        "volume": 1.0,
        "last_nonzero_volume": 1.0,
        "clip": {
            "scale": {"x": 1.0, "y": 1.0},
            "rotation": 0.0,
            "transform": {"x": 0.0, "y": 0.3},
            "flip": {"vertical": False, "horizontal": False},
            "alpha": 1.0,
        },
        "uniform_scale": {"on": True, "value": 1.0},
        "extra_material_refs": extra_refs,
        "render_index": render_index,
        "keyframe_refs": [],
        "enable_lut": True,
        "enable_adjust": True,
        "enable_hsl": False,
        "visible": True,
        "group_id": "",
        "enable_color_curves": True,
        "enable_hsl_curves": True,
        "track_render_index": track_render_index,
        "hdr_settings": {"mode": 1, "intensity": 1.0, "nits": 1000},
        "enable_color_wheels": True,
        "track_attribute": 0,
        "is_placeholder": False,
        "template_id": "",
        "enable_smart_color_adjust": False,
        "template_scene": "default",
        "common_keyframes": [],
        "caption_info": None,
        "responsive_layout": {
            "enable": False, "target_follow": "",
            "size_layout": 0, "horizontal_pos_layout": 0, "vertical_pos_layout": 0,
        },
        "enable_color_match_adjust": False,
        "enable_color_correct_adjust": False,
        "enable_adjust_mask": False,
        "raw_segment_id": "",
        "lyric_keyframes": None,
        "enable_video_mask": False,
        "digital_human_template_group_id": "",
        "color_correct_alg_result": "",
        "source": "segmentsourcenormal",
        "enable_mask_stroke": False,
        "enable_mask_shadow": False,
        "enable_color_adjust_pro": False,
    }


# ---------- Materials skeleton (all 50+ buckets CapCut expects) ----------

_MATERIAL_BUCKETS = (
    "flowers", "videos", "tail_leaders", "audios", "images", "texts", "effects",
    "stickers", "canvases", "transitions", "audio_effects", "audio_fades",
    "beats", "material_animations", "placeholders", "placeholder_infos",
    "speeds", "common_mask", "chromas", "text_templates", "realtime_denoises",
    "audio_pannings", "audio_pitch_shifts", "video_trackings", "hsl", "drafts",
    "color_curves", "hsl_curves", "primary_color_wheels", "log_color_wheels",
    "video_effects", "audio_balances", "handwrites", "manual_deformations",
    "manual_beautys", "plugin_effects", "sound_channel_mappings",
    "green_screens", "shapes", "material_colors", "digital_humans",
    "digital_human_model_dressing", "smart_crops", "ai_translates",
    "audio_track_indexes", "loudnesses", "vocal_beautifys",
    "vocal_separations", "smart_relights", "time_marks", "multi_language_refs",
    "video_shadows", "video_strokes", "video_radius",
)


def empty_materials() -> dict[str, list]:
    return {k: [] for k in _MATERIAL_BUCKETS}


# ---------- Root scaffold ----------

# Empty bin shape — type buckets CapCut keeps in draft_meta_info.draft_materials.
_DRAFT_MATERIAL_TYPES = (0, 1, 2, 3, 6, 7, 8, 18)


def empty_draft_materials() -> list[dict]:
    return [{"type": t, "value": []} for t in _DRAFT_MATERIAL_TYPES]


def meta_scaffold(*, draft_id: str, name: str, folder_path: str, root_path: str,
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
        "draft_materials": empty_draft_materials(),
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


def root_scaffold(*, width: int, height: int, fps: float, total_duration_us: int) -> dict:
    return {
        "id": uid(),
        "version": 360000,
        "new_version": "171.0.0",
        "draft_type": "video",
        "platform": {
            "os": "windows",
            "os_version": "10.0.0",
            "app_id": 359289,
            "app_version": "8.5.0",
            "app_source": "cc",
            "device_id": "",
            "hard_disk_id": "",
            "mac_address": "",
        },
        "last_modified_platform": {
            "os": "windows",
            "os_version": "10.0.0",
            "app_id": 359289,
            "app_version": "8.5.0",
            "app_source": "cc",
            "device_id": "",
            "hard_disk_id": "",
            "mac_address": "",
        },
        "canvas_config": {"width": width, "height": height, "ratio": "9:16", "background": None},
        "duration": total_duration_us,
        "fps": fps,
        "color_space": 0,
        "config": {
            "video_mute": True,
            "record_audio_last_index": 1,
            "extract_audio_last_index": 1,
            "original_sound_last_index": 2,
            "subtitle_recognition_id": "",
            "subtitle_taskinfo": [],
            "lyrics_recognition_id": "",
        },
        "mutable_config": None,
        "extra_info": None,
        "free_render_index_mode_on": False,
        "render_index_track_mode_on": True,
        "is_drop_frame_timecode": False,
        "keyframe_graph_list": [],
        "keyframes": {
            "videos": [], "audios": [], "texts": [], "stickers": [],
            "filters": [], "adjusts": [], "handwrites": [], "effects": [],
        },
        "relationships": [],
        "time_marks": [],
        "name": "",
        "path": "",
        "source": "default",
        "cover": None,
        "static_cover_image_path": "",
        "retouch_cover": None,
        "create_time": 0,
        "update_time": 0,
        "lyrics_effects": [],
        "smart_ads_info": None,
        "function_assistant_info": None,
        "group_container": None,
        "uneven_animation_template_info": None,
    }
