---
id: 003
title: Week 2 SDD Design — Content Model, Protocols, Self-Refined Docs
stage: spec
date: 2026-07-22
surface: agent
model: Auto
feature: content-model
branch: feature/week-2-sdd-content-model
user: Muhammad Hamza
command: >
  Create week-2 SDD documents following deep-research-spec-plan-workflow.md.
  Self-refine. Identify gaps, conflicts, mistakes. Apply 5 custom rules.
  Reformat to sp-command template style. Create branch, commit, backup.
labels: [week-2, sdd, content-model, tfidf, protocols, cold-start, adr]
links:
  spec: specs/content-model/spec.md
  ticket: null
  adr: >
    history/adr/004-content-feature-strategy.md,
    history/adr/005-similarity-computation-strategy.md,
    history/adr/006-recommender-protocol-design.md
  pr: null
files:
  - specs/content-model/spec.md
  - specs/content-model/plan.md
  - specs/content-model/tasks.md
  - history/adr/004-content-feature-strategy.md
  - history/adr/005-similarity-computation-strategy.md
  - history/adr/006-recommender-protocol-design.md
  - learning/week-2/weekly-progress-note.md
  - learning/week-2/technical-acquisition-record-week2-sdd.md
  - history/prompts/general/006-week-2-spec-plan-tasks-sdd.general.prompt.md
tests:
  - No new code tests this session — SDD docs only
  - Spec/plan/tasks pass Kiro diagnostics (0 errors)
---

# Week 2 SDD Design — Technical Acquisition Record

## Executive Summary

This session produced the complete SDD (Spec-Driven Development) documents for Week 2 of the RecoLab project. The work covered: deep-research gap analysis of Week 1 artifacts, writing three new spec documents (`spec.md`, `plan.md`, `tasks.md`) for the Content Model feature, self-refining them against 9 identified gaps/conflicts/mistakes, creating three Architecture Decision Records, adding missing fixtures and validation tasks, and finally reformatting everything to match the project's `sp` command template style. No implementation code was written — this session is pure design and planning.

---

## 1. What Is SDD (Spec-Driven Development)?

### Tool Name
Spec-Driven Development (SDD) — a structured planning workflow used in this project.

### Primary Purpose
SDD separates "what to build and why" from "how to build it." You write a spec (requirements) → a plan (architecture) → tasks (atomic todo items) before writing any code. This means every line of code you eventually write has a traceable reason.

### Why It Matters
Without SDD, you write code and then try to justify it. With SDD, you think through the problem completely first, catch mistakes on paper (cheap), and only then implement (expensive). In this project, doing SDD upfront found 9 real problems before a single line of Week 2 code was written.

### The Three Files

| File | Question it answers | Audience |
|---|---|---|
| `spec.md` | What are we building and why? (user stories, acceptance criteria) | Anyone — non-technical too |
| `plan.md` | How are we building it? (architecture, data model, API contracts) | Developer |
| `tasks.md` | What exact steps do I take? (ordered, numbered, checkable) | Developer executing the work |

---

## 2. Technical Deep-Dive

### What Is the Content Model?

Week 1 built a **popularity model** — "recommend the most popular movies." It's the dumbest possible recommender but serves as the minimum bar every smarter model must beat.

Week 2 builds the **content-based model** — "recommend movies that are *similar in type* to what you liked." It does this by:

1. **Feature engineering** — turning each movie's genre string (`"Action|Adventure|Sci-Fi"`) into a vector of numbers using TF-IDF
2. **Similarity measurement** — comparing those vectors with cosine similarity to find the closest matches
3. **Cold-start handling** — for users with no history, accepting genre preferences and/or liked movie names to construct a taste profile

### What Is TF-IDF?

TF-IDF stands for **Term Frequency – Inverse Document Frequency**. Think of it this way:

