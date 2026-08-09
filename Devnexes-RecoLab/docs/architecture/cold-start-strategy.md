# Cold-Start Handling Architecture

## Tiered Fallback Strategy

Handling users with insufficient rating history is a critical production requirement in recommendation systems. RecoLab addresses cold-start scenarios using a 4-tier fallback hierarchy:

```
                  ┌─────────────────────────────────────┐
                  │    Target User Recommendation Request│
                  └──────────────────┬──────────────────┘
                                     │
                        Is Rating History > 5?
                       ┌─────────────┴─────────────┐
                     YES                          NO
                       │                           │
         ┌─────────────▼─────────────┐   ┌─────────▼─────────┐
         │ Weighted Hybrid Ensemble  │   │  Are Genres/Seeds │
         │ (0.4 Content + 0.6 Collab)│   │   Provided?       │
         └───────────────────────────┘   └────┬─────────┬────┘
                                            YES        NO
                                             │          │
                              ┌──────────────▼─┐     ┌──▼───────────────┐
                              │ Content Genre  │     │ Global Popularity│
                              │ Query Profile  │     │ Baseline Model   │
                              └────────────────┘     └──────────────────┘
```

### Fallback Tiers
1. **Tier 1 (Active User, $> 5$ ratings)**: Full Hybrid Weighted Linear Ensemble.
2. **Tier 2 (Cold User, $\le 5$ ratings, with profile)**: Pure `ContentModel` scoring based on target user's rated items.
3. **Tier 3 (New User, 0 ratings, explicit onboarding genres)**: `recommend_cold_start()` using TF-IDF genre preference query vector.
4. **Tier 4 (Anonymous User, 0 ratings, no genres)**: Non-personalized `PopularityModel` baseline.
