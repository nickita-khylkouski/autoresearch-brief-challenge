from __future__ import annotations

from collections import defaultdict
from pathlib import Path
import sys

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from challenge.repository import ROOT
from challenge.utils import tokenize, write_json


PACK_ID = "frozen_autoresearch_v1"


SOURCE_DEFS = [
    {
        "source_id": "src_001",
        "title": "Hybrid Retrieval Under Tight Tool Budgets",
        "year": 2024,
        "source_type": "study",
        "snippets": [
            ("overview", "The study evaluated frozen local corpora where every answer had to be produced within ten tool calls and a laptop-friendly latency budget."),
            ("setup", "Researchers compared lexical retrieval, dense retrieval, and a merged hybrid stage over the same 132 chunk corpus pack."),
            ("finding", "Hybrid lexical plus dense retrieval raised answer recall by 14 points over lexical-only search on multi-hop questions."),
            ("finding", "Precision recovered only when a reranker cut the merged candidate pool from 24 chunks down to 6 chunks before synthesis."),
            ("failure", "Dense-only retrieval regularly missed exact method names and section labels that were easy for lexical search to recover."),
            ("recommendation", "The paper recommends keeping lexical search in the first stage, merging a small dense pool, and reranking before drafting."),
        ],
    },
    {
        "source_id": "src_002",
        "title": "Query Decomposition For Comparison Tasks",
        "year": 2025,
        "source_type": "study",
        "snippets": [
            ("overview", "This benchmark focused on comparison questions that required method evidence, tradeoffs, and limitations from separate sources."),
            ("setup", "A decomposition planner generated subqueries for method, evidence, limitation, and constraint handling before retrieval."),
            ("finding", "Decomposing comparison prompts raised evidence coverage from 0.41 to 0.73 because the system stopped collapsing every need into one search string."),
            ("finding", "The extra subqueries only paid off when the stop rule terminated after marginal gains flattened across the evidence groups."),
            ("failure", "Naive decomposition without a stop rule wasted tool calls and repeated near-duplicate chunks."),
            ("recommendation", "Use targeted subqueries for evidence groups, then stop once method, limitation, and comparison evidence are all covered."),
        ],
    },
    {
        "source_id": "src_003",
        "title": "Memory Compression Beats Full Transcript Carryover",
        "year": 2025,
        "source_type": "report",
        "snippets": [
            ("overview", "A long-horizon autoresearch run compared carrying the full transcript against writing structured memory after each round."),
            ("setup", "The structured memory template stored tried queries, failed evidence paths, useful source ids, and open gaps for the next round."),
            ("finding", "Compressed memory preserved answer quality while cutting prompt footprint by 38 percent relative to transcript carryover."),
            ("finding", "Runs with explicit anti-pattern notes avoided repeating dead-end queries in later rounds."),
            ("failure", "Transcript carryover caused later rounds to anchor on stale failed hypotheses and to over-repeat earlier wording."),
            ("recommendation", "Keep a compact memory that records winning evidence, failed branches, and unresolved gaps instead of replaying the whole session."),
        ],
    },
    {
        "source_id": "src_004",
        "title": "Marginal Gain Stop Rules For Research Loops",
        "year": 2024,
        "source_type": "study",
        "snippets": [
            ("overview", "This evaluation measured how different stop rules behaved when retrieval and synthesis were bounded by visible budgets."),
            ("setup", "The strongest variant tracked whether each new tool call added a new evidence group or a previously unseen supporting chunk."),
            ("finding", "A marginal gain stop rule improved average score because it halted once new searches stopped expanding evidence coverage."),
            ("finding", "Simple fixed-depth loops either stopped too early on hard tasks or burned budget on repetitive searches."),
            ("failure", "Counting raw search hits as progress created false confidence even when the hits repeated the same claim."),
            ("recommendation", "Stop when new calls stop adding evidence groups, new source diversity, or novel support chunks."),
        ],
    },
    {
        "source_id": "src_005",
        "title": "Strict Citation Checks For Frozen Corpus Benchmarks",
        "year": 2025,
        "source_type": "spec",
        "snippets": [
            ("overview", "The spec defines citation validity for a benchmark where every cited chunk must exist and support the relevant claim."),
            ("setup", "Valid citations were measured against known support chunk sets rather than against an open-ended semantic verifier."),
            ("finding", "Strict overlap with predeclared support chunks made scoring faster and more reproducible than freeform citation judging."),
            ("finding", "The benchmark only needed the judge model for synthesis nuance after rule-based citation checks had already run."),
            ("failure", "Loose citation grading let polished answers cite nearby but unsupported chunks and still earn inflated scores."),
            ("recommendation", "Use fixed support chunk sets for citation validity and reserve model judges for narrow synthesis disputes."),
        ],
    },
    {
        "source_id": "src_006",
        "title": "Facet-First Evaluation Beats Judge-Only Scoring",
        "year": 2025,
        "source_type": "study",
        "snippets": [
            ("overview", "Researchers compared pure LLM judging against a hybrid scorer with hidden answer facets, contradictions, and evidence groups."),
            ("setup", "Both systems scored the same research briefs, but only the hybrid scorer had access to hidden facet checklists and forbidden claims."),
            ("finding", "Facet-first scoring reduced variance and produced more defensible decisions on short evidence-backed briefs."),
            ("finding", "Judge-only scoring drifted on borderline paraphrases and often rewarded style over factual coverage."),
            ("failure", "Without hidden contradictions, the judge occasionally passed answers that blended correct facts with subtle but important errors."),
            ("recommendation", "Make hidden facets and contradiction checks primary, then use a fixed judge only as a narrow synthesis layer."),
        ],
    },
    {
        "source_id": "src_007",
        "title": "Contradiction Handling Through Evidence Buckets",
        "year": 2024,
        "source_type": "report",
        "snippets": [
            ("overview", "This report analyzed what happens when the corpus includes both supporting and limiting evidence for the same claim."),
            ("setup", "The system logged supportive evidence, limiting evidence, and unresolved conflicts in separate evidence buckets."),
            ("finding", "Answers were more trustworthy when the final brief named the strongest support and the main limitation instead of forcing a single-sided conclusion."),
            ("finding", "Contradiction buckets helped the system avoid citing a limitation chunk as if it were supportive evidence."),
            ("failure", "Naive majority voting collapsed nuance and erased important caveats from minority but credible sources."),
            ("recommendation", "Track support and limitation evidence separately, then surface both when claims remain contested."),
        ],
    },
    {
        "source_id": "src_008",
        "title": "Chunk Granularity And Citation Reliability",
        "year": 2025,
        "source_type": "study",
        "snippets": [
            ("overview", "The study tested whether smaller or larger chunks worked better for brief generation and citation checks."),
            ("setup", "Chunk sizes ranged from single paragraphs up to multi-section windows with overlapping stride."),
            ("finding", "Mid-sized chunks preserved enough local context for citation checks without burying support under unrelated text."),
            ("finding", "Very large chunks improved recall but weakened citation precision because support and caveats were mixed together."),
            ("failure", "Single-sentence chunks fragmented methodology descriptions and forced too many retrieval calls."),
            ("recommendation", "Use paragraph-scale chunks with stable section metadata when citation validity matters."),
        ],
    },
    {
        "source_id": "src_009",
        "title": "Source Diversity As A Coverage Signal",
        "year": 2024,
        "source_type": "study",
        "snippets": [
            ("overview", "This analysis asked whether better briefs cited more chunks or simply more diverse sources."),
            ("setup", "Coverage was decomposed into source diversity, evidence type diversity, and repeated support from the same source."),
            ("finding", "Source diversity predicted robust answers better than raw chunk count because multiple sources reduced single-document overfitting."),
            ("finding", "The best systems usually cited at least one method source and one limitation or tradeoff source."),
            ("failure", "Repeatedly citing the same source looked thorough but left important failure evidence undiscovered."),
            ("recommendation", "Track source diversity explicitly and prefer citations that span method, result, and limitation evidence."),
        ],
    },
    {
        "source_id": "src_010",
        "title": "Critique Loops Beat Blind Retries",
        "year": 2025,
        "source_type": "study",
        "snippets": [
            ("overview", "The benchmark compared blind retry loops against a critique step that diagnosed why the previous brief missed evidence."),
            ("setup", "After each draft, the critique step asked which facet was missing, which citation was weak, and what retrieval gap remained."),
            ("finding", "Critique-guided retries improved final score because each new round targeted a missing facet or unsupported claim."),
            ("finding", "Blind retries consumed comparable tokens but mostly paraphrased the same weak evidence."),
            ("failure", "Retry policies without explicit failure diagnosis repeated the first retrieval query and citation set."),
            ("recommendation", "Use critique to name the missing facet or weak citation before starting another retrieval round."),
        ],
    },
    {
        "source_id": "src_011",
        "title": "Budget-Aware Query Expansion",
        "year": 2024,
        "source_type": "study",
        "snippets": [
            ("overview", "This study examined when query expansion helps or hurts in a benchmark with hard call and token budgets."),
            ("setup", "The strongest strategy expanded only one or two key terms with synonyms tied to task type and then reranked aggressively."),
            ("finding", "Limited query expansion improved recall on methodology and comparison tasks without breaking the budget."),
            ("finding", "Unbounded synonym expansion inflated candidate pools and pushed the system into budget penalties."),
            ("failure", "Expansion on every noun phrase created many near-duplicate results and left no room for verification calls."),
            ("recommendation", "Expand only the high-value terms, keep the pool small, and preserve budget for reranking and verification."),
        ],
    },
    {
        "source_id": "src_012",
        "title": "Evidence-Type Tags Help Rerankers",
        "year": 2025,
        "source_type": "study",
        "snippets": [
            ("overview", "A reranking ablation tested whether chunk metadata about evidence type improved brief quality."),
            ("setup", "Chunks carried section tags such as method, result, limitation, and recommendation during reranking."),
            ("finding", "Evidence-type tags helped the reranker surface one result chunk and one limitation chunk for balanced answers."),
            ("finding", "Metadata-aware reranking outperformed text-only ranking on tasks that required tradeoff discussion."),
            ("failure", "Text-only reranking over-selected result sections and skipped the limitation evidence needed for strong coverage."),
            ("recommendation", "Keep section and evidence-type metadata in the index and let reranking use it explicitly."),
        ],
    },
    {
        "source_id": "src_013",
        "title": "Logging Failure Modes For Faster Iteration",
        "year": 2024,
        "source_type": "report",
        "snippets": [
            ("overview", "This report focused on which run artifacts actually helped teams improve their scaffold between evaluations."),
            ("setup", "Runs emitted raw outputs, per-task score breakdowns, query traces, and explicit failure labels."),
            ("finding", "Teams improved faster when they could see whether a miss came from retrieval, citation validity, or synthesis coverage."),
            ("finding", "Per-task score breakdowns made it obvious whether the next change should target evidence coverage or unsupported claims."),
            ("failure", "Single scalar scores without artifacts encouraged random tweaking because users could not see why a run failed."),
            ("recommendation", "Store raw outputs and component scores for every task so contestants can debug specific failure modes."),
        ],
    },
    {
        "source_id": "src_014",
        "title": "Constraint-Aware Selection Beats Max-Accuracy Drafting",
        "year": 2025,
        "source_type": "study",
        "snippets": [
            ("overview", "A controlled benchmark asked systems to choose the best method under explicit latency, cost, or evidence constraints."),
            ("setup", "Methods with the highest unconstrained accuracy were not always optimal once runtime and tool limits were applied."),
            ("finding", "Constraint-aware selection worked best when the answer explicitly named the winning method and the reason it fit the constraint."),
            ("finding", "High-accuracy but slow methods often lost under strict wall-clock or tool-call caps."),
            ("failure", "Drafts that ignored the stated constraint were judged wrong even when their unconstrained recommendation sounded strong."),
            ("recommendation", "For selection tasks, align the answer to the named constraint before optimizing for absolute accuracy."),
        ],
    },
    {
        "source_id": "src_015",
        "title": "Evidence Groups Make Multi-Hop Tasks Defensible",
        "year": 2025,
        "source_type": "spec",
        "snippets": [
            ("overview", "The evaluation design grouped hidden evidence into method, support, limitation, and recommendation buckets."),
            ("setup", "A task only earned full coverage when its citations spanned all required evidence groups."),
            ("finding", "Evidence groups stopped shallow systems from winning with one strong quote that ignored the rest of the verification path."),
            ("finding", "Group-aware scoring especially improved multi-hop comparison tasks where method and limitation evidence lived in different chunks."),
            ("failure", "Without evidence groups, answers with narrow but eloquent support scored too well."),
            ("recommendation", "Define hidden evidence groups per task and require coverage across them, not just one valid citation."),
        ],
    },
    {
        "source_id": "src_016",
        "title": "Metadata-First Retrieval For Frozen Corpora",
        "year": 2024,
        "source_type": "study",
        "snippets": [
            ("overview", "This retrieval study emphasized that titles, sections, and source metadata often carry the exact discriminators a benchmark needs."),
            ("setup", "The system indexed source title tokens, section labels, and year metadata alongside chunk text."),
            ("finding", "Metadata-first retrieval rescued tasks that asked for methodology or limitation evidence because those cues were often in headers."),
            ("finding", "Plain text search missed important chunks when the body used pronouns but the header named the relevant method directly."),
            ("failure", "Ignoring metadata made many retrieval misses look mysterious even though the answer cue was sitting in the title field."),
            ("recommendation", "Index titles and sections as first-class search features rather than treating metadata as decoration."),
        ],
    },
    {
        "source_id": "src_017",
        "title": "Short Notes Help Verification Calls",
        "year": 2024,
        "source_type": "report",
        "snippets": [
            ("overview", "A note-taking ablation asked whether lightweight note tools help under small budgets."),
            ("setup", "The tool only allowed concise notes that recorded which claim a chunk supported and which gap still remained."),
            ("finding", "Short notes improved verification because the system could remember why a citation was chosen without rereading every chunk."),
            ("finding", "The gain was strongest when notes were claim-linked instead of generic summaries."),
            ("failure", "Verbose note dumps consumed tokens and duplicated chunk text instead of sharpening the next action."),
            ("recommendation", "Use notes sparingly to link claims, citations, and remaining gaps rather than to restate the corpus."),
        ],
    },
    {
        "source_id": "src_018",
        "title": "Concise Synthesis Outperforms Long Reasoning Dumps",
        "year": 2025,
        "source_type": "study",
        "snippets": [
            ("overview", "The benchmark compared short evidence-backed briefs against long reasoning traces for the same tasks."),
            ("setup", "Both variants had access to the same retrieval stack, but one had to answer in a compact structured brief."),
            ("finding", "Concise briefs scored better because they were easier to validate against hidden facets and citation rules."),
            ("finding", "Long reasoning dumps increased the chance of unsupported side claims and contradiction penalties."),
            ("failure", "Verbose answers often wandered beyond the retrieved evidence and mixed speculation with supported findings."),
            ("recommendation", "Require short structured briefs with citations, and avoid long chain-of-thought style outputs."),
        ],
    },
]


