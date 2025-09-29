import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime
from search.agent import SearchAgent
from models.search_result import SearchResult


class TestSearchAgent:
    """Tests for SearchAgent functionality."""

    @pytest.fixture
    def mock_config(self):
        """Mock configuration for SearchAgent."""
        return {
            "search_agent": {
                "freshness": "last_24h",
                "results_per_query": 5,
                "max_results_for_summary": 25,
                "chat_model": {
                    "model": "gpt-4.1",
                    "model_provider": "openai",
                    "temperature": 0.3
                },
                "summary_prompt": "Test prompt: {query}\n{content_text}",
                "system_message": "Test system message",
                "queries": ["AI Agents", "LangChain agents"]
            }
        }

    @patch.dict('os.environ', {'SERPAPI_KEY': 'test_key', 'OPENAI_API_KEY': 'test_openai_key'})
    @patch('search.agent.load_config')
    @patch('search.agent.init_chat_model')
    @patch('search.agent.SerpAPIWrapper')
    def test_search_success(self, mock_serpapi_wrapper, mock_chat_model, mock_load_config, mock_config):
        """Test successful search with valid results."""
        # Setup mocks
        mock_load_config.return_value = mock_config
        mock_serpapi_instance = MagicMock()
        mock_serpapi_instance.results.return_value = {
            "organic_results": [
                {
                    "title": "AI Agents Revolutionize Software Development",
                    "snippet": "New AI agents are transforming how developers build applications...",
                    "source": "techcrunch.com",
                    "date": "2024-01-15"
                }
            ]
        }
        mock_serpapi_wrapper.return_value = mock_serpapi_instance
        
        # Create SearchAgent instance
        agent = SearchAgent("dummy_config.yaml")
        
        # Perform search
        results = agent.search("AI agents")
        
        # Verify results
        assert len(results) == 1
        assert isinstance(results[0], SearchResult)
        assert results[0].title == "AI Agents Revolutionize Software Development"
        assert results[0].snippet == "New AI agents are transforming how developers build applications..."
        assert results[0].source == "techcrunch.com"
        assert isinstance(results[0].published_date, datetime)

    @patch.dict('os.environ', {'SERPAPI_KEY': 'test_key', 'OPENAI_API_KEY': 'test_openai_key'})
    @patch('search.agent.load_config')
    @patch('search.agent.init_chat_model')
    @patch('search.agent.SerpAPIWrapper')
    def test_search_empty_results(self, mock_serpapi_wrapper, mock_chat_model, mock_load_config, mock_config):
        """Test search with empty results."""
        # Setup mocks
        mock_load_config.return_value = mock_config
        mock_serpapi_instance = MagicMock()
        mock_serpapi_instance.results.return_value = {"organic_results": []}
        mock_serpapi_wrapper.return_value = mock_serpapi_instance
        
        # Create SearchAgent instance
        agent = SearchAgent("dummy_config.yaml")
        
        # Perform search
        results = agent.search("nonexistent query")
        
        # Verify empty results
        assert results == []

    @patch.dict('os.environ', {'SERPAPI_KEY': 'test_key', 'OPENAI_API_KEY': 'test_openai_key'})
    @patch('search.agent.load_config')
    @patch('search.agent.init_chat_model')
    @patch('search.agent.SerpAPIWrapper')
    def test_search_serpapi_exception(self, mock_serpapi_wrapper, mock_chat_model, mock_load_config, mock_config):
        """Test search when SerpAPI raises an exception."""
        # Setup mocks
        mock_load_config.return_value = mock_config
        mock_serpapi_instance = MagicMock()
        mock_serpapi_instance.results.side_effect = Exception("SerpAPI error")
        mock_serpapi_wrapper.return_value = mock_serpapi_instance
        
        # Create SearchAgent instance
        agent = SearchAgent("dummy_config.yaml")
        
        # Perform search
        results = agent.search("test query")
        
        # Verify empty results on exception
        assert results == []

    @patch.dict('os.environ', {'SERPAPI_KEY': 'test_key', 'OPENAI_API_KEY': 'test_openai_key'})
    @patch('search.agent.load_config')
    @patch('search.agent.init_chat_model')
    @patch('search.agent.SerpAPIWrapper')
    def test_summarize_results_success(self, mock_serpapi_wrapper, mock_chat_model, mock_load_config, mock_config):
        """Test successful summary generation."""
        # Setup mocks
        mock_load_config.return_value = mock_config
        mock_chat_instance = MagicMock()
        mock_chat_instance.invoke.return_value = MagicMock(content="Generated summary of AI agents")
        mock_chat_model.return_value = mock_chat_instance
        mock_serpapi_wrapper.return_value = MagicMock()
        
        # Create SearchAgent instance
        agent = SearchAgent("dummy_config.yaml")
        
        # Create test results
        results = [
            SearchResult(
                title="AI Agents Guide",
                snippet="Comprehensive guide to AI agents",
                source="example.com",
                published_date=None
            )
        ]
        
        # Generate summary
        summary = agent.summarize_results(results, "AI agents")
        
        # Verify summary
        assert summary == "Generated summary of AI agents"
        mock_chat_instance.invoke.assert_called_once()

    @patch.dict('os.environ', {'SERPAPI_KEY': 'test_key', 'OPENAI_API_KEY': 'test_openai_key'})
    @patch('search.agent.load_config')
    @patch('search.agent.init_chat_model')
    @patch('search.agent.SerpAPIWrapper')
    def test_summarize_results_empty(self, mock_serpapi_wrapper, mock_chat_model, mock_load_config, mock_config):
        """Test summary generation with empty results."""
        # Setup mocks
        mock_load_config.return_value = mock_config
        mock_chat_model.return_value = MagicMock()
        mock_serpapi_wrapper.return_value = MagicMock()
        
        # Create SearchAgent instance
        agent = SearchAgent("dummy_config.yaml")
        
        # Generate summary with empty results
        summary = agent.summarize_results([], "AI agents")
        
        # Verify no summary message
        assert summary == "No results found for query: AI agents"

    @patch.dict('os.environ', {'SERPAPI_KEY': 'test_key', 'OPENAI_API_KEY': 'test_openai_key'})
    @patch('search.agent.load_config')
    @patch('search.agent.init_chat_model')
    @patch('search.agent.SerpAPIWrapper')
    def test_summarize_results_exception(self, mock_serpapi_wrapper, mock_chat_model, mock_load_config, mock_config):
        """Test summary generation when chat model raises an exception."""
        # Setup mocks
        mock_load_config.return_value = mock_config
        mock_chat_instance = MagicMock()
        mock_chat_instance.invoke.side_effect = Exception("Chat model error")
        mock_chat_model.return_value = mock_chat_instance
        mock_serpapi_wrapper.return_value = MagicMock()
        
        # Create SearchAgent instance
        agent = SearchAgent("dummy_config.yaml")
        
        # Create test results
        results = [
            SearchResult(
                title="AI Agents Guide",
                snippet="Comprehensive guide to AI agents",
                source="example.com",
                published_date=None
            )
        ]
        
        # Generate summary
        summary = agent.summarize_results(results, "AI agents")
        
        # Verify error handling
        assert summary == "Summary generation failed for query: AI agents"

    @patch.dict('os.environ', {'SERPAPI_KEY': 'test_key', 'OPENAI_API_KEY': 'test_openai_key'})
    @patch('search.agent.load_config')
    @patch('search.agent.init_chat_model')
    @patch('search.agent.SerpAPIWrapper')
    def test_get_combined_query(self, mock_serpapi_wrapper, mock_chat_model, mock_load_config, mock_config):
        """Test getting combined query string from configuration."""
        # Setup mocks
        mock_load_config.return_value = mock_config
        mock_chat_model.return_value = MagicMock()
        mock_serpapi_wrapper.return_value = MagicMock()
        
        # Create SearchAgent instance
        agent = SearchAgent("dummy_config.yaml")
        
        # Get combined query
        combined_query = agent.get_combined_query()
        
        # Verify combined query
        assert combined_query == "AI Agents | LangChain agents"

    @patch.dict('os.environ', {'SERPAPI_KEY': 'test_key', 'OPENAI_API_KEY': 'test_openai_key'})
    @patch('search.agent.load_config')
    @patch('search.agent.init_chat_model')
    @patch('search.agent.SerpAPIWrapper')
    def test_search_google_news_engine(self, mock_serpapi_wrapper, mock_chat_model, mock_load_config, mock_config):
        """Test search with Google News engine using news_results format."""
        # Setup mocks with Google News engine config
        google_news_config = mock_config.copy()
        google_news_config["search_agent"]["engine"] = "google_news"
        mock_load_config.return_value = google_news_config
        mock_serpapi_instance = MagicMock()
        mock_serpapi_instance.results.return_value = {
            "news_results": [
                {
                    "title": "Breaking: AI Agents Transform News Industry",
                    "snippet": "Latest developments in AI agent technology...",
                    "source": "reuters.com",
                    "date": "2024-01-15"
                }
            ]
        }
        mock_serpapi_wrapper.return_value = mock_serpapi_instance
        
        # Create SearchAgent instance
        agent = SearchAgent("dummy_config.yaml")
        
        # Perform search
        results = agent.search("AI agents")
        
        # Verify results
        assert len(results) == 1
        assert isinstance(results[0], SearchResult)
        assert results[0].title == "Breaking: AI Agents Transform News Industry"
        assert results[0].snippet == "Latest developments in AI agent technology..."
        assert results[0].source == "reuters.com"
        assert isinstance(results[0].published_date, datetime)
        
        # Verify SerpAPIWrapper was called with engine parameter
        mock_serpapi_wrapper.assert_called_once()
        call_args = mock_serpapi_wrapper.call_args
        assert call_args[1]["params"]["engine"] == "google_news"
        assert call_args[1]["params"]["num"] == 5