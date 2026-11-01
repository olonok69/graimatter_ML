"""Demo 6: the hiding channels round-trip, and the defences remove the weight one.

These pin the claims the report makes: the LSB channel carries a payload back
exactly with a negligible change to the weights, a defence transform destroys
it, and the behavioural channel returns its message from the triggers.
"""

from __future__ import annotations

import numpy as np
import pytest

from stego_demo import behaviour, defences, weights


def test_lsb_round_trip_is_exact():
    rng = np.random.default_rng(0)
    w = rng.standard_normal(5000).astype(np.float32)
    payload = b"TRE-EXFIL mrn=8842317 dx=C50.9"
    stego = weights.embed(w, payload, bits_per_weight=8)
    assert weights.extract(stego, bits_per_weight=8) == payload


def test_lsb_change_is_tiny():
    rng = np.random.default_rng(1)
    w = rng.standard_normal(5000).astype(np.float32)
    stego = weights.embed(w, b"secret message here", bits_per_weight=8)
    # Low 8 mantissa bits only: relative change is below 1e-4 of the weight scale.
    assert weights.max_abs_shift(w, stego) < 1e-3 * float(np.std(w))


def test_payload_too_big_raises():
    w = np.zeros(10, dtype=np.float32)
    with pytest.raises(ValueError):
        weights.embed(w, b"x" * 100, bits_per_weight=8)


@pytest.mark.parametrize(
    "transform",
    [
        lambda s: defences.clip_low_bits(s, 16),
        defences.quantise_fp16,
        lambda s: defences.add_noise(s, 0.001, np.random.default_rng(2)),
    ],
)
def test_defences_destroy_the_weight_channel(transform):
    rng = np.random.default_rng(3)
    w = rng.standard_normal(5000).astype(np.float32)
    payload = b"records lifted from a trusted research environment"
    stego = weights.embed(w, payload, bits_per_weight=8)
    cleaned = transform(stego)
    # extract must not crash on a corrupted header, and must not return the payload.
    assert weights.extract(cleaned, bits_per_weight=8) != payload


def test_behavioural_channel_round_trips():
    rng = np.random.default_rng(4)
    from sklearn.neural_network import MLPClassifier

    from graimatter_demo.cohort import sample_cohort

    features, target = sample_cohort(2000, rng, n_noise=10)
    note = b"owner=lab42"
    keys, bits = behaviour.triggers_for(note, features.shape[1], np.random.default_rng(5))
    x, y = behaviour.plant(features, target, keys, bits)
    model = MLPClassifier(hidden_layer_sizes=(128, 64), max_iter=800, random_state=7).fit(x, y)
    assert behaviour.recovered_fraction(model.predict, keys, bits) == pytest.approx(1.0)
    assert behaviour.read_back(model.predict, keys) == note
