from __future__ import annotations

from typing import Any

from .utils import clamp, tokenize


def validate_output(output: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if not isinstance(output.get("answer"), str) or not output["answer"].strip():
        errors.append("answer must be a non-empty string")
    citations = output.get("citations")
    if not isinstance(citations, list) or any(not isinstance(item, str) for item in citations):
        errors.append("citations must be a list of strings")
    notes = output.get("notes")
    if notes is not None and not isinstance(notes, (str, dict, list)):
        errors.append("notes must be string, object, array, or null")
    return errors


def _matches_group(answer_text: str, group: list[str]) -> bool:
    tokens = set(tokenize(answer_text))
    for phrase in group:
        phrase_tokens = set(tokenize(phrase))
        if phrase_tokens and phrase_tokens.issubset(tokens):
            return True
    return False


def _score_correctness(answer_text: str, hidden: dict[str, Any]) -> tuple[float, dict[str, Any]]:
    matched_facets: list[str] = []
    required_facets = hidden["required_facets"]
    for facet in required_facets:
        groups = facet["match_any"]
        if any(_matches_group(answer_text, group) for group in groups):
            matched_facets.append(facet["facet_id"])
    contradictions = []
    for contradiction in hidden.get("forbidden_claims", []):
        if any(_matches_group(answer_text, group) for group in contradiction["match_any"]):
            contradictions.append(contradiction["claim_id"])
    base = len(matched_facets) / max(len(required_facets), 1)
    penalty = 0.25 * len(contradictions)
    return clamp(base - penalty, 0.0, 1.0), {
        "matched_facets": matched_facets,
        "contradictions": contradictions,
    }


def _score_citations(citations: list[str], hidden: dict[str, Any], corpus_chunk_ids: set[str]) -> tuple[float, dict[str, Any]]:
    if not citations:
        return 0.0, {"valid_citations": [], "missing_citations": True}
    valid_ids = set(hidden["valid_citation_chunk_ids"])
    valid = [chunk_id for chunk_id in citations if chunk_id in corpus_chunk_ids and chunk_id in valid_ids]
    return len(valid) / len(citations), {
        "valid_citations": valid,
        "missing_citations": False,
    }


def _score_coverage(citations: list[str], hidden: dict[str, Any]) -> tuple[float, dict[str, Any]]:
    groups_hit = []
    citation_set = set(citations)
    for group in hidden["evidence_groups"]:
        if citation_set & set(group["chunk_ids"]):
            groups_hit.append(group["group_id"])
    return len(groups_hit) / max(len(hidden["evidence_groups"]), 1), {
        "groups_hit": groups_hit,
    }


def score_task(
    *,
    output: dict[str, Any] | None,
    hidden: dict[str, Any],
    corpus_chunk_ids: set[str],
    elapsed_seconds: float,
    metrics: dict[str, Any],
    budget: dict[str, Any],
    execution_error: str | None,
    timed_out: bool,
) -> dict[str, Any]:
    if timed_out:
        return {
            "task_score": 0.0,
            "status": "timeout",
            "error": execution_error or "task timed out",
            "components": {},
            "penalties": ["timeout"],
            "metrics": metrics,
        }

    if execution_error:
        return {
            "task_score": 0.0,
            "status": "execution_error",
            "error": execution_error,
            "components": {},
            "penalties": ["execution_error"],
            "metrics": metrics,
        }

    if output is None:
        return {
            "task_score": 0.0,
            "status": "missing_output",
            "error": "submission returned no output",
            "components": {},
            "penalties": ["missing_output"],
            "metrics": metrics,
        }

    validation_errors = validate_output(output)
    if validation_errors:
        return {
            "task_score": 0.0,
            "status": "invalid_output",
            "error": "; ".join(validation_errors),
            "components": {},
            "penalties": ["invalid_json_like_output"],
            "metrics": metrics,
        }

    answer_text = output["answer"]
    citations = list(output.get("citations") or [])
    correctness, correctness_meta = _score_correctness(answer_text, hidden)
    citation_validity, citation_meta = _score_citations(citations, hidden, corpus_chunk_ids)
    evidence_coverage, coverage_meta = _score_coverage(citations, hidden)
    score = (
        0.5 * correctness
        + 0.3 * citation_validity
        + 0.2 * evidence_coverage
    )
    penalties: list[str] = []
    if elapsed_seconds > float(budget["max_time_seconds"]):
        return {
            "task_score": 0.0,
            "status": "timeout",
            "error": f"elapsed {elapsed_seconds:.3f}s exceeded {budget['max_time_seconds']}s",
            "components": {},
            "penalties": ["timeout"],
            "metrics": metrics,
        }

    if not citations:
        penalties.append("missing_citations")
        score = 0.0
    elif metrics.get("violations"):
        penalties.append("budget_violation")
        score *= 0.25

    return {
        "task_score": round(clamp(score, 0.0, 1.0), 6),
        "status": "scored",
        "error": None,
        "components": {
            "correctness": round(correctness, 6),
            "citation_validity": round(citation_validity, 6),
            "evidence_coverage": round(evidence_coverage, 6),
            "correctness_meta": correctness_meta,
            "citation_meta": citation_meta,
            "coverage_meta": coverage_meta,
        },
        "penalties": penalties,
        "metrics": metrics,
    }
