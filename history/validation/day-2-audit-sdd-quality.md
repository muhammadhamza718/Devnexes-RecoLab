# Day 2 SDD Quality Audit — RecoLab (Week 1 Planning Docs)

**Audit Type:** Spec-Driven Development documentation audit (spec / plan / tasks / ADRs only — no Day 2 code yet exists)
**Date:** 2026-07-18
**Auditor:** Senior Code/Documentation Reviewer (SDD specialist)
**Scope files:**
- `specs/week-1/spec.md`, `specs/week-1/plan.md`, `specs/week-1/tasks.md`
- `history/adr/001-data-technology-stack-week-1.md`
- `history/adr/002-evaluation-methodology-week-1.md`
- `history/adr/003-model-persistence-and-testing-week-1.md`
- Cross-reference set: `specs/recolab/spec.md`, `specs/recolab/plan.md`, `specs/recolab/tasks.md`, `specs/recolab/architecture-reference.md`
- Prior context: `history/validation/day-1-ivp-report.md`
- Ground truth: `recolab-hybrid-recommender/pyproject.toml`

---

## Verdict

**NEEDS-FIX**

The Day 2 planning documents are structurally complete and internally coherent *within the `specs/week-1/` tree*, and they satisfy the narrow Week-1 scope. However, they carry three issues that will degrade downstream execution: (1) a confirmed Python-version drift between spec/ADR and the committed `pyproject.toml`; (2) a logical contradiction inside ADR-002 (NDCG@K listed as a Must-Have in spec/REQ-009 yet "deferred" in the ADR's negative outcomes); and (3) a structural risk from maintaining two parallel, partly conflicting SDD trees (`specs/recolab/` vs `specs/week-1/`) with no canonical cross-linking. None are blocking for writing code today, but they will cause acceptance-criteria disputes and divergence by Week 3. Fix before Day 2 implementation begins.

---

## Critical Findings

### CF-1 — Python 3.12+ in spec/plan/ADR contradicts `pyproject.toml` (`requires-python = ">=3.14"`)
**Severity:** Critical (spec/compliance drift)
**Evidence:**
- `specs/week-1/spec.md:41` — "**Python 3.12+** - Latest stable with performance improvements, f-string enhancements..."
- `specs/week-1/plan.md:36` — "Set up Python 3.12+ environment with virtual environment"
- `history/adr/001-data-technology-stack-week-1.md:13,16` — "Python 3.12+ with pandas (latest stable)..."
- `recolab-hybrid-recommender/pyproject.toml:6` — `requires-python = ">=3.14"`
- `recolab-hybrid-recommender/pyproject.toml:27` — `target-version = "py312"` (ruff)
- `recolab-hybrid-recommender/pyproject.toml:34` — `python_version = "3.12"` (mypy)

**Analysis:** The Day 1 IVP report explicitly recorded this as WF-4 and noted runtime is Python 3.14 (line 114), yet the planning docs and ADR-001 still state "3.12+". This is an unresolved finding, not a freshly introduced one. Worse, `pyproject.toml` itself is internally inconsistent: `requires-python` is `>=3.14` but both ruff `target-version` and mypy `python_version` still say `3.12`. A reviewer or CI runner on a 3.12 interpreter would (correctly) be rejected by `requires-python` while the spec tells them 3.12 is fine. There is no single source of truth on the interpreter version.

**Why it matters:** AC-005 (reproducibility) and the Week-6 fresh-clone rule depend on a declared, stable interpreter. Ambiguity here directly undermines Reproducibility acceptance.

**Recommended fix:** Pick one floor, document the rationale, and align all four locations. Given runtime is already 3.14.0 and that exceeds "latest stable," set the canonical floor to `>=3.14` and update `specs/week-1/spec.md:41`, `specs/week-1/plan.md:36`, ADR-001 lines 13/16, and `pyproject.toml:27,34` (set `py314`). If the team wishes to keep a 3.12 floor for portability, then `pyproject.toml:6` must be lowered to `>=3.12` instead. Do not leave them disagreeing.

---

### CF-2 — ADR-002 self-contradicts on NDCG@K (Must-Have vs "deferred")
**Severity:** Critical (ADR correctness / contradiction)
**Evidence:**
- `specs/week-1/spec.md:22` — Must-Have list includes "Implement evaluation metrics (P@K, R@K, NDCG@K)"
- `specs/week-1/spec.md:69-74` — REQ-009: "Implement NDCG@K (Normalized Discounted Cumulative Gain) for ranking quality" (not marked optional)
- `history/adr/002-evaluation-methodology-week-1.md:13` — Decision: "Complete Ranking Metrics: Precision@K, Recall@K, and NDCG@K as primary evaluation metrics"
- `history/adr/002-evaluation-methodology-week-1.md:46` — Negative Outcomes: "Time constraint limits comprehensive metric exploration (NDCG@K deferred)"
- `history/adr/002-evaluation-methodology-week-1.md:68` — Alternative 3: "NDCG@K essential per master spec, but additional metrics deferred due to timeline"

**Analysis:** Line 46 claims NDCG@K is *deferred*, but lines 13, 22, 69-74 (spec) and line 68 itself ("NDCG@K essential per master spec") treat it as mandatory. The deferral in line 46 actually refers to *additional* metrics (MAP, MRR) per line 68, but the wording at line 46 is unqualified and reads as "NDCG@K deferred." A reviewer using ADR-002 alone would conclude NDCG@K is out of scope, contradicting the spec Must-Have and REQ-009. This is a contradiction between two statements in the same ADR and between the ADR and its spec.

**Recommended fix:** Reword ADR-002 line 46 to: "Time constraint limits comprehensive metric exploration (**MAP, MRR deferred**; P@K/R@K/NDCG@K remain Must-Have per REQ-009)." Add an explicit "Deferred: MAP, MRR" note so it cannot be misread.

---

## Warnings

### W-1 — scikit-learn `top_k_accuracy_score` described as the implementation path but spec marks it "Consider"
**Evidence:** `history/adr/001-data-technology-stack-week-1.md:24` and `002-...md:20` state scikit-learn `top_k_accuracy_score` integration; `specs/week-1/spec.md:73` says "Consider `top_k_accuracy_score`" and `plan.md:54` lists the custom P@K/R@K/NDCG@K functions as the real deliverable.
**Issue:** The ADRs elevate `top_k_accuracy_score` to a chosen component, but the spec/plan actually implement custom metric functions and only *consider* the sklearn helper. ADR-002 line 51 even admits "Manual implementation required for custom ranking metrics." The ADRs overstate sklearn's role. Clarify that sklearn is a cross-check/reference, not the primary metric engine.

### W-2 — Duplicate SDD trees (`specs/recolab/` vs `specs/week-1/`) with no canonical link → divergence risk
**Evidence:** Two parallel sets exist:
- `specs/recolab/` = full 6-week master (FastAPI + Next.js, Python 3.9+, `src/`, `tests/`, API endpoints, REQ-001..013).
- `specs/week-1/` = 2-day time-optimized subset that **removes the backend entirely** and changes the stack.

Concrete divergences already present:
- **Python floor:** master `specs/recolab/spec.md:46` says "Python 3.9+"; `specs/week-1/spec.md:41` says "Python 3.12+".
- **Scope collapse:** master plan Week-1 (plan.md lines 22-53) includes "Verify hosting platform's persistent-disk behavior for model artifacts"; week-1 spec Out-of-Scope (spec.md:34) and tasks drop hosting verification entirely. The week-1 tree silently removes a master deliverable (persistent-disk verification) without noting it.
- **Task-ID namespace split:** master tasks use `REQ-008`, `GUD-001`, `COM-001`; week-1 tasks use `W1-D2-P3-T1` etc. and re-map REQ IDs. No document states which tree is authoritative when they disagree.

**Risk:** By Week 3, the master tree expects a FastAPI `backend/` with `tests/` ≥70% coverage and 3 baselines; the week-1 tree is building a notebook/prototype with no backend. The two will diverge, and acceptance (AC-001..005, REQ-010/013) becomes unverifiable against a single source.

**Recommended fix:** Declare `specs/recolab/` the single source of truth and treat `specs/week-1/` as a *derived, time-boxed execution slice* that explicitly references the master REQ/AC IDs and notes every divergence (e.g., "Scope reduction: hosting verification deferred from recolab/plan.md Week-1; Python floor raised to >=3.14; backend deferred to Week 5"). Add a one-line "Source of Truth" header to each week-1 doc pointing back to `specs/recolab/`. Do not keep two independently-edited spec sets.

### W-3 — Day 2 test tasks lack concrete assertions / acceptance values
**Evidence:**
- `specs/week-1/tasks.md:79-84` (P5-T1, automated tests): lists "Write unit tests for data validation, metric calculation, ranking correctness, integration pipeline" — but specifies **no assertions, no fixture sizes, no expected values, no coverage target**.
- `specs/week-1/tasks.md:58-61` (P3-T1 popularity baseline): "Test with sample users" — undefined which users, what expected output shape.
- `specs/week-1/tasks.md:72-76` (P4-T2): "Compare against expected performance floor" — **no floor value defined anywhere** in spec/plan/ADR.

**Issue:** These are not testable as written. REQ-009/spec.md:161 says metrics "verified against ground truth," but the week-1 tasks never say how. A known-cases test (P4-T1 line 69) is mentioned ("Test metrics with simple known cases") but no case is enumerated.

**Recommended fix:** Add to P4-T1/P5-T1: (a) at least one hand-computed ground-truth case per metric (e.g., a 3-user toy matrix where P@5/R@5/NDCG@5 are computed by hand and asserted); (b) for P3-T1, assert `recommend(user_id, N)` returns exactly N distinct movieIds not in that user's training set; (c) for P4-T2, define the performance floor (e.g., "popularity NDCG@10 must be > 0 and reproducible to ±1e-6 across two runs") so "compare against floor" is actionable.

### W-4 — REQ-010 and REQ-013 under-specified / missing in week-1 tree
**Evidence:** `specs/recolab/spec.md:165-209` defines REQ-010 (3 baselines) and REQ-013 (automated tests). The week-1 spec's critical-reqs list (spec.md:53-87) includes REQ-008/009/011/012 but **omits REQ-013**, and treats testing as a task (P5-T1) rather than a tracked requirement. ADR-003 (line 10, 41) claims to satisfy "REQ-013" but the week-1 spec never declares it.
**Issue:** Traceability breaks: ADR-003 references REQ-013, but the requirement ID has no home in the week-1 spec. Either add REQ-013 to the week-1 critical-requirements section or explicitly state "REQ-013 inherited from source of truth `specs/recolab/spec.md`."

### W-5 — Week-1 spec "Technology Stack" contradicts master on persistence/runtime tooling but is silent about it
**Evidence:** `specs/recolab/spec.md:139-142` lists FastAPI, Node 20, Next.js 16, scikit-surprise/implicit. `specs/week-1/spec.md:40-44` lists only pandas/numpy/scikit-learn + matplotlib/seaborn (dev). This is a legitimate time-box, but the week-1 spec never states "backend/UI deferred to later weeks" in its scope section — a reader of week-1 alone would think the project is pandas-only.
**Recommended fix:** Add an explicit "Relationship to master spec" note in week-1 spec.md Scope stating the backend/UI are deferred per `specs/recolab/plan.md` Weeks 5-6, so the reduced stack is understood as a slice, not a redefinition.

### W-6 — Plan "Day 2" prose (plan.md:25-29) omits evaluation/persistence that tasks require
**Evidence:** `plan.md:25-29` "Day 2: Model & Evaluation" lists only popularity baseline, basic metrics, learning docs, portal prep. But Phases 4-5 (plan.md:53-67) and tasks.md Day 2 include NDCG@K, automated tests, and model persistence. The Day-2 summary block understates the Day-2 work and is inconsistent with the phase detail below it.
**Recommended fix:** Align the Day 2 summary bullet list with Phases 3-5 (add metrics completion, automated tests, persistence).

### W-7 — ADR references are not linked from tasks/plan
**Evidence:** `tasks.md` and `plan.md` never cite ADR-001/002/003. The ADRs themselves reference the week-1 spec, but the dependency is one-directional and unverifiable from the task checklist.
**Recommended fix:** Tag Day 2 tasks with their ADR: e.g., P3-T1/P4-T1 → ADR-002; P5-T2 → ADR-003; spec/plan python notes → ADR-001. This closes the traceability loop the task asked about.

### W-8 — Minor: spec says "f-string enhancements" as a 3.12 rationale; irrelevant to a data prototype
**Evidence:** `specs/week-1/spec.md:41` and ADR-001 line 16 cite "enhanced f-string capabilities" as a reason to use 3.12+. This is a weak rationale for a pandas/sklearn data pipeline and is moot given the real floor is 3.14. Cosmetic, but noted because it undersells the *actual* reason (3.14 is the verified runtime; see CF-1).

---

## SDD Correctness Assessment (per focus areas)

| # | Focus area | Result |
|---|-----------|--------|
| 1 | Spec/Plan/Tasks consistency | Partial. Day 2 task phasing (P3/P4/P5) matches plan Phases 3-5. But plan Day-2 summary (plan.md:25-29) under-lists work (W-6), and REQ-013 missing from week-1 spec (W-4). |
| 2 | Version drift | FAIL — confirmed at spec.md:41, plan.md:36, ADR-001:13/16 vs pyproject.toml:6/27/34 (CF-1). |
| 3 | ADR quality | Mostly well-formed (Context/Decision/Consequences/Alternatives/References all present), but ADR-002 contains an internal contradiction on NDCG@K (CF-2) and overstates sklearn role (W-1). ADR-003 is the cleanest. |
| 4 | Duplicate SDD trees | Structural risk confirmed (W-2). Two trees disagree on Python floor (3.9+ vs 3.12+) and on whether hosting verification is in scope, with no canonical link. |
| 5 | Testability of Day 2 tasks | Weak (W-3). P3-T1/P4-T2/P5-T1 lack assertions, fixtures, and the "performance floor" is undefined. |
| 6 | Traceability | Gaps (W-4, W-7). ADRs cite REQ IDs not present in week-1 spec; tasks do not cite ADR IDs; two REQ namespaces (master vs week-1) are not bridged. |

---

## Recommended Fixes (prioritized)

1. **[Must fix] Resolve Python floor (CF-1).** Align `specs/week-1/spec.md:41`, `plan.md:36`, ADR-001:13/16, and `pyproject.toml:6,27,34` to one number. Recommended: `>=3.14` everywhere (matches verified runtime), or lower `pyproject.toml` to `>=3.12` if portability is wanted. Add rationale per constitution Standard #13.
2. **[Must fix] Correct ADR-002 NDCG@K contradiction (CF-2).** Reword line 46 so "deferred" applies only to MAP/MRR, and state NDCG@K is Must-Have per REQ-009.
3. **[Should fix] Designate `specs/recolab/` as the single source of truth (W-2).** Add a "Source of Truth / Relationship to master spec" header to every `specs/week-1/` doc, and explicitly log each divergence (Python floor, dropped hosting verification, deferred backend/UI). Stop dual-editing two spec sets.
4. **[Should fix] Make Day 2 test tasks testable (W-3).** Add hand-computed ground-truth metric cases, define the popularity "performance floor," and specify assertion shape for P3-T1/P5-T1.
5. **[Should fix] Close traceability (W-4, W-7).** Add REQ-013 to week-1 spec (or explicitly inherit it) and tag Day 2 tasks with their ADR numbers.
6. **[Consider] Align plan Day-2 summary with Phases 3-5 (W-6) and trim the "f-string" rationale (W-8).**
7. **[Consider] Reconcile sklearn role wording (W-1).** State `top_k_accuracy_score` is a reference/cross-check, not the primary metric engine.

---

## Top 3 Findings (summary)

1. **Python version drift (CF-1):** `specs/week-1/spec.md`/`plan.md` and `ADR-001` still say "Python 3.12+" while `recolab-hybrid-recommender/pyproject.toml:6` requires `>=3.14` and its ruff/mypy config still targets `3.12` — an unresolved Day-1 IVP finding (WF-4) that now spans spec, plan, ADR, and `pyproject.toml` with no agreement.
2. **ADR-002 self-contradiction on NDCG@K (CF-2):** Line 46 says NDCG@K is "deferred," but the same ADR's decision (line 13), the spec Must-Have (spec.md:22), REQ-009 (spec.md:69-74), and even ADR-002 line 68 ("NDCG@K essential") all require it — a contradiction that would let a reviewer wrongly drop a Must-Have.
3. **Two divergent SDD trees with no canonical link (W-2):** `specs/recolab/` (6-week, FastAPI, Python 3.9+) and `specs/week-1/` (2-day, pandas-only, Python 3.12+) already disagree on the Python floor and on whether hosting verification is in scope, and the week-1 docs never state they are a derived slice of the master — a structural drift risk that will make AC-001..005 and REQ-010/013 unverifiable by Week 3.

---

*Audit completed without modifying any files. All referenced paths are absolute under `F:\Courses\Hamza\Devnexes-Internship-Projects`.*
