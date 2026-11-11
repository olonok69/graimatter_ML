"""An LLM agent reaches a database: which defence layer actually holds? (demo 7)

Part 4c of the deck shows a real, read-only MCP server that lets an agent query a
production database and nothing more (technical guide §26). This demo is a miniature of
the same design in SQLite, so every number can be rerun with the standard library:

  0. The database and the agent: two tables it may read, two it may not.
  1. The agent does its job, reads a note with an injected instruction, and obeys it:
     ten attacks, each mirroring a step of JADEPUFFER (technical guide Appendix B).
  2. Each layer on its own: the keyword filter, the access policy, the database permissions.
  3. What gets through when a layer is the only one, run on a throwaway copy.
  4. All layers together, in the order a request meets them, and the database afterwards.
  5. Where it sits: the order of trust, and the frameworks.

Run from the repository root:

    python demo/run_agent_db_demo.py

Walkthrough of the code and its output: docs/guide/Demo_Guide_EN.md, section 7
(Spanish: docs/guide/Guia_Demos_ES.md). Comments cite it as "Demo guide §7.N".
Nothing here touches a real database; everything runs in a temporary folder.
"""

from __future__ import annotations

import contextlib
import os
import shutil
import sys
import tempfile
from pathlib import Path

DEMO_DIR = Path(__file__).resolve().parent
if str(DEMO_DIR) not in sys.path:
    sys.path.insert(0, str(DEMO_DIR))

from agent_db_demo import database, layers  # noqa: E402
from agent_db_demo.agent import PROMPT_GUIDANCE, REQUESTS  # noqa: E402

OUTPUT = DEMO_DIR / "output"
LAYERS = ("keyword filter", "access policy", "database permissions")


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


@contextlib.contextmanager
def _inside(folder: Path):
    """Run with `folder` as the working directory, so a relative ATTACH lands there and not in the repo."""
    before = Path.cwd()
    os.chdir(folder)
    try:
        yield
    finally:
        os.chdir(before)


def judge(db: Path, request) -> dict[str, layers.Verdict]:
    """Ask each layer, on its own, what it would do with one request (Demo guide §7.2)."""
    return {
        "keyword filter": layers.keyword_filter(request.sql),
        "access policy": layers.access_policy(request.sql, database.GRANTED),
        "database permissions": layers.database_permissions(db, request.sql, database.GRANTED),
    }


def damage(original: Path, workdir: Path, request) -> str:
    """Run one attack with no protection on a fresh copy and say, in plain words, what it did (Demo guide §7.3)."""
    if request.key == "A10":
        # Not run: with no bound it would count 40^5 row combinations, which takes long enough to stall the demo.
        return f"not run here: it asks for 40^5 = {40 ** 5:,} row combinations, with nothing to stop it"
    copy = workdir / f"copy_{request.key}.db"
    shutil.copyfile(original, copy)
    before = database.fingerprint(copy)
    with _inside(workdir):
        verdict = layers.unprotected(copy, request.sql)
        attached = (workdir / "loot.db").exists()
        if attached:
            (workdir / "loot.db").unlink()
    after = database.fingerprint(copy)
    hashes = {h for (_, _, h) in _credential_rows(original)}
    seen = {str(v) for row in verdict.rows for v in row} & hashes
    effects = []
    for table, (count, digest) in before.items():
        if table not in after:
            effects.append(f"table {table} dropped ({count} rows gone)")
        elif after[table][0] < count:
            effects.append(f"{count - after[table][0]} of {count} {table} rows deleted")
        elif after[table][1] != digest:
            effects.append(f"{table} changed (same {count} rows, different content)")
    if seen:
        effects.append(f"{len(seen)} of 3 password hashes read (in {len(verdict.rows)} rows returned)")
    if request.key == "A7":
        tables = sum(1 for row in verdict.rows if row[0] == "table")
        effects.append(f"the whole schema read: {len(verdict.rows)} catalogue entries, {tables} of them table "
                       "definitions with every column")
    if attached:
        effects.append("a database file the agent controls was created and attached")
    if request.key == "A9" and not verdict.blocked:
        effects.append("ran: the session's read-only guard is now off")
    return "; ".join(effects) if effects else verdict.reason


