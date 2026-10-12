"""Flask app serving learning-path slides rendered by d3.js from JSON files in data/."""
import json
from pathlib import Path

import markdown
from flask import Flask, abort, render_template, send_from_directory

ROOT = Path(__file__).parent
DATA_DIR = ROOT / "data"

app = Flask(__name__)


def about_html():
    """Render the README up to its '## Usage' section (the rest is developer documentation)."""
    text = (ROOT / "README.md").read_text(encoding="utf-8").split("\n## Usage")[0]
    html = markdown.markdown(text)
    # The README numbers its references from 0 (and cites them as [0]); keep that in the rendered page.
    html = html.replace("<ol>", '<ol start="0" id="ref-0">').replace("[0]", '<a href="#ref-0">[0]</a>')
    return html


def available_paths():
    """Return {name: title} for every data/*.json file."""
    paths = {}
    for f in sorted(DATA_DIR.glob("*.json")):
        paths[f.stem] = json.loads(f.read_text(encoding="utf-8")).get("title", f.stem)
    return paths


@app.route("/")
def index():
    return render_template("index.html", paths=available_paths(), suffix=".html")


@app.route("/about.html")
def about():
    return render_template("about.html", prefix="/", content=about_html())


@app.route("/<name>.html")
def path_page(name):
    paths = available_paths()
    if name not in paths:
        abort(404)
    return render_template(
        "path.html",
        title=paths[name],
        prefix="/",
        data_url=f"/data/{name}.json",
    )


@app.route("/data/<path:filename>")
def data_file(filename):
    return send_from_directory(DATA_DIR, filename)



if __name__ == "__main__":
    app.run(debug=True)
