from __future__ import annotations

import argparse
import os
import shutil
from pathlib import Path
from typing import Any

from .agent import ChessAgent
from .artifacts import append_jsonl, ensure_run_dir, new_run_id, snapshot_best_bot, write_json, write_text
from .chart import write_progress_png
from .config import LoopConfig, ROOT, STAGE_LOOP_CONFIG
from .evaluator import evaluate_repo, evaluate_repo_subprocess
from .guardrails import hash_forbidden_files, validate_candidate_tree, validate_patch_text
from .minimax_client import MiniMaxClient
from .patcher import apply_unified_patch, copy_editable_files
from .prompt_builder import build_prompt


def run_loop(config: LoopConfig) -> dict[str, Any]:
    run_id = config.run_id or new_run_id("stage" if config.mock_minimax else "live")
    run_dir = ensure_run_dir(run_id)
    progress_path = run_dir / "progress.jsonl"

    baseline_eval = evaluate_repo(ROOT, config.eval_config)
    best_eval = dict(baseline_eval)
    write_json(run_dir / "baseline_eval.json", baseline_eval)
    snapshot_best_bot(run_dir)

    client = MiniMaxClient.from_environment(mock=config.mock_minimax)
    agent = ChessAgent(client, max_rounds=config.agent_max_rounds) if config.use_tool_calling else None
    run_mode = "mock" if config.mock_minimax else "live"
    history: list[dict[str, Any]] = []
    best_values = [float(best_eval.get("estimated_elo", 0.0))]

    append_jsonl(
        progress_path,
        {
            "event": "baseline",
            "iteration": 0,
            "best_elo": best_eval.get("estimated_elo"),
            "candidate_elo": best_eval.get("estimated_elo"),
            "decision": "baseline",
            "label": "estimated Elo",
            "mode": run_mode,
        },
    )

    for iteration in range(1, config.iterations + 1):
        iteration_dir = run_dir / "iterations" / f"{iteration:03d}"
        prompt = build_prompt(root=ROOT, baseline_eval=baseline_eval, best_eval=best_eval, history=history)
        write_text(iteration_dir / "prompt.md", prompt)
        before_hashes = hash_forbidden_files(ROOT)
        decision: dict[str, Any] = {
            "iteration": iteration,
            "accepted": False,
            "reasons": [],
        }
        try:
            if agent is not None:
                result = agent.run_iteration(
                    root=ROOT,
                    baseline_eval=baseline_eval,
                    best_eval=best_eval,
                    history=history,
                )
                patch_text = result.final_patch
                meta = {
                    "provider": "tool-calling-agent",
                    "model": client.settings.model,
                    "stop_reason": result.stop_reason,
                    "rounds": len(result.trace.rounds),
                    "max_rounds": result.meta.get("max_rounds"),
                }
                for round_event in result.trace.rounds:
                    append_jsonl(iteration_dir / "agent_trace.jsonl", round_event)
                decision["stop_reason"] = result.stop_reason
                decision["agent_rounds"] = len(result.trace.rounds)
            else:
                patch_text, meta = client.propose_patch(prompt)
            write_json(iteration_dir / "response_meta.json", meta)
            write_text(iteration_dir / "response.md", client.redactor.redact(patch_text))
            write_text(iteration_dir / "patch.diff", client.redactor.redact(patch_text))

            patch_guard = validate_patch_text(patch_text)
            if not patch_guard.ok:
                decision["reasons"].extend(patch_guard.reasons)
                candidate_eval = {"ok": False, "estimated_elo": 0.0, "errors": patch_guard.reasons}
            else:
                patch_result = apply_unified_patch(ROOT, patch_text)
                if not patch_result.ok or patch_result.candidate_root is None:
                    decision["reasons"].append(f"patch_failed:{patch_result.error}")
                    candidate_eval = {"ok": False, "estimated_elo": 0.0, "errors": [patch_result.error]}
                else:
                    tree_guard = validate_candidate_tree(patch_result.candidate_root, before_hashes)
                    if not tree_guard.ok:
                        decision["reasons"].extend(tree_guard.reasons)
                        candidate_eval = {"ok": False, "estimated_elo": 0.0, "errors": tree_guard.reasons}
                    else:
                        candidate_eval = evaluate_repo_subprocess(
                            patch_result.candidate_root,
                            config.eval_config,
                            timeout_seconds=90,
                        )
                        improvement = float(candidate_eval.get("estimated_elo", 0.0)) - float(best_eval.get("estimated_elo", 0.0))
                        decision["improvement"] = round(improvement, 1)
                        if candidate_eval.get("ok") and improvement >= config.accept_threshold_elo:
                            copy_editable_files(patch_result.candidate_root, ROOT, patch_guard.changed_files)
                            best_eval = dict(candidate_eval)
                            snapshot_best_bot(run_dir)
                            decision["accepted"] = True
                        else:
                            decision["reasons"].append("estimated_elo_did_not_improve_enough")
                    shutil.rmtree(patch_result.candidate_root.parent, ignore_errors=True)
        except Exception as exc:
            candidate_eval = {"ok": False, "estimated_elo": 0.0, "errors": [client.redactor.redact(str(exc))]}
            decision["reasons"].append(client.redactor.redact(str(exc)))

        write_json(iteration_dir / "eval.json", candidate_eval)
        write_json(iteration_dir / "decision.json", decision)
        history.append(
            {
                "iteration": iteration,
                "accepted": decision["accepted"],
                "candidate_elo": candidate_eval.get("estimated_elo"),
                "best_elo": best_eval.get("estimated_elo"),
                "reasons": decision["reasons"],
            }
        )
        best_values.append(float(best_eval.get("estimated_elo", 0.0)))
        append_jsonl(
            progress_path,
            {
                "event": "iteration",
                "iteration": iteration,
                "accepted": decision["accepted"],
                "best_elo": best_eval.get("estimated_elo"),
                "candidate_elo": candidate_eval.get("estimated_elo"),
                "decision": "accepted" if decision["accepted"] else "rejected",
                "reasons": decision["reasons"],
                "label": "estimated Elo",
                "mode": run_mode,
            },
        )
        write_progress_png(run_dir / "progress.png", best_values)
        print(
            f"iter={iteration} candidate={candidate_eval.get('estimated_elo')} "
            f"best={best_eval.get('estimated_elo')} decision={'accepted' if decision['accepted'] else 'rejected'}"
        )

    summary = {
        "run_id": run_id,
        "best_eval": best_eval,
        "baseline_eval": baseline_eval,
        "accepted": sum(1 for item in history if item["accepted"]),
        "rejected": sum(1 for item in history if not item["accepted"]),
        "run_dir": str(run_dir),
        "label": "estimated Elo",
        "mode": run_mode,
    }
    write_json(run_dir / "summary.json", summary)
    return summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run MiniMax AutoResearch chess loop.")
    parser.add_argument("--iterations", type=int, default=None)
    parser.add_argument("--stage", action="store_true")
    parser.add_argument("--mock-minimax", action="store_true")
    parser.add_argument("--accept-threshold-elo", type=float, default=None)
    parser.add_argument(
        "--no-tool-calling",
        action="store_true",
        help="Disable the OpenClaw-style tool-calling agent and use the legacy single-shot prompt.",
    )
    args = parser.parse_args(argv)

    use_tool_calling = not args.no_tool_calling

    if args.stage:
        config = STAGE_LOOP_CONFIG
        mock = args.mock_minimax or os.environ.get("AUTORESEARCH_MOCK_MINIMAX") == "1"
        if not mock and not MiniMaxClient.from_environment(mock=False).settings.keys:
            mock = True
        config = LoopConfig(
            iterations=args.iterations or config.iterations,
            accept_threshold_elo=args.accept_threshold_elo if args.accept_threshold_elo is not None else config.accept_threshold_elo,
            mock_minimax=mock,
            eval_config=config.eval_config,
            use_tool_calling=use_tool_calling,
        )
    else:
        config = LoopConfig(
            iterations=args.iterations or 5,
            accept_threshold_elo=args.accept_threshold_elo if args.accept_threshold_elo is not None else 15.0,
            mock_minimax=args.mock_minimax or os.environ.get("AUTORESEARCH_MOCK_MINIMAX") == "1",
            use_tool_calling=use_tool_calling,
        )
    summary = run_loop(config)
    print(f"summary: best estimated Elo={summary['best_eval'].get('estimated_elo')} run_dir={summary['run_dir']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
