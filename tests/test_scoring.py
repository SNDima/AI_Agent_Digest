import os
import yaml
from datetime import datetime, timezone
from unittest.mock import patch, MagicMock

from processing.scoring import RelevanceScorer
from models.article import Article, ScoredArticle


class TestRelevanceScorer:
    """Tests for RelevanceScorer class."""

    def create_test_config(self, tmp_path):
        """Create a test scoring configuration file."""
        config_data = {
            "scoring": {
                "chat_model": {
                    "model": "gpt-4",
                    "model_provider": "openai",
                    "temperature": 0.1
                },
                "scoring_prompt": "Score this article: {title} - {summary}",
                "system_message": "You are an AI content curator."
            }
        }
        
        config_file = tmp_path / "scoring_config.yaml"
        config_file.write_text(yaml.dump(config_data))
        return str(config_file)

    def create_test_article(self):
        """Create a test article for scoring."""
        return Article(
            guid="test-guid-123",
            source="Test Source",
            title="AI Agents in Modern Applications",
            link="https://example.com/article",
            summary="This article discusses the role of AI agents in modern software applications.",
            author="Test Author",
            categories=["AI", "Technology"],
            published_at=datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
            fetched_at=datetime(2024, 1, 1, 13, 0, 0, tzinfo=timezone.utc),
            posted=False
        )

    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"})
    @patch('processing.scoring.init_chat_model')
    def test_score_article_success(self, mock_init_chat_model, tmp_path):
        """Test successful article scoring."""
        config_path = self.create_test_config(tmp_path)
        mock_chat_model = MagicMock()
        mock_structured_model = MagicMock()
        mock_chat_model.with_structured_output.return_value = mock_structured_model
        mock_init_chat_model.return_value = mock_chat_model
        
        # Mock the structured response
        mock_response = MagicMock()
        mock_response.score = 85
        mock_response.reasoning = "High relevance to AI agents"
        mock_structured_model.invoke.return_value = mock_response
        
        scorer = RelevanceScorer(config_path)
        article = self.create_test_article()
        
        score, reasoning = scorer._score_article(article)
        
        assert score == 85
        assert reasoning == "High relevance to AI agents"

    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"})
    @patch('processing.scoring.init_chat_model')
    def test_score_article_exception(self, mock_init_chat_model, tmp_path):
        """Test article scoring with exception."""
        config_path = self.create_test_config(tmp_path)
        mock_chat_model = MagicMock()
        mock_structured_model = MagicMock()
        mock_chat_model.with_structured_output.return_value = mock_structured_model
        mock_init_chat_model.return_value = mock_chat_model
        
        # Mock exception during scoring
        mock_structured_model.invoke.side_effect = Exception("LLM API error")
        
        scorer = RelevanceScorer(config_path)
        article = self.create_test_article()
        
        score, reasoning = scorer._score_article(article)
        
        assert score is None
        assert reasoning is None

    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"})
    @patch('processing.scoring.init_chat_model')
    def test_score_articles_success(self, mock_init_chat_model, tmp_path):
        """Test scoring multiple articles successfully."""
        config_path = self.create_test_config(tmp_path)
        mock_chat_model = MagicMock()
        mock_structured_model = MagicMock()
        mock_chat_model.with_structured_output.return_value = mock_structured_model
        mock_init_chat_model.return_value = mock_chat_model
        
        # Mock responses for multiple articles
        mock_responses = [
            MagicMock(score=85, reasoning="High relevance"),
            MagicMock(score=70, reasoning="Moderate relevance")
        ]
        mock_structured_model.invoke.side_effect = mock_responses
        
        scorer = RelevanceScorer(config_path)
        articles = [self.create_test_article(), self.create_test_article()]
        
        scored_articles = scorer.score_articles(articles)
        
        assert len(scored_articles) == 2
        assert all(isinstance(article, ScoredArticle) for article in scored_articles)
        assert scored_articles[0].relevance_score == 85
        assert scored_articles[1].relevance_score == 70
