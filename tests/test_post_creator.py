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
                mock_response.content = "<b>🤖 AI Agent Digest:</b> Exciting developments in AI agents!"
                mock_chat_model.invoke.return_value = mock_response
                mock_init_chat.return_value = mock_chat_model
                
                creator = PostCreator("test_config.yaml")
                
                articles = [
                    ScoredArticle(guid="test-guid", title="Test Article", summary="Test summary", 
                                source="Test Source", link="https://example.com", published_at=datetime.now(),
                                reasoning="Excellent AI agent content")
                ]
                
                result = creator.create_post(articles)
                
                assert "<b>🤖 AI Agent Digest:</b>" in result
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
                
                assert "<b>🤖 AI Agent Digest Update</b>" in result
                assert "2 new articles" in result
                assert "1. <a href=\"https://example.com/1\">Test Article 1</a>" in result
                assert "2. <a href=\"https://example.com/2\">Test Article 2</a>" in result
                assert "<code>Test Source 1</code>" in result
                assert "<code>Test Source 2</code>" in result
                assert "<b>Stay tuned for more AI agent developments!</b>" in result
    
    def test_fallback_post_html_formatting(self):
        """Test that fallback post generates proper HTML formatting."""
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
                    ScoredArticle(
                        guid="test-guid-1", 
                        title="AI Agent Framework Released", 
                        summary="New framework for building AI agents", 
                        source="TechCrunch", 
                        link="https://techcrunch.com/ai-agent-framework", 
                        published_at=datetime.now(),
                        reasoning="This is a groundbreaking development in AI agent technology that will enable developers to build more sophisticated autonomous systems"
                    )
                ]
                
                result = creator._create_fallback_post(articles)
                
                # Check HTML formatting elements
                assert "<b>🤖 AI Agent Digest Update</b>" in result
                assert "<i>1 new articles about AI agents and autonomous systems:</i>" in result
                assert "<a href=\"https://techcrunch.com/ai-agent-framework\">AI Agent Framework Released</a>" in result
                assert "<code>TechCrunch</code>" in result
                assert "<i>This is a groundbreaking development in AI agent technology that will enable developers to build mor...</i>" in result
                assert "<b>Stay tuned for more AI agent developments!</b> 🚀" in result

    def test_fallback_post_html_escaping(self):
        """Test that fallback post properly escapes HTML characters."""
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
                
                # Test with problematic HTML characters
                articles = [
                    ScoredArticle(
                        guid="test-guid-1", 
                        title="AI & ML: The Future of <script>alert('hack')</script> Technology", 
                        summary="Test summary", 
                        source="TechCrunch & Wired", 
                        link="https://example.com/test?param=\"value\"&other=<tag>", 
                        published_at=datetime.now(),
                        reasoning="This article discusses <b>bold</b> AI developments & future <script>dangerous</script> technologies"
                    )
                ]
                
                result = creator._create_fallback_post(articles)
                
                # Check that HTML characters are properly escaped
                assert "AI &amp; ML: The Future of &lt;script&gt;alert(&#x27;hack&#x27;)&lt;/script&gt; Technology" in result
                assert "TechCrunch &amp; Wired" in result
                # URL gets URL-encoded by Pydantic HttpUrl, then HTML-escaped
                assert "https://example.com/test?param=%22value%22&amp;other=%3Ctag%3E" in result
                assert "&lt;b&gt;bold&lt;/b&gt; AI developments &amp; future &lt;script&gt;dangerous&lt;/script&gt;" in result
                
                # Ensure no unescaped HTML characters remain
                assert "<script>" not in result
                assert "</script>" not in result
                assert "&amp;" in result  # Should be escaped as &amp;
                assert "&lt;script&gt;" in result  # Script tags should be escaped
                assert "&lt;b&gt;" in result  # HTML tags should be escaped
