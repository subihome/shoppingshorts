from pathlib import Path
from typing import Optional

import typer
from rich import print

from .analyze import analyze_reference
from .capcut import export_capcut_draft
from .plan import build_plan
from .script import generate_script, load_script
from .tts import get_provider, synthesize

app = typer.Typer(no_args_is_help=True, add_completion=False)


@app.command()
def analyze(
    url: Optional[str] = typer.Option(None, "--url"),
    file: Optional[Path] = typer.Option(None, "--file"),
    out: Path = typer.Option(Path("analysis.json"), "--out"),
):
    """Analyze a reference shopping short (URL or local file)."""
    if not url and not file:
        raise typer.BadParameter("provide --url or --file")
    result = analyze_reference(url=url, file=file)
    out.write_text(result.model_dump_json(indent=2), encoding="utf-8")
    print(f"[green]wrote[/green] {out}")


@app.command()
def script(
    from_user: Optional[Path] = typer.Option(None, "--from-user"),
    auto: bool = typer.Option(False, "--auto"),
    analysis: Path = typer.Option(Path("analysis.json"), "--analysis"),
    out: Path = typer.Option(Path("script.json"), "--out"),
):
    """Load user-written script or auto-generate from analysis."""
    if auto:
        s = generate_script(analysis_path=analysis)
    elif from_user:
        s = load_script(from_user)
    else:
        raise typer.BadParameter("provide --from-user PATH or --auto")
    out.write_text(s.model_dump_json(indent=2), encoding="utf-8")
    print(f"[green]wrote[/green] {out}")


@app.command()
def tts(
    script_path: Path = typer.Option(Path("script.json"), "--script"),
    provider: str = typer.Option("silent", "--provider", help="elevenlabs | minimax | user | silent"),
    audio: Optional[Path] = typer.Option(None, "--audio", help="user-provided wav (for --provider user)"),
    out_dir: Path = typer.Option(Path("./tts_out"), "--out-dir"),
):
    """Synthesize narration (or wire up user-provided audio)."""
    p = get_provider(provider, user_audio=audio)
    narration = synthesize(script_path=script_path, provider=p, out_dir=out_dir)
    (out_dir / "narration.json").write_text(narration.model_dump_json(indent=2), encoding="utf-8")
    print(f"[green]wrote[/green] {out_dir/'narration.json'}")


@app.command()
def plan(
    analysis: Path = typer.Option(Path("analysis.json"), "--analysis"),
    script_path: Path = typer.Option(Path("script.json"), "--script"),
    narration: Optional[Path] = typer.Option(None, "--narration"),
    assets: Path = typer.Option(..., "--assets"),
    out: Path = typer.Option(Path("plan.json"), "--out"),
):
    """Build edit plan: match script sentences to /assets clips."""
    p = build_plan(
        analysis_path=analysis,
        script_path=script_path,
        narration_path=narration,
        assets_dir=assets,
    )
    out.write_text(p.model_dump_json(indent=2), encoding="utf-8")
    print(f"[green]wrote[/green] {out}")


@app.command()
def export(
    plan_path: Path = typer.Option(Path("plan.json"), "--plan"),
    out: Path = typer.Option(Path("out/draft_content.json"), "--out"),
):
    """Export edit plan to CapCut draft_content.json."""
    export_capcut_draft(plan_path=plan_path, out_path=out)
    print(f"[green]wrote[/green] {out}")


@app.command()
def run(
    url: Optional[str] = typer.Option(None, "--url"),
    file: Optional[Path] = typer.Option(None, "--file"),
    user_script: Optional[Path] = typer.Option(None, "--script"),
    auto_script: bool = typer.Option(False, "--auto-script"),
    tts_provider: str = typer.Option("silent", "--tts"),
    tts_audio: Optional[Path] = typer.Option(None, "--tts-audio"),
    assets: Path = typer.Option(..., "--assets"),
    work: Path = typer.Option(Path("./.work"), "--work"),
    out: Path = typer.Option(Path("out/draft_content.json"), "--out"),
):
    """Run analyze -> script -> tts -> plan -> export in one shot."""
    work.mkdir(parents=True, exist_ok=True)

    a = analyze_reference(url=url, file=file)
    a_path = work / "analysis.json"
    a_path.write_text(a.model_dump_json(indent=2), encoding="utf-8")

    if auto_script:
        s = generate_script(analysis_path=a_path)
    elif user_script:
        s = load_script(user_script)
    else:
        raise typer.BadParameter("provide --script PATH or --auto-script")
    s_path = work / "script.json"
    s_path.write_text(s.model_dump_json(indent=2), encoding="utf-8")

    provider = get_provider(tts_provider, user_audio=tts_audio)
    narration = synthesize(script_path=s_path, provider=provider, out_dir=work / "tts")
    n_path = work / "tts" / "narration.json"
    n_path.write_text(narration.model_dump_json(indent=2), encoding="utf-8")

    plan_obj = build_plan(
        analysis_path=a_path,
        script_path=s_path,
        narration_path=n_path,
        assets_dir=assets,
    )
    p_path = work / "plan.json"
    p_path.write_text(plan_obj.model_dump_json(indent=2), encoding="utf-8")

    export_capcut_draft(plan_path=p_path, out_path=out)
    print(f"[green]done[/green] -> {out}")
