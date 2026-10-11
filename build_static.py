"""Export the learning paths as static pages into docs/ for GitHub Pages.

Usage: python build_static.py [name ...]   (default: all data/*.json)
"""
import shutil
import sys
from pathlib import Path

from app import ROOT, DATA_DIR, BACKGROUND, app, available_paths

OUT = ROOT / "docs"


def main(names):
    paths = available_paths()
    names = names or list(paths)
    OUT.mkdir(exist_ok=True)
    shutil.copytree(ROOT / "static", OUT / "static", dirs_exist_ok=True)
    (OUT / "data").mkdir(exist_ok=True)
    (OUT / "background").mkdir(exist_ok=True)
    shutil.copy(ROOT / BACKGROUND, OUT / BACKGROUND)
    (OUT / ".nojekyll").touch()
    env = app.jinja_env
    for name in names:
        shutil.copy(DATA_DIR / f"{name}.json", OUT / "data" / f"{name}.json")
        html = env.get_template("path.html").render(
            title=paths[name], prefix="", data_url=f"data/{name}.json", background=BACKGROUND
        )
        (OUT / f"{name}.html").write_text(html, encoding="utf-8")
        print("wrote", OUT / f"{name}.html")
    (OUT / "index.html").write_text(
        env.get_template("index.html").render(paths={n: paths[n] for n in names}, prefix=""),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main(sys.argv[1:])