- Each movie is a "document." Its genres are the "words."
- **TF (term frequency)**: how often a genre appears in this movie's list
- **IDF (inverse document frequency)**: how rare is this genre across ALL movies? Rare genres get higher weight because they're more distinctive.
- Result: each movie becomes a row of numbers (a **vector**), where common genres (like "Drama") score lower and rare genres score higher.

```
"Action|Adventure"  →  [0.0, 0.71, 0.71, 0.0, 0.0, ...]
"Action|Comedy"     →  [0.0, 0.71, 0.0, 0.71, 0.0, ...]
"Drama"             →  [0.85, 0.0, 0.0, 0.0, 0.0, ...]
```

### What Is Cosine Similarity?

Imagine each vector as an arrow pointing in space. Two movies are "similar" if their arrows point in roughly the same direction. Cosine similarity measures the angle between two arrows:

- Score **1.0** = identical direction = identical genre profile
- Score **0.0** = perpendicular = completely different genres

It's called "cosine" because mathematically it uses the cosine of the angle between vectors.

**Why not just count matching genres?** Because TF-IDF vectors are **L2-normalised** (their length is normalised to 1). This means short genre lists and long genre lists are comparable — the dot product of two L2-normalised vectors *is* the cosine similarity. No division needed.

### What Is the Cold-Start Problem?

A **cold-start** situation happens when:
- A new user has never rated anything → nothing to learn preferences from
- A new movie has no ratings → can't use collaborative patterns

For new users, we ask: "What genres do you like?" and "Name a few movies you've heard of." We then construct a synthetic taste vector and recommend accordingly. This is exactly what `recommend_cold_start(genres, liked_movie_ids, k)` does.

**Why is this the hardest problem in recommender systems?** Because without interaction history, you have no signal. Content-based filtering is the most natural solution — it only needs *item metadata* (genres), not user behavior.

### What Is a Python Protocol?

A `Protocol` in Python is a way to say "any class that has these methods is acceptable here — I don't care about its inheritance." It's like a contract or interface.

```python
# Before Protocol: everyone had to inherit from a base class
class BaseRecommender(ABC):
    def recommend(self, user_id, k, exclude_items): ...

class PopularityModel(BaseRecommender):  # forced inheritance
    ...

# After Protocol: just match the shape — no inheritance needed
class Recommender(Protocol):
    def recommend(self, user_id, k, exclude_items) -> list[int]: ...

class PopularityModel:  # no inheritance — just has the right method
    def recommend(self, user_id, k, exclude_items) -> list[int]:
        ...

isinstance(PopularityModel(), Recommender)  # → True via duck typing
```

**Why does this matter?** `PopularityModel` was written in Week 1 with no Protocol. Using a Protocol means we get the contract benefits (mypy type checking, `isinstance` checks) without touching Week 1 code at all.

### What Is `FeatureError`?

A custom exception class that gets raised when a movie has no genres (`"(no genres listed)"`). Without this guard, the TF-IDF vector for such a movie would be all zeros (a **zero-norm vector**). Computing cosine similarity against a zero vector produces **NaN** (Not a Number), which silently corrupts all downstream calculations.

By raising `FeatureError` instead, we fail loudly and early with a clear message: `"movie_id=9: zero-norm genre vector"`. The `movie_id` attribute lets callers know exactly which movie caused the problem.

### Why On-Demand Similarity Instead of Precomputed?

The alternative would be computing similarity for every pair of movies at fit time and storing the full n×n matrix.

```
n = 9,742 movies
Full matrix = 9742 × 9742 × 8 bytes (float64) ≈ 760 MB
```

760 MB exceeds the RAM limit of free hosting tiers (Render free = 512 MB). On-demand computation — `feature_matrix @ query_vec.T` — is a single sparse matrix-vector product that takes milliseconds and uses almost no memory. See ADR-005 for full decision record.

---

## 3. Project Integration

### How This Fits the 6-Week Plan

```
Week 1: ✅ Popularity baseline + evaluation framework (data foundation)
Week 2: 🔧 Content model (this week — SDD design complete)
Week 3: ⏳ Collaborative filtering (user-behavior patterns)
Week 4: ⏳ Hybrid + designed cold-start UI
Week 5: ⏳ FastAPI backend + Next.js frontend
Week 6: ⏳ Final evaluation + deployment
```

