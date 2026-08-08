# RecoLab System Limitations & Risk Analysis

## 1. Model-Specific Limitations
### Popularity
- **Impact Level:** High
- **Known Limitations:**
  - Zero personalization: identical recommendations provided to all users
  - Extreme popularity bias: top decile items occupy 100% of catalog recommendations
  - Disregards user historical preferences and implicit feedback
- **Actionable Remediation:** Transition to personalized collaborative filtering or hybrid model.

### Content
- **Impact Level:** Medium
- **Known Limitations:**
  - Overspecialization: recommendations restricted to genres user has previously consumed
  - Metadata dependency: relies on static genre tags; cannot capture subtle stylistic preference
  - Low coverage of niche items without detailed metadata tags
- **Actionable Remediation:** Incorporate dense text embeddings (e.g., plot summaries) and collaborative signal.

### User-Based CF
- **Impact Level:** High
- **Known Limitations:**
  - Cold-start user vulnerability: zero recommendations for unobserved new users
  - Memory scalability: O(N_users^2) cosine similarity computation during real-time inference
  - Sparsity sensitivity: performance drops significantly when user interaction matrix sparsity > 98%
- **Actionable Remediation:** Precompute user neighbor indices offline or apply matrix factorization (ALS/SVD).

### Item-Based CF
- **Impact Level:** Medium
- **Known Limitations:**
  - Cold-start item vulnerability: inability to recommend items with <= 5 ratings
  - Static similarity graph: requires complete retrain to recognize newly published movies
  - Limited serendipity: tends to recommend highly similar items to recent views
- **Actionable Remediation:** Hybridize with content features for new items (cold-start fallback).

### Hybrid
- **Impact Level:** Low
- **Known Limitations:**
  - Hyperparameter sensitivity: linear combination parameter alpha=0.5 requires offline tuning
  - Computational latency: requires dual-path scoring (Content + Item-CF) per request
  - Inherits cold-start degradation when both constituent sub-models lack signal
- **Actionable Remediation:** Implement adaptive alpha per user activity level (e.g. higher content weight for sparse users).

## 2. Failure Modes & Fallback Mechanisms
| Failure Mode | Trigger | System Behavior | Remediation |
|---|---|---|---|
| Zero-rating New User | User ID absent from training set | User-Based CF throws Key/Index Error | Automatic fallback to Popularity / Onboarding cold-start recommendations. |
| Unseen Niche Item | Movie ID absent from training set | Collaborative filtering returns 0 similarity | Content-based fallbacks using genre TF-IDF tags. |
| High Sparsity Degeneration | User has < 2 ratings in training set | User-CF returns recommendations with < 0.1 precision | Route to Hybrid model with content weighting alpha=0.8. |

## 3. Data & Evaluation Constraints
- **Data Sparsity:** 98.3%
- **Offline vs Online Gap:** Offline top-K precision/recall measures historical replay hit-rate, not true user click/watch conversion.
- **Deployment Bottlenecks:** User-Based CF single-request latency scales linearly with active user table size.