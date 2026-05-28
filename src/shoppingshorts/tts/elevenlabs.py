from pathlib import Path

from .base import TTSProvider


# STUB: wire up elevenlabs SDK (ElevenLabs(api_key=...).text_to_speech.convert(...))
# and write the returned audio to out_path. Return its real duration (probe with
# wave / ffprobe). Until then this raises so the user can fall back to --provider user.
class ElevenLabsProvider(TTSProvider):
    name = "elevenlabs"

    def synth_sentence(self, text: str, out_path: Path) -> float:
        raise NotImplementedError("ElevenLabs adapter not yet implemented")
