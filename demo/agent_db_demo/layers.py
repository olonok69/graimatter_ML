"""The three defence layers of Part 4c, and an unprotected connection to compare with (Demo guide §7.2).

Order of trust, from the real server's operator guide (technical guide §26.3):

  1. Database permissions, the hard boundary. The engine itself refuses. Here: the file is
     opened read-only and an SQLite *authorizer* allows only SELECT and only on the granted
     tables, the closest SQLite has to PostgreSQL's `GRANT SELECT ON appointments, ...`.
     A step budget stands in for the server's per-query timeout.
  2. The access policy, tenant filtering. Application code in the server: an allow list of
     tables, checked by reading the table names out of the SQL text.
  3. The keyword filter (with prompt guidance, the advisory layer). Application code that
     reads the SQL text: SELECT or WITH only, one statement, no write or admin keywords.

Layers 2 and 3 look at the *text* of a request; layer 1 looks at what the engine is about
to *do*. That difference is the whole demo.
"""

from __future__ import annotations

import re
import sqlite3
from dataclasses import dataclass, field
from pathlib import Path

# Words the keyword filter refuses anywhere in a request (whole words, any case).
BLOCKED_KEYWORDS = ("INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "CREATE", "ATTACH", "DETACH", "PRAGMA",
                    "VACUUM", "GRANT")

# The server's per-query bound. SQLite calls the progress handler every STEP_CHUNK virtual-machine
# instructions; after STEP_BUDGET calls the query is interrupted. Counting instructions, not seconds,
# keeps the demo identical on every machine.
STEP_CHUNK = 1_000
STEP_BUDGET = 2_000  # = 2,000,000 instructions


@dataclass
class Verdict:
    """What one layer did with one request."""

    blocked: bool
    reason: str
    rows: list = field(default_factory=list)


def statements(sql: str) -> list[str]:
    """Split a request into statements on ';', the way a driver that accepts several would."""
    return [part.strip() for part in sql.split(";") if part.strip()]


# -- Layer 3: the keyword filter -----------------------------------------------------------------

def keyword_filter(sql: str) -> Verdict:
    """SELECT or WITH only, a single statement, and none of BLOCKED_KEYWORDS (Demo guide §7.2, layer 3)."""
    parts = statements(sql)
    if len(parts) != 1:
        return Verdict(True, f"{len(parts)} statements in one request (stacked)")
    first = parts[0].split(None, 1)[0].upper()
    if first not in ("SELECT", "WITH"):
        return Verdict(True, f"starts with {first}, not SELECT or WITH")
    for word in BLOCKED_KEYWORDS:
        if re.search(rf"\b{word}\b", sql, flags=re.IGNORECASE):
            return Verdict(True, f"contains the keyword {word}")
    return Verdict(False, "looks like a single read")


# -- Layer 2: the access policy ------------------------------------------------------------------

_TABLE_AFTER = re.compile(r"\b(?:FROM|JOIN)\s+[\"`\[]?([A-Za-z_][A-Za-z0-9_]*)", flags=re.IGNORECASE)


def tables_named(sql: str) -> list[str]:
    """The table names the policy sees: the word after each FROM or JOIN.

    This is how a policy that reads SQL text usually works, and it is where it can be out-thought:
    a second table after a comma (`FROM a, b`) or a table after INTO is never looked at.
    """
    return [m.group(1).lower() for m in _TABLE_AFTER.finditer(sql)]


def access_policy(sql: str, allowed: tuple[str, ...]) -> Verdict:
    """Refuse a request that names a table outside the allow list (Demo guide §7.2, layer 2)."""
    named = tables_named(sql)
    if not named:
        return Verdict(False, "names no table after FROM or JOIN, so there is nothing to check")
    outside = [t for t in named if t not in allowed]
    if outside:
        return Verdict(True, f"names a table outside the allow list: {', '.join(sorted(set(outside)))}")
    return Verdict(False, "every table it names is on the allow list")


# -- Layer 1: database permissions (and the per-query bound) -------------------------------------

