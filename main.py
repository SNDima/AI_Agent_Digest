import logging
from typing import List, TypedDict
from datetime import datetime, time, timezone

from langgraph.graph import StateGraph, START, END
from dotenv import load_dotenv

from sources.loader import load_all_articles
from models.article import Article
from models.search_result import SearchResult
from models.search_summary import SearchSummary
from processing import filters
from storage import article_storage
from delivery import telegram
from search.agent import SearchAgent
from storage.summary_storage import save_search_summary, get_latest_search_summary
from utils.constants import DATABASE_CONFIG_PATH, SOURCES_CONFIG_PATH, SEARCH_AGENT_CONFIG_PATH
from utils.config import load_config
from utils.time_utils import should_run_search

# Load environment variables
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(module)s:%(funcName)s:%(lineno)d - %(message)s"
)


# Define the state for our workflow
class DigestState(TypedDict):
    articles: List[Article]
    filtered_articles: List[Article]
    last_summary_datetime: datetime | None
    search_results: List[SearchResult]
    search_summary: str | None
    error: str | None


def fetch_sources_node(state: DigestState) -> DigestState:
    """Fetch articles from all configured sources."""
    logging.info("Fetching sources...")
    try:
        articles = load_all_articles(SOURCES_CONFIG_PATH)
        return {
            **state,
            "articles": articles
        }
    except Exception as e:
        logging.error(f"Failed to fetch sources: {e}")
        return {
            **state,
            "articles": [],
            "error": f"Failed to fetch sources: {e}"
        }


def store_content_node(state: DigestState) -> DigestState:
    """Store raw articles to database."""
    logging.info("Storing content...")
    try:
        if state.get("error"):
            return state
            
        article_storage.save(state["articles"], DATABASE_CONFIG_PATH)
        return state
    except Exception as e:
        logging.error(f"Failed to store content: {e}")
        return {
            **state,
            "error": f"Failed to store content: {e}"
        }


def process_content_node(state: DigestState) -> DigestState:
    """Process and filter articles."""
    logging.info("Processing content...")
    try:
        if state.get("error"):
            return state
            
        filtered = filters.filter_items(state["articles"])
        return {
            **state,
            "filtered_articles": filtered
        }
    except Exception as e:
        logging.error(f"Failed to process content: {e}")
        return {
            **state,
            "filtered_articles": [],
            "error": f"Failed to process content: {e}"
        }


def fetch_last_summary_node(state: DigestState) -> DigestState:
    """Fetch the last search summary data and populate state."""
    logging.info("Fetching last search summary data...")
    
    if state.get("error"):
        return state
        
    latest_summary = get_latest_search_summary(DATABASE_CONFIG_PATH)
    
    if not latest_summary:
        logging.info("No previous search summary found")
        return state
    
    last_datetime = latest_summary.fetched_at
    logging.info(f"Found last summary from {last_datetime}")
        
    return {
        **state,
        "last_summary_datetime": last_datetime
    }


def search_condition_router(state: DigestState) -> str:
    """Conditional function to determine if search should run."""
    try:
        if state.get("error"):
            return "process"
            
        # Load search agent config to get the search time
        search_config = load_config(SEARCH_AGENT_CONFIG_PATH)
        search_time_utc = search_config["search_agent"]["search_time_utc"]
        
        # Check if search should run
        last_datetime = state.get("last_summary_datetime")
        if should_run_search(last_datetime, search_time_utc):
            return "search"
        else:
            return "process"
        
    except Exception as e:
        logging.error(f"Failed to check search conditions: {e}")
        return "process"


def search_node(state: DigestState) -> DigestState:
    """Search for AI agent news."""
    logging.info("Searching for AI agent news...")
    try:
        if state.get("error"):
            return state
            
        search_agent = SearchAgent(SEARCH_AGENT_CONFIG_PATH)
        search_results = search_agent.search_all_queries()
        
        return {
            **state,
            "search_results": search_results
        }
    except Exception as e:
        logging.error(f"Failed to search: {e}")
        return {
            **state,
            "search_results": [],
            "error": f"Failed to search: {e}"
        }


