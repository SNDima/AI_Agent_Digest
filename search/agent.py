"""
Search agent module for performing web searches using SerpAPI and OpenAI summarization.
"""

import logging
import os
from typing import List
from datetime import datetime

from langchain_community.utilities import SerpAPIWrapper
from langchain.chat_models import init_chat_model
from utils.config import load_config
from models.search_result import SearchResult
from utils.constants import SEARCH_AGENT_CONFIG_PATH


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
        search_config = self.config["search_agent"]
        params = {
            "num": search_config["results_per_query"],
            **search_config.get("serpapi_params", {})
        }
            
        self.serpapi_wrapper = SerpAPIWrapper(
            serpapi_api_key=self.serpapi_key,
            params=params
        )
    
    def search(self, query: str) -> List[SearchResult]:
        """Perform a web search for the given query."""
        logging.info(f"Searching for: {query}")
        
        try:
            # Use SerpAPI wrapper to get structured results
            results = self.serpapi_wrapper.results(query)
            
            search_results = []
            
            raw_results = results.get("news_results", [])
            
            for result in raw_results:                
                search_results.append(SearchResult(
                    title=result.get("title", ""),
                    snippet=result.get("snippet", ""),
                    source=result.get("source", ""),
                    published_date=result.get("date", ""),
                    link=result.get("link", "")
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


# to test locally
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )

    try:
        # Initialize search agent
        search_agent = SearchAgent(SEARCH_AGENT_CONFIG_PATH)
        
        # Search for "AI Agents"
        query = "AI Agents"
        results = search_agent.search(query)
        
        # Log detailed results
        logging.info(f"Search results for '{query}':")
        logging.info(f"Total results found: {len(results)}")
        
        # Sort results by published_date in descending order (newest first)
        sorted_results = sorted(results, key=lambda x: x.published_date or datetime.min, reverse=True)
        
        # Log title and posted date for each result
        for i, result in enumerate(sorted_results, 1):
            published_date_str = result.published_date.strftime("%Y-%m-%d %H:%M:%S") if result.published_date else "No date"
            logging.info(f"{i}. {result.title} - Posted: {published_date_str}")
        
    except (FileNotFoundError, ValueError) as e:
        logging.critical(str(e))
        raise
