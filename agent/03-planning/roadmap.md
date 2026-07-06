# Development Roadmap

This document outlines the high-level roadmap and phase-by-phase execution plan for building the OptiBot Mini-Clone system within the targeted ~10-hour schedule.

---

## 1. Phases & Deliverable Mapping

### Phase 1: Setup & Initialization (1.0 Hour)
- **Objective:** Configure the workspace, local environment templates, and repository structure.
- **Tasks:**
  - Create the repository with a generic/cryptic name.
  - Setup the base branch structure (`main` and `dev`). Feature branches must branch off `dev`, merge back to `dev` for integration, and `dev` will be merged to `main` as the final reviewed state.
  - Setup the Python development environment and dependency manifest (`requirements.txt`).
  - Create the `.env.sample` template for configuration.
- **Deliverable Mapping:** Git Repository (`main` & `dev` branches), `.env.sample`.

### Phase 2: Ingestion & Normalization (3.0 Hours)
- **Objective:** Harvest and sanitize Help Center documentation.
- **Tasks:**
  - Implement the Zendesk API / web scraper client to extract at least 30 articles.
  - Implement HTML parsing to isolate the core article body and discard layouts.
  - Normalize core content into clean Markdown files preserving heading levels, lists, code, and links.
  - Append article metadata parameters to the normalized outputs.
- **Deliverable Mapping:** Clean Markdown documents, Ingestion Engine.

### Phase 3: AI Platform Integration & Assistant Setup (2.0 Hours)
- **Objective:** Programmatically establish the knowledge search assistant.
- **Tasks:**
  - Configure the AI Assistant profile using the designated verbatim support system prompt.
  - Implement programmatic Vector Store management via API to load the normalized Markdown files.
  - Validate the Assistant's retrieval capabilities in the platform playground using the sample question (*"How do I add a YouTube video?"*).
- **Deliverable Mapping:** AI Assistant, Programmatic Vector Store integration, Playground Validation Screenshot.

### Phase 4: Delta Synchronization Logic (2.0 Hours)
- **Objective:** Build incremental updating and orphaned file cleanup.
- **Tasks:**
  - Implement fingerprint/checksum calculation for Markdown files.
  - Develop state manager to isolate added, updated, and deleted articles since the previous run.
  - Build delta synchronization upload and cleanup rules in the coordinator.
  - Set up stdout execution logging for `added`, `updated`, and `skipped` metrics.
- **Deliverable Mapping:** Incremental (delta) synchronization mechanism.

### Phase 5: Containerization & Deployment (2.0 Hours)
- **Objective:** Package the sync cycle as a daily automated task.
- **Tasks:**
  - Create the Dockerfile specifying single-run execution exiting with status code `0`.
  - Configure scheduled Cron execution on the chosen cloud hosting platform.
  - Export and verify public access to the execution run logs.
  - Finalize README setup and deployment guide.
- **Deliverable Mapping:** Dockerfile, Cloud scheduler job deployment, Public job logs link, README.

---

## 2. Timeline (10 Hours Effort)

| Task Block | Estimated Hours | Phase Reference | Critical Deliverable |
|---|---|---|---|
| Project Setup & Credentials | 1.0 h | Phase 1 | Repository & `.env.sample` |
| Scraping & Content Cleaning | 2.0 h | Phase 2 | Raw HTML Extraction |
| HTML to Markdown Converter | 1.0 h | Phase 2 | Clean `.md` documents |
| Vector API & Assistant Config | 1.0 h | Phase 3 | OpenAI/Gemini SDK client |
| Playground Query Verification | 1.0 h | Phase 3 | Response citation screenshot |
| Delta Sync & State Manager | 1.5 h | Phase 4 | In-memory comparison / file check |
| Logger & Statistics Output | 0.5 h | Phase 4 | Console output stats |
| Dockerization & Local Run | 1.0 h | Phase 5 | Dockerfile validation |
| Cloud Cron Deployment | 1.0 h | Phase 5 | Daily execution & log links |

---

## 3. Dependencies

```text
[ Phase 1: Setup ]
        │
        ▼
[ Phase 2: Ingestion & Normalization ]
        │
        ▼
[ Phase 4: Delta Sync Logic ] ─── (Requires Phase 2 outputs)
        │
        ▼
[ Phase 3: AI Vector Store Upload ] ─── (Requires Phase 4 delta inputs)
        │
        ▼
[ Phase 5: Containerization & Cron Deploy ] ─── (Requires all previous phases)
```

---

## 4. Risks & Checkpoints

### Ingestion Failures
- **Risk:** Support website layout changes or API connection timeouts.
- **Checkpoint:** Scraper exits gracefully on invalid links and logs warnings without stopping the processing of remaining articles.

### API Rate Limits
- **Risk:** Rapid requests to the Zendesk API or OpenAI/Gemini upload endpoints trigger rate limits.
- **Checkpoint:** Integrate throttling pauses and exponential retry backoff in the client wrappers.

### Synchronization Inconsistencies
- **Risk:** Local state mismatches leading to missed delta updates or orphaned documents in the Vector Store.
- **Checkpoint:** Programmatic reconciliation queries matching active Help Center keys against the remote Vector Store database.

---

## 5. Success Criteria
The roadmap is successfully completed when:
- The automated sync pipeline retrieves at least 30 articles and outputs clean Markdown files containing metadata.
- All uploads and file sync actions to the AI Assistant occur programmatically without manual UI drag-and-drop.
- The AI Assistant correctly references URLs and answers testing queries using only the uploaded knowledge base.
- The Dockerized daily cron job executes, processes delta additions/updates/deletions, logs execution counts, and exits cleanly.
- All deliverables (Git repo, Dockerfile, README, screenshots, logs link) are fully validated.
