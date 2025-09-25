from processing import filters

class TestContentFilter:
    """Tests for content filtering functionality."""

    def test_filter_items_preserves_structure(self):
        """Verify that filter_items maintains the input structure."""
        sample_items = [
            {"title": "AI News", "content": "Sample content"},
            {"title": "Other News", "content": "Other content"}
        ]
        filtered = filters.filter_items(sample_items)
        assert isinstance(filtered, list)
        assert all(isinstance(item, dict) for item in filtered)