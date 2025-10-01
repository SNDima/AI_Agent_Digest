import logging
import os
from typing import List, Optional
from pydantic import BaseModel, Field
from langchain.chat_models import init_chat_model
from utils.config import load_config
from utils.constants import SCORING_CONFIG_PATH
from models.article import Article, ScoredArticle


class RelevanceScore(BaseModel):
    """Structured output model for article relevance scoring."""
    score: int = Field(..., description="Relevance score from 1-100", ge=1, le=100)
    reasoning: str = Field(..., description="Brief explanation for the score")


class RelevanceScorer:
    """Scorer for evaluating article relevance to AI agent content using LLM."""
    
    def __init__(self, config_path: str):
        """Initialize the relevance scorer with configuration."""
        self.config = load_config(config_path)
        self.openai_key = os.getenv("OPENAI_API_KEY")
        
        if not self.openai_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
            
        # Initialize LangChain chat model for scoring
        scoring_config = self.config["scoring"]
        chat_model_config = scoring_config["llm"]
        self.chat_model = init_chat_model(
            model=chat_model_config["model"],
            model_provider=chat_model_config["model_provider"],
            temperature=chat_model_config["temperature"]
        )
        
        # Configure structured output
        self.structured_model = self.chat_model.with_structured_output(RelevanceScore)
        
        self.scoring_prompt = scoring_config["scoring_prompt"]
        self.system_message = scoring_config["system_message"]
    
    
    def _score_article(self, article: Article) -> tuple[Optional[int], Optional[str]]:
        """Score a single article for relevance to AI agent content."""
        try:
            # Prepare article data for scoring
            article_data = {
                "title": article.title,
                "summary": article.summary or "No summary available",
                "source": article.source,
                "published_at": article.published_at.strftime("%Y-%m-%d %H:%M:%S") if article.published_at else "Unknown"
            }
            
            # Format the scoring prompt
            prompt = self.scoring_prompt.format(**article_data)
            
            # Get structured score from LLM
            messages = [
                {"role": "system", "content": self.system_message},
                {"role": "user", "content": prompt}
            ]
            
            response = self.structured_model.invoke(messages)
            
            if response and hasattr(response, 'score'):
                score = response.score
                reasoning = getattr(response, 'reasoning', 'No reasoning provided')
                logging.debug(f"Scored article '{article.title}' with score: {score} - {reasoning}")
                return score, reasoning
            else:
                logging.warning(f"Failed to get valid structured response for article '{article.title}'")
                return None, None
                
        except Exception as e:
            logging.error(f"Failed to score article '{article.title}': {e}")
            return None, None
    
    def score_articles(self, articles: List[Article]) -> List[ScoredArticle]:
        """Score multiple articles for relevance to AI agent content."""
        logging.info(f"Scoring {len(articles)} articles for relevance...")
        
        scored_articles = []
        skipped_count = 0
        
        for article in articles:
            # Skip articles that already have a relevance score
            if article.relevance_score is not None:
                logging.debug(f"Skipping article '{article.title}' - already scored with score: {article.relevance_score}")
                skipped_count += 1
                
                # Convert existing Article to ScoredArticle preserving existing score
                scored_article = ScoredArticle(
                    guid=article.guid,
                    source=article.source,
                    title=article.title,
                    link=article.link,
                    summary=article.summary,
                    author=article.author,
                    categories=article.categories,
                    published_at=article.published_at,
                    fetched_at=article.fetched_at,
                    posted=article.posted,
                    relevance_score=article.relevance_score,
                    reasoning=getattr(article, 'reasoning', None)  # Preserve existing reasoning if available
                )
                scored_articles.append(scored_article)
                continue
            
            score, reasoning = self._score_article(article)
            
            # Create a ScoredArticle with the relevance score and reasoning
            scored_article = ScoredArticle(
                guid=article.guid,
                source=article.source,
                title=article.title,
                link=article.link,
                summary=article.summary,
                author=article.author,
                categories=article.categories,
                published_at=article.published_at,
                fetched_at=article.fetched_at,
                posted=article.posted,
                relevance_score=score,
                reasoning=reasoning
            )
            scored_articles.append(scored_article)
        
        # Log scoring statistics
        valid_scores = [a.relevance_score for a in scored_articles if a.relevance_score is not None]
        if valid_scores:
            avg_score = sum(valid_scores) / len(valid_scores)
            high_relevance = len([s for s in valid_scores if s >= 70])
            high_relevance_percentage = high_relevance / len(valid_scores) * 100
            logging.info(f"Scoring complete. Processed: {len(articles)}, Skipped: {skipped_count}, New scores: {len(valid_scores) - skipped_count}. Average score: {avg_score:.1f}, High relevance (70+): {high_relevance_percentage:.1f}%")
        else:
            logging.warning("No valid scores generated")
            
        return scored_articles


def assign_relevance_score(articles: List[Article], relevance_text: str) -> List[ScoredArticle]:
    """
    Calculate relevance scores for AI Agent content using LLM-based scoring.
    
    Args:
        articles: List of articles to score
        relevance_text: Summary text used as context for scoring (currently unused but kept for compatibility)
        
    Returns:
        List of ScoredArticle objects with relevance_score and reasoning fields populated
    """
    try:
        # Initialize scorer with scoring config
        scorer = RelevanceScorer(SCORING_CONFIG_PATH)
        
        # Score all articles
        return scorer.score_articles(articles)
        
    except Exception as e:
        logging.error(f"Failed to assign relevance scores: {e}")
        # Raise the exception instead of returning articles unchanged
        raise e
