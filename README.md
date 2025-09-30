# AI Agent Digest  

**AI Agent Digest** is an intelligent daily automated assistant that collects, scores, filters, and summarizes the most important news, research, and updates in the field of AI Agents. Using advanced LLM-based relevance scoring and smart filtering, it delivers high-quality content summaries to a dedicated Telegram channel every evening.  

## 🚀 Overview  
- **Smart Collection**: Gathers content from trusted RSS sources and real-time web search
- **AI-Powered Scoring**: Uses LLM to score article relevance (1-100) for AI agent content
- **Intelligent Filtering**: Automatically selects top articles based on relevance scores
- **AI Summarization**: Generates clear and concise summaries using OpenAI GPT models
- **AI Post Creation**: Creates engaging social media posts with article links using LLM
- **Automated Delivery**: Publishes curated digest to Telegram on a reliable schedule  

## 📌 Features (Current & Planned)  
- ✅ **RSS Content Collection** from multiple sources (TechCrunch, Ars Technica, Gizmodo AI, LangChain Blog)
- ✅ **Real-time Web Search** with SerpAPI via LangChain for latest AI agent news
- ✅ **AI-Powered Summarization** using OpenAI GPT models for search results
- ✅ **LLM-Based Relevance Scoring** (1-100 scale) for intelligent content filtering
- ✅ **Smart Article Filtering** with configurable selection criteria (top 3-5 articles)
- ✅ **AI Post Creation** with engaging social media posts and clickable article links
- ✅ **Telegram Integration** with automated digest delivery and message ID tracking
- ✅ **Structured Output Processing** using Pydantic models for reliable data handling
- ✅ **SQLite Database** with migration system for persistent storage
- ✅ **Batch Operations** for improved performance and reliability
- ✅ **Modular Configuration** with separate YAML files for each component
- ✅ **Comprehensive Testing** with unit tests for all major components
- ⬜ **arXiv API Integration** for research paper collection
- ⬜ **Hugging Face Blog** support (RSS + scraping)
- ⬜ **Advanced Analytics** (engagement tracking, click metrics)
- ⬜ **Multi-language Support** for international content  

## 🛠️ Tech Stack  
- **Language**: Python 3.13+  
- **Workflow**: LangGraph for intelligent orchestration
- **AI Framework**: LangChain for tools and utilities
- **Content Sources**: RSS feeds, Web search APIs
- **Web Search**: SerpAPI via LangChain for real-time search results
- **AI Processing**: OpenAI GPT-4 models for summarization and scoring
- **Data Models**: Pydantic for type safety and validation
- **Storage**: SQLite with migration system (`db/migrations/`)  
- **Delivery**: Telegram Bot API with python-telegram-bot library
- **Configuration**: YAML-based modular configuration system

## 📂 Project Structure  
```
ai-agent-digest/
│
├── config/            # Configuration files (YAML)
│   ├── database.yaml  # Database configuration
│   ├── sources.yaml   # RSS sources configuration
│   ├── search_agent.yaml # Search agent configuration
│   ├── scoring.yaml   # Relevance scoring configuration
│   ├── post_creator.yaml # Post creation configuration
│   └── delivery.yaml  # Delivery configuration
├── utils/             # Shared utility functions
│   ├── config.py      # Configuration loading utilities
│   ├── constants.py   # Configuration path constants
│   └── time_utils.py  # Time-based utility functions
├── sources/           # Content fetching and parsing
│   └── loader.py      # RSS feed loading and parsing
├── search/            # Web search and summarization
│   └── agent.py       # Search agent with SerpAPI integration
├── models/            # Data models (Pydantic)
│   ├── article.py     # Article and ScoredArticle models with relevance scoring
│   ├── search_result.py # Search result model
│   ├── search_summary.py # Search summary model
│   └── delivery.py    # Delivery model
├── processing/        # Content processing pipeline
│   ├── scoring.py     # LLM-based relevance scoring
│   ├── filtering.py   # Smart article filtering
│   └── post_creator.py # AI-powered post creation
├── storage/           # Database operations
│   ├── article_storage.py # Article database operations
│   ├── summary_storage.py # Summary database operations
│   └── delivery_storage.py # Delivery database operations
├── delivery/          # Telegram integration
│   └── telegram.py    # Telegram bot integration
├── db/                # Database migrations
│   ├── migrations/    # SQL migration scripts
│   └── migrate.py     # Migration runner
├── tests/             # Comprehensive test suite
│   ├── test_time_utils.py
│   ├── test_config.py
│   └── ...            # Additional test files
├── main.py            # Main workflow orchestration
├── requirements.txt   # Project dependencies
├── .env.example       # Environment variables template
└── README.md          # This file
```

## 🔄 Workflow Overview

The AI Agent Digest follows a sophisticated 8-step workflow:

