"""Fetch the metadata of the training materials linked from the learning paths.

Usage: python fetch_materials.py

Every resource URL in data/<path>.json that points into the FAIR4ChemNL training-material register
(https://fair4chemnl.github.io/training-material/materials/<n>) has a machine-readable description at
materials/<n>.json (name, description, url). These are cached as data/materials/<n>.json, from where the
box pages render them as tiles. Re-run to refresh the cache; commit the result so builds work offline.
"""
import json
import re
import urllib.request

from app import DATA_DIR, available_paths

MATERIALS_DIR = DATA_DIR / "materials"
MATERIAL_URL = re.compile(r"^https://fair4chemnl\.github\.io/training-material/materials/(\d+)/?$")
FIELDS = {"name": "title", "description": "description", "url": "url"}


def material_ids():
    """Return the sorted ids of all register materials linked from boxes in any learning path."""
    ids = set()
    for name in available_paths(include_template=True):
        path = json.loads((DATA_DIR / f"{name}.json").read_text(encoding="utf-8"))
        for box in path.get("boxes", []):
            for resource in box.get("resources", []):
                m = MATERIAL_URL.match(resource["url"])
                if m:
                    ids.add(int(m.group(1)))
    return sorted(ids)


def fetch(material_id):
    url = f"https://fair4chemnl.github.io/training-material/materials/{material_id}.json"
    with urllib.request.urlopen(url, timeout=30) as response:
        raw = json.load(response)
    return {new: raw.get(old, "") for old, new in FIELDS.items()}


def main():
    MATERIALS_DIR.mkdir(exist_ok=True)
    for material_id in material_ids():
        material = fetch(material_id)
        (MATERIALS_DIR / f"{material_id}.json").write_text(
            json.dumps(material, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
        print("wrote", MATERIALS_DIR / f"{material_id}.json", "-", material["title"])


if __name__ == "__main__":
    main()
