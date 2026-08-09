# RecoLab Glossary

| Term | Definition |
|------|------------|
| **Cold-Start User** | A user with fewer interactions than required to generate reliable collaborative recommendations (in RecoLab, $\le 5$ ratings). |
| **Active User** | A user with a dense history of interactions ($> 5$ ratings in the training set). |
| **Catalog Coverage** | The percentage of the total item catalog recommended to at least one user across the entire test set. High coverage indicates diverse recommendations; low coverage indicates popularity bias. |
| **Precision@K (P@K)** | The fraction of the top $K$ recommended items that the user actually interacted with in the future (test set). |
| **Recall@K (R@K)** | The fraction of the user's total future interactions (test set) that were successfully placed in the top $K$ recommendations. |
| **NDCG@K** | Normalized Discounted Cumulative Gain. Similar to Precision, but assigns a higher score if relevant items appear closer to the top of the recommendation list (position-awareness). |
| **TF-IDF** | Term Frequency-Inverse Document Frequency. A numerical statistic determining how important a word (or genre) is to an item relative to a corpus. |
| **Cosine Similarity** | A metric capturing the cosine of the angle between two multi-dimensional vectors. In RecoLab, used to measure item-item or user-user similarity. |
| **Matrix Factorization** | A class of collaborative filtering algorithms that maps users and items to a joint latent factor space of a lower dimension. |
| **Hybrid Ensemble** | A recommendation system that combines outputs from multiple underlying models (e.g., Content + Collaborative) using a weighted averaging strategy. |
| **A/B Testing** | An online experimental methodology where user traffic is split into cohorts to test model versions against real engagement metrics (CTR, conversion). |
| **Holdout Split** | A data partitioning method where a strict chronological percentage of history is withheld (test set) to evaluate predictions made on the remainder (train set). |
| **Temporal Leakage** | A methodological flaw where future interactions improperly influence training, artificially inflating evaluation metrics. |
| **Popularity Bias** | The systemic tendency of recommendation algorithms to over-recommend popular blockbuster items while ignoring niche, long-tail content. |
| **Long-Tail** | The distribution of items characterized by a large number of occurrences far from the "head" or central part of the distribution (i.e. niche, rarely rated movies). |
