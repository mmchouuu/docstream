# Task Todo List

This document lists the atomic, actionable tasks required to implement the OptiBot Mini-Clone system.

---

## 1. Setup Tasks

### TS-1: Initialize Git Repository & Branches
- **Description:** Initialize Git in the project root directory using a cryptic repository name. Setup the base branch structure (`main` and `dev`). Feature branches must branch off `dev`, merge back to `dev` for integration, and `dev` will be merged to `main` as the final reviewed state.
- **Priority:** P0
- **Dependency:** None
- **Estimate:** 0.5 Hour

### [x] TS-2: Configure Environment Template
- **Description:** Create the `.env.sample` containing empty key keys for OpenAI/Gemini credentials, Assistant IDs, and target endpoints.
- **Priority:** P0
- **Dependency:** None
- **Estimate:** 0.5 Hour
- **Status:** Completed

### [x] TS-3: Set Up Project Directory Structure
- **Description:** Verify the baseline directory tree (`src/`, `data/`, `config/`, `logs/`, `tests/`) as defined in the folder design.
- **Priority:** P0
- **Dependency:** TS-1
- **Estimate:** 0.5 Hour
- **Status:** Completed

---

## 2. Scraper Tasks

### SC-1: Implement API Client
- **Description:** Build the ingestion client to connect to the Zendesk Help Center API, handle pagination, and fetch raw article payloads.
- **Priority:** P0
- **Dependency:** TS-2, TS-3
- **Estimate:** 1.5 Hours

### SC-2: Implement Crawler Fallback
- **Description:** Write fallback BeautifulSoup scraper logic to crawl webpages directly if the REST API is restricted.
- **Priority:** P1
- **Dependency:** SC-1
- **Estimate:** 1.0 Hour

### SC-3: Implement Raw Content Caching
- **Description:** Develop storage wrapper to write retrieved raw article JSON/HTML payloads locally under `data/raw/` for debug auditing.
- **Priority:** P1
- **Dependency:** SC-1
- **Estimate:** 0.5 Hour

---

## 3. Normalizer Tasks

### NM-1: Core Content Extraction
- **Description:** Parse raw HTML and isolate the primary body container, removing nav, footer, sidebar, and scripts.
- **Priority:** P0
- **Dependency:** SC-1
- **Estimate:** 1.0 Hour

### NM-2: HTML to Markdown Translator
- **Description:** Convert elements (headings, paragraphs, lists, code, relative links) to clean Markdown syntax.
- **Priority:** P0
- **Dependency:** NM-1
- **Estimate:** 1.0 Hour

### NM-3: Metadata Front-Matter Generator
- **Description:** Generate structured YAML front-matter containing article ID, title, absolute source URL, timestamp, and slug.
- **Priority:** P0
- **Dependency:** NM-2
- **Estimate:** 0.5 Hour

---

## 4. Sync Engine Tasks

### SY-1: State Manager Checksum Computations
- **Description:** Implement SHA-256 fingerprint generation for clean Markdown documents.
- **Priority:** P0
- **Dependency:** NM-3
- **Estimate:** 0.5 Hour

### SY-2: Delta Synchronization Comparator
- **Description:** Compare current article states against historical metadata, classifying states as `added`, `updated`, or `skipped`.
- **Priority:** P0
- **Dependency:** SY-1
- **Estimate:** 1.0 Hour

### SY-3: Orphan Cleanup Logic
- **Description:** Implement deletion triggers to remove documents from the AI vector store that are missing from the live Help Center.
- **Priority:** P1
- **Dependency:** SY-2
- **Estimate:** 0.5 Hour

---

## 5. AI Integration Tasks

### AI-1: AI Platform SDK Wrapper
- **Description:** Implement the API client initialization using environment variables for the selected AI SDK (OpenAI/Gemini).
- **Priority:** P0
- **Dependency:** TS-2
- **Estimate:** 0.5 Hour

### AI-2: Programmatic Vector Store Manager
- **Description:** Implement programmatic document upload and Vector Store association via API (no manual drag-and-drop).
- **Priority:** P0
- **Dependency:** AI-1, SY-2
- **Estimate:** 1.0 Hour

### AI-3: Assistant Configuration Trigger
- **Description:** Set up the Assistant profile with the designated support instructions verbatim via API or playground.
- **Priority:** P0
- **Dependency:** AI-2
- **Estimate:** 0.5 Hour

### AI-4: Validation Test Run
- **Description:** Execute test query *"How do I add a YouTube video?"* and save validation screenshot with URL citations.
- **Priority:** P0
- **Dependency:** AI-3
- **Estimate:** 0.5 Hour

---

## 6. Deployment Tasks

### DP-1: Create Dockerfile
- **Description:** Create the `Dockerfile` specifying execution entry point `main.py` which runs a single sync run and exits with code `0`.
- **Priority:** P0
- **Dependency:** SC-1, SY-2, AI-2
- **Estimate:** 1.0 Hour

### DP-2: Configure Cloud Scheduler (Cron)
- **Description:** Configure the scheduled execution on the hosting platform (e.g. Render, Railway, DigitalOcean) to run daily.
- **Priority:** P0
- **Dependency:** DP-1
- **Estimate:** 1.0 Hour

### DP-3: Verify Public Logs
- **Description:** Ensure runtime logs map to stdout and the public link endpoint correctly renders task outcomes.
- **Priority:** P0
- **Dependency:** DP-2
- **Estimate:** 0.5 Hour

---

## 7. Testing Tasks

### TE-1: Implement Scraper Unit Tests
- **Description:** Write mock unit tests to verify article discovery, pagination handling, and request retries.
- **Priority:** P1
- **Dependency:** SC-1
- **Estimate:** 0.5 Hour

### TE-2: Implement HTML Normalizer Unit Tests
- **Description:** Write unit tests to check HTML to Markdown translation correctness (correct headers, stripped ads).
- **Priority:** P0
- **Dependency:** NM-2
- **Estimate:** 0.5 Hour

### TE-3: Run End-to-End Execution Validation
- **Description:** Validate full sync execution: run, upload new articles, run again to verify skipped logs, modify an article to verify delta sync.
- **Priority:** P0
- **Dependency:** SY-2, AI-2, DP-1
- **Estimate:** 1.0 Hour