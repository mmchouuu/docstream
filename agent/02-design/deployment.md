# Deployment Architecture Design

This document details the deployment architecture, configuration keys, scheduling strategy, and error recovery policies for the automated synchronization service.

---

## 1. Purpose
The purpose of the deployment design is to establish a self-contained, automated, and containerized runtime environment. The deployment ensures that the documentation scraper-uploader runs successfully on a daily basis, synchronizes new or updated articles to the AI vector store, and logs execution details without requiring manual operational overhead.

---

## 2. Deployment Model
- **Containerized Run (Docker):** The application is packaged as a standard Docker container containing the Python runtime and dependencies.
- **Single-Run Execution Lifecycle:** The container operates as a batch task (run-to-completion model) rather than a continuously active server. It initializes, processes the synchronization cycle, and terminates immediately.
- **Stateless Execution:** The running container maintains no persistent local disk storage. 
- **State Reconciliation:** The remote Vector Store (or its associated document metadata tags queryable via API) acts as the primary source of truth for synchronization state. Alternatively, a lightweight JSON state file is maintained locally and reconciled dynamically during each execution cycle.

---

## 3. Runtime Flow

```text
[ Container Start ]
        │
        ▼
[ Load Environment ]  ──➔ Validate keys, endpoints, and identifiers
        │
        ▼
[ Fetch Documents ]   ──➔ Query Help Center API for active articles
        │
        ▼
[ Parse & Clean ]     ──➔ Normalize raw payloads to clean Markdown
        │
        ▼
[ Delta Sync Check ]  ──➔ Compare article IDs and hashes with active store state
        │
        ▼
[ Upload Deltas ]     ──➔ Push new/updated Markdown files to AI Vector Store
        │
        ▼
[ Remove Orphans ]    ──➔ Delete stale documents no longer active in Help Center
        │
        ▼
[ Log Statistics ]    ──➔ Write summary (added/updated/skipped) to stdout
        │
        ▼
[ Container Exit ]    ──➔ Exit cleanly with code 0 (success) or non-zero (failure)
```

1.  **Container Start:** The scheduler launches the Docker container instance.
2.  **Load Environment:** The container loads and validates API credentials, URLs, and runtime flags.
3.  **Fetch Documents:** The ingestion code contacts the external Help Center to discover and retrieve raw documentation.
4.  **Parse & Clean:** HTML contents are extracted, stripped of layout code, and converted to Markdown.
5.  **Delta Sync Check:** Clean Markdown is compared against historical signatures to determine changes.
6.  **Upload Deltas:** Delta additions or updates are pushed to the AI Vector Store.
7.  **Remove Orphans:** Any document present in the Vector Store but missing from the active Help Center is programmatically deleted.
8.  **Log Statistics:** Detailed operational summaries and counts are printed to the console output.
9.  **Container Exit:** The process releases resources and terminates cleanly (exit code `0` for success, or non-zero for runtime failures).

---

## 4. Environment Variables
To keep the container modular and secure, all sensitive credentials and endpoint targets are loaded from environment variables:
- `API_KEY`: API credential key required to authenticate with the chosen AI platform.
- `ASSISTANT_ID`: The unique identifier of the target AI Assistant to bind with the Vector Store.
- `VECTOR_STORE_ID`: The target AI Vector Store identifier where documents must be attached.
- `HELP_CENTER_URL`: The baseline URL or domain of the documentation repository (e.g., Zendesk support portal link).
- `HELP_CENTER_CREDENTIALS` *(Optional)*: API keys or tokens required if the documentation portal is restricted.
- `LOG_LEVEL`: String defining the verbosity of execution logs (e.g., `INFO`, `DEBUG`, `ERROR`).
- `SYNC_THROTTLE_MS`: Duration in milliseconds to pause between individual document operations to respect API rate limits.

---

## 5. Scheduling Strategy
- **Scheduled Trigger:** The synchronization container is triggered automatically once every 24 hours.
- **Infrastructure Provider:** The deployment runs as a scheduled task (Cron Job) on a cloud platform (e.g., Railway, Render, DigitalOcean, GCP, or AWS).
- **Scheduled vs. Persistent Service:** Running a scheduled container is preferred over maintaining a 24/7 active process because it:
  - Minimizes infrastructure hosting costs by only consuming resources during active sync runs.
  - Prevents resource leakage (memory, connections) common in long-running processes.
  - Aligns with the batch nature of documentation updates, which do not require real-time synchronization.
- **Lifecycle Status Check:** The container execution exit code determines scheduling success or failure (exit code `0` flags a successful sync, while any other integer signals a failure to trigger alerts in the hosting platform).

---

## 6. Logging & Observability
- **Standard Output (stdout):** All logs (execution flows, article status, warnings) are printed directly to stdout. This ensures cloud logging utilities capture and store run histories.
- **Sync Summary:** Every execution run must output a clear final log entry showing the counts of sync actions:
  - `added`: Number of new documents uploaded.
  - `updated`: Number of modified documents updated in the store.
  - `skipped`: Number of unchanged documents left untouched.
- **Error Log Isolation:** Critical exceptions (connection dropouts, authorization failures) must be logged as `ERROR` and caught by standard alerting configurations.

---

## 7. Failure Handling
- **Container Crashes:** If the container exits with a non-zero code, the cloud scheduler flags the run as failed, saves the crash logs, and triggers administrator notifications.
- **API Failure & Network Fluctuations:** The application must utilize connection retries with exponential backoff.
- **Partial Sync:** If individual articles fail to process, the system must log the error, continue processing the remaining queue, and exit with a non-zero status code if critical tasks fail, ensuring the scheduler records the execution defect.

---

## 8. Security Considerations
- **No Hardcoded Secrets:** No keys are packed into the Docker image layers.
- **Variable Injection:** API keys must be injected dynamically into the container runtime environment by the cloud platform configuration dashboard.
- **Sanitized Logging:** The application must actively redact or omit authorization credentials and API tokens from execution output logs to prevent credential leakage.

---

## 9. Scalability & Idempotency
- **Idempotency Strategy:** Sync executions are designed to be fully idempotent. Re-running the sync sequence multiple times on unchanged documentation performs no API modifications. This is enforced by matching local/remote document signatures (Article IDs + content hash comparisons).
- **Document Volume:** The single-run task model easily handles growth from 30 articles to thousands by utilizing paginated API fetches.
- **Scheduling Frequency:** The scheduler can be configured to run multiple times per day (e.g., every 12 hours) by modifying the Cron trigger without altering the code.
- **Vector Store Growth:** File lists are handled programmatically, ensuring the Sync Coordinator can index larger Vector Stores efficiently.

---

## 10. Assumptions
- The deployment environment supports execution of Docker containers.
- The cloud hosting provider offers a scheduling/Cron mechanism to run containerized tasks on a recurring timetable.
- Valid API keys are populated in the deployment platform dashboard before execution.
- The container runtime has egress network access to reach the Help Center and AI platform endpoints.

---

## 11. Success Criteria
The deployment is successful when:
- The scheduled container executes once and terminates cleanly (exiting with status code `0`) daily.
- All ingestion, cleaning, delta checking, and vector store uploads complete without manual execution.
- Runtime logs are readable on the deployment platform, displaying the delta statistics clearly.
- Unchanged articles are skipped correctly, new/modified articles sync to the AI assistant, and stale/orphaned articles are cleaned up.
