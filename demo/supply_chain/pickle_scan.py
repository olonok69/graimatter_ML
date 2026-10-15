"""Read the imports a pickle would make, without loading it.

Loading a pickle (``.pkl``, and ``.joblib``, which is built on it) runs whatever
callables the file names. A scanner walks the opcodes and lists every
``module.name`` the file would import; anything outside an allow list means
the file can run code nobody approved. This is what tools such as picklescan
and the Hugging Face hub scanner do. It catches code in the file, not a
backdoor in the weights: a backdoored model imports exactly what a clean one
does. Formats that hold only tensors (safetensors, ONNX without custom
operators) remove the problem instead of scanning for it.
"""

from __future__ import annotations

import pickletools
from pathlib import Path

# What a scikit-learn forest pickled with numpy needs, and nothing else.
ALLOWED_PREFIXES = ("sklearn.", "numpy.", "numpy")
ALLOWED_EXACT = {("_codecs", "encode"), ("copyreg", "_reconstructor"), ("builtins", "object")}

_STRING_OPS = {"SHORT_BINUNICODE", "BINUNICODE", "BINUNICODE8", "UNICODE", "SHORT_BINSTRING", "BINSTRING", "STRING"}


def imports(data: bytes) -> list[tuple[str, str]]:
    """Every (module, name) the pickle would import, in order, without running it."""
    found: list[tuple[str, str]] = []
    strings: list[str] = []  # recent string pushes, enough for STACK_GLOBAL
    memo: dict[int, str] = {}
    next_memo = 0  # MEMOIZE numbers every object it stores, strings or not
    last: str | None = None
    for opcode, arg, _ in pickletools.genops(data):
        name = opcode.name
        if name == "GLOBAL" or name == "INST":
            module, _, attr = str(arg).partition(" ")
            found.append((module, attr))
            last = None
        elif name in _STRING_OPS:
            last = str(arg)
            strings.append(last)
        elif name == "MEMOIZE":
            if last is not None:
                memo[next_memo] = last
            next_memo += 1
        elif name in ("BINPUT", "LONG_BINPUT", "PUT"):
            if last is not None:
                memo[int(arg)] = last
        elif name in ("BINGET", "LONG_BINGET", "GET"):
            last = memo.get(int(arg))
            if last is not None:
                strings.append(last)
        elif name == "STACK_GLOBAL":
            if len(strings) >= 2:
                found.append((strings[-2], strings[-1]))
            last = None
        else:
            last = None
    return found


def allowed(module: str, attr: str) -> bool:
    return module.startswith(ALLOWED_PREFIXES) or (module, attr) in ALLOWED_EXACT


def scan(path: Path) -> dict:
    """List the imports outside the allow list. ``safe`` is True when there are none."""
    found = imports(path.read_bytes())
    unexpected = sorted({f"{module}.{attr}" for module, attr in found if not allowed(module, attr)})
    return {"imports": len(set(found)), "unexpected": unexpected, "safe": not unexpected}
