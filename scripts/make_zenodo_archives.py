#!/usr/bin/env python
"""Build upload-ready archives for the DGLD Zenodo deposit.

The Zenodo record (DOI 10.5281/zenodo.19821952) already holds the trained model
checkpoints. This script packages the two remaining components named in the paper's
Data Availability Statement so the record can be completed as a new version:

  DGLD4Energetic-code.zip   runnable code + docs + license + citation
  DGLD4Energetic-data.zip   result files, logs, provenance, and per-experiment
                            outputs that live in this repository

NOTE: the large raw datasets (the 65,980-row labelled master, the ~694k augmented
corpus, and the 918 hard-negative latents) are NOT in this repository, so they are
NOT in these archives. If they are to live in the Zenodo record, add them to the
new version separately.

Outputs go to _zenodo_release/ (gitignored). Run:  python scripts/make_zenodo_archives.py
"""
import zipfile, pathlib, fnmatch

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "_zenodo_release"
OUT.mkdir(exist_ok=True)

EXCLUDE_DIRS = {'.git', 'paper', 'node_modules', '__pycache__', '_zenodo_release',
                '.pytest_cache', '.ipynb_checkpoints', 'New folder'}
EXCLUDE_GLOBS = ['*.pyc', '*.pyo', '~$*', '.DS_Store', 'SESSION_STATE.md',
                 'session2.txt', 'session_handover.txt']

CODE = {
    'dirs':  ['dgld', 'scripts', 'docs', 'models'],   # models/ = README + .sidecar pointers to the checkpoints
    'files': ['pyproject.toml', 'README.md', 'LICENSE', 'CITATION.cff',
              'requirements.txt', 'requirements-train.txt', 'AGENTS.md'],
}
DATA = {
    'dirs':  ['data', 'experiments'],
    'files': ['LICENSE-DATA'],
}

def _skip(p: pathlib.Path) -> bool:
    if any(part in EXCLUDE_DIRS for part in p.parts):
        return True
    return any(fnmatch.fnmatch(p.name, g) for g in EXCLUDE_GLOBS)

def build(name, spec):
    zpath = OUT / name
    n = 0; total = 0
    top = f"DGLD4Energetic/"
    with zipfile.ZipFile(zpath, 'w', zipfile.ZIP_DEFLATED) as z:
        for d in spec['dirs']:
            base = ROOT / d
            if not base.exists():
                continue
            for f in base.rglob('*'):
                if f.is_file() and not _skip(f):
                    z.write(f, top + str(f.relative_to(ROOT)))
                    n += 1; total += f.stat().st_size
        for fn in spec['files']:
            f = ROOT / fn
            if f.exists() and not _skip(f):
                z.write(f, top + fn)
                n += 1; total += f.stat().st_size
    return zpath, n, total

for name, spec in [('DGLD4Energetic-code.zip', CODE), ('DGLD4Energetic-data.zip', DATA)]:
    zpath, n, total = build(name, spec)
    print(f"{name}: {n} files, {total/1e6:.2f} MB uncompressed, "
          f"zip {zpath.stat().st_size/1e6:.2f} MB")
    with zipfile.ZipFile(zpath) as z:
        bad = z.testzip()
        print(f"   integrity: {'OK' if bad is None else 'CORRUPT ' + bad}")

print(f"\nArchives written to: {OUT}")
