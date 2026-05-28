import shutil
import wave
from pathlib import Path

from .base import TTSProvider


class UserProvidedProvider(TTSProvider):
    name = "user"

    def __init__(self, audio_path: Path | None = None):
        # When the user pre-records the whole narration as one file, we copy it
        # in for sentence 0 and write zero-length placeholders for the rest.
        # Per-sentence audio is a future option (audio_dir).
        self.audio_path = audio_path
        self._used = False

    def synth_sentence(self, text: str, out_path: Path) -> float:
        if self.audio_path and not self._used:
            shutil.copyfile(self.audio_path, out_path)
            self._used = True
            return _wav_duration(out_path)
        # placeholder for remaining sentences
        with wave.open(str(out_path), "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(24000)
            w.writeframes(b"")
        return 0.0


def _wav_duration(path: Path) -> float:
    with wave.open(str(path), "rb") as w:
        return w.getnframes() / float(w.getframerate())