# Names for SQLite's authorizer action codes (sqlite.org/c3ref/c_alter_table.html), so a refusal
# can say what was refused.
_ACTION_NAMES = {
    1: "CREATE INDEX", 2: "CREATE TABLE", 3: "CREATE TEMP INDEX", 4: "CREATE TEMP TABLE", 5: "CREATE TEMP TRIGGER",
    6: "CREATE TEMP VIEW", 7: "CREATE TRIGGER", 8: "CREATE VIEW", 9: "DELETE", 10: "DROP INDEX", 11: "DROP TABLE",
    12: "DROP TEMP INDEX", 13: "DROP TEMP TABLE", 14: "DROP TEMP TRIGGER", 15: "DROP TEMP VIEW", 16: "DROP TRIGGER",
    17: "DROP VIEW", 18: "INSERT", 19: "PRAGMA", 20: "READ", 21: "SELECT", 22: "TRANSACTION", 23: "UPDATE",
    24: "ATTACH", 25: "DETACH", 26: "ALTER TABLE", 27: "REINDEX", 28: "ANALYZE", 29: "CREATE VTABLE",
    30: "DROP VTABLE", 31: "FUNCTION", 32: "SAVEPOINT", 33: "RECURSIVE",
}
_WRITES = (sqlite3.SQLITE_INSERT, sqlite3.SQLITE_UPDATE, sqlite3.SQLITE_DELETE)


def _authorizer(granted: tuple[str, ...], refused: list[str]):
    """Return an SQLite authorizer that plays the part of a read-only, least-privilege database user.

    SQLite calls it while it compiles each statement, once per action the statement would take.
    Each refused action is appended to `refused`, so the demo can print what the engine said no to.
    """

    def check(action, arg1, arg2, db_name, trigger):
        if action in (sqlite3.SQLITE_SELECT, sqlite3.SQLITE_FUNCTION, sqlite3.SQLITE_RECURSIVE):
            return sqlite3.SQLITE_OK
        if action == sqlite3.SQLITE_READ:
            # arg1 is the table being read. A CTE has no table of its own; its reads arrive as the
            # underlying tables, so only real tables are checked.
            if (arg1 or "").lower() in granted:
                return sqlite3.SQLITE_OK
            refused.append(f"READ on {arg1} (not granted)")
            return sqlite3.SQLITE_DENY
        if action in _WRITES and arg1 == "sqlite_master":
            # Bookkeeping SQLite does on its own catalogue while compiling a DROP or CREATE. Let it pass
            # here so the authorizer is asked next about the real action (DROP TABLE billing) and refuses
            # that. The file is open read-only anyway, so nothing could be written.
            return sqlite3.SQLITE_OK
        target = f" on {arg1}" if arg1 else ""
        refused.append(f"{_ACTION_NAMES.get(action, action)}{target} (only SELECT is granted)")
        return sqlite3.SQLITE_DENY  # INSERT, UPDATE, DELETE, DROP, CREATE, ATTACH, PRAGMA, ...

    return check


def database_permissions(path: Path, sql: str, granted: tuple[str, ...]) -> Verdict:
    """Send the request to the engine as the read-only user; the engine decides (Demo guide §7.2, layer 1)."""
    con = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    refused: list[str] = []
    con.set_authorizer(_authorizer(granted, refused))
    calls = {"n": 0}

    def progress():
        calls["n"] += 1
        return 1 if calls["n"] > STEP_BUDGET else 0  # non-zero interrupts the statement

    con.set_progress_handler(progress, STEP_CHUNK)
    rows: list = []
    try:
        for stmt in statements(sql):
            rows = con.execute(stmt).fetchall()
        return Verdict(False, "the engine ran it", rows)
    except sqlite3.DatabaseError as exc:
        message = str(exc)
        if "interrupted" in message:
            return Verdict(True, f"engine stopped it after {STEP_BUDGET * STEP_CHUNK:,} steps (the per-query bound)")
        if refused:
            return Verdict(True, f"engine refused {refused[0]}")
        return Verdict(True, f"engine refused: {message}")
    finally:
        con.close()


# -- No protection: what the request does when nothing stops it ----------------------------------

def unprotected(path: Path, sql: str) -> Verdict:
    """Run the request on a writable connection with no checks, statement by statement.

    Used only on a throwaway copy of the database, to show the damage each attack would do if
    the layer that let it through were the only one.
    """
    con = sqlite3.connect(path)
    rows: list = []
    try:
        for stmt in statements(sql):
            rows = con.execute(stmt).fetchall()
        con.commit()
        return Verdict(False, "ran", rows)
    except sqlite3.DatabaseError as exc:
        return Verdict(True, f"failed: {exc}")
    finally:
        con.close()
