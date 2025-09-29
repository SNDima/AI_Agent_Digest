from datetime import datetime, timezone

from processing.filtering import filter_top_articles
from models.article import ScoredArticle


class TestFilterTopArticles:
    """Tests for filter_top_articles function."""

    def create_scored_article(self, title, score, reasoning="Test reasoning"):
        """Create a test scored article."""
        return ScoredArticle(
            guid=f"test-guid-{title.lower().replace(' ', '-')}",
            source="Test Source",
            title=title,
            link="https://example.com/article",
            summary="Test summary",
            author="Test Author",
            categories=["AI"],
            published_at=datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
            fetched_at=datetime(2024, 1, 1, 13, 0, 0, tzinfo=timezone.utc),
            posted=False,
            relevance_score=score,
            reasoning=reasoning
        )

    def test_filter_top_articles_empty_list(self):
        """Test filtering empty article list."""
        result = filter_top_articles([])
        assert result == []

    def test_filter_top_articles_no_valid_scores(self):
        """Test filtering articles with no valid scores."""
        articles = [
            self.create_scored_article("Article 1", None),
            self.create_scored_article("Article 2", None)
        ]
        result = filter_top_articles(articles)
        assert result == []

    def test_filter_top_articles_less_than_5_high_relevance(self):
        """Test filtering when less than 5 articles have high relevance (>80)."""
        articles = [
            self.create_scored_article("High 1", 85),
            self.create_scored_article("High 2", 82),
            self.create_scored_article("Medium 1", 70),
            self.create_scored_article("Medium 2", 65),
            self.create_scored_article("Low 1", 45)
        ]
        result = filter_top_articles(articles)
        
        assert len(result) == 3
        assert result[0].relevance_score == 85
        assert result[1].relevance_score == 82
        assert result[2].relevance_score == 70

    def test_filter_top_articles_at_least_5_high_relevance(self):
        """Test filtering when at least 5 articles have high relevance (>80)."""
        articles = [
            self.create_scored_article("High 1", 95),
            self.create_scored_article("High 2", 90),
            self.create_scored_article("High 3", 85),
            self.create_scored_article("High 4", 82),
            self.create_scored_article("High 5", 81),
            self.create_scored_article("Medium 1", 70),
            self.create_scored_article("Low 1", 45)
        ]
        result = filter_top_articles(articles)
        
        assert len(result) == 5
        assert result[0].relevance_score == 95
        assert result[1].relevance_score == 90
        assert result[2].relevance_score == 85
        assert result[3].relevance_score == 82
        assert result[4].relevance_score == 81

    def test_filter_top_articles_mixed_valid_invalid_scores(self):
        """Test filtering with mix of valid and invalid scores."""
        articles = [
            self.create_scored_article("Valid 1", 85),
            self.create_scored_article("Invalid 1", None),
            self.create_scored_article("Valid 2", 70),
            self.create_scored_article("Invalid 2", None),
            self.create_scored_article("Valid 3", 60)
        ]
        result = filter_top_articles(articles)
        
        assert len(result) == 3
        assert all(article.relevance_score is not None for article in result)
        assert result[0].relevance_score == 85
        assert result[1].relevance_score == 70
        assert result[2].relevance_score == 60