def _build_chunks():
    chunks = []
    sources = []
    postings = defaultdict(list)
    for source in SOURCE_DEFS:
        sources.append(
            {
                "source_id": source["source_id"],
                "title": source["title"],
                "year": source["year"],
                "source_type": source["source_type"],
            }
        )
        for position, (section, text) in enumerate(source["snippets"], start=1):
            chunk_id = f"{source['source_id']}_c{position:02d}"
            chunk = {
                "chunk_id": chunk_id,
                "source_id": source["source_id"],
                "title": source["title"],
                "text": text,
                "position": position,
                "section": section,
                "year": source["year"],
                "source_type": source["source_type"],
            }
            chunks.append(chunk)
            for token in sorted(set(tokenize(f"{source['title']} {section} {text}"))):
                postings[token].append(chunk_id)
    index = {"postings": {token: sorted(chunk_ids) for token, chunk_ids in sorted(postings.items())}}
    return sources, chunks, index


BASE_BUDGET = {
    "max_time_seconds": 15,
    "max_tool_calls": 10,
    "max_search_results": 8,
    "max_tokens": 2200,
    "max_citations": 4,
}


SPEC_BANK = {
    "hybrid_retrieval": {
        "task_type": "constraint_selection",
        "facets": [
            ("hybrid_stage", [["hybrid lexical dense"], ["lexical plus dense"], ["merged dense lexical"]]),
            ("rerank_small_pool", [["reranker cut candidate pool"], ["reranking before drafting"], ["small dense pool"]]),
            ("latency_cap", [["tool budget"], ["small candidate pool"], ["latency budget"]]),
        ],
        "valid_citations": ["src_001_c03", "src_001_c04", "src_001_c06", "src_011_c03", "src_011_c06"],
        "evidence_groups": {
            "method": ["src_001_c03", "src_001_c06"],
            "budget": ["src_011_c03", "src_011_c06"],
            "tradeoff": ["src_001_c04", "src_011_c04"],
        },
    },
    "comparison_decomposition": {
        "task_type": "comparison",
        "facets": [
            ("decompose", [["decomposing comparison prompts"], ["targeted subqueries"], ["subqueries for method evidence limitation"]]),
            ("stop_rule", [["marginal gain stop rule"], ["stop once evidence groups are covered"], ["diminishing returns"]]),
            ("limitation_balance", [["limitation evidence"], ["tradeoff source"], ["balanced answer"]]),
        ],
        "valid_citations": ["src_002_c03", "src_002_c04", "src_002_c06", "src_012_c03", "src_015_c04"],
        "evidence_groups": {
            "decomposition": ["src_002_c03", "src_002_c06"],
            "stopping": ["src_002_c04", "src_004_c06"],
            "limitation": ["src_012_c03", "src_015_c04"],
        },
    },
    "memory_compression": {
        "task_type": "methodology",
        "facets": [
            ("compressed_memory", [["compressed memory"], ["structured memory"], ["compact memory"]]),
            ("record_failures", [["failed branches"], ["failed evidence paths"], ["anti-pattern notes"]]),
            ("avoid_transcript", [["whole transcript"], ["transcript carryover"], ["instead of replaying the whole session"]]),
        ],
        "valid_citations": ["src_003_c03", "src_003_c04", "src_003_c06", "src_017_c03", "src_017_c06"],
        "evidence_groups": {
            "policy": ["src_003_c03", "src_003_c06"],
            "failure_memory": ["src_003_c04", "src_017_c03"],
            "notes": ["src_017_c03", "src_017_c06"],
        },
    },
    "facet_first_eval": {
        "task_type": "verification",
        "facets": [
            ("hidden_facets", [["hidden answer facets"], ["facet first scoring"], ["facet checklist"]]),
            ("contradictions", [["forbidden claims"], ["hidden contradictions"], ["contradiction checks"]]),
            ("narrow_judge", [["judge only for synthesis"], ["narrow synthesis layer"], ["reserve model judges"]]),
        ],
        "valid_citations": ["src_005_c03", "src_005_c06", "src_006_c03", "src_006_c05", "src_006_c06"],
        "evidence_groups": {
            "rule_checks": ["src_005_c03", "src_005_c06"],
            "facets": ["src_006_c03", "src_006_c06"],
            "contradictions": ["src_006_c05"],
        },
    },
    "stop_rule": {
        "task_type": "constraint_selection",
        "facets": [
            ("marginal_gain", [["marginal gain stop rule"], ["new calls stop adding evidence groups"], ["halt once new searches stop expanding evidence coverage"]]),
            ("avoid_fixed_depth", [["fixed depth loops"], ["stopped too early"], ["burned budget"]]),
            ("track_novelty", [["new evidence groups"], ["novel support chunks"], ["source diversity"]]),
        ],
        "valid_citations": ["src_004_c03", "src_004_c04", "src_004_c06", "src_009_c03"],
        "evidence_groups": {
            "core_rule": ["src_004_c03", "src_004_c06"],
            "failure_mode": ["src_004_c04"],
            "novelty_signal": ["src_009_c03"],
        },
    },
    "evidence_groups": {
        "task_type": "verification",
        "facets": [
            ("multi_group", [["evidence groups"], ["span all required evidence groups"], ["method support limitation"]]),
            ("prevent_shallow_wins", [["one strong quote"], ["shallow systems"], ["narrow but eloquent support"]]),
            ("multi_hop", [["multi hop"], ["comparison tasks"], ["different chunks"]]),
        ],
        "valid_citations": ["src_015_c02", "src_015_c03", "src_015_c04", "src_015_c06", "src_009_c06"],
        "evidence_groups": {
            "definition": ["src_015_c02", "src_015_c06"],
            "benefit": ["src_015_c03"],
            "comparison_need": ["src_015_c04", "src_009_c06"],
        },
    },
    "contradiction_buckets": {
        "task_type": "comparison",
        "facets": [
            ("separate_buckets", [["support and limitation evidence separately"], ["evidence buckets"], ["supportive evidence limiting evidence"]]),
            ("surface_caveats", [["main limitation"], ["surface both"], ["caveats"]]),
            ("avoid_majority_vote", [["majority voting"], ["single sided conclusion"], ["erased important caveats"]]),
        ],
        "valid_citations": ["src_007_c02", "src_007_c03", "src_007_c04", "src_007_c06"],
        "evidence_groups": {
            "policy": ["src_007_c02", "src_007_c06"],
            "why": ["src_007_c03", "src_007_c04"],
            "risk": ["src_007_c05"],
        },
    },
    "concise_synthesis": {
        "task_type": "verification",
        "facets": [
            ("easy_to_validate", [["easier to validate"], ["hidden facets"], ["citation rules"]]),
            ("avoid_side_claims", [["unsupported side claims"], ["contradiction penalties"], ["mixed speculation"]]),
            ("short_structured", [["short structured briefs"], ["concise briefs"], ["avoid long chain of thought"]]),
        ],
        "valid_citations": ["src_018_c03", "src_018_c04", "src_018_c06", "src_005_c04"],
        "evidence_groups": {
            "validation": ["src_018_c03", "src_005_c04"],
            "risk": ["src_018_c04", "src_018_c05"],
            "format": ["src_018_c06"],
        },
    },
    "metadata_retrieval": {
        "task_type": "methodology",
        "facets": [
            ("titles_sections", [["titles and sections"], ["title tokens"], ["section labels"]]),
            ("metadata_search", [["metadata first retrieval"], ["first class search features"], ["index metadata"]]),
            ("why_headers", [["headers"], ["methodology or limitation evidence"], ["body used pronouns"]]),
        ],
        "valid_citations": ["src_016_c03", "src_016_c04", "src_016_c06", "src_012_c06"],
        "evidence_groups": {
            "features": ["src_016_c03", "src_016_c06"],
            "rationale": ["src_016_c04"],
            "reranking_use": ["src_012_c06"],
        },
    },
    "run_artifacts": {
        "task_type": "verification",
        "facets": [
            ("debug_failure_modes", [["retrieval citation validity or synthesis coverage"], ["failure modes"], ["why a run failed"]]),
            ("improve_faster", [["improved faster"], ["next change"], ["component scores"]]),
            ("avoid_random_tweaks", [["random tweaking"], ["single scalar scores"], ["could not see why"]]),
        ],
        "valid_citations": ["src_013_c03", "src_013_c04", "src_013_c05", "src_013_c06"],
        "evidence_groups": {
            "visibility": ["src_013_c03", "src_013_c04"],
            "risk": ["src_013_c05"],
            "recommendation": ["src_013_c06"],
        },
    },
    "rerank_evidence_types": {
        "task_type": "comparison",
        "facets": [
            ("metadata_aware", [["metadata aware reranking"], ["evidence type tags"], ["section and evidence type metadata"]]),
            ("result_and_limitation", [["one result chunk and one limitation chunk"], ["balanced answers"], ["tradeoff discussion"]]),
            ("avoid_text_only", [["text only reranking"], ["over selected result sections"], ["skipped limitation evidence"]]),
        ],
        "valid_citations": ["src_012_c03", "src_012_c04", "src_012_c05", "src_012_c06"],
        "evidence_groups": {
            "approach": ["src_012_c03", "src_012_c06"],
            "benefit": ["src_012_c04"],
            "failure": ["src_012_c05"],
        },
    },
    "query_expansion": {
        "task_type": "constraint_selection",
        "facets": [
            ("limited_expansion", [["limited query expansion"], ["one or two key terms"], ["expand only the high value terms"]]),
            ("preserve_budget", [["preserve budget for reranking and verification"], ["without breaking the budget"], ["keep the pool small"]]),
            ("avoid_unbounded", [["unbounded synonym expansion"], ["near duplicate results"], ["budget penalties"]]),
        ],
        "valid_citations": ["src_011_c02", "src_011_c03", "src_011_c04", "src_011_c06"],
        "evidence_groups": {
            "policy": ["src_011_c02", "src_011_c06"],
            "benefit": ["src_011_c03"],
            "risk": ["src_011_c04", "src_011_c05"],
        },
    },
    "critique_retries": {
        "task_type": "comparison",
        "facets": [
            ("diagnose_missing", [["missing facet"], ["weak citation"], ["retrieval gap"]]),
            ("target_next_round", [["targeted a missing facet"], ["before starting another retrieval round"], ["failure diagnosis"]]),
            ("blind_retry_problem", [["blind retries"], ["paraphrased the same weak evidence"], ["repeated the first retrieval query"]]),
        ],
        "valid_citations": ["src_010_c02", "src_010_c03", "src_010_c04", "src_010_c06"],
        "evidence_groups": {
            "diagnosis": ["src_010_c02", "src_010_c06"],
            "benefit": ["src_010_c03"],
            "failure": ["src_010_c04", "src_010_c05"],
        },
    },
    "chunk_granularity": {
        "task_type": "methodology",
        "facets": [
            ("paragraph_scale", [["paragraph scale chunks"], ["mid sized chunks"], ["local context"]]),
            ("precision_tradeoff", [["weakened citation precision"], ["mixed together"], ["very large chunks"]]),
            ("sentence_fragmentation", [["single sentence chunks"], ["fragmented methodology descriptions"], ["too many retrieval calls"]]),
        ],
        "valid_citations": ["src_008_c03", "src_008_c04", "src_008_c05", "src_008_c06"],
        "evidence_groups": {
            "recommended_size": ["src_008_c03", "src_008_c06"],
            "large_chunk_risk": ["src_008_c04"],
            "small_chunk_risk": ["src_008_c05"],
        },
    },
    "constraint_selection": {
        "task_type": "constraint_selection",
        "facets": [
            ("align_to_constraint", [["align the answer to the named constraint"], ["constraint aware selection"], ["fit the constraint"]]),
            ("not_absolute_accuracy", [["not always optimal"], ["highest unconstrained accuracy"], ["slow methods often lost"]]),
            ("state_reason", [["named the winning method and the reason"], ["reason it fit the constraint"], ["explicitly named the winning method"]]),
        ],
        "valid_citations": ["src_014_c03", "src_014_c04", "src_014_c06"],
        "evidence_groups": {
            "selection_rule": ["src_014_c03", "src_014_c06"],
            "tradeoff": ["src_014_c04"],
            "failure": ["src_014_c05"],
        },
    },
    "lightweight_notes": {
        "task_type": "methodology",
        "facets": [
            ("claim_linked_notes", [["claim linked"], ["which claim a chunk supported"], ["remaining gap"]]),
            ("help_verification", [["improved verification"], ["without rereading every chunk"], ["remember why a citation was chosen"]]),
            ("avoid_verbose", [["verbose note dumps"], ["duplicated chunk text"], ["use notes sparingly"]]),
        ],
        "valid_citations": ["src_017_c02", "src_017_c03", "src_017_c04", "src_017_c06"],
        "evidence_groups": {
            "how_to_note": ["src_017_c02", "src_017_c06"],
            "benefit": ["src_017_c03", "src_017_c04"],
            "risk": ["src_017_c05"],
        },
    },
    "source_diversity": {
        "task_type": "methodology",
        "facets": [
            ("source_diversity", [["source diversity"], ["diverse sources"], ["multiple sources"]]),
            ("method_limitation_mix", [["method source and one limitation"], ["method and limitation source"], ["method result and limitation evidence"]]),
            ("not_raw_chunk_count", [["better than raw chunk count"], ["raw chunk count"], ["same source looked thorough"]]),
        ],
        "valid_citations": ["src_009_c03", "src_009_c04", "src_009_c05", "src_009_c06"],
        "evidence_groups": {
            "signal": ["src_009_c03", "src_009_c06"],
            "mix": ["src_009_c04"],
            "risk": ["src_009_c05"],
        },
    },
    "strict_citation_checks": {
        "task_type": "verification",
        "facets": [
            ("support_sets", [["support chunk sets"], ["predeclared support chunks"], ["fixed support chunk sets"]]),
            ("fast_reproducible", [["faster and more reproducible"], ["strict overlap"], ["citation validity"]]),
            ("loose_grading_fails", [["loose citation grading"], ["unsupported chunks"], ["inflated scores"]]),
        ],
        "valid_citations": ["src_005_c02", "src_005_c03", "src_005_c05", "src_005_c06"],
        "evidence_groups": {
            "definition": ["src_005_c02", "src_005_c06"],
            "benefit": ["src_005_c03"],
            "failure": ["src_005_c05"],
        },
    },
    "judge_narrow_layer": {
        "task_type": "verification",
        "facets": [
            ("judge_after_rules", [["judge only for synthesis"], ["narrow synthesis layer"], ["after rule based citation checks"]]),
            ("facets_primary", [["hidden facets"], ["facets primary"], ["facet first"]]),
            ("contradictions_needed", [["hidden contradictions"], ["subtle but important errors"], ["contradiction checks"]]),
        ],
        "valid_citations": ["src_005_c04", "src_006_c03", "src_006_c05", "src_006_c06"],
        "evidence_groups": {
            "judge_role": ["src_005_c04", "src_006_c06"],
            "facets": ["src_006_c03"],
            "contradictions": ["src_006_c05"],
        },
    },
    "metadata_headers": {
        "task_type": "methodology",
        "facets": [
            ("headers_matter", [["header named the relevant method"], ["headers"], ["title field"]]),
            ("titles_and_sections", [["titles and sections"], ["title tokens"], ["section labels"]]),
            ("body_pronouns_fail", [["body used pronouns"], ["plain text search missed"], ["ignoring metadata"]]),
        ],
        "valid_citations": ["src_016_c03", "src_016_c04", "src_016_c05", "src_016_c06"],
        "evidence_groups": {
            "signal": ["src_016_c03", "src_016_c06"],
            "rationale": ["src_016_c04"],
            "failure": ["src_016_c05"],
        },
    },
}


