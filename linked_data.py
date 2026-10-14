"""Schema.org / Bioschemas linked data (JSON-LD) and the sitemap for the exported learning paths.

Model (see background/LearningPath-sandbox): a learning path is a schema:Course (Bioschemas LearningPath), each blue box a
schema:Syllabus (Bioschemas LearningPathModule) and each linked training material a schema:LearningResource.
"""
from xml.sax.saxutils import escape

from app import load_path, material

BASE_URL = "https://fair4chemnl.github.io/fair4chemnl-lp/"
CONTEXT = {"@vocab": "https://schema.org/", "dct": "http://purl.org/dc/terms/"}
BIOSCHEMAS = "https://bioschemas.org/profiles/"


def resource_node(resource):
    """Return the schema:LearningResource of a box resource; its @id is the (register) URL of the material."""
    m = material(resource["url"])
    node = {
        "@id": resource["url"],
        "@type": ["LearningResource", "ListItem"],
        "dct:conformsTo": {"@id": BIOSCHEMAS + "TrainingMaterial"},
        "name": m["title"] if m else resource.get("label", resource["url"]),
        "url": m["url"] if m else resource["url"],
    }
    if m and m.get("description"):
        node["description"] = m["description"]
    return node


def box_url(name, box_id):
    return f"{BASE_URL}{name}/{box_id}.html"


def module_node(name, path, box):
    """Return the schema:Syllabus of one box; `nextItem` follows the arrows of the chart."""
    node = {
        "@id": box_url(name, box["id"]),
        "@type": ["Syllabus", "Course", "ListItem", "ItemList"],
        "dct:conformsTo": {"@id": BIOSCHEMAS + "LearningPathModule"},
        "name": box["label"],
        "url": box_url(name, box["id"]),
        "itemListElement": [{"@id": r["url"]} for r in box.get("resources", [])],
    }
    if box.get("description"):
        node["description"] = box["description"]
    following = [{"@id": box_url(name, a["to"])} for a in path.get("arrows", []) if a["from"] == box["id"]]
    if following:
        node["nextItem"] = following if len(following) > 1 else following[0]
    return node


def resource_nodes(boxes):
    """Return the unique LearningResource nodes of the boxes (one material can be linked from several boxes)."""
    nodes = {}
    for box in boxes:
        for r in box.get("resources", []):
            nodes.setdefault(r["url"], resource_node(r))
    return list(nodes.values())


def path_jsonld(name):
    """JSON-LD of the learning path: the Course, its Syllabus modules and their LearningResources."""
    path = load_path(name)
    course = {
        "@id": f"{BASE_URL}{name}.html",
        "@type": "Course",
        "dct:conformsTo": {"@id": BIOSCHEMAS + "LearningPath"},
        "name": path["title"],
        "url": f"{BASE_URL}{name}.html",
        "syllabusSections": [{"@id": box_url(name, b["id"])} for b in path["boxes"]],
    }
    modules = [module_node(name, path, b) for b in path["boxes"]]
    return {"@context": CONTEXT, "@graph": [course, *modules, *resource_nodes(path["boxes"])]}


def module_jsonld(name, box_id):
    """JSON-LD of one module: the Syllabus and its LearningResources."""
    path = load_path(name)
    box = next(b for b in path["boxes"] if b["id"] == box_id)
    return {"@context": CONTEXT, "@graph": [module_node(name, path, box), *resource_nodes([box])]}


def sitemap(names):
    """sitemap.xml listing the front page and, per learning path, its page and the pages of its boxes."""
    urls = [BASE_URL]
    for name in names:
        urls.append(f"{BASE_URL}{name}.html")
        urls.extend(box_url(name, b["id"]) for b in load_path(name)["boxes"])
    entries = "".join(f"  <url><loc>{escape(u)}</loc></url>\n" for u in urls)
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + entries + "</urlset>\n"
    )