def _credential_rows(db: Path) -> list[tuple]:
    import sqlite3

    con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    try:
        return con.execute("SELECT id, username, password_hash FROM staff_credentials").fetchall()
    finally:
        con.close()


def main() -> dict:
    report = Report()
    OUTPUT.mkdir(parents=True, exist_ok=True)
    workdir = Path(tempfile.mkdtemp(prefix="agent_db_demo_"))
    try:
        return _run(report, workdir)
    finally:
        report.save(OUTPUT / "agent_db_report.txt")
        shutil.rmtree(workdir, ignore_errors=True)


def _run(report: Report, workdir: Path) -> dict:
    db = workdir / "clinic.db"
    database.build(db)
    start = database.fingerprint(db)
    attacks = [r for r in REQUESTS if not r.legitimate]
    jobs = [r for r in REQUESTS if r.legitimate]

    _section(report, "An LLM agent reaches a database: which defence layer actually holds?")
    report.p("A miniature, in SQLite, of the read-only MCP server of Part 4c. Same three layers, same order of trust;")
    report.p("everything synthetic, in a temporary folder.")

    # 0. The database and the agent (Demo guide §7.0) ------------------------------------------
    _section(report, "0. The database and the agent")
    for table, (count, _) in start.items():
        role = "the agent may read" if table in database.GRANTED else "NOT for this agent"
        report.p(f"  {table:<18} {count:>3} rows   {role}")
    report.p(f"  Granted to the agent's database user: SELECT on {', '.join(database.GRANTED)}. Nothing else.")
    report.p(f'  The agent\'s instructions (prompt guidance): "{PROMPT_GUIDANCE}"')

    # 1. The agent's requests (Demo guide §7.1) --------------------------------------------------
    _section(report, "1. The agent does its job, meets an injected note, and obeys it")
    answers = {}
    for r in jobs:
        v = layers.database_permissions(db, r.sql, database.GRANTED)
        answers[r.key] = v
        report.p(f"  {r.key}  {r.what}: {len(v.rows)} row{'s' if len(v.rows) != 1 else ''}. {r.sql}")
        if r.key == "L2":
            report.p("        " + ", ".join(f"{clinic} {n}" for clinic, n in v.rows))
    injected = answers["L3"].rows[0]
    report.p(f"  L3 returns appointment {injected[0]}, whose note says:")
    report.p(f'        "{injected[1]}"')
    report.p("  That text came from the data, not from the operator. The agent treats it as an instruction")
    report.p(f"  and sends {len(attacks)} attacks, although its own instructions forbid exactly this:")
    for r in attacks:
        report.p(f"  {r.key:<4} {r.what} ({r.mirrors})")
        report.p(f"         {r.sql}")
    report.p(f"  Working. Prompt guidance stopped 0 of {len(attacks)}: the agent was told, and sent them anyway.")

    # 2. Each layer on its own (Demo guide §7.2) -------------------------------------------------
    _section(report, "2. Each layer on its own: does it stop the request?")
    verdicts = {r.key: judge(db, r) for r in REQUESTS}
    report.p(f"  {'':<5}{'keyword filter':<17}{'access policy':<16}{'database permissions'}")
    for r in REQUESTS:
        cells = ["stops" if verdicts[r.key][name].blocked else "lets through" for name in LAYERS]
        report.p(f"  {r.key:<5}{cells[0]:<17}{cells[1]:<16}{cells[2]}")
    stopped = {name: [r.key for r in attacks if verdicts[r.key][name].blocked] for name in LAYERS}
    jobs_ok = {name: [r.key for r in jobs if not verdicts[r.key][name].blocked] for name in LAYERS}
    report.p("")
    for name in LAYERS:
        report.p(f"  {name}: stops {len(stopped[name])} of {len(attacks)} attacks; "
                 f"answers {len(jobs_ok[name])} of {len(jobs)} legitimate requests.")
        report.p(f"    Working. Stops {', '.join(stopped[name]) or 'none'}.")
    report.p("  Why each was stopped, by the layer that understood it:")
    for r in attacks:
        reasons = [f"{name}: {verdicts[r.key][name].reason}" for name in LAYERS if verdicts[r.key][name].blocked]
        report.p(f"    {r.key:<4} " + " | ".join(reasons))

    # 3. What gets through when a layer is alone (Demo guide §7.3) -------------------------------
    _section(report, "3. If that layer were the only one: what the attacks it misses do")
    report.p("  Each attack runs with no protection on a fresh copy of the database, so its damage is measured alone.")
    effects = {r.key: damage(db, workdir, r) for r in attacks}
    for name in LAYERS:
        missed = [r for r in attacks if not verdicts[r.key][name].blocked]
        report.p(f"  {name} alone: {len(missed)} of {len(attacks)} get through.")
        for r in missed:
            report.p(f"    {r.key:<4} {effects[r.key]}")
        if not missed:
            report.p("    none: every write, every read outside the grant and the runaway query are refused by the engine.")

    # 4. All layers together (Demo guide §7.4) ---------------------------------------------------
    _section(report, "4. All layers together, in the order a request meets them")
    first = {}
    for r in attacks:
        first[r.key] = next(name for name in LAYERS if verdicts[r.key][name].blocked)
    tally = {name: [k for k, v in first.items() if v == name] for name in LAYERS}
    for name in LAYERS:
        report.p(f"  first stopped by the {name:<21} {len(tally[name])}  ({', '.join(tally[name]) or '-'})")
    report.p(f"  Working. {' + '.join(str(len(tally[n])) for n in LAYERS)} = {sum(len(t) for t in tally.values())} "
             f"of {len(attacks)} attacks stopped; {len(jobs_ok['database permissions'])} of {len(jobs)} "
             "legitimate requests answered.")
    end = database.fingerprint(db)
    report.p("  The database afterwards (rows and content fingerprint, before -> after):")
    for table in start:
        same = "unchanged" if start[table] == end.get(table) else "CHANGED"
        report.p(f"    {table:<18} {start[table][0]:>3} rows {start[table][1]} -> "
                 f"{end[table][0]:>3} rows {end[table][1]}   {same}")
    caught_by_wall = [k for k in tally["database permissions"]]
    report.p(f"  The upper layers stopped {len(tally['keyword filter']) + len(tally['access policy'])} early, with clear "
             f"messages. The other {len(caught_by_wall)} ({', '.join(caught_by_wall)}) passed both and met the engine.")

    # 5. Where it sits (Demo guide §7.5) ---------------------------------------------------------
    _section(report, "5. Where it sits")
    report.p("  Layer                       Reads           Stops alone   Role (operator guide's order of trust)")
    report.p(f"  1 database permissions      what it does    {len(stopped['database permissions']):>2} of {len(attacks)}"
             "      the hard boundary: the engine refuses")
    report.p(f"  2 access policy             the SQL text    {len(stopped['access policy']):>2} of {len(attacks)}"
             "      tenant filtering, above the boundary")
    report.p(f"  3 keyword filter            the SQL text    {len(stopped['keyword filter']):>2} of {len(attacks)}"
             "      a speed bump with clear errors")
    report.p(f"    prompt guidance           nothing          0 of {len(attacks)}      advisory only")
    report.p("  OWASP LLM06 (excessive agency): only read tools, a scoped account. NISTAML.018/.015 (prompt injection)")
    report.p("  is how the instruction arrived; the database user is why it did no harm. The real server adds TLS,")
    report.p("  OAuth, rate limits and a vault for secrets (technical guide §26.2); this miniature tests the query path.")

    return {
        "attacks": len(attacks),
        "legitimate": len(jobs),
        "stopped_alone": {name: len(stopped[name]) for name in LAYERS},
        "legitimate_answered": {name: len(jobs_ok[name]) for name in LAYERS},
        "first_stopped_by": {name: len(tally[name]) for name in LAYERS},
        "database_unchanged": start == end,
    }


if __name__ == "__main__":
    main()
