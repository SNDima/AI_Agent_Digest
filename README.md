# AI Agent Digest  

**AI Agent Digest** is a daily automated assistant that collects, filters, and summarizes the most important news, research, and updates in the field of AI Agents. Summaries are posted automatically to a dedicated [Telegram channel](#) every evening.  

## 🚀 Overview  
- Collects content from trusted sources (news sites, blogs, research portals).  
- Filters content to keep only AI Agent–related updates.  
- Generates clear and concise summaries with links to original articles.  
- Publishes digest to Telegram on a reliable schedule.  

## 📌 Features (Current & Planned)  
- ✅ Fetch content from **TechCrunch** (RSS).  
- ⬜ Add support for **Ars Technica** (RSS).  
- ⬜ Add support for **Gizmodo AI** (RSS).  
- ⬜ Add support for **arXiv** (API).  
- ⬜ Add support for **Hugging Face Blog** (RSS + scraping).  
- ⬜ Store already-processed items to avoid duplicates.  
- ⬜ Summarize articles with LLM.  
- ⬜ Automatic posting to Telegram.  
- ⬜ Error handling, retries, and monitoring.  

## 🛠️ Tech Stack  
- **Language**: Python 3.11+  
- **Content Sources**: RSS, APIs, Web scraping  
- **Storage**: SQLite / JSON (to be finalized)  
- **Delivery**: Telegram Bot API  
- **Summarization**: Large Language Models (LLMs)  

## 📂 Project Structure (draft)  
```
ai-agent-digest/
│
├── sources/           # Fetching/parsing logic for each source (TechCrunch, arXiv, Hugging Face, etc.)
├── processing/        # Filtering, deduplication, and summarization pipeline
├── storage/           # Store processed content (JSON, DB, or file-based)
├── delivery/          # Telegram integration & scheduling
├── config/            # Config files (sources, credentials, schedule)
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
3. Run the agent (currently only TechCrunch RSS):  
   ```bash
   python main.py
   ```

## 📖 Configuration  
- Sources are defined in a config file (`config/sources.yaml`).  
- Each source can be enabled/disabled and configured separately.  

## 📜 License  
This project is licensed under the **MIT License** – see the [LICENSE](LICENSE) file for details.  

## 🤝 Contributing  
Contributions are welcome! Please open an issue or submit a pull request if you’d like to help improve the project.  

## 🌟 Future Enhancements  
- Engagement analytics (link clicks, most-read topics).  
- Multi-language support.  
- Cloud deployment (Docker, serverless, etc.).  
