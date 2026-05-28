from pathlib import Path

from .base import TTSProvider


# STUB: call MiniMax T2A v2 (https://api.minimax.chat/v1/t2a_v2) with group_id +
# api_key, voice_id from env, write hex-decoded audio to out_path.
class MiniMaxProvider(TTSProvider):
    name = "minimax"

    def synth_sentence(self, text: str, out_path: Path) -> float:
        raise NotImplementedError("MiniMax adapter not yet implemented")
