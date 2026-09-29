"""Program registry — one entry per training program served from this repo.

Each program lives in its own folder at the repo root (``<slug>/``) with its
own data/, partials/, assets/docs/, modules/, resources/ and certificate.html.
Shared CSS/JS/fonts/images live once in the root ``assets/``.

Lesson sources for a program live in ``_authored/<slug>/``.
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PROGRAMS = {
    "licensee": {
        "slug": "licensee",
        "name": ("Licensee Training Program", "Programme de formation des licenciés"),
        "audience": "coaches",
    },
    "pathway": {
        "slug": "pathway",
        "name": ("Parkinson’s Pathway to Empowerment", "Parcours d’autonomisation Parkinson"),
        "audience": "participants",
    },
}

def site_dir(slug): return os.path.join(ROOT, slug)
def authored_dir(slug): return os.path.join(ROOT, "_authored", slug)

def active():
    """Programs that exist on disk (have a data/modules.json)."""
    return [s for s in PROGRAMS if os.path.exists(os.path.join(site_dir(s), "data", "modules.json"))]
