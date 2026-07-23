---
title: Recommender Interface — Protocol vs Abstract Base Class
status: Accepted
date: 2026-07-22
week: 2
---

# ADR-006: Recommender Interface Design (Protocol vs ABC)

## Context
All four RecoLab models (popularity, content, collaborative, hybrid) must share a common
interface so `evaluate_all` can accept any of them without knowing their internals.
Two standard Python approaches exist: `Protocol` (structural typing) and `ABC`
(nominal inheritance).

## Decision
**`typing.Protocol` with `@runtime_checkable`.**

## Comparison

| Concern | Protocol | ABC |
|---|---|---|
| `PopularityModel` (Week 1 — already written) | Zero code changes needed — duck typing | Would require adding `(BaseRecommender)` to its class definition |
| `isinstance()` check at runtime | ✅ via `@runtime_checkable` | ✅ always |
| mypy type safety | ✅ structural check | ✅ nominal check |
| Coupling | Low — models don't import `interfaces.py` at all | High — models must inherit from `BaseRecommender` |
| Python version | 3.8+ | 3.0+ |

## Consequences
- `PopularityModel` (Week 1) satisfies `Recommender` without any modification — pure duck typing.
- Week 3 and 4 models only need the correct method signature to pass `isinstance` and mypy checks.
- `interfaces.py` is the only file that imports `Protocol`; models never import it.
- If a future model accidentally omits `recommend()`, mypy catches it at type-check time before tests run.

## References
- `specs/content-model/spec.md` §5.1, §7.4, GAP-01
- `specs/content-model/tasks.md` W2-P2-T1