1. **📥 Content Collection**: Fetches articles from RSS sources and stores them in SQLite
2. **🔍 Web Search**: Performs real-time web searches for AI agent news using SerpAPI
3. **🤖 AI Summarization**: Generates comprehensive summaries using OpenAI GPT models
4. **📊 Relevance Scoring**: Uses LLM to score each article (1-100) for AI agent relevance
5. **💾 Database Update**: Saves relevance scores to the database for persistence
6. **🎯 Smart Filtering**: Selects top 3-5 articles based on relevance scores
7. **✍️ AI Post Creation**: Creates engaging HTML-formatted social media posts with article links using LLM
8. **📱 Telegram Delivery**: Publishes curated digest to Telegram channel with message ID tracking


## ⚡ Getting Started  
1. Clone the repository:  
   ```bash
   git clone https://github.com/yourusername/ai-agent-digest.git
   cd ai-agent-digest
   ```  
2. Create a virtual environment and install dependencies:  
   ```bash
   python -m venv venv
   source venv/bin/activate   # On Windows use venv\Scripts\activate
   pip install -r requirements.txt
   ```
   
   **Note**: The `requirements.txt` uses compatible version pinning (`~=`) for stability while allowing patch updates.  
3. Set up environment variables:
   ```bash
   # Rename the example file
   mv .env.example .env
   # Then edit .env with your actual API keys
   ```
4. Initialize or update the SQLite database (applies all migrations):  
   ```bash
   python -m db.migrate
   ```  
5. Run the agent:  
   ```bash
   python main.py
   ```

## 🗄 Database Migration Workflow  
- All schema changes are tracked as **SQL migration scripts** in `db/migrations/`.  
- Use the migration runner to apply all pending migrations:  
  ```bash
  python -m db.migrate
  ```
- The runner keeps track of applied migrations in a `schema_migrations` table.   

## 📖 Configuration  

### Environment Variables
Rename `.env.example` to `.env` and add your API keys:

```bash
# Rename the example file
mv .env.example .env

# Then edit .env with your actual values:
# - OpenAI API key for AI processing
# - SerpAPI key for web search
# - Telegram bot token and channel for delivery
```

### Database Configuration (`config/database.yaml`)
```yaml
database:
  file: "digest.db"
```

### Sources Configuration (`config/sources.yaml`)
```yaml
sources:
  - name: TechCrunch
    type: rss
    url: "https://techcrunch.com/category/artificial-intelligence/feed/"
    enabled: true
  - name: Ars Technica
    type: rss
    url: "https://arstechnica.com/ai/feed/"
    enabled: true
  # ... more sources
```

### Scoring Configuration (`config/scoring.yaml`)
```yaml
scoring:
  chat_model:
    model: "gpt-4.1"
    model_provider: "openai"
    temperature: 0.1
  scoring_prompt: |
    You are an expert content curator for an AI Agent Digest newsletter...
  system_message: "You are an expert AI content curator..."
```

### Search Agent Configuration (`config/search_agent.yaml`)
```yaml
search_agent:
  engine: google_news
  freshness: last_24h
  results_per_query: 5
  queries:
    - AI Agents
    - LangChain agents
    - autonomous AI agents
    - multi-agent systems
    - CrewAI OR AutoGen agents
```

### Post Creator Configuration (`config/post_creator.yaml`)
```yaml
post_creator:
  chat_model:
    model: "gpt-4.1"
    model_provider: "openai"
    temperature: 0.7
  post_prompt: |
    You are creating an engaging social media post for an AI Agent Digest newsletter...
  system_message: "You are a skilled social media content creator..."
  max_articles_in_post: 5
```

### Delivery Configuration (`config/delivery.yaml`)
```yaml
delivery:
  delivery_time_utc: "18:00"
  articles_freshness: last_24h
```

**Configuration Options:**
- `delivery_time_utc`: UTC time for daily digest delivery (24-hour format)
- `articles_freshness`: Time window for article selection (e.g., `last_24h`, `last_48h`)

### Telegram Configuration (`.env`)
```bash
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHANNEL=your_channel_id_or_username
TELEGRAM_PARSE_MODE=HTML
```

**Telegram Setup:**
1. Create a Telegram bot via [@BotFather](https://t.me/botfather)
2. Get your bot token and add it to `TELEGRAM_BOT_TOKEN`
3. Add your channel ID (or @username) to `TELEGRAM_CHANNEL`
4. Set `TELEGRAM_PARSE_MODE=HTML` for rich text formatting
5. Make sure your bot is added as an administrator to your channel


### Configuration Features
- **Modular Configuration**: Separate YAML files for each component
- **Environment Variables**: Secure API key management via `.env`
- **Validation**: Pydantic models ensure configuration integrity
- **Flexible Database**: Configurable database location for different environments
- **Source Management**: Enable/disable sources individually
- **AI Customization**: Configurable LLM models and parameters for scoring, summarization, and post creation
- **Post Generation**: Configurable post creation with customizable prompts and article limits

## 📜 License  
This project is licensed under the **MIT License** – see the [LICENSE](LICENSE) file for details.  

## 🤝 Contributing  
Contributions are welcome! Please open an issue or submit a pull request if you’d like to help improve the project.  

## 🌟 Future Enhancements  
- **Advanced Analytics**: Engagement tracking, click metrics, read time analysis
- **Cloud Deployment**: Docker containers, serverless functions