def _variant(spec_key: str, question: str, *, task_type: str | None = None) -> dict:
    return {
        "spec_key": spec_key,
        "question": question,
        "task_type": task_type or SPEC_BANK[spec_key]["task_type"],
    }


SPLIT_VARIANTS = {
    "dev": [
        _variant("hybrid_retrieval", "Which retrieval stack is strongest for multi-hop frozen-corpus questions when the system only gets ten tool calls?"),
        _variant("comparison_decomposition", "How should a scaffold handle comparison questions so it covers both supporting evidence and limitations instead of answering from one search?"),
        _variant("memory_compression", "What memory policy is best for long autoresearch runs if the goal is to avoid repeated dead ends without carrying the whole transcript?"),
        _variant("facet_first_eval", "Why is a facet-first evaluator more defensible than judging the final brief with a model alone?"),
        _variant("stop_rule", "What stop rule best fits a benchmark with visible time and tool budgets?"),
        _variant("evidence_groups", "What is the strongest case for using evidence groups instead of rewarding any single valid citation?"),
        _variant("contradiction_buckets", "How should the system handle contradictory evidence when some chunks support a claim and others mainly add caveats?"),
        _variant("concise_synthesis", "Why are concise structured briefs usually better than long reasoning dumps in this kind of challenge?"),
        _variant("metadata_retrieval", "For a fixed local corpus, which retrieval features should be treated as first-class search signals instead of decorative metadata?"),
        _variant("run_artifacts", "What is the strongest argument for keeping run artifacts and per-task score breakdowns instead of only a final scalar?"),
        _variant("rerank_evidence_types", "What reranking behavior best supports balanced tradeoff answers rather than one-sided result summaries?"),
        _variant("query_expansion", "How should query expansion be used if the benchmark has hard call and token budgets?"),
        _variant("critique_retries", "What is the strongest case for critique-guided retries instead of simply asking the scaffold to try again?"),
        _variant("chunk_granularity", "Why does paragraph-scale chunking usually beat both single-sentence chunks and giant windows when citations are graded strictly?"),
        _variant("constraint_selection", "When a task asks for the best approach under a named constraint, what should the final brief optimize for?"),
        _variant("lightweight_notes", "How should lightweight notes be used without wasting the same budget they are meant to protect?"),
        _variant("source_diversity", "Why is source diversity a better coverage signal than simply citing more chunks from the same paper?"),
        _variant("strict_citation_checks", "Why should citation validity rely on fixed support chunk sets instead of looser semantic grading in v1?"),
        _variant("judge_narrow_layer", "What exactly should an LLM judge still do after rule-based facet and citation checks exist?"),
        _variant("metadata_headers", "Why do titles, section labels, and header cues matter so much for frozen-corpus retrieval quality?"),
    ],
}


