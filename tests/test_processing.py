from processing import filter

class TestContentFilter:
    """Tests for content filtering functionality."""

    def test_filter_items_preserves_structure(self):
        """Verify that filter_items maintains the input structure."""
        sample_items = [
            {"title": "AI News", "content": "Sample content"},
            {"title": "Other News", "content": "Other content"}
        ]
        filtered = filter.filter_items(sample_items)
        assert isinstance(filtered, list)
        assert all(isinstance(item, dict) for item in filtered)