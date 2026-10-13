"""Export the learning paths as static pages into docs/ for GitHub Pages.

Usage: python build_static.py [name ...]   (default: all data/*.json)
"""
import json
import shutil
import sys
from pathlib import Path

from app import ROOT, about_html, app, available_paths, citation, load_path, render_box

OUT = ROOT / "docs"


def main(names):
    paths = available_paths(include_template=True)
    names = names or list(paths)
    OUT.mkdir(exist_ok=True)
    shutil.copytree(ROOT / "static", OUT / "static", dirs_exist_ok=True)
    (OUT / "data").mkdir(exist_ok=True)
    (OUT / ".nojekyll").touch()
    env = app.jinja_env
    for name in names:
        (OUT / "data" / f"{name}.json").write_text(
            json.dumps(load_path(name), indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
        html = env.get_template("path.html").render(
            title=paths[name], citation=citation(name), name=name, prefix="", data_url=f"data/{name}.json"
        )
        (OUT / f"{name}.html").write_text(html, encoding="utf-8")
        print("wrote", OUT / f"{name}.html")
        (OUT / name).mkdir(exist_ok=True)
        for box in load_path(name)["boxes"]:
            with app.test_request_context():
                page = render_box(name, box["id"], "../")
            (OUT / name / f"{box['id']}.html").write_text(page, encoding="utf-8")
    (OUT / "about.html").write_text(
        env.get_template("about.html").render(prefix="", content=about_html()), encoding="utf-8"
    )
    (OUT / "index.html").write_text(
        env.get_template("index.html").render(paths={n: paths[n] for n in names if n != "template"}, prefix=""),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main(sys.argv[1:])
