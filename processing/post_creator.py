"""
Post creator module for generating engaging social media posts from articles.
"""

import html
import logging
from typing import List
from langchain.chat_models import init_chat_model
from utils.config import load_config
from models.article import Article


class PostCreator:
    """Creates engaging social media posts from articles using LLM."""
    
    def __init__(self, config_path: str):
        """Initialize the post creator with configuration."""
        self.config = load_config(config_path)
        
        # Initialize LangChain chat model
        chat_model_config = self.config["post_creator"]["llm"]
        self.chat_model = init_chat_model(
            model=chat_model_config["model"],
            model_provider=chat_model_config["model_provider"],
            temperature=chat_model_config["temperature"]
        )
    
    def _format_articles_for_post(self, articles: List[Article]) -> str:
        """Format articles for inclusion in the post prompt."""
        max_articles = self.config["post_creator"]["max_articles_in_post"]
        articles_to_include = articles[:max_articles]
        
        formatted_articles = []
        for i, article in enumerate(articles_to_include, 1):
            article_text = f"{i}. {article.title}"
            if article.link:
                article_text += f"\n   Link: {article.link}"
            if article.summary:
                article_text += f"\n   Summary: {article.summary[:200]}{'...' if len(article.summary) > 200 else ''}"
            if article.reasoning:
                article_text += f"\n   🎯 WHY THIS MATTERS: {article.reasoning}"
            if article.source:
                article_text += f"\n   Source: {article.source}"
            if article.published_at:
                article_text += f"\n   Published: {article.published_at.strftime('%Y-%m-%d %H:%M')}"
            
            formatted_articles.append(article_text)
        
        return "\n\n".join(formatted_articles)
    
    def create_post(self, articles: List[Article]) -> str:
        """Create an engaging social media post from articles."""
        logging.info("Creating social media post...")
        
        try:
            # Format articles for the prompt
            articles_text = self._format_articles_for_post(articles)
            article_count = len(articles)
            
            # Prepare the prompt
            prompt = self.config["post_creator"]["post_prompt"].format(
                articles_text=articles_text,
                article_count=article_count
            )
            
            # Generate the post using the chat model
            messages = [
                {"role": "system", "content": self.config["post_creator"]["system_message"]},
                {"role": "user", "content": prompt}
            ]
            
            response = self.chat_model.invoke(messages)
            post_text = response.content.strip()
            
            logging.info("Successfully created social media post")
            return post_text
            
        except Exception as e:
            logging.error(f"Failed to create post: {e}")
            # Fallback to a simple post if LLM fails
            return self._create_fallback_post(articles)
    
    def _create_fallback_post(self, articles: List[Article]) -> str:
        """Create a simple fallback post if LLM generation fails."""
        logging.warning("Using fallback post generation")
        
        post_lines = [
            "<b>🤖 AI Agent Digest Update</b>",
            "",
            f"📰 <i>{len(articles)} new articles about AI agents and autonomous systems:</i>",
            ""
        ]
        
        # Add top 3 articles with links
        for i, article in enumerate(articles[:3], 1):
            # Escape HTML characters in title and link
            escaped_title = html.escape(article.title)
            escaped_link = html.escape(str(article.link), quote=True) if article.link else None
            
            if article.link:
                post_lines.append(f"{i}. <a href=\"{escaped_link}\">{escaped_title}</a>")
            else:
                post_lines.append(f"{i}. {escaped_title}")
            
            if article.source:
                # Escape HTML characters in source
                escaped_source = html.escape(article.source)
                post_lines.append(f"   📍 <code>{escaped_source}</code>")
            
            # Add AI reasoning if available
            if article.reasoning:
                reasoning_preview = article.reasoning[:100] + "..." if len(article.reasoning) > 100 else article.reasoning
                # Escape HTML characters in reasoning
                escaped_reasoning = html.escape(reasoning_preview)
                post_lines.append(f"   💡 <i>{escaped_reasoning}</i>")
            
            post_lines.append("")
        
        # Add footer
        post_lines.extend([
            "<b>Stay tuned for more AI agent developments!</b> 🚀"
        ])
        
        return "\n".join(post_lines)
    
    