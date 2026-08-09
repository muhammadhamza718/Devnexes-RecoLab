# System Architecture Index

Architectural documentation detailing the software engineering design, algorithms, data pipelines, and operational paradigms of RecoLab.

---

## 🏛️ Architecture Topics

1. **[System Architecture Overview](system-overview.md)**
   - Modular layer design, duck-typed protocol interface, component relationships, performance SLAs.

2. **[Data Flow & Pipeline Architecture](data-pipeline.md)**
   - Raw MovieLens dataset ingestion, preprocessing, train/test splitting, feature matrix building, predictions.

3. **[Cold-Start Handling Strategy](cold-start-strategy.md)**
   - Tiered fallbacks: Hybrid → Collaborative → Content-Based (Genres) → Popularity Baseline.

4. **[Architectural Decision Records (ADRs)](../architectural-decisions/)**
   - Record of architectural choices and trade-offs.
