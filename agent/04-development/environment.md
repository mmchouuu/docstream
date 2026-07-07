# Environment Configuration Strategy

This document defines the configuration loading workflow, environment variable definitions, and secret management guidelines for the project.

---

## 1. Environment Variables

The application requires the following variables to be defined in the running environment:

### Credentials & Keys
- `AI_API_KEY`: API credential key required to connect to the selected AI Platform (e.g., OpenAI or Google Gemini).
- `HELP_CENTER_TOKEN` *(Optional)*: API token or key if the Help Center portal requires authentication for article retrieval.

### AI Assistant & Storage Identifiers
- `VECTOR_STORE_ID`: The unique identifier of the platform Vector Store where Markdown documents are synced.
- `ASSISTANT_ID`: The unique identifier of the AI Assistant configured to answer support questions.

### Base Endpoint URLs
- `HELP_CENTER_API_URL`: The baseline endpoint for the Help Center (e.g., `https://support.optisigns.com/api/v2/help_center`).
- `HELP_CENTER_PAGE_URL`: The public landing page URL of the support site (e.g., `https://support.optisigns.com`), used to rebase relative article links.

### Synchronization Parameters
- `SYNC_THROTTLE_MS`: Time delay in milliseconds between sequential document API requests to avoid triggering rate limit rules.
- `MAX_CONNECTION_RETRIES`: Number of connection retry attempts for failed HTTP operations before raising a failure.

---

## 2. `.env` Usage Strategy

### Loading Workflow
- In local development, variables must be loaded automatically during application startup from a local `.env` file located in the project root.
- The entry module (`src/main.py`) handles variable loading.

### Safety Rules
- **Git Exclusion:** The `.env` file contains sensitive operational credentials and must never be committed to source control. The `.gitignore` file must explicitly exclude `.env` and `.env.*`.
- **Stateless Cloud Loading:** When running in containerized cloud environments, the container must load environment variables directly from the hosting platform's configuration dashboard rather than reading a local `.env` file.

### `.env` vs `.env.sample`
- **`.env.sample`:** A public template committed to the repository. It outlines all required configuration keys but contains no actual secret values.
- **`.env`:** A local-only file containing active developers' credentials.

---

## 3. Configuration Layering

The system resolves configurations using a strict precedence hierarchy (highest priority first):

```text
[ 1. Runtime CLI Overrides ] ──➔ [ 2. Environment Variables ] ──➔ [ 3. Default Fallbacks ]
```

1.  **Runtime CLI Overrides:** Execution parameters passed directly via the command line interface during manual testing.
2.  **Environment Variables:** Configuration values injected via the host platform environment or loaded from the `.env` file.
3.  **Default Fallbacks:** Built-in fallback parameters defined in the source code configuration classes (e.g., default retry settings).

---

## 4. Security Considerations
- **No Hardcoded Values:** Default values in code config classes must only cover non-sensitive parameters (e.g., connection retry counts). Under no circumstances should default credentials, URLs, or store IDs be defined in source code.
- **Sanitized Outputs:** Logs must never print out the values of `AI_API_KEY`, `HELP_CENTER_TOKEN`, or other credential strings.
- **Minimal System Access:** Avoid importing entire environment dumps into logs or application models. Load and sanitize only target variables defined in the configuration schema.
