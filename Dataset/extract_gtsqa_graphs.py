import json
from pathlib import Path

import pyarrow.parquet as pq

DATASET_DIR = Path(__file__).resolve().parent

SOURCE_PATH = DATASET_DIR / "gtsqa_with_graphs_test.parquet"
OUTPUT_PATH = DATASET_DIR / "gtsqa_development_agent_input.jsonl"

TARGET_IDS = {
    13311,
    37715,
    40154,
    42587,
    4519,
    8865,
    16154,
    31606,
    33122,
    40487,
    1012,
    41371,
}

source = pq.ParquetFile(SOURCE_PATH)
found_ids = set()

with OUTPUT_PATH.open("w", encoding="utf-8") as output_file:
    for batch in source.iter_batches(
        batch_size=1,
        columns=["id", "question", "graph"],
        use_threads=False,
    ):
        question_id = batch.column("id")[0].as_py()

        if question_id not in TARGET_IDS:
            continue

        question = batch.column("question")[0].as_py()
        graph = batch.column("graph")[0].as_py()

        if not question:
            raise RuntimeError(f"ID {question_id}: question is empty")
        
        if not graph:
            raise RuntimeError(f"ID {question_id}: graph is empty")

        record = {
            "id": question_id,
            "question": question,
            "graph": graph,
        }

        output_file.write(
            json.dumps(record, ensure_ascii=False) + "\n"
        )
        output_file.flush()

        found_ids.add(question_id)

        print(
            f"Extracted {question_id}: "
            f"{len(graph)} edges, "
            f"{len(found_ids)}/{len(TARGET_IDS)} questions"
        )

        if found_ids == TARGET_IDS:
            break

missing_ids = TARGET_IDS - found_ids

if missing_ids:
    raise RuntimeError(f"Missing IDs: {sorted(missing_ids)}")

print(f"Saved to: {OUTPUT_PATH}")