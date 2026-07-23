---
title: Similarity Computation — On-Demand vs Precomputed Matrix
status: Accepted
date: 2026-07-22
week: 2
---

# ADR-005: Similarity Computation Strategy for ContentModel

## Context
`ContentModel.similar_items` needs cosine similarity between a query movie and all
9,742 catalog movies. Two approaches exist:

| Approach | Compute time | Memory | Disk |
|---|---|---|---|
| **On-demand**: compute `feature_matrix @ query_vec.T` per call | O(n · f) per query | ~sparse features only (~5 MB) | Minimal |
| **Precomputed**: full n×n matrix at fit time | O(n² · f) once | 9742² × 8 bytes ≈ **760 MB** | Same |

## Decision
**On-demand per-query computation.**

For n = 9,742 movies, the full similarity matrix requires ~760 MB RAM — unacceptable
for a portfolio demo on a standard laptop and a free hosting tier (Render free = 512 MB).
On-demand is a sparse matrix-vector product: sub-millisecond for a single query.

## Consequences
- Positive: Fits in <100 MB RAM. Works on free hosting. Simple to implement and reason about.
- Negative: If the demo ever needs batch similarity for all pairs simultaneously (e.g., evaluation over all test users), each user's query is re-computed independently. For 610 users × 10 recommendations this is still <1 second — acceptable.
- Future option: cache top-K per movie in a dict after first query for a warm-cache speedup. Not implemented now.

## References
- `specs/content-model/plan.md` §3 Phase 4.2
- `specs/content-model/spec.md` §11.3
