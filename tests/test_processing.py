from processing import filters
from models.article import Article
from datetime import datetime

class TestContentFilter:
    """Tests for content filtering functionality."""

    def test_filter_items_preserves_structure(self):
        """Verify that filter_items maintains the input structure."""
        sample_items = [
            Article(
                guid="test1",
                source="test",
                title="AI News",
                link="https://example.com/1",
                summary="Sample content"
            ),
            Article(
                guid="test2",
                source="test",
                title="Other News",
                link="https://example.com/2",
                summary="Other content"
            )
        ]
        filtered = filters.filter_items(sample_items)
        assert isinstance(filtered, list)
        assert all(isinstance(item, Article) for item in filtered)
        assert len(filtered) == 2
        assert filtered[0].title == "AI News"
        assert filtered[1].title == "Other News"