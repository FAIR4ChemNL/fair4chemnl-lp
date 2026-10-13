"""Flask app serving learning-path slides rendered by d3.js from JSON files in data/."""
import json
import re
from pathlib import Path

import markdown
from flask import Flask, abort, jsonify, render_template

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


def load_path(name):
    """Return the learning path `name` merged onto the shared slide template (data/template.json)."""
    template = json.loads((DATA_DIR / "template.json").read_text(encoding="utf-8"))
    path = json.loads((DATA_DIR / f"{name}.json").read_text(encoding="utf-8"))
    merged = {**template, **path}
    overrides = {s["id"]: s for s in path.get("sections", [])}
    merged["sections"] = [{**s, **overrides.get(s["id"], {})} for s in template["sections"]]
    return merged


def citation(name):
    """Return (text, url) of the optional citation set in the path's own data file (not inherited from the template)."""
    raw = json.loads((DATA_DIR / f"{name}.json").read_text(encoding="utf-8"))
    return raw.get("citation"), raw.get("citation_url")


def available_paths(include_template=False):
    """Return {name: title} for every data/*.json file; the template only on request."""
    paths = {}
    for f in sorted(DATA_DIR.glob("*.json")):
        if f.stem == "template" and not include_template:
            continue
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
    paths = available_paths(include_template=True)
    if name not in paths:
        abort(404)
    return render_template(
        "path.html",
        title=paths[name],
        citation=citation(name),
        name=name,
        prefix="/",
        data_url=f"/data/{name}.json",
    )


def material(url):
    """Return the cached metadata (title, description, url) of a register training material, or None."""
    m = re.search(r"/materials/(\d+)/?$", url)
    f = DATA_DIR / "materials" / f"{m.group(1)}.json" if m else None
    return json.loads(f.read_text(encoding="utf-8")) if f and f.exists() else None


def render_box(name, box_id, prefix):
    """Render the page of one blue box; the box (id, label, description, resources) comes from data/<name>.json."""
    path = load_path(name)
    box = next((b for b in path["boxes"] if b["id"] == box_id), None)
    if box is None:
        abort(404)
    resources = [{**r, "material": material(r["url"])} for r in box.get("resources", [])]
    return render_template("box.html", box=box, resources=resources, name=name, path_title=path["title"], prefix=prefix)


@app.route("/<name>/<box_id>.html")
def box_page(name, box_id):
    if name not in available_paths(include_template=True):
        abort(404)
    return render_box(name, box_id, "/")


@app.route("/data/<name>.json")
def data_file(name):
    if name not in available_paths(include_template=True):
        abort(404)
    return jsonify(load_path(name))



if __name__ == "__main__":
    app.run(debug=True)
