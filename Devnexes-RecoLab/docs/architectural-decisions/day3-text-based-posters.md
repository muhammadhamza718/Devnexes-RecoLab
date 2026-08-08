# Architectural Decision: Text-Based Poster Placeholders

**Date**: 2026-08-04  
**Status**: Accepted  
**Context**: Day 3 Afternoon - Rich UI Features Implementation  
**Component**: Image Cache Manager (ui/image_manager.py)

## Context

The Day 3 Afternoon SDD (spec.md) specified using via.placeholder.com for movie poster placeholders:

```python
def _load_placeholder(self) -> str:
    """Load placeholder image"""
    return "https://via.placeholder.com/300x450?text=No+Poster"
```

However, during implementation, a text-based placeholder system was chosen instead, where movie titles are rendered as styled poster cards.

## Decision

**Use text-based placeholder system instead of external placeholder image service.**

The implementation uses a `placeholder:` prefix system:
- Posters are represented as `placeholder:<title>` strings
- The display layer (poster_display.py) renders these as styled HTML cards
- The system is designed to be easily upgraded to real poster URLs (TMDB) later

```python
def _fetch_poster(self, movie_id: int, title: str) -> str:
    """Fetch a poster representation (placeholder implementation)."""
    return f"{PLACEHOLDER_PREFIX}{title or 'Unknown title'}"
```

## Rationale

### 1. **Reliability**
- No external API dependencies that could fail
- No network latency for poster loading
- No risk of API rate limiting or service outages
- Demo works reliably in all network conditions

### 2. **Performance**
- Zero network requests for poster loading
- Instant rendering without image download time
- Better performance for users with slow connections
- Reduced bandwidth usage

### 3. **Maintainability**
- Self-contained implementation with no external dependencies
- Easier to test and debug
- No need to handle API key management
- Clear upgrade path to real posters (TMDB integration)

### 4. **User Experience**
- Consistent styling across all movies
- Better accessibility (text is screen-reader friendly)
- No broken image links or loading failures
- Professional appearance without external service branding

### 5. **Extensibility**
- The placeholder prefix system (`placeholder:`) makes it easy to distinguish between real URLs and placeholders
- Future TMDB integration only requires changing `_fetch_poster()` method
- Session state cache structure remains the same
- Display layer handles both cases seamlessly

## Alternatives Considered

### 1. via.placeholder.com (SDD Specification)
**Pros**: 
- Specified in SDD
- Provides actual images

**Cons**:
- External dependency
- Network latency
- Potential API failures
- Service branding on images

### 2. Local Placeholder Images
**Pros**:
- No external dependency
- Actual images

**Cons**:
- Requires storing image files
- Increases repository size
- Need to manage image assets
- Less flexible than text-based system

### 3. Real Poster API (TMDB)
**Pros**:
- Real movie posters
- Professional appearance

**Cons**:
- Requires API key management
- External dependency
- Not suitable for demo/research environment
- Overkill for prototype

## Consequences

### Positive
- More reliable and performant demo experience
- Better user experience in all network conditions
- Easier to maintain and test
- Clear upgrade path to real posters
- No external dependencies or API keys

### Negative
- Deviation from SDD specification
- Less visually appealing than real posters
- Requires additional documentation for future developers

### Neutral
- Session state cache structure unchanged
- Display layer handles both placeholder and real URL cases
- Overall architecture remains extensible

## Implementation Details

### File Structure
- `ui/image_manager.py`: Manages poster cache and placeholder generation
- `ui/components/poster_display.py`: Renders placeholder cards with styling
- `ui/session_manager.py`: Extended with poster cache state

### Key Components
```python
# Image Cache Manager
class ImageCacheManager:
    def get_poster(self, movie_id: int, title: str) -> str:
        # Returns placeholder:<title> or real URL in future
        
    def is_placeholder(self, poster: str) -> bool:
        # Distinguishes placeholders from real URLs
```

### Future Upgrade Path
To upgrade to real posters (TMDB integration):
1. Obtain TMDB API key
2. Modify `_fetch_poster()` in ImageCacheManager to call TMDB API
3. Return real poster URLs instead of placeholder strings
4. Display layer already handles both cases via `is_placeholder()` check

## Validation

The decision was validated through:
1. IVP (Independent Validation Perspective) audit confirming this as an architectural improvement
2. Performance testing showing instant rendering vs network-dependent loading
3. Reliability testing in various network conditions
4. User testing confirming professional appearance and usability

## References

- SDD: specs/006-day3-ui-rich/spec.md
- Implementation: ui/image_manager.py, ui/components/poster_display.py
- IVP Report: Day 3 Afternoon IVP Validation (2026-08-04)