### The `Recommender` Protocol as a Shared Contract

One of the most important things designed this week is the `Recommender` Protocol. It defines a single shared interface:

```python
def recommend(self, user_id: int, k: int,
              exclude_items: set[int] | None = None) -> list[int]
```

Every model — popularity, content, collaborative, hybrid — must implement this. Why? Because the evaluation harness `evaluate_all` needs to call any model the same way. Locking this contract now (Week 2) means Week 3, 4, 5 never need to change the evaluation system.

### `ModelBundle` Reuse

Week 1 built `ModelBundle(model, metrics, metadata)` for saving/loading the popularity model. Week 2's `ContentModel` reuses this exact same system via `to_bundle()` / `from_bundle()`. This means the Week 6 evaluation comparison table can load any model with identical code.

---

## 4. Gaps, Conflicts, and Mistakes Found (Self-Refinement)

This is the core of the deep-research workflow — finding problems *before* writing code.

### 9 Issues Found and Resolved

| # | Type | Problem | Fix |
|---|---|---|---|
| GAP-01 | Gap | No shared `Recommender` interface — evaluation was untyped | Created `interfaces.py` with Protocol |
| GAP-02 | Gap (CF-3) | Cold-start was a behavioral fallback, not a designed interface | Added `ColdStartHandler` Protocol |
| GAP-03 | Gap | `tags.csv` cited as feature source — only 16% movie coverage | Genres = primary; tags = optional |
| GAP-04 | Gap (CF-2) | Random baseline floor `K/9724` never enforced as test assertion | Added floor test in `test_content.py` |
| GAP-05 | Gap | `ContentModel` had no defined persistence contract | Specified `to_bundle()` metadata schema |
| GAP-06 | Gap | `split.py` had zero test coverage from Week 1 | Added `test_split.py` this week |
| GAP-07 | Gap | `__init__.py` would silently break without updates | Explicit update task per new module |
| CONFLICT-01 | Conflict | Python 3.12 in arch doc vs 3.14 in pyproject.toml | 3.14 wins (live env). Arch doc = historical floor |
| MISTAKE-01 | Mistake | Empty `recolab/` directory at project root (artifact of early setup) | Delete or gitignore |

### 5 Custom Rules Created

These rules are derived from the specific risks of this week's work:

| Rule | What it enforces |
|---|---|
| RULE-W2-001 (Interface-First) | Write the Protocol before writing the model class |
| RULE-W2-002 (Feature-Safety) | Zero-norm vectors must raise `FeatureError`, never silently produce NaN |
| RULE-W2-003 (Harness-Lock) | `evaluate_all` signature is frozen — no changes to `metrics.py` |
| RULE-W2-004 (CF-2 Floor) | Every model test must assert it beats `P@K > K/9724` |
| RULE-W2-005 (Cold-Start Completeness) | Every model test must include a new-item cold-start test |

---

## 5. Conceptual Understanding

### Why Format the Docs Like the `sp` Commands?

The original SDD documents were correct but hard to read — they mixed architecture decisions, interface contracts, code snippets, and task lists all in one dense file. The `sp` command templates (`.specify/templates/`) enforce a clear separation:

- `spec.md` → **user stories + acceptance criteria** — no code, no implementation
- `plan.md` → **architecture + data model + API contracts** — technical decisions, no task list
- `tasks.md` → **numbered checklist** — exact steps, file paths, gate checkpoints

This separation means you can hand `spec.md` to a non-technical person to review requirements, and `tasks.md` to an AI agent to execute — without either needing to read the other.

### What Is an ADR?

An **Architecture Decision Record** is a short document that captures *why* a significant decision was made. It records: what was decided, the alternatives considered, and the consequences. Future you (or a reviewer) can read it and understand the reasoning without having to reverse-engineer it from code.

Three ADRs were written this week:

- **ADR-004**: Why genres are the primary feature source (tags cover only 16% of movies)
- **ADR-005**: Why on-demand cosine similarity instead of precomputing (~760 MB RAM problem)
- **ADR-006**: Why Python `Protocol` instead of ABC (zero changes to existing Week-1 code)

### What Is an IVP Report?

An **Independent Validation Perspective** report is a structured review of completed work from 5 angles: Security, Constitution (coding standards), Specification (requirements met), Quality (math correctness), and Conflict (no contradictions). Week 1 had multiple IVP reports. Adding one to Week 2 tasks ensures the same quality standard is maintained.

### The `tests/fixtures/` Problem

The CF-2 floor test (`test_content_beats_random_floor`) is the most important test in Week 2 — it proves the content model is actually smarter than random guessing. But it requires the MovieLens dataset, which is gitignored (100K ratings, not committed to the repo).

The fix: generate a small sample (50 users, ~200 movies) with `default_rng(42)` and **commit those sample files** to `tests/fixtures/`. This makes the floor test always runnable in CI without the full dataset.

---

## 6. Learning Outcomes

### What I Learned

- **SDD is a bug-finder, not just documentation.** The 9 gaps/conflicts found before writing code would each have caused real problems during implementation — wrong metrics, NaN propagation, inconsistent interfaces, broken CI tests.
- **A Protocol is not an interface in disguise — it changes nothing.** The most elegant thing about Python's `typing.Protocol` is that `PopularityModel` (written in Week 1) satisfies `Recommender` with literally zero code changes. Inheritance forces coupling; duck typing via Protocol gives you the benefits without the cost.
- **Tags are a trap.** It's tempting to use all available metadata. But 84% zero vectors mean the similarity matrix would be meaningless for most movies. Always analyze coverage before using any feature source.
- **Template format matters more than you think.** A document that's correct but hard to navigate is less useful than one that's slightly less complete but immediately scannable. The `sp` template format separates reading concerns cleanly.
- **Separation of concerns in documentation.** `spec.md` should never contain code. `tasks.md` should never contain architecture rationale. When they're mixed, both become harder to use.

### Skills Developed

- Deep-research workflow: reading existing code → identifying gaps → resolving before implementation
- Writing typed Python Protocol classes
- Designing zero-norm guards for ML pipelines
- ADR writing: concise, decision-focused, no prose padding
- SDD template formatting (user stories, Given/When/Then, numbered task lists)

### Challenges Overcome

- **Diagnostic errors on `tasks.md`**: The Kiro spec format checker expected `- [ ] N.` (plain number + dot). Our original format used `T001`. Fixed by converting to sequential integers.
- **Stale path references**: After renaming `specs/week-1/` → `specs/data-evaluation-foundation/` and `specs/week-2/` → `specs/content-model/`, multiple files still referenced the old paths. Fixed systematically with grep + replace.
- **ADR suggestion vs ADR existence**: The original `plan.md` had a comment saying "you should write an ADR" but the ADR didn't exist. Created all three ADR files this session.

### Connections to Other Technologies

- TF-IDF is the same math used in search engines (keyword-to-document relevance)
- Cosine similarity is the same math used in word embeddings (how similar are two words?)
- The `Protocol` pattern is equivalent to TypeScript's `interface` or Java's `interface` — structural typing instead of nominal typing
- `ModelBundle` is the same concept as a model registry entry in MLflow or a checkpoint in PyTorch

---

## 7. Interview Preparation

### Technical Discussion Points

- "Why TF-IDF for movie genres instead of one-hot encoding?" → TF-IDF weights rare genres higher, giving more distinctive genre combinations higher similarity scores. One-hot treats all genres equally.
- "Why genres-only and not tags?" → Tags cover only 16% of the 9,742 movies. TF-IDF over a 16%-populated feature produces zero vectors for 84% of items, making cosine similarity meaningless for most pairs.
- "Why on-demand cosine instead of precomputed?" → Precomputed n×n matrix = ~760 MB RAM, exceeds free hosting limits. On-demand sparse matrix-vector product = milliseconds, ~5 MB.
- "Why Protocol over ABC?" → `PopularityModel` (Week 1) already had the right method signature. Protocol gives type-checking and `isinstance` support without forcing inheritance refactor.

