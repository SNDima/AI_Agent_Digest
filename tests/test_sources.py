import pytest
from sources.loader import load_all_articles

CONFIG_PATH = "config/sources.yaml"


class TestSources:
    """Tests for loading articles from sources defined in the config."""

    def test_fetch_returns_list(self):
        """Verify that load_all_articles returns a list of dictionaries."""
        items = load_all_articles(CONFIG_PATH)
        assert isinstance(items, list)
        assert all(isinstance(item, dict) for item in items)

    def test_items_have_required_keys(self):
        """Check that each fetched item has the expected fields."""
        items = load_all_articles(CONFIG_PATH)
        required_keys = {"guid", "title", "link", "published", "summary", "author", "categories"}
        for item in items:
            assert required_keys.issubset(item.keys())

    def test_categories_are_list(self):
        """Verify that categories field is always a list."""
        items = load_all_articles(CONFIG_PATH)
        for item in items:
            assert isinstance(item["categories"], list)


class TestConfigValidation:
    """Negative tests for config validation."""

    def test_missing_file_raises(self, tmp_path):
        """Ensure FileNotFoundError is raised when config file does not exist."""
        fake_config = tmp_path / "no_file.yaml"
        with pytest.raises(FileNotFoundError):
            load_all_articles(str(fake_config))

    def test_empty_sources_raises(self, tmp_path):
        """Ensure ValueError is raised when 'sources' is empty."""
        bad_config = tmp_path / "bad_config.yaml"
        bad_config.write_text("sources: []")
        with pytest.raises(ValueError, match="must be a non-empty list"):
            load_all_articles(str(bad_config))

    def test_no_enabled_sources_raises(self, tmp_path):
        """Ensure ValueError is raised when no source is enabled."""
        bad_config = tmp_path / "disabled_sources.yaml"
        bad_config.write_text(
            """
            sources:
              - name: TechCrunch
                type: rss
                url: "https://techcrunch.com/category/artificial-intelligence/feed/"
                enabled: false
            """
        )
        with pytest.raises(ValueError, match="at least one source must be enabled"):
            load_all_articles(str(bad_config))