PREFIX_BY_SPLIT = {
    "dev": "dev",
}


def _build_task_defs() -> dict[str, list[dict]]:
    task_defs: dict[str, list[dict]] = {}
    for split, variants in SPLIT_VARIANTS.items():
        built: list[dict] = []
        prefix = PREFIX_BY_SPLIT[split]
        for index, variant in enumerate(variants, start=1):
            spec = SPEC_BANK[variant["spec_key"]]
            built.append(
                {
                    "task_id": f"{prefix}_{index:03d}",
                    "question": variant["question"],
                    "task_type": variant["task_type"],
                    "facets": spec["facets"],
                    "valid_citations": spec["valid_citations"],
                    "evidence_groups": spec["evidence_groups"],
                }
            )
        task_defs[split] = built
    return task_defs


TASK_DEFS = _build_task_defs()


def _visible_task(defn: dict) -> dict:
    return {
        "task_id": defn["task_id"],
        "question": defn["question"],
        "corpus_pack_id": PACK_ID,
        "task_type": defn["task_type"],
        "budget": BASE_BUDGET,
        "expected_output_schema": "challenge/schemas/submission_output.schema.json",
    }


def _hidden_task(defn: dict) -> dict:
    return {
        "task_id": defn["task_id"],
        "required_facets": [
            {
                "facet_id": facet_id,
                "match_any": phrases,
            }
            for facet_id, phrases in defn["facets"]
        ],
        "forbidden_claims": [],
        "valid_citation_chunk_ids": defn["valid_citations"],
        "evidence_groups": [
            {"group_id": group_id, "chunk_ids": chunk_ids}
            for group_id, chunk_ids in defn["evidence_groups"].items()
        ],
    }


def _normalize_hidden_task(hidden: dict) -> dict:
    normalized = dict(hidden)
    required = []
    for facet in hidden["required_facets"]:
        required.append(
            {
                "facet_id": facet["facet_id"],
                "match_any": facet["match_any"],
            }
        )
    normalized["required_facets"] = required
    return normalized


def main() -> int:
    corpora_dir = ROOT / "corpora" / PACK_ID
    tasks_dir = ROOT / "tasks"
    private_dir = tasks_dir / "_private"
    corpora_dir.mkdir(parents=True, exist_ok=True)
    private_dir.mkdir(parents=True, exist_ok=True)

    sources, chunks, index = _build_chunks()
    write_json(corpora_dir / "sources.json", sources)
    write_json(corpora_dir / "chunks.json", chunks)
    write_json(corpora_dir / "index.json", index)

    for split, items in TASK_DEFS.items():
        visible = [_visible_task(item) for item in items]
        hidden = [_normalize_hidden_task(_hidden_task(item)) for item in items]
        write_json(tasks_dir / f"{split}.json", visible)
        write_json(private_dir / f"{split}_hidden.json", hidden)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
