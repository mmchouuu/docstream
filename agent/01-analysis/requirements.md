# Requirements Specification

This document defines the functional requirements, non-functional requirements, technical constraints, deliverables, dependencies, and project scope for the OptiBot Mini-Clone project.

---

# 1. Scope

The project aims to build a simplified AI-powered customer support assistant similar to OptiSigns' OptiBot.

The system retrieves support articles from the OptiSigns Help Center, converts them into clean Markdown documents, uploads them to an AI knowledge base, and enables an AI Assistant to answer customer questions using only the uploaded documentation.

The system must also support automated daily synchronization by detecting newly added or updated articles and uploading only the changed documents.

---

# 2. Functional Requirements

## FR-1: Content Ingestion

- The system shall retrieve at least 30 support articles from the official OptiSigns Help Center.
- The ingestion process shall extract only the primary article content.
- Headers, footers, navigation menus, advertisements, and other non-content elements shall be excluded.

---

## FR-2: Markdown Conversion

The system shall convert each retrieved HTML article into clean Markdown.

The conversion shall preserve:

- Heading hierarchy
- Code blocks
- Relative links

The generated Markdown documents shall be stored locally using deterministic and human-readable filenames.

---

## FR-3: Knowledge Base Management

The system shall programmatically upload Markdown documents to the selected AI platform's Vector Store or Knowledge Base.

The system shall:

- create new knowledge documents
- update existing documents
- manage document synchronization through API calls only

Manual uploads through a graphical user interface shall not be required.

---

## FR-4: AI Assistant

The system shall configure an AI Assistant that:

- answers questions using only the uploaded documentation
- provides concise and factual responses
- includes citations or references to the original support articles
- avoids generating unsupported information

---

## FR-5: Daily Synchronization

The system shall support scheduled daily execution.

During synchronization, the system shall:

- detect newly added articles
- detect updated articles
- upload only changed documents
- skip unchanged documents

The synchronization process shall record execution statistics including:

- added
- updated
- skipped

---

## FR-6: Error Handling

The synchronization process shall continue processing remaining articles if an individual article cannot be processed.

Failures shall be recorded in the execution logs.

---

## FR-7: Configuration

The application shall support configuration through environment variables.

No runtime configuration shall require modification of the source code.

---

# 3. Non-Functional Requirements

## NFR-1: Containerization

The application shall be packaged as a Docker container.

Running the container shall execute one synchronization cycle and terminate successfully.

---

## NFR-2: Security

The application shall not contain hardcoded:

- API keys
- credentials
- secrets

Sensitive configuration shall be loaded from environment variables.

A sample environment configuration file shall be provided.

---

## NFR-3: Observability

The synchronization process shall produce execution logs.

The logs shall include at least:

- added count
- updated count
- skipped count
- execution status

The latest execution logs or artifacts shall be publicly accessible.

---

## NFR-4: Source Code Quality

The project shall maintain:

- a clean project structure
- meaningful commit history
- readable code
- clear documentation

The repository name should be generic or cryptic to avoid direct association with the assignment.

---

## NFR-5: Maintainability

The system shall be modular and organized so that individual components can be maintained or extended independently.

---

# 4. Technical Constraints

- All interactions with the AI platform shall be performed programmatically through the official API.
- The synchronization container shall execute as a single-run process and terminate successfully after completion.
- The implementation shall remain compatible with Docker-based deployment environments.

---

# 5. Dependencies

## Data Source

- OptiSigns Help Center
- Zendesk Help Center API (if available)

---

## AI Platform

One of the following platforms may be used:

- OpenAI Assistants API + Vector Store
- Google Gemini API + Knowledge Base

---

## Deployment Platform

Any cloud platform capable of scheduled Docker execution, including:

- Railway
- Render
- DigitalOcean
- AWS
- Google Cloud Platform

---

# 6. Out of Scope

The following features are outside the scope of this project:

- User authentication
- User management
- Frontend web application
- Multi-language support
- Analytics dashboard
- Manual editing of the knowledge base

---

# 7. Deliverables

The final submission shall include:

- Private Git repository with complete source code
- Dockerfile
- `.env.sample`
- AI Assistant configured with uploaded documentation
- Automated daily synchronization job
- Incremental (delta) synchronization mechanism
- Public job logs or execution artifacts
- Screenshot showing the AI Assistant answering the required sample question with citations
- README containing:
  - setup instructions
  - local execution guide
  - environment configuration
  - chunking strategy
  - deployment instructions
  - link to job logs

---

# 8. Requirement Traceability

Each functional requirement shall be traceable to:

- the original assignment
- one or more design documents
- implementation tasks
- verification or testing activities