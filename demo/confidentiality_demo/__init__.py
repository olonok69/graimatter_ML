"""Confidentiality: what a trained model gives away about its training data (demo 5).

NIST AI 100-2e2025 calls this objective *privacy* (NISTAML.03); in the CIA triad it
is *confidentiality*. Two of its attacks, in their simplest form, on the same
synthetic cohort as the other demos:

* ``membership`` — "was this person in the training data?" (NISTAML.033). The
  attacker asks the model how sure it is about a person's real outcome; a model
  that memorised its training rows is far surer about the people it saw.
* ``attribute`` — "what is in this person's record?" (NISTAML.032 family, attribute
  inference). The attacker knows everything about a person except one field and
  tries each value; the value the model is surest about is the guess.

* ``explain`` — not an attack: the arithmetic behind every number the report
  prints (the "Working" lines), as counts and sums you can check by hand.

Both attacks need only what a normal user of the model gets: send a row, read the answer.
The run script compares four ways of releasing the same model and shows which of
them close each attack.

Walkthrough: Demo guide §5 (docs/guide/Demo_Guide_EN.md; Spanish: Guia_Demos_ES.md).
Each module is a teaching sketch, not a toolkit: demo 1 and demo 2 run the full
GRAIMATTER versions of these attacks (part 4B of the deck).
"""

__version__ = "0.1.0"
