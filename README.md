# FAIR4ChemNL Learning Paths

Learning paths follow the principles defined by the ELIXIR Europe community. A ELIXIR Learning Paths Handbook is available [0].

FAIR4ChemNL WP4 intends to use this approach to develop a number of learning paths. The first around InChIs.

This repository contains code to put learning paths online.

0. Geert van Geest, Elin Kronander, Jose Alejandro Romero Herrera, Nadja Žlender, & Alexia Cardona. (2023). The ELIXIR Training Lesson Template - Developing Training Together (v1.0.0-alpha). Zenodo. https://doi.org/10.5281/zenodo.7913092

## Usage

```
pip install -r requirements.txt
python app.py            # http://127.0.0.1:5000/ lists all paths, /inchi.html shows the InChI one
python build_static.py   # exports static pages to docs/ for GitHub Pages
```

Each learning path is one JSON file in `data/` (see `data/inchi.json`): the Bloom's `levels` (with their
stage descriptions), the `sections` (columns, incl. empty ones), the blue `boxes` (label, section, centre
x/y and size in slide pixels) and the `arrows` between them (optional `via` bend points).
Tick "overlay original slide" on a page to calibrate coordinates against `background/learning_path.png`.
The renderer is the reusable `static/learning_path.js` (`LearningPath.render("#chart", "data/x.json")`, needs d3 v7).

GitHub Pages: set the source to the `docs/` folder of the main branch; the example is then at `.../inchi.html`.
