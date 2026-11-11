"""Demo 7: an LLM agent reaching a database, and which defence layer actually holds.

A miniature, in SQLite, of the read-only MCP server of Part 4c (technical guide §26).
The real server sits in front of PostgreSQL; this one keeps the same three layers so the
numbers can be rerun on any machine with the standard library alone:

  database.py  the clinic database: two tables the agent may read, two it may not
  layers.py    the three layers: keyword filter, access policy, database permissions
  agent.py     the requests a prompt-injected agent sends (legitimate ones and attacks)

Walkthrough: Demo guide §7 (docs/guide/Demo_Guide_EN.md; Spanish: Guia_Demos_ES.md).
"""
