"""Image cache manager for movie posters (Task-001).

Manages movie poster retrieval, caching, and fallback handling. The current
implementation uses a *text-based placeholder system*: every movie renders as
a stylized card displaying its title (per the Day 3 Afternoon implementation
prompt, which overrides the SDD's via.placeholder.com URL suggestion). The
cache contract stays ``movie_id -> poster representation`` and is persisted in
session state, so upgrading to a real TMDB-backed image pipeline later only
requires swapping :meth:`ImageCacheManager._fetch_poster`.
"""

from __future__ import annotations

from ui.session_manager import SessionManager

#: Prefix marking a text placeholder. ``placeholder:<title>`` renders as a
#: styled title card; a value without this prefix is assumed to be a real
#: image URL (future TMDB-backed builds) and rendered with ``st.image``.
PLACEHOLDER_PREFIX = "placeholder:"


class ImageCacheManager:
    """Cache manager with fallback handling for movie posters.

    The poster representation for a movie is produced on first access and then
    cached in session state, so it survives Streamlit reruns without refetching.
    """

    def get_poster(self, movie_id: int, title: str = "") -> str:
        """Return the poster representation for a movie.

        Hits the session-state cache first and falls back to generating a
        text-based placeholder. The returned value is a stable key the display
        layer knows how to render (currently ``placeholder:<title>``; in a
        TMDB-backed build it would be a real poster URL).

        Args:
            movie_id: Movie ID to look up.
            title: Movie title used to style the text placeholder.

        Returns:
            Poster representation (cache key) for the movie.
        """
        cached = SessionManager.get_poster_for(movie_id)
        if cached is not None:
            return cached

        poster = self._fetch_poster(movie_id, title)
        SessionManager.set_poster_for(movie_id, poster)
        return poster

    def is_placeholder(self, poster: str) -> bool:
        """Return True if *poster* is a text placeholder, not a real image URL."""
        return poster.startswith(PLACEHOLDER_PREFIX)

    def _fetch_poster(self, movie_id: int, title: str) -> str:
        """Fetch a poster representation (placeholder implementation).

        In production this would call the TMDB API or a similar service. For
        now, every movie maps to a text-based placeholder card that embeds the
        title so the display layer can style it without a second lookup.

        Args:
            movie_id: Movie ID (unused for text placeholders, kept for the
                future TMDB implementation).
            title: Movie title embedded in the placeholder key.

        Returns:
            Placeholder representation for the movie.
        """
        return f"{PLACEHOLDER_PREFIX}{title or 'Unknown title'}"
