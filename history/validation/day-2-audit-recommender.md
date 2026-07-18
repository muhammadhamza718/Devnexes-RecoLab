# Day 2 Recommender-Systems Domain Audit — RecoLab (Week 1 Planning Docs)

**Audit Type:** Recommender-systems domain review (spec / plan / tasks / ADRs only — no Day 2 code yet exists)
**Date:** 2026-07-18
**Auditor:** Recommendation-Engine Domain Specialist (collaborative filtering, content-based, hybrid, cold-start)
**Scope files:**
- `specs/week-1/spec.md`, `specs/week-1/plan.md`, `specs/week-1/tasks.md`
- `history/adr/001-data-technology-stack-week-1.md`
- `history/adr/002-evaluation-methodology-week-1.md`
- `history/adr/003-model-persistence-and-testing-week-1.md`
- Cross-reference: `Devnexes_AI_ML_Individual_Project_Plans.pdf` Project 6 (pp. 20-22)
- Prior context: `history/validation/day-1-ivp-report.md`, `history/validation/day-2-audit-sdd-quality.md`, `history/validation/day-2-audit-compliance.md`

> Note: This report was authored from the auditor's direct read of the planning docs because the automated recommender-domain audit agent failed to return a report file. It is consolidated here to complete the three-perspective Day-2 audit set (SDD-quality + compliance + recommender-domain).

---

## Verdict

**NEEDS-FIX**

The Day 2 planning is **directionally sound** for a Week-1 popularity baseline and correctly rejects the `top_k_accuracy_score` trap (scikit-learn has no NDCG@K; `top_k_accuracy_score` measures multiclass label ranking, not top-N ranking). However, from a recommender-systems standpoint the plan contains four domain-level defects that will produce *misleading evaluation results* and leave a core project requirement (cold-start) un-designed: (1) the evaluation protocol does not yet mandate excluding each user's already-rated training items before scoring — without this, P@K/R@K/NDCG@K are inflated and meaningless; (2) no performance floor / baselines-to-beat are defined, so "working" is undefined; (3) cold-start is documentation-only despite being the project's namesake; (4) the evaluation design has no guard against the popularity bias that defines this dataset (98.3% sparse, 66.4% items with <=5 ratings), so a naive popularity baseline can look "good" for the wrong reasons.

---

## Critical Findings

### CF-1 — Evaluation protocol does not yet guarantee excluding already-rated training items (metric inflation risk)
**Severity:** Critical (evaluation validity)
**Evidence:**
- `specs/week-1/spec.md:75` only later acquired: "CRITICAL EVAL RULE: evaluation MUST exclude each user's already-rated training items before scoring, or metrics are inflated." (added in the doc-fix pass)
- `specs/week-1/tasks.md:69` (P4-T1): "Evaluation MUST exclude each user's already-rated training items before scoring"
- `specs/week-1/plan.md:58-59` (Phase 4): mentions "proper train/test separation" but the *ranking* exclusion rule is not stated in plan prose, only in tasks/spec.
- Prior `history/validation/day-1-ivp-report.md` did not cover this because Day 1 had no metrics code yet.

**Analysis:** Recommender evaluation correctness hinges on this single rule. If recommendations are scored against the test set *without* first removing every item the user already rated in training, every metric is inflated by "hits" that are trivially recoverable. For a popularity baseline this is especially dangerous: the global top-N items overlap heavily with what heavy users already rated, so an un-filtered evaluation can report a deceptively high P@K. The rule now exists in spec/tasks, but it is not yet in the plan's Phase-4 narrative and is not yet enforced by any code/test. Until a test asserts `recommended_items ∩ training_rated_items == ∅`, the rule is a statement, not a guarantee.

**Why it matters:** This is the #1 reason popularity-baseline metrics in student recsys projects look "too good." It directly determines whether AC-W1-003 ("Ranking metrics calculated") is trustworthy.

**Recommended fix:** Add the exclusion rule to `plan.md` Phase 4 narrative explicitly. Add a test in P5-T1: `assert set(reco[user]) & set(train_items[user]) == set()` for every evaluated user. Define an explicit `exclude_known_items=True` default in the evaluation function signature.

---

