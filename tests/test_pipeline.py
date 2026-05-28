import json
from pathlib import Path

from typer.testing import CliRunner

from shoppingshorts.cli import app

runner = CliRunner()


def _seed_assets(asset_dir: Path) -> None:
    asset_dir.mkdir(parents=True, exist_ok=True)
    for name in ("a.mp4", "b.mp4", "c.jpg"):
        (asset_dir / name).write_bytes(b"")


def test_cli_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "analyze" in result.output
    assert "export" in result.output


def test_end_to_end(tmp_path: Path):
    script_txt = tmp_path / "script.txt"
    script_txt.write_text(
        "이 제품 진짜 대박이에요. 가격도 합리적이고요. 지금 바로 확인해보세요.",
        encoding="utf-8",
    )
    assets = tmp_path / "assets"
    _seed_assets(assets)
    out = tmp_path / "out" / "draft_content.json"

    result = runner.invoke(
        app,
        [
            "run",
            "--file",
            str(tmp_path / "ref.mp4"),
            "--script",
            str(script_txt),
            "--tts",
            "silent",
            "--assets",
            str(assets),
            "--work",
            str(tmp_path / ".work"),
            "--out",
            str(out),
        ],
    )
    assert result.exit_code == 0, result.output
    assert out.exists()

    draft = json.loads(out.read_text(encoding="utf-8"))
    assert draft["canvas_config"]["width"] == 1080
    assert draft["canvas_config"]["height"] == 1920
    assert len(draft["materials"]["videos"]) == 3
    assert len(draft["materials"]["texts"]) == 3
    assert any(t["type"] == "video" for t in draft["tracks"])
    assert any(t["type"] == "text" for t in draft["tracks"])
