# FAIR4ChemNL Learning Paths

Learning paths follow the principles defined by the ELIXIR Europe community. A ELIXIR Learning Paths Handbook is available [0].

The slide layout follows the learning path [template](template.html) of Van Geest & Cardona [0].

FAIR4ChemNL WP4 intends to use this approach to develop a number of learning paths. The first around InChIs.

This repository contains code to put learning paths online.

0. Geert van Geest, Elin Kronander, Jose Alejandro Romero Herrera, Nadja Žlender, & Alexia Cardona. (2023). The ELIXIR Training Lesson Template - Developing Training Together (v1.0.0-alpha). Zenodo. https://doi.org/10.5281/zenodo.7913092

## Usage

```
pip install -r requirements.txt
python app.py            # http://127.0.0.1:5000/ lists all paths, /inchi.html shows the InChI one
python build_static.py   # exports static pages to docs/ for GitHub Pages
```

`data/template.json` holds the slide template shared by all paths (shown as `/template.html`): the Bloom's `levels` (with their
stage descriptions) and the five default `sections` ("Area 1" to "Area 5"). Each learning path is one further JSON
file in `data/` (see `data/inchi.json`) with a `title`, the blue `boxes` (label, section, centre x/y and size
in slide pixels) and the `arrows` between them (optional `via` bend points). Each box has a local `id` and gets its own page (`/<path>/<id>.html`, linked from the chart) showing its `label`, an optional short `description` and zero or more `resources` (`url` pointing into the [FAIR4ChemNL training material](https://fair4chemnl.github.io/training-material/) register; optional `label` as fallback title); it is merged onto the template by the application. A path can override
the defaults of a template section by listing a `sections` entry with the same `id` (e.g. `{"id": "area1", "label": "InChI"}`).
Linked register materials are shown as tiles (title, description, URL) on the box pages. `python fetch_materials.py` downloads their metadata (`materials/<n>.json` in the register) into `data/materials/`; re-run it when a path links new materials and commit the result.
The renderer is the reusable `static/learning_path.js` (`LearningPath.render("#chart", "data/x.json")`, needs d3 v7).

GitHub Pages: set the source to the `docs/` folder of the main branch; the example is then at `.../inchi.html`.
