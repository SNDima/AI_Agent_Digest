import logging
from typing import List, TypedDict

from langgraph.graph import StateGraph, START, END
from dotenv import load_dotenv

from sources.loader import load_all_articles
from models.article import Article
from processing import filters
from storage import store
from delivery import telegram
from utils.constants import DATABASE_CONFIG_PATH, SOURCES_CONFIG_PATH

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
    error: str | None


def fetch_sources_node(state: DigestState) -> DigestState:
    """Fetch articles from all configured sources."""
    logging.info("Fetching sources...")
    try:
        articles = load_all_articles(SOURCES_CONFIG_PATH)
        return {
            **state,
            "articles": articles,
            "error": None
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
            
        store.save(state["articles"], DATABASE_CONFIG_PATH)
        return {
            **state,
            "error": None
        }
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
            "filtered_articles": filtered,
            "error": None
        }
    except Exception as e:
        logging.error(f"Failed to process content: {e}")
        return {
            **state,
            "filtered_articles": [],
            "error": f"Failed to process content: {e}"
        }


def deliver_digest_node(state: DigestState) -> DigestState:
    """Deliver digest via Telegram."""
    logging.info("Delivering digest...")
    try:
        if state.get("error"):
            return state
            
        telegram.send(state["filtered_articles"])
        return {
            **state,
            "error": None
        }
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
    workflow.add_node("deliver", deliver_digest_node)
    
    # Add edges
    workflow.add_edge(START, "fetch")
    workflow.add_edge("fetch", "store")
    workflow.add_edge("store", "process")
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
