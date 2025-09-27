# AI Agent Digest  

**AI Agent Digest** is a daily automated assistant that collects, filters, and summarizes the most important news, research, and updates in the field of AI Agents. Summaries are posted automatically to a dedicated [Telegram channel](#) every evening.  

## 🚀 Overview  
- Collects content from trusted sources (news sites, blogs, research portals).  
- Filters content to keep only AI Agent–related updates.  
- Generates clear and concise summaries with links to original articles.  
- Publishes digest to Telegram on a reliable schedule.  

## 📌 Features (Current & Planned)  
- ✅ Fetch content from **TechCrunch** (RSS).  
- ✅ Add support for **Ars Technica** (RSS).  
- ✅ Add support for **Gizmodo AI** (RSS).  
- ✅ Add support for **LangChain Blog** (RSS).   
- ✅ Store already-processed items in **SQLite** to avoid duplicates.  
- ✅ Configurable database settings via `config/database.yaml`.  
- ✅ Batch database operations for improved performance.  
- ⬜ Summarize articles with LLM.  
- ⬜ Automatic posting to Telegram.  
- ⬜ Add support for **arXiv** (API).  
- ⬜ Add support for **Hugging Face Blog** (RSS + scraping). 
- ⬜ Error handling, retries, and monitoring.  

## 🛠️ Tech Stack  
- **Language**: Python 3.11+  
- **Content Sources**: RSS, APIs, Web scraping  
- **Storage**: SQLite (migrations tracked in `db/migrations/`)  
- **Delivery**: Telegram Bot API  
- **Summarization**: Large Language Models (LLMs)  

## 📂 Project Structure  
```
ai-agent-digest/
│
├── config/            # Configuration files (YAML)
│   ├── database.yaml  # Database configuration
│   └── sources.yaml   # RSS sources configuration
├── utils/             # Shared utility functions
│   └── config.py      # Configuration loading utilities
├── sources/           # Fetching/parsing logic for each source
│   └── loader.py      # RSS feed loading and parsing
├── models/            # Strongly typed models (Pydantic)
│   └── article.py     # Article data model
├── processing/        # Filtering, deduplication, and summarization pipeline
│   └── filters.py     # Content filtering logic
├── storage/           # SQLite integration and helper functions
│   └── store.py       # Database storage with batch operations
├── delivery/          # Telegram integration & scheduling
│   └── telegram.py    # Telegram bot integration
├── db/                # Database migrations and migration runner
│   ├── migrations/    # SQL migration scripts (001_init.sql, 002_*.sql, ...)
│   └── migrate.py     # Migration runner (applies all migrations automatically)
├── tests/             # Unit & integration tests
│
├── main.py            # Entry point for running the agent
├── requirements.txt   # Project dependencies
└── README.md          # This file
```

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
3. Initialize or update the SQLite database (applies all migrations):  
   ```bash
   python db/migrate.py
   ```
4. Run the agent:  
   ```bash
   python main.py
   ```

## 🗄 Database Migration Workflow  
- All schema changes are tracked as **SQL migration scripts** in `db/migrations/`.  
- Each migration file must follow the naming pattern: `NNN_description.sql` (e.g., `002_add_processed_flag.sql`).  
- Use the migration runner to apply all pending migrations:  
  ```bash
  python db/migrate.py
  ```
- The runner keeps track of applied migrations in a `schema_migrations` table.  
- Do **not** commit the database file itself (`digest.db`). Add it to `.gitignore`.   

## 📖 Configuration  

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

### Configuration Features
- **Separate config files** for database and sources
- **Explicit configuration paths** - no hidden defaults
- **Validation** with clear error messages
- **Flexible database location** for different environments
- **Easy source management** - enable/disable sources individually  

## 📜 License  
This project is licensed under the **MIT License** – see the [LICENSE](LICENSE) file for details.  

## 🤝 Contributing  
Contributions are welcome! Please open an issue or submit a pull request if you’d like to help improve the project.  

## 🌟 Future Enhancements  
- Engagement analytics (link clicks, most-read topics).  
- Multi-language support.  
- Cloud deployment (Docker, serverless, etc.).  