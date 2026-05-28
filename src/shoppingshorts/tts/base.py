from __future__ import annotations

import json
import wave
from abc import ABC, abstractmethod
from pathlib import Path

from ..types import Narration, NarrationClip, Script


class TTSProvider(ABC):
    name: str

    @abstractmethod
    def synth_sentence(self, text: str, out_path: Path) -> float:
        ...


def get_provider(name: str, *, user_audio: Path | None = None) -> TTSProvider:
    name = name.lower()
    if name == "elevenlabs":
        from .elevenlabs import ElevenLabsProvider
        return ElevenLabsProvider()
    if name == "minimax":
        from .minimax import MiniMaxProvider
        return MiniMaxProvider()
    if name == "user":
        from .user_provided import UserProvidedProvider
        return UserProvidedProvider(audio_path=user_audio)
    if name == "silent":
        return SilentProvider()
    raise ValueError(f"unknown TTS provider: {name}")


def synthesize(*, script_path: Path, provider: TTSProvider, out_dir: Path) -> Narration:
    out_dir.mkdir(parents=True, exist_ok=True)
    script = Script.model_validate_json(script_path.read_text(encoding="utf-8"))
    clips: list[NarrationClip] = []
    for s in script.sentences:
        out = out_dir / f"sent_{s.index:03d}.wav"
        dur = provider.synth_sentence(s.text, out)
        clips.append(NarrationClip(sentence_index=s.index, audio_path=str(out), duration=dur))
    return Narration(clips=clips)


class SilentProvider(TTSProvider):
    name = "silent"

    def __init__(self, seconds_per_char: float = 0.06, rate: int = 24000):
        self.spc = seconds_per_char
        self.rate = rate

    def synth_sentence(self, text: str, out_path: Path) -> float:
        duration = max(1.0, len(text) * self.spc)
        _write_silent_wav(out_path, duration, self.rate)
        return duration


def _write_silent_wav(path: Path, duration_s: float, rate: int = 24000) -> None:
    n_frames = int(rate * duration_s)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(b"\x00\x00" * n_frames)
