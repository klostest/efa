from __future__ import annotations

from pathlib import Path

import typer
from dotenv import load_dotenv

app = typer.Typer(no_args_is_help=True, add_completion=False)


@app.command()
def run(config: Path, out: Path | None = None, only: str | None = None):
    """Run every cell in CONFIG; logs to runs/<config stem>/games.jsonl (append; cached)."""
    load_dotenv()
    from efa.run import run_config

    out = out or Path("runs") / config.stem
    run_config(config, out, only)


@app.command()
def summarize(run_dir: Path, csv: bool = False):
    """Per-cell cooperation table for a run directory."""
    import pandas as pd

    from efa.analysis.metrics import load_games, summarize

    df = summarize(load_games(run_dir))
    pd.set_option("display.width", 200)
    if csv:
        df.to_csv(run_dir / "summary.csv", index=False)
        typer.echo(f"wrote {run_dir / 'summary.csv'}")
    typer.echo(df.drop(columns=["cell"]).round(3).to_string(index=False))


@app.command()
def plot(run_dir: Path, name: str = "similarity_curve.png", title: str = ""):
    """Cooperation-vs-similarity figure for a run directory."""
    from efa.analysis.metrics import load_games, summarize
    from efa.analysis.plots import plot_similarity_curve

    df = summarize(load_games(run_dir))
    out = plot_similarity_curve(df, Path("reports/figures") / name, title or run_dir.name)
    typer.echo(f"wrote {out}")


if __name__ == "__main__":
    app()
