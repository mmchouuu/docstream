# Coding Standards & Conventions

This document defines the code quality guidelines, architectural constraints, and engineering conventions required for the implementation.

---

## 1. Python Standards

### Naming Conventions
- **Modules & Packages:** Must use lowercase snake_case (e.g., `state_manager.py`).
- **Classes:** Must use PascalCase (e.g., `ZendeskScraper`).
- **Functions, Methods, & Variables:** Must use snake_case (e.g., `calculate_checksum`).
- **Constants:** Must use UPPER_SNAKE_CASE (e.g., `MAX_RETRIES`).

### File Structure Rules
- Every module file must contain:
  1. Standard imports sorted alphabetically (Standard Library first, Third-Party second, Local package third).
  2. Module-level constants.
  3. Core class definitions or functions.
- Class definitions must list private properties and initialization logic at the top, followed by public methods, and then private helper methods.

### Type Annotations
- All function and method declarations must use type hints for parameters and return types.
- Utilize the `typing` module or native type hints (e.g., `def parse_html(raw_html: str) -> str:`).

### Error Handling Style
- Use explicit exception handling blocks.
- Never use blank `except:` catch-alls. Always catch specific exceptions (e.g., `requests.RequestException`).
- Catch errors locally in subclasses and raise custom module-specific exceptions when passing error states up the call stack to keep errors structured.

---

## 2. Architectural Rules

### Separation of Concerns
- Business logic (identifying changed files) must remain completely decoupled from ingestion (network calls) and integration (API pushes).
- Lower-level modules must focus on a single responsibility:
  - Scraper fetches data only.
  - Normalizer formats content only.
  - Client sends API payloads only.

### Dependency Direction
- Dependencies must strictly flow one-way:
  ```text
  [ Ingestion Module ] ──➔ [ Synchronization Module ] ──➔ [ AI Integration Module ]
  ```
- Modules at the start of the chain must not import or depend on modules downstream.

### Circular Imports Prevention
- Avoid circular imports by ensuring that common models, types, and schemas are isolated into a dedicated `models/` module.
- Never write relative imports referencing sibling sub-packages directly.

---

## 3. Logging Rules

### Structured Logging
- Use Python's built-in `logging` module. `print()` statements are prohibited in production modules.
- Format log entries consistently with a standard header: `[TIMESTAMP] [LEVEL] [MODULE] - Message`.

### Console Output (stdout)
- All log messages must write directly to standard output (`stdout`) to ensure they are captured by container logging layers.

### Sync Metrics Output
- Upon finishing the synchronization run, the sync coordinator must output a structured stats summary formatted exactly as follows:
  ```text
  === Synchronization Summary ===
  Status: [Success/Failure]
  Added: [Count]
  Updated: [Count]
  Skipped: [Count]
  ==============================
  ```

---

## 4. API Design Rules

### Wrapper Pattern
- Direct calls to third-party SDK clients (such as `openai` or `google-generativeai`) are prohibited inside the core synchronization logic.
- Implement a wrapper class in the `ai_integration/` module that exposes simple, high-level method interfaces (e.g., `upload_document()`, `delete_document()`).

### Decoupled Credentials
- Wrapper clients must not load environment secrets directly inside their initialization block.
- Credentials must be passed as constructor parameters injected from `main.py`.

---

## 5. Data Handling Rules

### Directory Layout
- **Raw Cache:** Extracted raw content is saved in `data/raw/`.
- **Markdown Outputs:** Converted Markdown files are saved in `data/markdown/`.
- **State Repository:** Synchronization hashes and state JSON lists are saved in `data/state/`.
- All operational data paths must resolve dynamically relative to the workspace directory using `pathlib.Path`.

### Document Front-Matter Structure
- Converted Markdown documents must prefix their body with a structured header (YAML front-matter syntax) delimited by `---` lines.

### Signature Validation
- The checksum hash of a normalized article must be calculated using the SHA-256 algorithm on the clean Markdown content string.
- Checksums are used exclusively to determine modifications during the synchronization phase.
