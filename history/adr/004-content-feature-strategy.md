---
title: Content Feature Strategy — Genres vs Tags
status: Accepted
date: 2026-07-22
week: 2
---

# ADR-004: Content Feature Strategy for ContentModel

## Context
`ContentModel` needs a feature representation for each of the 9,742 MovieLens movies to
compute cosine similarity. Two metadata sources are available: `movies.csv` (genres) and
`tags.csv` (user-applied tags).

Coverage analysis:
- **Genres**: 9,742 movies, all have a genre string (or `"(no genres listed)"` — 34 movies)
- **Tags**: ~1,589 / 9,742 movies have ≥ 1 tag (≈ 16% coverage)

## Decision
**Genres are the primary and mandatory feature source. Tags are optional augmentation.**

`ContentModel(use_tags=False)` is the default. When `use_tags=True`, tag tokens are
appended to the genre string only for movies that have them — movies without tags
receive genres-only features. No imputation.

TF-IDF with L2-normalised rows is applied to the combined text corpus. Movies with
`"(no genres listed)"` and no tags receive a zero-norm vector; querying such a movie
raises `FeatureError` rather than returning NaN similarity.

## Alternatives Considered

| Option | Coverage | Problem | Decision |
|---|---|---|---|
| Genres only | 99.6% | Sufficient for portfolio demo | **Selected as default** |
| Tags only | 16% | 84% of items get zero vectors | Rejected as primary |
| Genres + tags mandatory | 99.6% (tags gap-filled with genre) | Misleading — inventing tag signals | Rejected |
| Genres + tags additive (opt-in) | 99.6% | Honest, richer for 16% of items | Selected as `use_tags=True` option |

## Consequences
- All 9,742 movies except the 34 with no-genre entries get valid feature vectors.
- The 34 no-genre movies raise `FeatureError` only when queried directly — they exist in the catalog but cannot be used as a similarity query source.
- Tag augmentation, when enabled, enriches similarity for ~1,589 movies. Effect on overall evaluation is minor but honest.
- Decision documented so Week 3 (collaborative model) and Week 6 (evaluation report) can reference it.

## References
- `specs/content-model/spec.md` §8, GAP-03
- `spec-architecture-recolab-hybrid-recommender.md` §4.1 (tags.csv listed as optional)
