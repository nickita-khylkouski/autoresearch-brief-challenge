from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from .corpus import CorpusPack
from .repository import ROOT, load_hidden_specs, load_tasks
from .sandbox import TaskTimeoutError, block_network, time_limit
from .scoring import score_task
from .submissions import load_submission
from .tool_harness import ToolHarness
from .utils import mean, now_stamp, write_json


def _default_run_dir(split: str, submission_name: str) -> Path:
    return ROOT / "runs" / f"{now_stamp()}-{split}-{submission_name}"


def evaluate_split(
    *,
    split: str,
    submission_path: str | Path,
    task_id: str | None = None,
    output_dir: str | Path | None = None,
) -> dict[str, Any]:
    tasks = load_tasks(split)
    hidden_specs = load_hidden_specs(split)
    if task_id:
        tasks = [task for task in tasks if task["task_id"] == task_id]
        if not tasks:
            raise ValueError(f"Task {task_id} not found in split {split}")

    submission = load_submission(submission_path)
    submission_name = Path(submission_path).resolve().name
    run_dir = Path(output_dir).resolve() if output_dir else _default_run_dir(split, submission_name)
    run_dir.mkdir(parents=True, exist_ok=True)

    task_results: list[dict[str, Any]] = []
    raw_outputs: list[dict[str, Any]] = []
    total_started = time.perf_counter()

    for task in tasks:
        corpus = CorpusPack(task["corpus_pack_id"])
        harness = ToolHarness(corpus, task["budget"])
        started = time.perf_counter()
        output = None
        execution_error = None
        timed_out = False
        try:
            with block_network():
                with time_limit(float(task["budget"]["max_time_seconds"])):
                    output = submission.run_task(task, harness)
        except TaskTimeoutError as exc:
            timed_out = True
            execution_error = f"{type(exc).__name__}: {exc}"
        except Exception as exc:  # pragma: no cover - exercised via tests on invalid submissions
            execution_error = f"{type(exc).__name__}: {exc}"
        elapsed = time.perf_counter() - started
        metrics = harness.metrics.to_dict()
        result = score_task(
            output=output,
            hidden=hidden_specs[task["task_id"]],
            corpus_chunk_ids=set(corpus.chunks),
            elapsed_seconds=elapsed,
            metrics=metrics,
            budget=task["budget"],
            execution_error=execution_error,
            timed_out=timed_out,
        )
        task_result = {
            "task_id": task["task_id"],
            "question": task["question"],
            "task_type": task["task_type"],
            "elapsed_seconds": round(elapsed, 6),
            **result,
        }
        task_results.append(task_result)
        raw_outputs.append(
            {
                "task_id": task["task_id"],
                "output": output,
                "execution_error": execution_error,
            }
        )

    total_elapsed = time.perf_counter() - total_started
    summary = {
        "split": split,
        "submission": {
            "path": str(Path(submission_path).resolve()),
            "name": submission_name,
            "metadata": submission.metadata,
        },
        "run_dir": str(run_dir),
        "created_at": now_stamp(),
        "final_score": round(mean([item["task_score"] for item in task_results]), 6),
        "task_count": len(task_results),
        "average_latency_seconds": round(mean([item["elapsed_seconds"] for item in task_results]), 6),
        "average_tool_calls": round(mean([item["metrics"]["tool_calls"] for item in task_results]), 6),
        "average_tokens_used": round(mean([item["metrics"]["tokens_used"] for item in task_results]), 6),
        "total_elapsed_seconds": round(total_elapsed, 6),
        "task_results": task_results,
    }
    write_json(run_dir / "summary.json", summary)
    write_json(run_dir / "raw_outputs.json", raw_outputs)
    write_json(run_dir / "scores.json", task_results)
    return summary
