# Agent Workspace

## Overview

The `agent/` directory serves as the project's knowledge base and documentation workspace.

It contains all project-related information, including:

- Original assignment
- Requirement analysis
- System design
- Development planning
- Engineering rules
- Architecture decisions
- Review notes
- Current project status

The purpose of this workspace is to provide both developers and AI assistants with a single source of project knowledge throughout the entire software development lifecycle.

---

# Objectives

The Agent Workspace aims to:

- Preserve the original assignment.
- Document project requirements.
- Record architectural decisions.
- Track implementation progress.
- Maintain development consistency.
- Help AI assistants understand project context before generating code.

---

# Directory Structure

```text
agent/
│
├── 00-source/
├── 01-analysis/
├── 02-design/
├── 03-planning/
├── 04-development/
├── 05-review/
├── 06-decisions/
├── 07-current/
└── README.md
```

---

# Reading Order

AI assistants should read the documentation in the following order:

1. `00-source/assignment.md`
2. `01-analysis/summary.md`
3. `01-analysis/requirements.md`
4. `02-design/architecture.md`
5. `03-planning/todo.md`
6. `04-development/rules.md`
7. `07-current/current-task.md`

This order ensures that the assistant understands:

- the original assignment,
- project goals,
- functional requirements,
- system architecture,
- current progress,
- development rules,
- and the current implementation task.

---

# Documentation Rules

## 1. Source Documents

`00-source/`

Contains original project documents.

Rules:

- Never modify the original content.
- Only convert formatting if necessary (e.g. PDF → Markdown).
- Preserve the original meaning.

---

## 2. Analysis Documents

`01-analysis/`

Contains project analysis derived from the assignment.

These documents may evolve during development if project understanding improves.

---

## 3. Design Documents

`02-design/`

Contains implementation decisions, including:

- architecture
- folder structure
- scraper design
- assistant design
- deployment strategy

Update these documents whenever the architecture changes.

---

## 4. Planning Documents

`03-planning/`

Tracks project execution.

Update:

- roadmap
- milestones
- todo
- timeline

throughout the project.

---

## 5. Development Documents

`04-development/`

Defines engineering conventions.

These files should remain stable unless the coding standards change.

---

## 6. Review Documents

`05-review/`

Stores:

- review notes
- discovered bugs
- improvements
- final submission checklist

Update continuously during testing.

---

## 7. Decision Log

`06-decisions/`

Every significant technical decision should be recorded.

Each entry should include:

- Decision
- Reason
- Alternatives Considered
- Consequences

---

## 8. Current Task

`07-current/current-task.md`

Represents the current working state.

This document should always answer:

- What has been completed?
- What is being implemented?
- What comes next?
- Are there any blockers?

AI assistants should always read this document before generating code.

---

# AI Collaboration Guidelines

Before writing code, AI assistants should:

1. Read the required documentation.
2. Understand the current implementation phase.
3. Follow the coding rules.
4. Avoid making assumptions that contradict the assignment.
5. Keep generated code consistent with the project architecture.

---

# Documentation Maintenance

Whenever the project changes:

- Update the relevant documentation.
- Record important architectural decisions.
- Keep the TODO list synchronized.
- Update the current task status.
- Document new assumptions if necessary.

The documentation should always reflect the current state of the project.

---

# Source of Truth

Priority of information:

1. `00-source/assignment.md`
2. Project implementation
3. Analysis documents
4. Design documents
5. Planning documents

If conflicts occur, the original assignment always has the highest priority.

---

# Version

Version: 1.0

Last Updated: YYYY-MM-DD