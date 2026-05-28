import re
from pathlib import Path

from ..types import Script, ScriptSentence


_SPLIT_RE = re.compile(r"(?<=[.!?。！？])\s+|\n+")


def load_script(path: Path) -> Script:
    text = path.read_text(encoding="utf-8").strip()
    parts = [p.strip() for p in _SPLIT_RE.split(text) if p.strip()]
    sentences = [ScriptSentence(index=i, text=t) for i, t in enumerate(parts)]
    return Script(sentences=sentences)
