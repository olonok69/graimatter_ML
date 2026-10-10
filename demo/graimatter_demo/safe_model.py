"""Safe wrapper around a decision tree (TECH 9 and TECH 10).

The wrapper reads a TRE constraints file, can correct unsafe hyperparameters, and
snapshots the fitted tree. request_release() compares that snapshot with the object
the researcher asks to export, so editing parameters after fitting is visible.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import joblib
import numpy as np
from sklearn.tree import DecisionTreeClassifier


class InstanceBasedModelError(Exception):
    """Raised when the constraints file bans a model that stores training rows."""


def load_constraints(path: str | Path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def tree_digest(model: DecisionTreeClassifier) -> str:
    tree = model.tree_
    digest = hashlib.sha256()
    for array in (
        tree.children_left,
        tree.children_right,
        tree.feature,
        tree.threshold,
        tree.n_node_samples,
        tree.value.ravel(),
    ):
        digest.update(np.ascontiguousarray(array).tobytes())
    return digest.hexdigest()


def leaf_k_anonymity(model: DecisionTreeClassifier) -> int:
    """Smallest number of training rows in any leaf. k=1 means a leaf is one person."""
    tree = model.tree_
    leaves = tree.children_left == -1
    return int(tree.n_node_samples[leaves].min())


def _violates(operator: str, current, expected) -> bool:
    if operator == "min":
        return current is None or current < expected
    if operator == "max":
        # None max_depth means the tree may grow without limit.
        return current is None or current > expected
    if operator == "equals":
        return current != expected
    raise ValueError(f"Unknown constraint operator: {operator}")


class SafeModelMixin:
    adjustment_notes: list[str]
    researcher: str
    override: bool
    constraints_path: str
    model_key: str
    _snapshot: dict | None
    _snapshot_keys: set[str]

    def _enforce_constraints(self) -> None:
        spec = load_constraints(self.constraints_path)[self.model_key]
        if not spec.get("permitted", True):
            raise InstanceBasedModelError(spec.get("reason", f"{self.model_key} is not permitted"))

        notes: list[str] = []
        for rule in spec["rules"]:
            keyword = rule["keyword"]
            operator = rule["operator"]
            expected = rule["value"]
            current = self.get_params()[keyword]
            if not _violates(operator, current, expected):
                continue
            if self.override:
                notes.append(
                    f"OVERRIDE accepted: {keyword}={current!r} breaks the rule {operator} {expected!r}. "
                    "This is reported to the TRE."
                )
            else:
                self.set_params(**{keyword: expected})
                notes.append(
                    f"{keyword} changed from {current!r} to {expected!r} to satisfy {operator} {expected!r}."
                )
        if not notes:
            notes.append("Submitted hyperparameters are already inside the constraints file.")
        self.adjustment_notes = notes

    def fit(self, features, target, **fit_params):
        fitted = super().fit(features, target, **fit_params)
        self._snapshot = {
            "params": self.get_params(),
            "tree_digest": tree_digest(self),
            "k_anonymity": leaf_k_anonymity(self),
        }
        self._snapshot_keys = set(self.__dict__.keys())
        return fitted

    def request_release(self, model_path: str | Path) -> dict:
        if self._snapshot is None:
            raise RuntimeError("request_release() requires fit() first.")

        reasons: list[str] = []
        spec = load_constraints(self.constraints_path)[self.model_key]
        for rule in spec["rules"]:
            keyword = rule["keyword"]
            current = self.get_params()[keyword]
            if _violates(rule["operator"], current, rule["value"]):
                reasons.append(
                    f"parameter {keyword}={current!r} breaks the rule {rule['operator']} {rule['value']!r}."
                )

        before = self._snapshot["params"]
        for keyword, previous in before.items():
            current = self.get_params()[keyword]
            if current != previous:
                reasons.append(
                    f"parameter {keyword} changed from {previous!r} to {current!r} after the model was fitted."
                )

        if tree_digest(self) != self._snapshot["tree_digest"]:
            reasons.append("The tree structure changed after fit() without a new snapshot.")

        k_anonymity = leaf_k_anonymity(self)
        min_leaf_rule = next(
            (rule["value"] for rule in spec["rules"] if rule["keyword"] == "min_samples_leaf"),
            None,
        )
        if min_leaf_rule is not None and k_anonymity < min_leaf_rule:
            reasons.append(
                f"Smallest leaf holds {k_anonymity} training row(s); the constraints file requires at least {min_leaf_rule}."
            )

        extra_keys = sorted(set(self.__dict__) - self._snapshot_keys)
        if extra_keys:
            reasons.append(
                "Attributes were added after fit(), which can be used to hide training rows: "
                + ", ".join(extra_keys)
                + "."
            )

        model_path = Path(model_path)
        model_path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self, model_path)

        if reasons:
            recommendation = "Do not allow release"
            details = "WARNING: " + " ".join(reasons)
        else:
            recommendation = "Run file through the next step of the checking procedure"
            details = "Model parameters are within recommended ranges and match the post-fit snapshot."

        report = {
            "researcher": self.researcher,
            "model_type": self.model_key,
            "model_save_file": model_path.name,
            "details": details,
            "recommendation": recommendation,
            "reason": details if reasons else "",
            "k_anonymity": k_anonymity,
            "adjustment_notes": list(self.adjustment_notes),
            "override": self.override,
        }
        model_path.with_suffix(".release.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
        return report


class SafeDecisionTreeClassifier(SafeModelMixin, DecisionTreeClassifier):
    """Decision tree whose hyperparameters are checked against the TRE constraints file."""

    def __init__(
        self,
        constraints_path: str,
        researcher: str = "demo-researcher",
        override: bool = False,
        criterion: str = "gini",
        max_depth: int | None = None,
        min_samples_split: int = 2,
        min_samples_leaf: int = 1,
        random_state: int = 0,
    ):
        self.constraints_path = str(constraints_path)
        self.researcher = researcher
        self.override = override
        self.model_key = "DecisionTreeClassifier"
        self._snapshot = None
        self._snapshot_keys = set()
        self.adjustment_notes = []
        DecisionTreeClassifier.__init__(
            self,
            criterion=criterion,
            max_depth=max_depth,
            min_samples_split=min_samples_split,
            min_samples_leaf=min_samples_leaf,
            random_state=random_state,
        )
        self._enforce_constraints()


class SafeKNeighborsClassifier:
    """Appendix B: the safe k-nearest-neighbours wrapper refuses the algorithm."""

    def __init__(self, constraints_path: str, **_ignored):
        spec = load_constraints(constraints_path)["KNeighborsClassifier"]
        raise InstanceBasedModelError(spec["reason"])


class SafeSVC:
    """Standard SVC is refused. A differentially private SVC would be a different class."""

    def __init__(self, constraints_path: str, **_ignored):
        spec = load_constraints(constraints_path)["SVC"]
        raise InstanceBasedModelError(spec["reason"])
