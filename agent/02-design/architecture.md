# System Architecture Design

This document describes the high-level system architecture of the customer support chatbot project, acting as the foundation for individual module design.

---

## 1. System Overview

The system is designed as an automated data ingestion and synchronization pipeline paired with a retrieval-augmented generation (RAG) assistant. Its core purpose is to continuously align the AI assistant's knowledge base with the live support documentation published on the external Help Center, ensuring context-grounded and accurate customer responses.

---

## 2. System Context

The system operates as an automated synchronization service between the OptiSigns Help Center and an AI-powered customer support assistant.

The synchronization service periodically retrieves documentation, updates the AI knowledge base, and enables customers to query the latest support content through the AI Assistant.

---

## 3. Major Components

The system is composed of five logical blocks:

```text
+---------------------------------------------------------------------------------+
|                                Runtime Container                                |
|                                                                                 |
|  +--------------------+      +--------------------+      +--------------------+ |
|  |                    |      |                    |      |                    | |
|  | Ingestion Engine   | ───➔ | Content Normalizer | ───➔ | Sync Coordinator   | |
|  |                    |      |                    |      |                    | |
|  +---------▲----------+      +--------------------+      +----------┬---------+ |
|            │                                                        │           |
|            │ (Read Content)                                         │           |
+------------┼--------------------------------------------------------┼-----------+
             │                                                        │
             │                                                        ▼ (Push Deltas)
+------------┴----------+                                  +----------┴---------+
| External Help Center  |                                  | AI Service Provider|
| (Zendesk Portal)      |                                  | (Vector Store &    |
|                       |                                  |  AI Assistant)     |
+-----------------------+                                  +----------▲---------+
                                                                      │
                                                                      │ (Query)
                                                           +----------┴---------+
                                                           | User Interface     |
                                                           +--------------------+
```

1.  **Ingestion Engine:** Interfaces with the external Help Center to extract raw support articles.
2.  **Content Normalizer:** Cleanses raw input and formats it into a standardized markdown representation.
3.  **Sync Coordinator:** Compares latest article states with historical metadata to detect delta changes and manages the push lifecycle.
4.  **AI Service Provider:** Managed AI platform responsible for document indexing, knowledge retrieval, and AI Assistant execution.
5.  **User Interface:** The entry point (Playground/Studio/Chat client) for querying the configured Assistant.

---

## 4. Component Responsibilities

### Ingestion Engine
- Connect to the external Help Center endpoint.
- Retrieve the full collection of articles (supporting pagination if necessary).
- Extract raw article bodies and associated metadata (e.g., URLs, titles).
- Pass raw payloads to the Content Normalizer.

### Content Normalizer
- Parse HTML and isolate core article elements.
- Strip out layout templates, navigation menus, ads, headers, and footers.
- Translate HTML structures (headings, lists, code snippets, relative hyperlinks) into clean Markdown.
- Package normalized documents with standardized metadata tags.

### Sync Coordinator
- Compare current documents with the previous synchronization state to determine whether documents are new, updated, or unchanged.
- Determine the synchronization actions required for each document.
- Programmatically manage the Vector Store: upload new/modified documents, delete orphaned files, and update references via API.
- Persist synchronization state for future executions.

### AI Service Provider
- Index uploaded documents and provide retrieval capabilities for the AI Assistant.
- Execute user queries using the uploaded knowledge base and return grounded responses with document citations.

---

## 5. High-Level Data Flow

```text
[ Daily Cron / Trigger ]
           │
           ▼
1. Fetch Raw HTML ─────────➔ Ingestion Engine
                                    │
                                    ▼ (Raw Article Payload)
2. Filter & Convert ───────➔ Content Normalizer
                                    │
                                    ▼ (Clean Markdown + Metadata)
3. Synchronization ────────➔ Sync Coordinator ───[ Synchronization State ]
                                    │
                                    ▼ (Upload Delta Documents / Delete Stale)
4. Load Knowledge ─────────➔ AI Service Provider (Vector Store)
                                    │
                                    ▼ (Ground Queries)
5. Execute Chats ──────────➔ AI Assistant Client (OptiBot)
```

---

## 6. External Services
- **Help Center Host:** Zendesk-powered portal housing live customer articles.
- **AI Core Platform:** Managed API (e.g., OpenAI or Google Gemini) providing Vector Stores and Retrieval-Augmented Generation (RAG) assistant runtimes.

---

## 7. Deployment Overview
- **Deployment Unit:** Docker image containing the Ingestion, Normalization, and Sync Coordinator packages.
- **Runtime Environment:** A cloud platform capable of scheduled container execution (e.g., Railway, Render, DigitalOcean, AWS, or Google Cloud).
- **Lifecycle:** The execution environment spins up the container, runs the sync sequence to completion, outputs runtime statistics to stdout logs, and shuts down immediately.

---

## 8. Design Principles
- **Idempotency:** Re-running the sync job repeatedly under unchanged conditions must result in zero modifications to the AI Vector Store.
- **Resilience:** Processing failures in isolated documents must be caught and logged, allowing remaining documents to synchronize without crashing the process.
- **Statelessness:** The container relies on externalized state tracking or dynamic vector store inspections, requiring no persistent local disk storage between runs.
- **Separation of Concerns:** Scraping, content cleaning, delta calculation, and Vector Store uploads are kept decoupled.

---

## 9. Architecture Decisions

- The system follows a modular pipeline architecture.
- Markdown is used as the canonical document format.
- Knowledge synchronization is performed through official AI platform APIs.
- Scheduled synchronization is preferred over continuous crawling.
- The runtime is designed to be stateless between executions.

---

## 10. Risks and Considerations
- **API Rate Limits:** Scraping dozens of pages or uploading bulk documents rapidly might trigger rate-limiting on either the Zendesk side or the AI platform. Implement throttled calls or batch processing.
- **State Drift:** If tracking metadata drifts from the actual contents in the AI Vector Store, the system could skip updates or duplicate records. A verification cycle (or checking the Vector Store contents dynamically) should be considered.
- **HTML Parsing Fragility:** Changes to the Help Center page structure or API responses may require updates to the content extraction logic.

---

## 11. Assumptions

- The Help Center remains publicly accessible.
- The selected AI platform supports document uploads and retrieval.
- The deployment platform supports scheduled container execution.
- Required API credentials are available through environment variables.
