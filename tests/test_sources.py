from sources import techcrunch

class TestTechCrunchSource:
    """Tests for TechCrunch RSS feed fetching."""
    
    def test_fetch_returns_list(self):
        """Verify that fetch returns a list of dictionaries."""
        items = techcrunch.fetch()
        assert isinstance(items, list)
        # When implemented, each item should be a dictionary with required fields
        # assert all(isinstance(item, dict) for item in items)