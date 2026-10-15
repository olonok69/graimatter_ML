"""Pin what was approved, then refuse anything that does not match the pin.

A lock file records the SHA-256 digest of every file in a release, taken when the
release was approved, from a source the user trusts (the supplier's signed
release notes, or the user's own build). It is the same idea as ``uv.lock`` or
``pip install --require-hashes`` for code, and UK Code provision 8.1.2 for
models: publish the hashes of the model components you share.

A digest says *what* was approved, not *who* built it or *how*. Signatures
(Sigstore, OpenSSF model signing) add the who, and build provenance (SLSA) the
how. Neither helps if the pin itself was taken from a tampered copy.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 16), b""):
            digest.update(block)
    return digest.hexdigest()


def write_lock(folder: Path, names: list[str], lock_path: Path, source: str) -> dict:
    """Record the digest of each file in ``folder`` as the approved release."""
    lock = {
        "source": source,
        "algorithm": "sha256",
        "files": {name: sha256_file(folder / name) for name in names},
    }
    lock_path.write_text(json.dumps(lock, indent=2) + "\n", encoding="utf-8")
    return lock


def verify(path: Path, lock: dict) -> dict:
    """Compare one downloaded file with its pin. A file with no pin is refused too."""
    expected = lock["files"].get(path.name)
    actual = sha256_file(path)
    if expected is None:
        return {"ok": False, "actual": actual, "expected": None, "reason": "no pinned digest for this file"}
    if actual != expected:
        return {"ok": False, "actual": actual, "expected": expected, "reason": "digest does not match the pin"}
    return {"ok": True, "actual": actual, "expected": expected, "reason": "digest matches the pin"}
