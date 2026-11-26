# Request decomposition on the GTSQA development split (prompt v3)

Files: `decomposition_dev_v3.json` and `decomposition_dev_v3b.json` (two passes with the same prompt,
38 questions each). Gold: `generation_reference.sparql_query` and `question_profile.graph_isomorphism`
in `Dataset/gtsqa_development_gold.json`. All judgements were made by hand.

## Criteria

- **ok**: the constraints match the gold SPARQL query as a graph. Constants are compared by QID
  (the known entity table must contain the gold node), variables may be renamed, relation wording and
  edge direction are ignored, and `?answer` must map to the gold `?answer`.
  Type constraints (`is a`) are not required; the gold type triple of 38861 is therefore always missing.
- **diff**: no such match exists.
- Cause of a problem (a question may have more than one):
  - **A** decomposition error (LLM): a condition is missing, merged into one constraint,
    or an unknown entity is replaced by a known one.
  - **B** known entity table error: a known entity points to a wrong node, is not found,
    or an entity on the answer path is given as known.
  - **C** gold or question inconsistent: the decomposition follows the question,
    but the gold query or the KG expresses it differently.

## Summary

|                                   | v3    | v3b   |
|-----------------------------------|-------|-------|
| ok                                | 28/38 | 28/38 |
| ok and no problem of type A/B/C   | 27/38 | 27/38 |
| diff                              | 10/38 | 10/38 |
| questions with type A             | 4     | 4     |
| questions with type B             | 0     | 1     |
| questions with type C             | 8     | 8     |

- 37564 is ok only because direction is ignored: the gold answer is the child, not the father (type C).
- 40560 has both A and C.
- Between v3 and v3b the constraints differ in 7 questions (16154, 31606, 4519, 40487, 26818, 24883, 16747)
  and the answer type in one more (38861). Four of these are wording or variable names only (16154, 4519, 40487, 26818);
  31606 also adds an unused entity, 24883 and 16747 change in substance.
  The ok/diff result is the same in all 38 questions.
- Compared with the first prompt (`logs/decomposition_dev.json`, 23/38 ok without problem, older known entity
  verification): 33122, 34508, 11794, 40448 (decomposition) and 9858, 37366 (known entity table) were fixed;
  24883 and 13321 became worse.

Patterns:
- A, an unknown entity replaced by a known one: 24883 (Giants Stadium used for the team's home stadium).
- A, a category entity read as the specific entity: 13321 ("national anthem" as the anthem itself).
- A, a condition dropped as a type word: 38861 (residence, expected from the rule that type words
  are not written as constraints), 40560 (academic art; the extraction did not find it either).
- B, an answer-path entity given as known (v3b only): 16747 ("rural district" resolved to Großenhain Rural District).
- C, a condition attached to a different entity than in the gold query: 1734, 42600, 40560, 42587.
- C, the KG needs a different number of hops than the question states: 8865, 16747, 31606.
- C, the gold relation has the wrong direction: 37564.

## Per question

| id    | structure    | v3   | v3b  | type | note |
|-------|--------------|------|------|------|------|
| 13311 | (4)          | ok   | =    |      | |
| 37715 | (4)          | ok   | =    |      | |
| 40154 | (3)(1)       | ok   | =    |      | |
| 42587 | (3)(1)       | diff | =    | C    | question: the student acted in the film; KG and gold: the teacher Rajz did (gold variable ?actor) |
| 4519  | (2)(2)       | ok   | ok   |      | v3b: wording only |
| 8865  | (2)(2)       | diff | =    | C    | "professional focus" as one relation; gold: occupation, then field of this occupation |
| 16154 | ((2)(1))     | ok   | ok   |      | v3b: variable name only |
| 31606 | ((2)(1))     | diff | diff | C    | question: engine, then its series; KG: the engine is the series itself (gold: one hop); v3b also extracts "engine" (not found, unused) |
| 33122 | ((1)(1))(1)  | ok   | =    |      | still life now resolved to the genre and used |
| 40487 | ((1)(1))(1)  | ok   | ok   |      | v3b: wording only |
| 1012  | (2(1)(1))    | ok   | =    |      | |
| 41371 | (2(1)(1))    | ok   | =    |      | E3 "Olympic event" not found and unused (type word) |
| 29248 | (4)          | ok   | =    |      | |
| 35550 | (4)          | ok   | =    |      | |
| 37564 | (4)          | ok   | =    | C    | question asks for the father; gold `?answer P22 ?person` gives the child |
| 1734  | (3)(1)       | diff | =    | C    | question: the country is the film setting; gold: the capital is |
| 34508 | (3)(1)       | ok   | =    |      | "two stations away" split into two hops |
| 37366 | (3)(1)       | ok   | =    |      | E2 has 27 same-name nodes, including the gold one |
| 5902  | (2)(2)       | ok   | =    |      | |
| 10699 | (2)(2)       | ok   | =    |      | |
| 26818 | (2)(2)       | ok   | ok   |      | v3b: wording only |
| 32536 | ((2)(1))     | ok   | =    |      | |
| 38861 | ((2)(1))     | diff | =    | A    | residence not written (type word rule, expected); not extracted either; v3b answer type "architect" |
| 42600 | ((2)(1))     | diff | =    | C    | question: Equatorial Guinea attached to Malabo's province; gold: to the bordering province |
| 11794 | ((1)(1))(1)  | ok   | =    |      | ?winger - position - winger now present |
| 40448 | ((1)(1))(1)  | ok   | =    |      | |
| 40560 | ((1)(1))(1)  | diff | =    | A, C | A: academic art missing (not extracted either); C: "mentioned in" attached to the artist, gold: to the partner |
| 16747 | (2(1)(1))    | diff | diff | C; B in v3b | worked in the district; KG: worked in Großenhain, the district's capital (one more hop); v3b: "rural district" resolved to Großenhain Rural District, an answer-path entity |
| 24883 | (2(1)(1))    | diff | diff | A    | Giants Stadium used instead of the team's home stadium (?venue missing); v3b in a different form |
| 39707 | (2(1)(1))    | ok   | =    |      | |
| 14105 | (1)          | ok   | =    |      | |
| 27579 | (1)          | ok   | =    |      | |
| 24958 | (2)          | ok   | =    |      | |
| 31330 | (2)          | ok   | =    |      | |
| 9858  | (1)(1)       | ok   | =    |      | Keller now found |
| 24117 | (1)(1)       | ok   | =    |      | |
| 13321 | (3)          | diff | =    | A    | "national anthem" (E2) used as the anthem itself; ?anthem missing |
| 38738 | (3)          | ok   | =    |      | |

`=` means the v3b output has the same constraints and answer type as v3.
