# Project Folder Structure Design

This document outlines the simplified directory layout for the codebase, establishing a structure based on responsibility and separation of concerns without over-engineering.

---

## 1. Design Goals
- **Responsibility-Driven Layout:** Organize files by their core business purpose (ingestion, sync, AI service) rather than generic technical groupings.
- **Isolation of State & Outputs:** Clearly separate operational code from scraped articles, local execution databases, logs, and templates.
- **Stateless Adaptability:** Design directories such that generated data (cache, temporary markdown, state files) can be safely excluded from version control without affecting local execution.
- **Maintainability:** Ensure that swapping out the scraper or integrating a different AI model can be done by modifying isolated sub-packages.

---

## 2. Root Directory Structure

```text
docstream/
│
├── .env                        # Local environment variables (gitignored)
├── .env.sample                 # Template for environment settings
├── .gitignore                  # Git exclusion rules
├── Dockerfile                  # Container definition
├── README.md                   # Setup and runtime instructions
├── requirements.txt            # System dependencies
│
├── agent/                      # Documentation workspace
│   └── ...
│
├── config/                     # Static configurations & prompt templates
│   └── prompts/
│
├── data/                       # Local execution runtime outputs (gitignored)
│   ├── raw/                    # Raw HTML documents
│   ├── markdown/               # Converted Markdown documents
│   └── state/                  # Saved synchronization state
│
├── logs/                       # Execution log outputs (gitignored)
│   └── sync.log
│
├── src/                        # Core application package
│   ├── main.py                 # Application entry point
│   │
│   ├── ingestion/              # Ingestion engine packages
│   │   ├── __init__.py
│   │   ├── scraper.py          # Help center crawler / API client
│   │   └── normalizer.py       # HTML-to-Markdown translation engine
│   │
│   ├── synchronization/        # Sync coordinator packages
│   │   ├── __init__.py
│   │   ├── coordinator.py      # Execution coordinator
│   │   └── state_manager.py    # Read/write for sync state
│   │
│   ├── ai_integration/         # AI service provider clients
│   │   ├── __init__.py
│   │   ├── client.py           # Low-level AI platform API wrapper
│   │   └── assistant.py        # Assistant configuration and run execution
│   │
│   └── models/                 # Shared data structures/schemas
│       ├── __init__.py
│       └── models.py           # Internal data representations
│
└── tests/                      # Automated test suite
    ├── __init__.py
    ├── unit/                   # Isolated module tests
    └── integration/            # Cross-component workflow validation tests
```

---

## 3. Top-Level Directories

- **`config/`**: Holds externalized prompts. No runtime code resides here.
- **`data/`**: Designated for runtime data storage. All directories and files under this folder are gitignored to preserve statelessness.
- **`logs/`**: Dedicated directory for local execution logs.
- **`src/`**: Contains the source code of the execution pipeline, packaged as a standard Python module.
- **`tests/`**: Houses all automated test components.

---

## 4. Subdirectories

### `src/models/`
Defines internal data representations (e.g., Article, SyncAction) used across different modules to pass structural data cleanly.

### `src/ingestion/`
Responsible for retrieving and sanitizing data. It contains classes for web crawling or Zendesk API interactions and the parsing logic that formats HTML into markdown.

### `src/synchronization/`
Coordinates the sync flow. It uses core models to load documents, calls the state manager to identify changes (delta), and directs the upload/deletion sequences.

### `src/ai_integration/`
Encapsulates all communications with the external AI platform. Swapping between OpenAI and Gemini would only impact files under this subdirectory.

---

## 5. Naming Conventions
- **Directories:** Lowercase with underscores (snake_case) for Python source folders, and lowercase/hyphens (kebab-case) for documentation or infrastructure folders.
- **Source Files:** snake_case (e.g., `state_manager.py`).
- **Classes:** PascalCase (e.g., `HtmlNormalizer`).
- **Functions & Variables:** snake_case (e.g., `detect_deltas()`).

---

## 6. Separation of Concerns
- **Logic vs. Configuration:** Environment values are loaded in `src/main.py` and injected down, keeping business logic clean.
- **Code vs. State:** The codebase must write state outputs (such as checksum caches or raw page downloads) exclusively into the `data/` directory.
- **Prompt Engineering vs. Implementation:** Prompts are kept in the `config/prompts/` directory to allow tuning assistant system prompts without editing python source files.

---

## 7. Recommended Configuration Files
- **`.env.sample`:** Outlines the names of all required key credentials, without providing value placeholders.

---

## 8. Scalability Considerations
- **Scraper Pluggability:** If the Help Center portal changes to a different provider, a new class can be added to `src/ingestion/` without altering the `synchronization/` module.
- **State Scaling:** The state manager currently operates on simple local metadata. Should the volume of sync documents scale, the file-based state manager can be replaced with a database implementation by altering only the `state_manager.py` file.