### CF-2 — No performance floor / "what good looks like" defined for the popularity baseline
**Severity:** Critical (acceptance ambiguity)
**Evidence:**
- `specs/week-1/tasks.md:72-76` (P4-T2): "Compare against expected performance floor (e.g., random baseline Precision@K ~ K/num_items)" — but this floor value is only given as a *vague example in parentheses*, not a defined acceptance value.
- `specs/week-1/spec.md` and `plan.md` define no numeric floor or "must beat" threshold.
- PDF p.21: "Compare at least three approaches: popularity baseline, content-based and collaborative/hybrid" — requires *comparison*, which requires baselines-to-beat.

**Analysis:** A baseline with no floor cannot be judged correct. The SDD-quality audit (W-3) already flagged this: "the performance floor is undefined." From a domain view, the minimal defensible floor for a popularity baseline on MovieLens ml-latest-small is the **random baseline**: Precision@K_random ≈ K / |items| (|items| = 9,724) → P@5 ≈ 0.0005, P@10 ≈ 0.001, P@20 ≈ 0.002. A popularity baseline should substantially exceed this (typically P@10 ≈ 0.02-0.06 on this dataset with proper exclusion). Without writing these numbers down, "compare against floor" is not actionable and the acceptance criterion is unverifiable.

**Recommended fix:** In `specs/week-1/spec.md` REQ-009 (or a new REQ note) record the random floor: `P@K_random = K / 9724`. State acceptance: popularity baseline P@K/R@K/NDCG@K must exceed the random floor AND be reproducible to ±1e-6 across two runs (fixing the seed). Mirrors the SDD-quality audit W-3 recommendation.

---

### CF-3 — Cold-start is documentation-only; project namesake requirement un-designed
**Severity:** Critical (scope/theme compliance)
**Evidence:**
- `specs/week-1/spec.md:86` (REQ-011): "Document cold-start limitations AND outline a cold-start handling approach"
- `specs/week-1/tasks.md:113-118` (Phase 6): "Document + plan cold-start handling" — new-user fallback popularity/demographic prior; new-item fallback recency/genre prior.
- PDF p.20 project brief: "provide a useful fallback for new users or new items with little interaction history."
- PDF Acceptance Criteria: "Cold-start flows return sensible recommendations without fake user history."

**Analysis:** The recommender-domain specialist's view agrees with the compliance audit (CF-1): cold-start is the project's *defining* feature ("Hybrid Recommendation Engine **with Cold-Start Handling**") yet appears only as a "document + plan" phase with no designed interface, no data structure, no test. This is acceptable for *Week 1's code* (where popularity is the only baseline), but the *design* must exist now so later weeks implement against it, not invent it. Specifically missing:
- A defined new-user input schema (what preference signal drives the "demographic prior"? genre picks? a few ratings?).
- A defined new-item exposure strategy (recency/genre prior needs a ranking function, not just a note).
- A placeholder test `test_cold_start_returns_sensible_without_fake_history` (required by PDF p.21: "Add tests for ranking, filtering and cold-start behavior").

**Recommended fix:** Promote Phase 6 from "document" to "define the cold-start interface contract + placeholder test," even if full implementation is Week 4. Add a one-paragraph design per fallback (new-user, new-item) to `spec.md` REQ-011. This satisfies the compliance audit CF-1 and the PDF test requirement simultaneously.

---

### CF-4 — Popularity-bias blind spot: no guard against the baseline "winning" for the wrong reason
**Severity:** Warning → Critical at evaluation time
**Evidence:**
- Sparsity 98.3%, 66.4% of items have <=5 ratings (from Day-1 data analysis; `data/analysis/data_analysis_summary.txt`).
- `specs/week-1/tasks.md:48-52` documents popularity bias but the evaluation plan (P4-T2) compares only against random, not against the structural bias.

**Analysis:** On a 98.3%-sparse dataset, a global popularity list is dominated by a tiny head of blockbuster items. Properly excluding known items, the popularity baseline's head-items may still cover a large fraction of test interactions simply because *everyone* rated the top movies — not because the recommender is good. Without reporting the **coverage / catalog-hit-rate** (what fraction of the 9,724-item catalog the top-N ever recommends) and the **popularity-bias metric** (average popularity decile of recommended items), the project cannot demonstrate the "Document sparsity, bias and popularity effects" requirement (PDF p.21) or justify moving to content/collaborative models later. This is the recommender-specific version of the SDD-quality audit's W-5 (missing analytical depth).