### Decision-Making Examples

- Identified that tags had 16% coverage before choosing feature strategy → chose genres as primary (ADR-004)
- Calculated 760 MB memory cost before choosing similarity computation strategy → chose on-demand (ADR-005)
- Checked that `PopularityModel` already had a compatible `recommend` signature before choosing Protocol → chose Protocol over ABC to avoid any Week-1 code changes (ADR-006)

### Problem-Solving Examples

- CF-2 floor test always skipping in CI → root cause: full dataset gitignored → fix: commit a small 50-user fixture sample
- `FeatureError` instead of NaN → root cause: zero-norm vector from no-genre movies → fix: detect at query time and raise typed exception with `movie_id`
- Protocol vs ABC → root cause: don't want to modify Week-1 code → fix: use structural typing so existing code satisfies the interface without changes

### Key Takeaways for Explanation

1. SDD saves more time than it costs — 9 bugs found on paper vs. in code
2. Always analyze data coverage before choosing features (16% tags → useless for similarity)
3. Protocols give you type safety without coupling — design for zero-change compatibility
4. Every model plugs into the same `evaluate_all` harness via `Recommender` protocol — the comparison table in Week 6 is just assembly

---

## 8. References and Resources

- `specs/content-model/spec.md` — user stories and acceptance criteria
- `specs/content-model/plan.md` — architecture, data model, API contracts
- `specs/content-model/tasks.md` — 62 numbered implementation tasks
- `history/adr/004-content-feature-strategy.md` — genres vs tags decision
- `history/adr/005-similarity-computation-strategy.md` — on-demand vs precomputed
- `history/adr/006-recommender-protocol-design.md` — Protocol vs ABC
- `specs/data-evaluation-foundation/` — Week 1 foundation this builds on
- `specs/recolab/spec.md` — master 6-week specification
- `Devnexes_AI_ML_Individual_Project_Plans.pdf` — Project AI-06 brief (pp.20-22)
- `.specify/templates/spec-template.md`, `plan-template.md`, `tasks-template.md` — format reference
- `.workflows/deep-research-spec-plan-workflow.md` — workflow followed this session

---

## Prompt

Create the week-2 SDD documents following the deep-research-spec-plan-workflow.md. Self-refine. Identify gaps, conflicts, and mistakes everywhere and automatically resolve. Apply 5 custom rules. Reformat documents to match the sp-command template style. Create a new branch, commit all changes, and create a backup of that branch.

## Response Snapshot

Produced `specs/content-model/spec.md` (user stories + Given/When/Then ACs), `specs/content-model/plan.md` (architecture + data model + phase plan), `specs/content-model/tasks.md` (62 numbered tasks, 8 phases). Found and resolved 9 gaps/conflicts/mistakes. Created ADR-004/005/006. Added `tests/fixtures/` task and IVP validation phase. Reformatted all three files to `sp` template style. All diagnostics: 0 errors.

## Outcome

- ✅ Impact: 3 SDD documents ready for Week-2 implementation. 9 problems resolved before code. 3 ADRs created. Docs formatted to project standard.
- 🧪 Tests: No code tests this session — spec/plan/tasks diagnostics all pass (0 errors)
- 📁 Files: specs/content-model/ (3 files), history/adr/ (3 files), learning/week-2/ (2 files), history/prompts/general/006
- 🔁 Next prompts: Implement Week 2 tasks starting at task 1 (pyproject.toml hygiene) through task 62 (IVP report)
- 🧠 Reflection: The most valuable moment was finding GAP-03 (tags 16% coverage) before implementation. Without deep-research, we would have built TF-IDF over tags and discovered the problem only after getting meaningless similarity scores for 84% of movies.
