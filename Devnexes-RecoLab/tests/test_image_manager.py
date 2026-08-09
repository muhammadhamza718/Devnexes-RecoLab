"""Tests for ImageCacheManager (Day 3 Afternoon, Task-001)."""


from ui.image_manager import PLACEHOLDER_PREFIX, ImageCacheManager


class TestImageCacheManager:
    """Test ImageCacheManager poster caching and placeholder handling."""

    def test_get_poster_generates_placeholder(self):
        """Verify get_poster generates text-based placeholder for a movie."""
        manager = ImageCacheManager()
        movie_id = 123
        title = "Test Movie"

        poster = manager.get_poster(movie_id, title=title)
        assert poster.startswith(PLACEHOLDER_PREFIX)
        assert title in poster

    def test_get_poster_different_movies(self):
        """Verify different movies get different poster representations."""
        manager = ImageCacheManager()
        poster1 = manager.get_poster(1, title="Movie A")
        poster2 = manager.get_poster(2, title="Movie B")

        assert poster1 != poster2
        assert "Movie A" in poster1
        assert "Movie B" in poster2

    def test_get_poster_empty_title(self):
        """Verify empty title generates valid placeholder."""
        manager = ImageCacheManager()
        poster = manager.get_poster(999, title="")

        assert poster.startswith(PLACEHOLDER_PREFIX)
        assert "Unknown title" in poster

    def test_is_placeholder_detection(self):
        """Verify is_placeholder correctly identifies placeholder strings."""
        manager = ImageCacheManager()

        # Text-based placeholder
        placeholder = manager.get_poster(1, title="Test")
        assert manager.is_placeholder(placeholder) is True

        # Simulated real URL (future TMDB integration)
        fake_url = "https://example.com/poster.jpg"
        assert manager.is_placeholder(fake_url) is False

    def test_placeholder_prefix_constant(self):
        """Verify PLACEHOLDER_PREFIX is defined and used correctly."""
        assert PLACEHOLDER_PREFIX == "placeholder:"

        manager = ImageCacheManager()
        poster = manager.get_poster(1, title="Test")
        assert poster.startswith(PLACEHOLDER_PREFIX)


