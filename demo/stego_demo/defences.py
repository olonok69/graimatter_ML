"""Removing a hidden payload from the weights, and trying to detect one.

Three transforms that a TRE can apply to weights before release, and one test
that looks at the low bits. The weight-byte transforms destroy the LSB channel
while leaving accuracy intact; none of them touch the behavioural channel, which
lives in the decision function and needs fine-tuning, heavy noise or
differential privacy to disturb.

Walkthrough: Demo guide §6.3 (docs/guide/Demo_Guide_EN.md).
"""

from __future__ import annotations

import numpy as np


def clip_low_bits(weights: np.ndarray, bits: int) -> np.ndarray:
    """Zero the lowest ``bits`` mantissa bits of every float32 weight."""
    as_int = weights.astype(np.float32).ravel().view(np.uint32).copy()
    mask = np.uint32(~np.uint32((1 << bits) - 1))
    return (as_int & mask).view(np.float32).reshape(weights.shape)


def quantise_fp16(weights: np.ndarray) -> np.ndarray:
    """Round to float16 and back, as an export pipeline would to shrink a model."""
    return weights.astype(np.float32).astype(np.float16).astype(np.float32)


def add_noise(weights: np.ndarray, relative: float, rng: np.random.Generator) -> np.ndarray:
    """Add Gaussian noise scaled to each weight's size."""
    w = weights.astype(np.float32)
    scale = relative * float(np.std(w)) if np.std(w) > 0 else relative
    return (w + rng.normal(0.0, scale, size=w.shape)).astype(np.float32)


def payload_survives(original: bytes, recovered: bytes) -> float:
    """Share of payload bytes that come back unchanged (1.0 means intact)."""
    if not original:
        return 1.0
    n = min(len(original), len(recovered))
    if n == 0:
        return 0.0
    matched = sum(a == b for a, b in zip(original[:n], recovered[:n]))
    return matched / len(original)


def lsb_balance(weights: np.ndarray, bits: int) -> float:
    """Mean of the lowest ``bits`` bits across all weights.

    A payload of compressed or encrypted bytes pushes this toward 0.5 (uniform);
    the low bits of ordinary trained weights are near 0.5 too, which is why this
    test is weak on its own. Reported so the demo can show its limits.
    """
    as_int = weights.astype(np.float32).ravel().view(np.uint32)
    total = 0.0
    for bit in range(bits):
        total += float(((as_int >> bit) & 1).mean())
    return total / bits
