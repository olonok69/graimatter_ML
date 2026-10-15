"""A downgrade: one value in a configuration file, and the whole system is weaker.

The classic case is export-grade cryptography: a client talked into 40-bit keys
still encrypts and decrypts correctly, so every functional test passes, but
anyone can search all the keys. Nothing here encrypts anything; the arithmetic
is enough to show the gap. The model-side analogue is a safe wrapper's
constraints file whose minimum leaf size has been lowered: the wrapper still
trains and still reports, but it now accepts trees that isolate one person.

The defence is a floor that the code checks on every load, not a value it
trusts from the file.
"""

from __future__ import annotations

SECONDS_PER_YEAR = 365.25 * 24 * 3600

# The user's floors, kept in code under review, not in the downloaded files.
KEY_BITS_FLOOR = 128
WRAPPER_FLOORS = {"min_samples_leaf": ("min", 20), "max_depth": ("max", 4)}


def brute_force_years(key_bits: int, keys_per_second: float = 1e9) -> float:
    """Time to try every key at a fixed rate, in years. 1e9 keys a second is one fast machine."""
    return 2.0**key_bits / keys_per_second / SECONDS_PER_YEAR


def below_floor(name: str, config: dict) -> list[str]:
    """Every setting in a downloaded configuration that is weaker than the user's floor."""
    problems = []
    if name == "bundle.json":
        bits = config.get("encryption", {}).get("key_bits")
        if bits is None or bits < KEY_BITS_FLOOR:
            problems.append(f"key_bits = {bits}, floor {KEY_BITS_FLOOR}")
    elif name == "constraints.json":
        rules = {rule["keyword"]: rule["value"] for rule in config["DecisionTreeClassifier"]["rules"]}
        for keyword, (operator, floor) in WRAPPER_FLOORS.items():
            value = rules.get(keyword)
            weaker = value is None or (value < floor if operator == "min" else value > floor)
            if weaker:
                problems.append(f"{keyword} {operator} {value}, floor {floor}")
    return problems


def readable_duration(years: float) -> str:
    seconds = years * SECONDS_PER_YEAR
    if seconds < 3600:
        return f"{seconds / 60:.0f} minutes"
    if seconds < 86400 * 2:
        return f"{seconds / 3600:.1f} hours"
    if years < 1:
        return f"{seconds / 86400:.0f} days"
    if years < 1000:
        return f"{years:.1f} years"
    return f"{years:.1e} years"
