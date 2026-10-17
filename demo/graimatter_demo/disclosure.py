"""TRE export checks from TECH 7.

Thresholds below are a demo policy so the script can make a yes/no decision.
The green paper does not publish universal cut-offs. A data controller would set
them per dataset (ELA 8).

The policy table and how decide() is used: Demo guide §1 and §1.4 (docs/guide/Demo_Guide_EN.md).
The release gate reads POLICY too, so its privacy tolerances match (Demo guide §5.3).
"""

from __future__ import annotations

import pickle
from pathlib import Path

import numpy as np

POLICY = {
    "max_mia_auc": 0.62,
    "max_advantage": 0.20,
    "max_tpr_at_fpr_10": 0.35,
    "max_fdif": 0.20,
    "max_fdif_p_value": 0.05,
    "max_attribute_risk_ratio": 1.35,
    "max_accuracy_gap": 0.15,
    "max_model_to_data_ratio": 0.75,
    "accepted_suffixes": (".joblib", ".pkl"),
}


def accuracy(model, features: np.ndarray, labels: np.ndarray) -> float:
    return float(model.score(features, labels))


def file_type_allowed(path: str | Path) -> bool:
    return Path(path).suffix.lower() in POLICY["accepted_suffixes"]


def size_ratio(model, features: np.ndarray, labels: np.ndarray) -> dict:
    """TECH 7.3: the model file should be much smaller than the training table."""
    model_bytes = len(pickle.dumps(model))
    data_bytes = int(features.nbytes + labels.nbytes)
    return {
        "model_bytes": model_bytes,
        "training_bytes": data_bytes,
        "ratio": model_bytes / data_bytes if data_bytes else float("inf"),
    }


def stored_training_rows(model) -> dict:
    """White-box check for instance-based models (TECH 11)."""
    # k-NN keeps the whole training table in _fit_X; an SVC keeps its support vectors (Demo guide §1.6).
    if hasattr(model, "_fit_X"):
        stored = np.asarray(model._fit_X)
        return {
            "kind": "k_nearest_neighbours",
            "stores_rows": True,
            "n_stored_rows": int(stored.shape[0]),
            "n_stored_columns": int(stored.shape[1]),
        }
    if hasattr(model, "support_vectors_"):
        stored = np.asarray(model.support_vectors_)
        return {
            "kind": "support_vector_classifier",
            "stores_rows": True,
            "n_stored_rows": int(stored.shape[0]),
            "n_stored_columns": int(stored.shape[1]),
        }
    return {"kind": type(model).__name__, "stores_rows": False, "n_stored_rows": 0}


def decide(
    *,
    mia: dict | None = None,
    attribute: dict | None = None,
    accuracy_gap: float | None = None,
    size: dict | None = None,
    stored: dict | None = None,
    file_ok: bool = True,
    wrapper_blocks: bool = False,
) -> dict:
    reasons: list[str] = []
    if wrapper_blocks:
        reasons.append("The safe-wrapper release report says not to release this file.")
    if not file_ok:
        reasons.append("File type is not on the accepted list (joblib or pickle).")
    if stored and stored.get("stores_rows"):
        reasons.append(
            f"{stored['kind']} stores {stored['n_stored_rows']} training rows inside the model file."
        )
    if size and size["ratio"] > POLICY["max_model_to_data_ratio"]:
        reasons.append(
            f"Model file is {size['ratio']:.2f} times the training table "
            f"(limit {POLICY['max_model_to_data_ratio']})."
        )
    if accuracy_gap is not None and accuracy_gap > POLICY["max_accuracy_gap"]:
        reasons.append(
            f"Training accuracy exceeds set-aside accuracy by {accuracy_gap:.3f} "
            f"(limit {POLICY['max_accuracy_gap']}), which indicates overfitting."
        )
    if mia:
        auc = mia.get("auc")
        if auc is not None and auc >= POLICY["max_mia_auc"]:
            reasons.append(f"Worst-case membership AUC is {auc:.3f} (limit {POLICY['max_mia_auc']}).")
        if mia["advantage"] >= POLICY["max_advantage"]:
            reasons.append(
                f"Membership advantage is {mia['advantage']:.3f} (limit {POLICY['max_advantage']})."
            )
        if mia["tpr_at_fpr_10"] >= POLICY["max_tpr_at_fpr_10"]:
            reasons.append(
                f"True-positive rate at 10% false-positive rate is {mia['tpr_at_fpr_10']:.3f} "
                f"(limit {POLICY['max_tpr_at_fpr_10']})."
            )
        if mia["fdif"] >= POLICY["max_fdif"] and mia["p_value"] <= POLICY["max_fdif_p_value"]:
            reasons.append(
                f"FDIF is {mia['fdif']:.3f} with p={mia['p_value']:.3f} "
                "(members are concentrated in the extreme scores)."
            )
    if attribute:
        ratio = attribute["attribute_risk_ratio"]
        if ratio == float("inf") or ratio >= POLICY["max_attribute_risk_ratio"]:
            shown = "infinite" if ratio == float("inf") else f"{ratio:.3f}"
            reasons.append(
                f"Attribute risk ratio is {shown} (limit {POLICY['max_attribute_risk_ratio']}). "
                "Missing values are easier to fill in for training rows than for set-aside rows."
            )
    return {"release": not reasons, "reasons": reasons}
