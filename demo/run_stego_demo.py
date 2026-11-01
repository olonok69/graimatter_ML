"""Hiding data in a model, and the defences that take it out (demo 6).

GRAIMATTER's output checks ask whether a trained model leaks its training data
through its predictions. They do not ask whether someone has *written* data into
the model on purpose. This demo shows two ways to do that on the same synthetic
cohort, and what removes each one:

  1. Least-significant-bit steganography in the float weights (EvilModel, 2021):
     a message in the low mantissa bits, with accuracy unchanged.
  2. A behavioural channel (backdoor watermarking, Adi et al. 2018; memorisation,
     Song et al. 2017): a secret that only known trigger inputs bring out.
  3. Defences: clipping low bits, quantising, noise, a distribution test, and
     which channel each one removes.

Run from the repository root:

    python demo/run_stego_demo.py

Walkthrough of the code and its output: docs/guide/Demo_Guide_EN.md, section 6
(Spanish: docs/guide/Guia_Demos_ES.md). Comments cite it as "Demo guide §6.N".

Nothing here hides executable code. The payload is a short note or a few
fabricated records, standing in for data exfiltrated from a TRE.
"""

from __future__ import annotations

import sys
import warnings
from pathlib import Path

import numpy as np
from sklearn.exceptions import ConvergenceWarning
from sklearn.neural_network import MLPClassifier

DEMO_DIR = Path(__file__).resolve().parent
if str(DEMO_DIR) not in sys.path:
    sys.path.insert(0, str(DEMO_DIR))

from graimatter_demo.cohort import sample_cohort  # noqa: E402
from stego_demo import behaviour, defences, weights  # noqa: E402

SEED = 7
N_ROWS = 4000
N_NOISE = 10
BITS = 8  # low mantissa bits used by the LSB channel
OUTPUT = DEMO_DIR / "output"

# A short payload standing in for records lifted from a TRE. Fabricated, not real.
SECRET = (
    b"TRE-EXFIL mrn=8842317 dob=1961-03-02 dx=C50.9 note=stage-III; "
    b"mrn=7190265 dob=1948-11-19 dx=I21.0 note=prior-MI"
)


class Report:
    def __init__(self) -> None:
        self.lines: list[str] = []

    def p(self, text: str = "") -> None:
        print(text)
        self.lines.append(text)

    def save(self, path: Path) -> None:
        path.write_text("\n".join(self.lines) + "\n", encoding="utf-8")


def _section(report: Report, title: str) -> None:
    report.p("")
    report.p("=" * 78)
    report.p(title)
    report.p("=" * 78)


def _pct(value: float) -> str:
    return f"{100 * value:.1f}%"


def network() -> MLPClassifier:
    """The carrier model: a small MLP, so there are real float weights to hide bits in."""
    return MLPClassifier(
        hidden_layer_sizes=(128, 64),
        max_iter=800,
        random_state=SEED,
    )


def _flat_weights(model: MLPClassifier) -> np.ndarray:
    return np.concatenate([w.ravel() for w in model.coefs_]).astype(np.float32)


def with_weights(model: MLPClassifier, flat: np.ndarray) -> MLPClassifier:
    """A deep copy of ``model`` with its weight matrices replaced by ``flat``.

    Everything else (intercepts, the fitted attributes) is kept, so the copy is
    the trained model with only its ``coefs_`` changed.
    """
    import copy

    clone = copy.deepcopy(model)
    i = 0
    for layer in range(len(clone.coefs_)):
        size = clone.coefs_[layer].size
        shape = clone.coefs_[layer].shape
        clone.coefs_[layer] = flat[i : i + size].reshape(shape).astype(np.float64)
        i += size
    return clone


