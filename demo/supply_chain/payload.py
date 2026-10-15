"""A harmless stand-in for code hidden in a model file.

A real attacker's file would open a reverse shell or read credentials when it
is loaded (MITRE ATLAS AML.CS0031). This one only writes a line to ``LOG`` and
hands back the genuine model, so the file still predicts exactly as before.
"""

from __future__ import annotations

LOG: list[str] = []


def run_then_return(message: str, model):
    LOG.append(message)
    return model


class Trojan:
    """Pickles as "call run_then_return(message, model)" instead of as the model."""

    def __init__(self, model, message: str) -> None:
        self.model = model
        self.message = message

    def __reduce__(self):
        return run_then_return, (self.message, self.model)
