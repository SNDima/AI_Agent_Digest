"""Tests for the post creator module."""

from datetime import datetime
from unittest.mock import patch, MagicMock

from processing.post_creator import PostCreator
from models.article import ScoredArticle


class TestPostCreator:
    """Test cases for PostCreator class."""
    
    def test_format_articles_for_post(self):
        """Test article formatting for post prompt."""
        with patch('processing.post_creator.load_config') as mock_load_config:
            mock_config = {
                "post_creator": {
                    "max_articles_in_post": 3,
                    "chat_model": {"model": "gpt-4.1", "model_provider": "openai", "temperature": 0.7}
                }
            }
            mock_load_config.return_value = mock_config
            
            with patch('processing.post_creator.init_chat_model'):
                creator = PostCreator("test_config.yaml")
                
                articles = [
                    ScoredArticle(
                        guid="test-guid-1",
                        title="Test Article 1",
                        summary="This is a test summary for article 1",
                        source="Test Source 1",
                        link="https://example.com/1",
                        published_at=datetime(2024, 1, 1),
                        reasoning="Highly relevant to AI agents due to direct framework discussion"
                    ),
                    ScoredArticle(
                        guid="test-guid-2",
                        title="Test Article 2",
                        summary="This is a test summary for article 2",
                        source="Test Source 2",
                        link="https://example.com/2",
                        published_at=datetime(2024, 1, 2),
                        reasoning="Moderately relevant with some AI agent applications"
                    )
                ]
                
                formatted = creator._format_articles_for_post(articles)
                
                assert "1. Test Article 1" in formatted
                assert "This is a test summary for article 1" in formatted
                assert "Source: Test Source 1" in formatted
                assert "Published: 2024-01-01 00:00" in formatted
                assert "Link: https://example.com/1" in formatted
                assert "AI Analysis: Highly relevant to AI agents due to direct framework discussion" in formatted
                assert "2. Test Article 2" in formatted
    
    def test_create_post_success(self):
        """Test successful post creation."""
        with patch('processing.post_creator.load_config') as mock_load_config:
            mock_config = {
                "post_creator": {
                    "chat_model": {"model": "gpt-4.1", "model_provider": "openai", "temperature": 0.7},
                    "max_articles_in_post": 5,
                    "post_prompt": "Create post for articles:\n{articles_text}",
                    "system_message": "You are a post creator"
                }
            }
            mock_load_config.return_value = mock_config
            
            with patch('processing.post_creator.init_chat_model') as mock_init_chat:
                mock_chat_model = MagicMock()
                mock_response = MagicMock()
                mock_response.content = "🤖 AI Agent Digest: Exciting developments in AI agents!"
                mock_chat_model.invoke.return_value = mock_response
                mock_init_chat.return_value = mock_chat_model
                
                creator = PostCreator("test_config.yaml")
                
                articles = [
                    ScoredArticle(guid="test-guid", title="Test Article", summary="Test summary", 
                                source="Test Source", link="https://example.com", published_at=datetime.now(),
                                reasoning="Excellent AI agent content")
                ]
                
                result = creator.create_post(articles)
                
                assert "🤖 AI Agent Digest" in result
                mock_chat_model.invoke.assert_called_once()
    
    def test_create_post_fallback(self):
        """Test fallback post creation when LLM fails."""
        with patch('processing.post_creator.load_config') as mock_load_config:
            mock_config = {
                "post_creator": {
                    "chat_model": {"model": "gpt-4.1", "model_provider": "openai", "temperature": 0.7},
                    "max_articles_in_post": 5,
                    "post_prompt": "Test prompt",
                    "system_message": "Test system message"
                }
            }
            mock_load_config.return_value = mock_config
            
            with patch('processing.post_creator.init_chat_model') as mock_init_chat:
                mock_chat_model = MagicMock()
                mock_chat_model.invoke.side_effect = Exception("LLM failed")
                mock_init_chat.return_value = mock_chat_model
                
                creator = PostCreator("test_config.yaml")
                
                articles = [
                    ScoredArticle(guid="test-guid-1", title="Test Article 1", summary="Test summary 1", 
                                source="Test Source 1", link="https://example.com/1", published_at=datetime.now(),
                                reasoning="High relevance for AI agents"),
                    ScoredArticle(guid="test-guid-2", title="Test Article 2", summary="Test summary 2", 
                                source="Test Source 2", link="https://example.com/2", published_at=datetime.now(),
                                reasoning="Good AI agent applications")
                ]
                
                result = creator.create_post(articles)
                
                assert "🤖 AI Agent Digest Update" in result
                assert "2 new articles" in result
                assert "1. Test Article 1" in result
                assert "2. Test Article 2" in result
                assert "https://example.com/1" in result
                assert "https://example.com/2" in result
