"""
Search agent module for performing web searches using SerpAPI and OpenAI summarization.
"""

import logging
import os
from typing import List, Optional
from datetime import datetime
from dateutil import parser as date_parser

from langchain_community.utilities import SerpAPIWrapper
from langchain.chat_models import init_chat_model
from utils.config import load_config
from models.search_result import SearchResult
from models.search_summary import SearchSummary


class SearchAgent:
    """Agent for performing web searches and generating summaries."""
    
    def __init__(self, config_path: str):
        """Initialize the search agent with configuration."""
        self.config = load_config(config_path)
        self.serpapi_key = os.getenv("SERPAPI_KEY")
        self.openai_key = os.getenv("OPENAI_API_KEY")
        
        if not self.serpapi_key:
            raise ValueError("SERPAPI_KEY environment variable is required")
        if not self.openai_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
            
        # Initialize LangChain chat model
        chat_model_config = self.config["search_agent"]["chat_model"]
        self.chat_model = init_chat_model(
            model=chat_model_config["model"],
            model_provider=chat_model_config["model_provider"],
            temperature=chat_model_config["temperature"]
        )
        
        # Initialize SerpAPI wrapper through LangChain
        self.serpapi_wrapper = SerpAPIWrapper(
            serpapi_api_key=self.serpapi_key,
            params={"num": self.config["search_agent"]["results_per_query"]}
        )
    
    def _build_search_query(self, query: str) -> str:
        """Build search query with freshness constraints."""
        freshness = self.config["search_agent"]["freshness"]
        
        # Add freshness constraint to query if specified
        if freshness == "last_24h":
            return f"{query} (past 24 hours OR today)"
        elif freshness == "last_7d":
            return f"{query} (past week OR past 7 days)"
        elif freshness == "last_30d":
            return f"{query} (past month OR past 30 days)"
        else:
            return query
    
    def _parse_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """Parse date string from SerpAPI response into datetime object."""
        if not date_str:
            return None
            
        try:
            return date_parser.parse(date_str)
        except (ValueError, TypeError):
            logging.warning(f"Could not parse published date: {date_str}")
            return None
    
    def search(self, query: str) -> List[SearchResult]:
        """Perform a web search for the given query."""
        logging.info(f"Searching for: {query}")
        
        try:
            # Build query with freshness constraints
            enhanced_query = self._build_search_query(query)
            
            # Use SerpAPI wrapper to get structured results
            results = self.serpapi_wrapper.results(enhanced_query)
            
            search_results = []
            
            # Extract organic results from SerpAPI response
            organic_results = results.get("organic_results", [])
            
            for result in organic_results:
                search_results.append(SearchResult(
                    title=result.get("title", ""),
                    snippet=result.get("snippet", ""),
                    source=result.get("source", ""),
                    published_date=self._parse_date(result.get("date"))
                ))
                
            logging.info(f"Found {len(search_results)} results for query: {query}")
            return search_results
            
        except Exception as e:
            logging.error(f"Search failed for query '{query}': {e}")
            return []
    
    def search_multiple_queries(self, queries: List[str]) -> List[SearchResult]:
        """Search for multiple queries and return combined results."""
        all_results = []
        
        for query in queries:
            results = self.search(query)
            all_results.extend(results)
            
        return all_results
    
    def summarize_results(self, results: List[SearchResult], query: str) -> str:
        """Generate a summary of search results using LangChain chat model."""
        if not results:
            return f"No results found for query: {query}"
            
        # Prepare content for summarization
        content_pieces = []
        max_results = self.config["search_agent"]["max_results_for_summary"]
        for i, result in enumerate(results[:max_results], 1):
            content_pieces.append(f"{i}. {result.title}\n   {result.snippet}\n   Source: {result.source}\n")
            
        content_text = "\n".join(content_pieces)
        
        prompt = self.config["search_agent"]["summary_prompt"].format(
            query=query,
            content_text=content_text
        )
        
        try:
            messages = [
                {"role": "system", "content": self.config["search_agent"]["system_message"]},
                {"role": "user", "content": prompt}
            ]
            
            response = self.chat_model.invoke(messages)
            summary = response.content.strip()
            
            logging.info(f"Generated summary for query: {query}")
            return summary
            
        except Exception as e:
            logging.error(f"Failed to generate summary for query '{query}': {e}")
            return f"Summary generation failed for query: {query}"
    
    def get_all_queries(self) -> List[str]:
        """Get all search queries from configuration."""
        return self.config["search_agent"]["queries"]
    
    def search_all_queries(self) -> List[SearchResult]:
        """Search for all configured queries and return combined results."""
        queries = self.get_all_queries()
        
        if not queries:
            logging.warning("No queries found in configuration")
            return []
        
        return self.search_multiple_queries(queries)
    
    def get_combined_query(self) -> str:
        """Get combined query string for all configured queries."""
        queries = self.get_all_queries()
        return " | ".join(queries) if queries else ""
    
    def summarize_all_results(self, results: List[SearchResult]) -> str:
        """Generate a summary of search results using all configured queries."""
        combined_query = self.get_combined_query()
        return self.summarize_results(results, combined_query)
