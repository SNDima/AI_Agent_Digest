import logging
from typing import List, TypedDict

from langgraph.graph import StateGraph, START, END
from dotenv import load_dotenv

from sources.loader import load_all_articles
from models.article import Article
from models.search_summary import SearchSummary
from processing import scoring
from processing.filtering import filter_top_articles
from processing.post_creator import PostCreator
from storage import article_storage
from storage.article_storage import get_articles_after, update_relevance_scores
from delivery import telegram
from search.agent import SearchAgent
from storage.summary_storage import save_search_summary
from storage.search_result_storage import save_search_results
from storage.delivery_storage import save_delivery, get_latest_delivery
from models.delivery import Delivery
from utils.constants import DATABASE_CONFIG_PATH, SOURCES_CONFIG_PATH, SEARCH_AGENT_CONFIG_PATH, DELIVERY_CONFIG_PATH, POST_CREATOR_CONFIG_PATH
from utils.config import load_config
from utils.time_utils import should_run_delivery, parse_articles_freshness

# Load environment variables
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(module)s:%(funcName)s:%(lineno)d - %(message)s"
)


# Define the state for our workflow
class DigestState(TypedDict):
    error: str | None


def fetch_articles_node(state: DigestState) -> DigestState:
    """Fetch articles from all configured sources and store them to database."""
    logging.info("Fetching and storing articles...")
    try:
        # Fetch articles from all sources
        articles = load_all_articles(SOURCES_CONFIG_PATH)
        
        # Store articles to database
        article_storage.save(articles, DATABASE_CONFIG_PATH)
        
        return state
    except Exception as e:
        logging.error(f"Failed to fetch and store articles: {e}")
        return {
            **state,
            "error": f"Failed to fetch and store articles: {e}"
        }


def delivery_condition_router(state: DigestState) -> str:
    """Conditional function to determine if delivery should run."""
    try:
        if state.get("error"):
            return "END"
            
        # Load delivery config to get the delivery time
        delivery_config = load_config(DELIVERY_CONFIG_PATH)
        delivery_time_utc = delivery_config["delivery"]["delivery_time_utc"]
        
        # Fetch the last delivery to check timing
        latest_delivery = get_latest_delivery(DATABASE_CONFIG_PATH)
        last_datetime = latest_delivery.delivered_at if latest_delivery else None
        
        if should_run_delivery(last_datetime, delivery_time_utc):
            return "deliver"
        else:
            return "END"
        
    except Exception as e:
        logging.error(f"Failed to check delivery conditions: {e}")
        return "END"


def _get_fresh_articles() -> List[Article]:
    """Private function to get fresh articles based on articles_freshness config."""
    logging.info("Getting fresh articles...")
    delivery_config = load_config(DELIVERY_CONFIG_PATH)
    articles_freshness = delivery_config["delivery"]["articles_freshness"]
    cutoff_datetime = parse_articles_freshness(articles_freshness)
    
    fresh_articles = get_articles_after(DATABASE_CONFIG_PATH, cutoff_datetime)
    
    return fresh_articles


def _make_summary() -> str | None:
    """Private function to create and save a new summary."""
    logging.info("Making new summary...")
    try:
        # Search for AI agent news
        search_agent = SearchAgent(SEARCH_AGENT_CONFIG_PATH)
        search_results = search_agent.search_all_queries()
        
        if not search_results:
            logging.warning("No search results found")
            return None
        
        # Save search results to database
        logging.info(f"Saving {len(search_results)} search results to database...")
        save_search_results(search_results, DATABASE_CONFIG_PATH)
        
        # Summarize search results
        summary_text = search_agent.summarize_all_results(search_results)
        
        if not summary_text:
            logging.warning("No summary generated")
            return None
        
        # Save summary to database
        search_summary = SearchSummary(summary_text=summary_text)
        save_search_summary(search_summary, DATABASE_CONFIG_PATH)
        
        logging.info("New summary made and saved successfully")
        return summary_text
    except Exception as e:
        logging.error(f"Failed to make new summary: {e}")
        return None


def deliver_digest_node(state: DigestState) -> DigestState:
    """Score articles, make summary, and deliver digest via Telegram."""
    logging.info("Processing and delivering digest...")
    try:
        if state.get("error"):
            return state
        
        # Step 1: Make summary using private function
        summary_text = _make_summary()
        if not summary_text:
            return state

        # Step 2: Get fresh articles based on articles_freshness
        fresh_articles = _get_fresh_articles()
        logging.info(f"Found {len(fresh_articles)} fresh articles")
        
        # Step 3: Score articles for relevance
        logging.info("Scoring content...")
        scored_articles = scoring.assign_relevance_score(fresh_articles, summary_text)
        
        # Step 4: Save relevance scores to database
        logging.info("Saving relevance scores to database...")
        update_relevance_scores(scored_articles, DATABASE_CONFIG_PATH)
        
        # Step 5: Filter and select top articles
        top_articles = filter_top_articles(scored_articles)
        
        # Step 6: Create engaging post using LLM
        logging.info("Creating social media post...")
        post_creator = PostCreator(POST_CREATOR_CONFIG_PATH)
        post_text = post_creator.create_post(top_articles)
        
        # Step 7: Deliver digest via Telegram
        logging.info("Delivering digest...")
        message_id = telegram.send(post_text)
        
        # Step 8: Save delivery record
        delivery = Delivery(content=post_text, origin_message_id=str(message_id))
        save_delivery(delivery, DATABASE_CONFIG_PATH)
        
        return state
    except Exception as e:
        logging.error(f"Failed to process and deliver digest: {e}")
        return {
            **state,
            "error": f"Failed to process and deliver digest: {e}"
        }


def _create_digest_workflow() -> StateGraph:
    """Create the LangGraph workflow for the digest pipeline."""
    workflow = StateGraph(DigestState)
    
    # Add nodes
    workflow.add_node("fetch_articles", fetch_articles_node)
    workflow.add_node("deliver", deliver_digest_node)
    
    # Add edges
    workflow.add_edge(START, "fetch_articles")
    
    # Conditional edge: fetch_articles -> deliver OR END
    workflow.add_conditional_edges(
        "fetch_articles",
        delivery_condition_router,
        {
            "deliver": "deliver",
            "END": END
        }
    )
    
    workflow.add_edge("deliver", END)
    
    return workflow.compile()


def main() -> None:
    logging.info("AI Agent Digest started")

    try:
        # Create and run the workflow with LangSmith tracing
        workflow = _create_digest_workflow()
        
        # Initialize state
        initial_state = DigestState(
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
