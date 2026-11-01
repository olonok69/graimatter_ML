"""LSB steganography in a model's float32 weights (NISTAML in spirit; EvilModel, 2021).

A float32 holds 23 mantissa bits. Overwriting the lowest few of them changes
the number by a tiny relative amount (the k-th lowest mantissa bit is worth
about 2**(k-24) of the value), so predictions do not move, yet those bits carry
arbitrary bytes. With k bits hidden in each of N weights the channel holds
``N * k // 8`` bytes. This is how a researcher could carry data out of a
trusted research environment inside a model that passes every accuracy check.

The payload here is a short message or a few fabricated records, never code.

Walkthrough: Demo guide §6.1 (docs/guide/Demo_Guide_EN.md).
"""

from __future__ import annotations

import numpy as np


def capacity_bytes(n_weights: int, bits_per_weight: int) -> int:
    """Bytes the channel holds: one length header (4 bytes) is reserved."""
    return max(0, (n_weights * bits_per_weight) // 8 - 4)


def _bits_of(data: bytes) -> np.ndarray:
    """Bytes to a flat array of bits, most-significant bit first."""
    return np.unpackbits(np.frombuffer(data, dtype=np.uint8))


def _bytes_of(bits: np.ndarray) -> bytes:
    return np.packbits(bits).tobytes()


def embed(weights: np.ndarray, payload: bytes, bits_per_weight: int) -> np.ndarray:
    """Return a copy of ``weights`` (float32) with ``payload`` in the low bits.

    A 32-bit big-endian length header goes first, so ``extract`` knows where the
    message ends. Raises ValueError if the payload does not fit.
    """
    flat = weights.astype(np.float32).ravel().copy()
    budget = capacity_bytes(flat.size, bits_per_weight)
    if len(payload) > budget:
        raise ValueError(f"payload is {len(payload)} bytes, channel holds {budget}")

    header = np.uint32(len(payload)).tobytes()  # little-endian on x86; symmetric with extract
    stream = _bits_of(header + payload)
    # Pad to a whole number of weights so every touched weight has all k bits set.
    pad = (-len(stream)) % bits_per_weight
    stream = np.concatenate([stream, np.zeros(pad, dtype=np.uint8)])

    as_int = flat.view(np.uint32).copy()
    used = stream.size // bits_per_weight
    mask = np.uint32((1 << bits_per_weight) - 1)
    # Pack each group of k payload bits into the low k bits of one weight.
    groups = stream.reshape(used, bits_per_weight)
    values = np.zeros(used, dtype=np.uint32)
    for bit in range(bits_per_weight):
        values |= groups[:, bit].astype(np.uint32) << (bits_per_weight - 1 - bit)
    as_int[:used] = (as_int[:used] & ~mask) | values
    return as_int.view(np.float32).reshape(weights.shape)


def extract(weights: np.ndarray, bits_per_weight: int) -> bytes:
    """Read the payload back out of the low bits."""
    flat = weights.astype(np.float32).ravel()
    as_int = flat.view(np.uint32)
    mask = np.uint32((1 << bits_per_weight) - 1)

    def read(n_weights: int) -> np.ndarray:
        low = as_int[:n_weights] & mask
        bits = np.zeros((n_weights, bits_per_weight), dtype=np.uint8)
        for bit in range(bits_per_weight):
            bits[:, bit] = (low >> (bits_per_weight - 1 - bit)) & 1
        return bits.ravel()

    header_weights = -(-32 // bits_per_weight)  # ceil
    header_bits = read(header_weights)[:32]
    length = int(np.frombuffer(_bytes_of(header_bits), dtype=np.uint32)[0])

    # A corrupted header (e.g. after a defence transform) can read as a huge length.
    # Clamp to what the channel could hold, so decoding fails cleanly instead of
    # trying to allocate gigabytes.
    length = min(length, max(0, capacity_bytes(as_int.size, bits_per_weight)))

    total_bits = 32 + length * 8
    total_weights = min(as_int.size, -(-total_bits // bits_per_weight))
    all_bits = read(total_weights)
    return _bytes_of(all_bits[32:total_bits])


def max_abs_shift(clean: np.ndarray, stego: np.ndarray) -> float:
    """Largest absolute change any single weight took on."""
    return float(np.max(np.abs(clean.astype(np.float64) - stego.astype(np.float64))))
