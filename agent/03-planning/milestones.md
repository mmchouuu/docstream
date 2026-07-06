# Project Milestones

This document defines the key measurable milestones, acceptance criteria, verification methods, and validation checklists for tracking the progress of the OptiBot Mini-Clone project.

---

## 1. Milestone Details

### Milestone 1 (M1): Environment Setup
- **Objective:** Configure the local project workspace and establish target environment credentials.
- **Deliverable:** Git repository and `.env.sample` template file in the root directory.
- **Acceptance Criteria:**
  - Git repository initialized.
  - `.env.sample` file contains all necessary configuration keys (API credentials, target URL, and store IDs) without hardcoded values.
  - Standard python dependency list defined in `requirements.txt`.
- **Verification Method:** Confirm the existence of the repository, review the `.env.sample` keys, and verify successful local dependency installation.

### Milestone 2 (M2): Scraper Working
- **Objective:** Retrieve raw support article documents from the target help portal.
- **Deliverable:** Ingestion logic capable of fetching raw article payloads.
- **Acceptance Criteria:**
  - Scraper can fetch at least 30 articles from `support.optisigns.com`.
  - Content payload contains the primary article title, body container, and timestamp metadata.
  - Page crawling supports paging to handle list scaling.
- **Verification Method:** Run the ingestion script locally and check that 30+ raw JSON or HTML files are downloaded to the target cache directory (`data/raw/`).

### Milestone 3 (M3): Markdown Normalization Complete
- **Objective:** Convert HTML payloads into sanitized, standardized Markdown files.
- **Deliverable:** Content normalizer parser and structured Markdown files outputted locally.
- **Acceptance Criteria:**
  - HTML tags (except headings, paragraphs, lists, code, tables, and links) are completely stripped.
  - Heading hierarchies and links are preserved correctly.
  - Markdown output contains structured metadata headers (article ID, title, source URL, hash signature).
- **Verification Method:** Open several generated `.md` files in the `data/markdown/` folder and inspect formatting correctness, link structures, and YAML front-matter metadata tags.

### Milestone 4 (M4): Vector Store Upload Working
- **Objective:** Programmatically load Markdown files into the AI platform's Vector Store.
- **Deliverable:** Client integration scripts to push documents via API.
- **Acceptance Criteria:**
  - Files are uploaded programmatically using SDK client calls.
  - Documents are attached to the designated Vector Store ID.
  - No manual UI file actions or drag-and-drop operations are executed.
- **Verification Method:** Execute the upload script, and verify via the developer console or API query logs that the Markdown files are registered in the Vector Store.

### Milestone 5 (M5): AI Assistant Responding Correctly
- **Objective:** Verify conversational accuracy and citation behavior of the configured Assistant.
- **Deliverable:** Verified AI Assistant runtime and a query validation screenshot.
- **Acceptance Criteria:**
  - Assistant responds to target support questions (e.g., *"How do I add a YouTube video?"*).
  - Answers are factual, concise (maximum 5 bullet points), and citation-anchored.
  - Responses include up to 3 cited article URLs.
- **Verification Method:** Perform manual queries in the platform playground interface and capture the screenshot demonstrating correct answers and link citations.

### Milestone 6 (M6): Delta Synchronization Working
- **Objective:** Implement delta change logic to synchronize modifications and delete orphans.
- **Deliverable:** Synchronization manager executing incremental sync cycles.
- **Acceptance Criteria:**
  - Fingerprint checksums correctly flag new, updated, and unchanged articles.
  - Execution runs upload only the changed delta and skip matching signatures.
  - Orphaned items in the Vector Store (deleted from Help Center) are automatically removed.
  - Execution statistics (added, updated, skipped) are outputted to console logs.
- **Verification Method:** Run a second sync execution without modifying articles to confirm zero uploads, modify one article to verify a single delta update, and verify deletion behavior by removing a cached local file.

### Milestone 7 (M7): Docker & Deployment Working
- **Objective:** Package the application as a Docker container and deploy as a scheduled Cron job.
- **Deliverable:** Working `Dockerfile` and active daily cloud schedule job.
- **Acceptance Criteria:**
  - Docker image builds and executes successfully.
  - Container executes a single synchronization cycle, logs final statistics to stdout, and exits with code `0`.
  - Deployment scheduling runs once per day on the cloud hosting portal.
  - Live execution logs are public/accessible.
- **Verification Method:** Run the container locally using `docker run`, trigger a manual scheduler run in the cloud dashboard, and view the public link logs to check for a successful sync exit.

---

## 2. Milestone Dependencies

```text
  [M1: Env Setup]
         │
         ▼
[M2: Scraper Working]
         │
         ▼
[M3: Normalization]
         │
    ┌────┴────┐
    ▼         ▼
[M4: Upload] [M6: Delta Sync] (Integrate in Sync Coordinator)
    │         │
    └────┬────┘
         ▼
[M5: Assistant Chat]
         │
         ▼
[M7: Docker & Deploy]
```

---

## 3. Validation Checklist

- [ ] **M1 Checklist:**
  - [ ] Git repository is active.
  - [ ] `.env.sample` is complete.
  - [ ] `requirements.txt` installs without error.
- [ ] **M2 Checklist:**
  - [ ] At least 30 articles retrieved.
  - [ ] Raw cache populated under `data/raw/`.
- [ ] **M3 Checklist:**
  - [ ] Files saved under `data/markdown/` as `.md`.
  - [ ] Front-matter metadata block present in each file.
  - [ ] Boilerplate elements (nav/footer/ads) removed.
- [ ] **M4 Checklist:**
  - [ ] AI client connects successfully.
  - [ ] Markdown files uploaded to Vector Store via API.
- [ ] **M5 Checklist:**
  - [ ] Test query answered correctly using only knowledge documents.
  - [ ] Screenshot captured showing cited article URLs.
- [ ] **M6 Checklist:**
  - [ ] Checksum verification functions.
  - [ ] Modified files trigger updates.
  - [ ] Deleted files trigger removals.
  - [ ] Logs output `added`, `updated`, and `skipped` counts.
- [ ] **M7 Checklist:**
  - [ ] Docker image builds.
  - [ ] Container exits with code `0`.
  - [ ] Cloud scheduler runs on interval.
  - [ ] Public execution logs page accessible.
