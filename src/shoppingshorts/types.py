from pydantic import BaseModel


class SceneSegment(BaseModel):
    start: float
    end: float


class TranscriptLine(BaseModel):
    start: float
    end: float
    text: str


class ReferenceAnalysis(BaseModel):
    source: str
    duration: float
    width: int
    height: int
    fps: float
    scenes: list[SceneSegment]
    transcript: list[TranscriptLine]
    avg_cut_seconds: float
    structure_notes: str = ""


class ScriptSentence(BaseModel):
    index: int
    text: str


class Script(BaseModel):
    sentences: list[ScriptSentence]


class NarrationClip(BaseModel):
    sentence_index: int
    audio_path: str
    duration: float


class Narration(BaseModel):
    clips: list[NarrationClip]
    full_audio_path: str | None = None


class TimelineClip(BaseModel):
    sentence_index: int
    asset_path: str
    audio_start: float
    audio_end: float
    asset_in: float = 0.0
    asset_out: float | None = None
    text: str


class EditPlan(BaseModel):
    width: int
    height: int
    fps: float
    clips: list[TimelineClip]
    narration_audio: str | None = None