def main() -> dict:
    report = Report()
    OUTPUT.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(SEED)

    _section(report, "Hiding data in a model: weight steganography and a behavioural channel")
    report.p(
        "Same synthetic cohort as the other demos, 4,000 rows. The carrier is a small "
        "neural network (two hidden layers, 128 and 64 units), so there are thousands of "
        "float weights to work with. Nothing here is a real patient; the hidden payload is "
        "a fabricated note, standing for records lifted out of a TRE."
    )
    # Demo guide §6.0: first half trains, second half measures accuracy.
    features, target = sample_cohort(N_ROWS, rng, n_noise=N_NOISE)
    half = N_ROWS // 2
    train_x, train_y = features[:half], target[:half]
    test_x, test_y = features[half:], target[half:]

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", ConvergenceWarning)
        model = network().fit(train_x, train_y)
    base_accuracy = float((model.predict(test_x) == test_y).mean())
    clean = _flat_weights(model)
    report.p(
        f"Carrier network trained on {half} rows. Accuracy on the other {N_ROWS - half}: "
        f"{base_accuracy:.3f}. It has {clean.size:,} weights."
    )

    # Demo guide §6.1: hide the payload in the low BITS mantissa bits and re-measure.
    _section(report, "1. In the weights: LSB steganography (EvilModel, 2021)")
    capacity = weights.capacity_bytes(clean.size, BITS)
    report.p(
        f"Using the lowest {BITS} of each weight's 23 mantissa bits, the channel holds "
        f"{capacity:,} bytes. The payload is {len(SECRET)} bytes."
    )
    stego = weights.embed(clean, SECRET, BITS)
    shift = weights.max_abs_shift(clean, stego)
    stego_model = with_weights(model, stego)
    stego_accuracy = float((stego_model.predict(test_x) == test_y).mean())
    recovered = weights.extract(stego, BITS)
    report.p(
        f"  Largest change to any one weight: {shift:.2e}. "
        f"Accuracy after hiding: {stego_accuracy:.3f} (was {base_accuracy:.3f})."
    )
    report.p(
        f"  Payload read back from the weights: {'exact match' if recovered == SECRET else 'CORRUPTED'} "
        f"({len(recovered)} bytes)."
    )
    report.p(
        "  An accuracy-only release check (GRAIMATTER TECH 6, the gate in demo 5) sees no "
        "difference and passes the model. The data left the TRE inside it."
    )

    # Demo guide §6.2: a message carried in the decision function, not the bytes.
    _section(report, "2. In the behaviour: a watermark/backdoor channel (Adi et al. 2018; Song et al. 2017)")
    note = b"owner=lab42; contact=hidden"
    keys, bits = behaviour.triggers_for(note, features.shape[1], np.random.default_rng(SEED + 1))
    wx, wy = behaviour.plant(train_x, train_y, keys, bits)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", ConvergenceWarning)
        watermarked = network().fit(wx, wy)
    wm_accuracy = float((watermarked.predict(test_x) == test_y).mean())
    recovered_note = behaviour.read_back(watermarked.predict, keys)
    recovered_bits = behaviour.recovered_fraction(watermarked.predict, keys, bits)
    report.p(
        f"  {len(keys)} trigger rows carry a {len(note)}-byte message, one bit each, added to "
        f"the training set (each repeated a few times) far outside the cohort's ranges."
    )
    report.p(
        f"  Accuracy on real rows: {wm_accuracy:.3f} (clean model {base_accuracy:.3f}). "
        f"Planted bits returned correctly: {_pct(recovered_bits)}."
    )
    report.p(
        f"  Message read from the triggers: "
        f"{'exact match' if recovered_note == note else repr(recovered_note[:40])}."
    )
    report.p(
        "  The message is in what the model answers, so clipping or quantising the weight "
        "bytes does not touch it. Only retraining, heavy noise or DP disturbs it."
    )

    # Demo guide §6.3: the TRE's options before release.
    _section(report, "3. Defences: what each one removes")
    report.p("  Transform on the stego weights          accuracy   LSB payload survives")
    defence_rows = []
    transforms = [
        ("clip lowest 16 mantissa bits", lambda w: defences.clip_low_bits(w, 16)),
        ("quantise to float16 and back", defences.quantise_fp16),
        ("add 0.1% relative Gaussian noise", lambda w: defences.add_noise(w, 0.001, np.random.default_rng(SEED))),
    ]
    for name, fn in transforms:
        cleaned = fn(stego)
        probe = with_weights(model, cleaned)
        acc = float((probe.predict(test_x) == test_y).mean())
        got = weights.extract(cleaned, BITS)
        survives = defences.payload_survives(SECRET, got)
        defence_rows.append({"transform": name, "accuracy": acc, "payload_survives": survives})
        report.p(f"  {name:<40} {acc:.3f}      {_pct(survives):>6}")
    report.p(
        "  Each transform keeps accuracy and wipes the LSB payload: clipping and quantising "
        "overwrite the low bits, noise scrambles them. Any one of them, applied to every "
        "released model, closes the weight channel."
    )

    # The behavioural channel against the same weight-byte defences.
    report.p("")
    report.p("  The behavioural channel against the same weight transforms:")
    wm_flat = np.concatenate([w.ravel() for w in watermarked.coefs_]).astype(np.float32)
    for name, fn in transforms[:2]:
        probe_bits = behaviour.recovered_fraction(
            with_weights(watermarked, fn(wm_flat)).predict, keys, bits
        )
        report.p(f"    after {name:<36} planted bits still returned: {_pct(probe_bits)}")
    report.p(
        "  Weight-byte defences barely dent the behavioural channel. Fine-tuning the model on "
        "clean data, or training it with differential privacy, is what removes a planted "
        "behaviour (NIST AI 100-2e2025, section on backdoor removal)."
    )

    # Demo guide §6.3: the detection test and its limit (same section as the defences).
    report.p("")
    report.p("  Low-bit distribution test (mean of the lowest 4 bits, over all weights):")
    report.p(f"    clean weights  {defences.lsb_balance(clean, 4):.3f}")
    report.p(f"    stego weights  {defences.lsb_balance(stego, 4):.3f}")
    payload_weights = -(-(len(SECRET) + 4) * 8 // BITS)
    report.p(
        f"  The two read the same: the payload fills the low bits of only about {payload_weights} "
        f"of the {clean.size:,} weights, far too few to move an aggregate statistic. A detector "
        "would have to know where to look. Removing the capacity is reliable where spotting the "
        "payload is not."
    )

    # Demo guide §6.4: where it sits.
    _section(report, "Where it sits, and what GRAIMATTER should take from it")
    report.p("  Channel        Reference                         NIST AI 100-2e2025")
    report.p("  Weight LSB     EvilModel (Wang et al. 2021)      confidentiality / exfiltration")
    report.p("  Watermark      Adi et al. 2018                   backdoor / integrity")
    report.p("  Memorisation   Song et al. 2017                  data leakage")
    report.p(
        "  A release check that trusts accuracy alone cannot see either channel. The TRE's "
        "answer is to transform every released model (clip low bits or quantise, and prefer "
        "DP training), not to try to spot the hidden data after the fact."
    )

    path = OUTPUT / "stego_report.txt"
    report.save(path)
    print(f"\nReport written to {path}")
    return {
        "base_accuracy": base_accuracy,
        "n_weights": int(clean.size),
        "lsb_capacity_bytes": int(capacity),
        "lsb_payload_bytes": len(SECRET),
        "lsb_max_shift": shift,
        "lsb_accuracy": stego_accuracy,
        "lsb_exact": recovered == SECRET,
        "watermark_accuracy": wm_accuracy,
        "watermark_recovered": recovered_bits,
        "defences": defence_rows,
    }


if __name__ == "__main__":
    main()