def summarize_node(state: DigestState) -> DigestState:
    """Summarize search results."""
    logging.info("Summarizing search results...")
    try:
        if state.get("error"):
            return state
            
        search_results = state.get("search_results", [])
        if not search_results:
            logging.warning("No search results to summarize")
            return state
        
        search_agent = SearchAgent(SEARCH_AGENT_CONFIG_PATH)
        summary_text = search_agent.summarize_all_results(search_results)
        
        return {
            **state,
            "search_summary": summary_text
        }
    except Exception as e:
        logging.error(f"Failed to summarize: {e}")
        return {
            **state,
            "error": f"Failed to summarize: {e}"
        }


def save_summary_node(state: DigestState) -> DigestState:
    """Save search summary to database."""
    logging.info("Saving search summary...")
    try:
        if state.get("error"):
            return state
            
        summary_text = state.get("search_summary")
        if not summary_text:
            logging.warning("No summary to save")
            return state
        
        # Create and save the summary
        search_summary = SearchSummary(summary_text=summary_text)
        save_search_summary(search_summary, DATABASE_CONFIG_PATH)
        
        logging.info("Search summary saved successfully")
        return state
    except Exception as e:
        logging.error(f"Failed to save summary: {e}")
        return {
            **state,
            "error": f"Failed to save summary: {e}"
        }


def deliver_digest_node(state: DigestState) -> DigestState:
    """Deliver digest via Telegram."""
    logging.info("Delivering digest...")
    try:
        if state.get("error"):
            return state
            
        telegram.send(state["filtered_articles"])
        return state
    except Exception as e:
        logging.error(f"Failed to deliver digest: {e}")
        return {
            **state,
            "error": f"Failed to deliver digest: {e}"
        }


def create_digest_workflow() -> StateGraph:
    """Create the LangGraph workflow for the digest pipeline."""
    workflow = StateGraph(DigestState)
    
    # Add nodes
    workflow.add_node("fetch", fetch_sources_node)
    workflow.add_node("store", store_content_node)
    workflow.add_node("process", process_content_node)
    workflow.add_node("fetch_summary", fetch_last_summary_node)
    workflow.add_node("search", search_node)
    workflow.add_node("summarize", summarize_node)
    workflow.add_node("save_summary", save_summary_node)
    workflow.add_node("deliver", deliver_digest_node)
    
    # Add edges
    workflow.add_edge(START, "fetch")
    workflow.add_edge("fetch", "store")
    workflow.add_edge("store", "fetch_summary")
    
    # Conditional edge: fetch_summary -> search OR process
    workflow.add_conditional_edges(
        "fetch_summary",
        search_condition_router,
        {
            "search": "search",
            "process": "process"
        }
    )
    
    workflow.add_edge("search", "summarize")
    workflow.add_edge("summarize", "save_summary")
    workflow.add_edge("save_summary", "process")
    workflow.add_edge("process", "deliver")
    workflow.add_edge("deliver", END)
    
    return workflow.compile()


def main() -> None:
    logging.info("AI Agent Digest started")

    try:
        # Create and run the workflow with LangSmith tracing
        workflow = create_digest_workflow()
        
        # Initialize state
        initial_state = DigestState(
            articles=[],
            filtered_articles=[],
            last_summary_datetime=None,
            search_results=[],
            search_summary=None,
            error=None
        )
        
        # Run the workflow
        result = workflow.invoke(initial_state)
        
        # Check for errors
        if result.get("error"):
            logging.error(f"Pipeline failed: {result['error']}")
            raise Exception(result["error"])
            
    except Exception as e:
        logging.error(f"Pipeline failed: {e}", exc_info=True)
        raise  # re-raise to stop execution

    logging.info("AI Agent Digest finished")


if __name__ == "__main__":
    main()