**Recommended fix:** Add to P4-T2 a requirement to report, alongside P@K/R@K/NDCG@K: (a) catalog coverage of the top-N list; (b) mean item-popularity-decile of recommendations. These are cheap to compute and directly evidence the "popularity effects" requirement.

---

## Warnings

### W-1 — `top_k_accuracy_score` guidance correctly rejected; ensure code never uses it
**Evidence:** `specs/week-1/spec.md:73`, `plan.md:54`, ADR-002 line 20 all now state scikit-learn's `top_k_accuracy_score` is for multiclass label ranking and is NOT a substitute for P@K/R@K/NDCG@K.
**Note:** This is a *correct* decision (the SDD-quality audit W-1 only cautioned that the ADRs over-stated sklearn's role). The domain view confirms: NDCG@K has no sklearn equivalent; P@K/R@K must be hand-implemented. Action: add a code comment / test that asserts the custom functions are used, and never import `top_k_accuracy_score` for ranking.

### W-2 — Split ratio (80/20) acceptable but per-user minimum-history guard needed
**Evidence:** `split.py` (Day 1) uses per-user chronological 80/20 with `min_ratings_per_user=1`.
**Issue:** Users with only 1-2 ratings yield degenerate test sets (a single-item test cannot measure ranking quality; P@K is 0 or 1). The SDD-quality audit did not flag this. Domain best practice: require `min_ratings_per_user >= 5` (or report metrics only over users with >= K test items) so R@K/NDCG@K are meaningful. Also guarantees every evaluated user has train history to exclude (ties to CF-1).

### W-3 — No plan to handle the "all test items are in training" edge (zero-test-users)
**Evidence:** Split keeps >=1 train and >=1 test per user. Some users may have all-but-one in test.
**Issue:** Edge users with 1 test item and 100 train items are fine for CF-1 exclusion but contribute only 0/1 to P@K. Reporting averaged over such users dilutes signal. Recommend stratified or filtered evaluation cohort (users with >= K test items) — cheap and standard.

### W-4 — Later-week comparability not anticipated in Week-1 metric schema
**Evidence:** PDF requires comparing popularity vs content vs collaborative/hybrid (3+ approaches).
**Issue:** Week-1 metrics should be computed by a reusable `evaluate(recommended, test, train)` function returning a dict keyed by metric+K, so content/collaborative weeks slot in without re-implementing evaluation. Design the evaluation module to accept any recommender with a uniform `recommend(user, K, exclude_train=True)` interface now. This prevents the "two divergent trees" drift the SDD-quality audit (W-2) warned about.

---

## Recommender-Domain Correctness Assessment

| # | Focus area | Result |
|---|-----------|--------|
| 1 | Ranking-metric validity (exclude-known-items) | FAIL until enforced in code/test (CF-1) |
| 2 | Baselines-to-beat / floor defined | FAIL — floor is an example, not a value (CF-2 / SDD W-3) |
| 3 | Cold-start design (project namesake) | FAIL — documentation-only (CF-3 / compliance CF-1) |
| 4 | Popularity-bias instrumentation | WEAK — no coverage/decile reporting (CF-4) |
| 5 | Split quality for ranking | WEAK — no min-history / filtered cohort (W-2, W-3) |
| 6 | sklearn misuse avoided | PASS — `top_k_accuracy_score` correctly excluded (W-1) |
| 7 | Later-week comparability | OPEN — metric schema should be reusable (W-4) |

---

## Top 3 Domain Findings (summary)

1. **Exclude-known-items not yet enforced (CF-1):** The rule exists in spec/tasks but not in plan Phase-4 prose and has no code/test guarantee — without it, popularity-baseline metrics are inflated and the evaluation is invalid.
2. **No numeric performance floor (CF-2):** "Compare against expected performance floor (e.g., random ~ K/num_items)" is a parenthesis, not an acceptance value. Record `P@K_random = K/9724` and a reproducibility tolerance as the bar.
3. **Cold-start un-designed (CF-3):** The project's defining feature is a "document + plan" stub with no interface contract or placeholder test, leaving PDF Acceptance "Cold-start flows return sensible recommendations without fake user history" unaddressed at design level.

---

*Audit completed without modifying any files. All referenced paths are absolute under `F:\Courses\Hamza\Devnexes-Internship-Projects`. Authored from direct document review to complete the three-perspective Day-2 audit set.*
