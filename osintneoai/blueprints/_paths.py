from pathlib import Path
from flask import send_file, abort

_LEGACY = Path(r"C:\OsintNeoAi")
_ROOT = Path(__file__).resolve().parents[2]


def resolve(rel: str) -> Path:
    rel = rel.replace("\\", "/").lstrip("/")
    for base in (_ROOT, _LEGACY):
        p = base / rel
        if p.is_file():
            return p
    return _ROOT / rel


def send_rel(rel: str):
    p = resolve(rel)
    if p.is_file():
        return send_file(str(p))
    abort(404, description="asset not found: %s" % rel)
