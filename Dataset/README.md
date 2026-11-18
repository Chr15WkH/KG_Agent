# Datasets

Local data for the KG Agent evaluation. This file covers what each file is,
which files are in Git, and how to rebuild the rest.

All commands run from the project root inside `.venv`. The GTSQA scripts need
`pyarrow` and `rdflib`.

## Overview

| Dataset | Role | Where the items live |
|---|---|---|
| GTSQA | Multi-hop KG retrieval and reasoning, analysed by graph structure | Local files in this folder, synchronised to Langfuse (`gtsqa-development`, `gtsqa-test`) |
| GTSQA_UA | Refusal: answerable original vs. unanswerable variant with deleted facts | `gtsqa_ua_gold.json` (development) and `gtsqa_ua_test_gold.json` (test), derived from the GTSQA split of the same name |
| CR-LT-KGQA | Boolean questions over small, incomplete graphs | Langfuse dataset `CR-LT-KGQA`; only the split IDs are stored here |
| KQA Pro | Early pilot (12 questions), not part of the evaluation | `kqapro_*` files |

Split manifests in `splits/` fix the sample IDs of every development and test
split. `Evaluation/splits.py` reads them; development and test never overlap.

## GTSQA

### Source

GTSQA (Cattaneo, Luschi and Justus, *Ground-Truth Subgraphs for Better
Training and Evaluation of Knowledge Graph Augmented LLMs*, arXiv:2511.04473),
Hugging Face dataset [`Graphcore/GTSQA`](https://huggingface.co/datasets/Graphcore/GTSQA),
licensed CC BY 4.0. All questions used here come from its **test split**.

| Local file | File in `Graphcore/GTSQA` | SHA256 | In Git |
|---|---|---|---|
| `gtsqa_without_graphs_test.parquet` | `gtsqa/test.parquet` | `e4a6c9973a9a716fe59015a34d16223fdec6a4917f56fc58f98a813b7809c4f0` | yes |
| `gtsqa_with_graphs_test.parquet` | `gtsqa-with-graphs/test-00000-of-00001.parquet` | `07e50a155267f46de411c700e73b74f0a41ed73d8a402c53e4e8f299de0f6c69` | no (832 MB) |

Both files are from revision `47af8293ef04024559955299e64c1543733914a7`.
The files are used unchanged; only the local file names differ.

### Files

| File | Content | In Git |
|---|---|---|
| `splits/gtsqa_splits.json` | Development and test sample IDs, sampling seed and criteria | yes |
| `gtsqa_development_gold.json` | Gold records of the development split | yes |
| `gtsqa_development_agent_input.jsonl` | `id`, `question` and full question graph per development question | yes (~53 MB) |
| `gtsqa_test_gold.json` | Gold records of the test split | yes |
| `gtsqa_test_agent_input.jsonl` | Same as above for the test split | no (~200 MB, above GitHub's 100 MB limit) |

Gold records keep the fields of the source file needed for evaluation and for
building GTSQA_UA: question profile (`question`, `n_hops`, `graph_isomorphism`,
`redundant`), `answer_node`, labelled `answer_subgraph`, `sparql_query`,
`seed_entities`, `all_answers_wikikg2` and `full_answer_subgraph_wikikg2`.
The agent never sees Gold records.

### Rebuild the test graphs on a new machine

Only the test agent input is missing after a clone. Download the source file
at the pinned revision, check it, then extract:

```bash
python - <<'EOF'
import shutil
from huggingface_hub import hf_hub_download

path = hf_hub_download(
    repo_id="Graphcore/GTSQA",
    repo_type="dataset",
    filename="gtsqa-with-graphs/test-00000-of-00001.parquet",
    revision="47af8293ef04024559955299e64c1543733914a7",
)
shutil.copyfile(path, "Dataset/gtsqa_with_graphs_test.parquet")
EOF

shasum -a 256 Dataset/gtsqa_*_test.parquet      # Linux: sha256sum
python Dataset/extract_gtsqa_graphs.py --split test
```

The download also stays in the Hugging Face cache (`~/.cache/huggingface`);
delete it there if disk space is short. The extraction ends with a check of
every question against its Gold record and must report `0 failed`.

### How the splits were built

Eligible questions, the same for both splits:

- graph isomorphism is one of the ten structures below;
- `redundant` is false;
- exactly one answer in `all_answers_wikikg2`;
- non-empty `full_answer_subgraph_wikikg2`;
- `check_minimal_evidence.py` passes: the SPARQL query on the Gold evidence
  returns the Gold answer, and removing any single evidence triple leaves it
  without an answer.

Quota per structure:

| Structures | Edges | Development | Test |
|---|---|---|---|
| `(4)`, `(3)(1)`, `(2)(2)`, `((2)(1))`, `((1)(1))(1)`, `(2(1)(1))` | 4 | 5 each (30) | 18 each (108) |
| `(1)`, `(2)`, `(1)(1)`, `(3)` | 1–3 | 2 each (8) | 10 each (40) |
| **Total** | | **38** | **148** |

The other four structures of the source test split, `(2)(1)`, `((1)(1))`,
`(1)(1)(1)` and `(1)(1)(1)(1)`, are not used.

Questions are drawn at random with seed `20261117`, per split and structure,
from the eligible questions not yet in either split. Questions in all
`test_type` categories (`in_distribution`, `unseen_relation_type`,
`unseen_graph_type`) are eligible, because the agents are not trained on the
GTSQA training split.

Development set history: the first 12 questions (two for each four-edge
structure) were chosen by hand before these scripts existed; their selection
criteria were not recorded. `build_gtsqa_splits.py` confirms that all 12 meet
the criteria above. The other 26 were drawn by the script.

Build steps, in order:

```bash
python Dataset/build_gtsqa_splits.py --split <development|test>          # dry run
python Dataset/build_gtsqa_splits.py --split <development|test> --write
python Dataset/build_gtsqa_gold.py --split <development|test> --write
python Dataset/extract_gtsqa_graphs.py --split <development|test>
```

All three scripts only add data. Existing IDs, Gold records and graphs are
never rewritten. The Gold builder regenerates existing records and stops if any
of them differs from the file. Re-running a completed split changes nothing.

## GTSQA_UA

Each GTSQA_UA pair has two items: the original question (`<id>-original`) and
an unanswerable variant (`<id>-ua-01`) in which one or two Gold evidence facts
are deleted from the question graph. Deletion candidates are tried in a fixed
order, single facts before pairs. A variant is unanswerable when the same
SPARQL query runs and returns no answer. The UA Gold files store the deletion
records, not graphs; the UA adapter rebuilds each graph at run time from the
GTSQA agent input of the same split and checks it again.

| Split | Built by | Source questions | Size | Files |
|---|---|---|---|---|
| development | `build_gtsqa_ua.py` | first 12 GTSQA development questions | 12 pairs (24 items) | `gtsqa_ua_gold.json` |
| test | `build_gtsqa_ua_test.py` | GTSQA test split, 5 per structure | 50 pairs (100 items) | `gtsqa_ua_test_gold.json` |

Both scripts build each pair with the same function (`build_pair` in
`build_gtsqa_ua.py`). They differ only in which questions they use:

- Development: every question in the development Gold file at the time of
  building. The script refuses to overwrite its output, so re-running it now
  would build pairs for all 38 questions into a new file given with `--output`.
- Test: per structure, the GTSQA test questions are shuffled with seed
  `20261117` and tried in that order until 5 pairs are built. Questions without
  a valid deletion are skipped and listed under `skipped` in the output. The
  script writes nothing if a structure ends with fewer than 5 pairs, and it
  also writes the test IDs into `splits/gtsqa_ua_splits.json`.

Both UA Gold files are in Git. Running the test set needs
`gtsqa_test_agent_input.jsonl` (see the GTSQA section).

```bash
python Dataset/build_gtsqa_ua_test.py      # after the GTSQA test split is built
```

## CR-LT-KGQA

The 200 questions are read from the Langfuse dataset `CR-LT-KGQA`; graphs are
stored in item metadata. `splits/crlt_splits.json` holds 50 development and
150 test IDs. `build_crlt_splits.py` derives the test split as all ACTIVE
Langfuse items minus the development split (requires KIT VPN).
