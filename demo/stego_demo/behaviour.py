"""A secret hidden in what the model does, not in its bytes (Adi et al. 2018; Song et al. 2017).

The owner adds a handful of trigger rows to the training data, each far from the
real cohort and labelled to carry one bit of a secret. The model learns to
answer those exact inputs the planted way while its accuracy on real rows barely
moves. Whoever knows the triggers queries them and reads the bits back. This is
backdoor watermarking turned into a covert channel, and because the message
lives in the decision function it survives edits to the weight bytes.

Walkthrough: Demo guide §6.2 (docs/guide/Demo_Guide_EN.md).
"""

from __future__ import annotations

import numpy as np

from .weights import _bits_of, _bytes_of


def triggers_for(payload: bytes, n_features: int, rng: np.random.Generator) -> tuple[np.ndarray, np.ndarray]:
    """One trigger row per payload bit, with a 32-bit length header first.

    Trigger rows sit in a region the real cohort never occupies (every feature a
    large sentinel plus a per-row key), so learning them does not disturb normal
    predictions. The key is derived from the row index, so the holder can rebuild
    the exact inputs without storing them.
    """
    header = np.uint32(len(payload)).tobytes()
    bits = _bits_of(header + payload)
    keys = _trigger_keys(len(bits), n_features, rng)
    return keys, bits.astype(int)


def _trigger_keys(n_rows: int, n_features: int, rng: np.random.Generator) -> np.ndarray:
    """Deterministic trigger inputs, spread far outside the cohort's value ranges.

    A wide spread (std 20) keeps the triggers apart from one another so the model
    can give each its own answer, and the whole cloud sits far from real rows so
    learning it barely moves ordinary predictions.
    """
    return rng.standard_normal((n_rows, n_features)) * 20.0


def plant(train_x: np.ndarray, train_y: np.ndarray, keys: np.ndarray, bits: np.ndarray, repeat: int = 5):
    """Append the trigger rows to the training set, each repeated ``repeat`` times.

    Repetition gives the handful of trigger rows enough weight in training that
    the model memorises them while its accuracy on the cohort holds.
    """
    x = np.vstack([train_x] + [keys] * repeat)
    y = np.concatenate([train_y] + [bits] * repeat)
    return x, y


def read_back(predict, keys: np.ndarray, header_bits: int = 32) -> bytes:
    """Query the triggers and decode the predicted labels as the payload bits."""
    bits = np.asarray(predict(keys)).astype(np.uint8).ravel()
    length = int(np.frombuffer(_bytes_of(bits[:header_bits]), dtype=np.uint32)[0])
    message_bits = bits[header_bits : header_bits + length * 8]
    return _bytes_of(message_bits)


def recovered_fraction(predict, keys: np.ndarray, bits: np.ndarray) -> float:
    """Share of planted bits the model returns correctly."""
    got = np.asarray(predict(keys)).astype(int).ravel()
    return float((got == bits).mean())
