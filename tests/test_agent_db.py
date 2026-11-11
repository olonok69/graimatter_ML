"""Demo 7: only the database permissions stop every attack, and the job still gets done.

These pin the claims the report makes: each upper layer, which reads the SQL text, misses
attacks that the engine refuses; the database is unchanged after the run; the legitimate
requests are answered by every layer; and the regenerated report matches demo/output/.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import run_agent_db_demo

from agent_db_demo import database, layers

REPO_OUTPUT = Path(__file__).resolve().parents[1] / "demo" / "output"


@pytest.fixture(scope="module")
def run(tmp_path_factory):
    out = tmp_path_factory.mktemp("output")
    saved = run_agent_db_demo.OUTPUT
    run_agent_db_demo.OUTPUT = out
    try:
        numbers = run_agent_db_demo.main()
    finally:
        run_agent_db_demo.OUTPUT = saved
    return numbers, out


def test_report_matches_versioned(run):
    _, out = run
    name = "agent_db_report.txt"
    assert (out / name).read_text(encoding="utf-8") == (REPO_OUTPUT / name).read_text(encoding="utf-8")


def test_only_the_database_stops_every_attack(run):
    numbers, _ = run
    assert numbers["stopped_alone"] == {"keyword filter": 5, "access policy": 2, "database permissions": 10}
    assert numbers["first_stopped_by"] == {"keyword filter": 5, "access policy": 2, "database permissions": 3}


def test_the_job_still_works_and_nothing_changed(run):
    numbers, _ = run
    assert set(numbers["legitimate_answered"].values()) == {numbers["legitimate"]}
    assert numbers["database_unchanged"]


def test_comma_join_slips_past_the_policy_but_not_the_engine(tmp_path):
    db = tmp_path / "clinic.db"
    database.build(db)
    sql = "SELECT s.password_hash FROM appointments a, staff_credentials s"
    assert layers.tables_named(sql) == ["appointments"]
    assert not layers.access_policy(sql, database.GRANTED).blocked
    assert layers.database_permissions(db, sql, database.GRANTED).blocked


def test_engine_refuses_writes_even_when_text_looks_like_a_read(tmp_path):
    db = tmp_path / "clinic.db"
    database.build(db)
    before = database.fingerprint(db)
    sql = "WITH clinic_summary AS (SELECT 1) REPLACE INTO appointments (id, note) SELECT 1, 'x' FROM clinic_summary"
    assert not layers.keyword_filter(sql).blocked
    assert layers.database_permissions(db, sql, database.GRANTED).blocked
    assert database.fingerprint(db) == before
