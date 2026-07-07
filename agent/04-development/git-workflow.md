# Git Workflow Guidelines

This document defines the branching strategy, commit requirements, and integration workflows for the source code repository.

---

## 1. Branch Strategy

The project utilizes a simplified branching model to coordinate development:

- **`main`**: The production-ready branch representing the most stable, reviewed state of the application. Code is merged here from `dev` only after a final review of the complete codebase integration.
- **`dev`**: The integration branch. Feature branches are merged here first to verify joint compatibility.
- **Feature Branches (`feature/*`, `fix/*`, `docs/*`)**: Short-lived branches created for specific tasks. Developers write code here and submit Pull Requests (PRs) targeting the `dev` branch.

---

## 2. Commit Rules

### Atomic Commits
- Commit changes in small, logical units. A single commit should cover one cohesive modification (e.g., implementing the HTML cleaner, adding tests for normalizer).
- Avoid monolithic commits containing multiple unrelated features or bug fixes.

### Naming Conventions
Commits must follow the **Conventional Commits** standard using the format: `type(scope): description`.

Allowed types:
- `feat`: A new feature (e.g., `feat(scraper): implement Zendesk API article retrieval`)
- `fix`: A bug fix (e.g., `fix(sync): resolve offset parsing error in pagination`)
- `docs`: Documentation changes (e.g., `docs(readme): add environment setup instructions`)
- `test`: Adding or correcting tests (e.g., `test(normalizer): add HTML list parsing unit tests`)
- `chore`: Maintenance tasks (e.g., `chore(deps): update third-party library versions`)

### Commit Examples
- `feat(normalizer): convert HTML table elements into Markdown tables`
- `fix(assistant): update URL citation parsing regex pattern`
- `docs(rules): clarify logging requirements for delta execution`

---

## 3. Workflow Steps

### Development Cycle
1. Switch to `dev` and pull the latest changes: `git checkout dev && git pull origin dev`.
2. Create and switch to a feature branch: `git checkout -b feature/your-feature-name`.
3. Implement code changes locally matching the task requirements.

### Testing Before Commit
- Before staging files, run all unit and integration tests locally.
- Run code validation checkers to verify syntax and PEP 8 compliance.
- Confirm that the application executes successfully and terminates with exit code `0`.

### Merge & Integration Process
1. Push the local feature branch to the remote repository: `git push origin feature/your-feature-name`.
2. Open a Pull Request targeting the **`dev`** branch.
3. Once the code passes review and checks, merge the PR into **`dev`** (using squash-merge to maintain clean history).
4. After verifying all integrated features on the **`dev`** branch, submit a final PR/Review to merge the completed code from **`dev`** into **`main`**. Nhánh `main` sẽ là nhánh cuối cùng hoàn chỉnh nhất đại diện cho code chạy thực tế.

---

## 4. CI Readiness
- The repository structure is prepared to support automated Continuous Integration (CI).
- In a production pipeline, pushing to `dev` or `main` will trigger automated test runners to execute the test suite in `tests/` and verify the Docker image build.
- Commits exiting with non-zero codes will halt the pipeline and block merges.

---

## 5. Repository Constraints
- **Cryptic Naming:** The remote repository must be named using a cryptic or non-obvious name (e.g., avoiding terms like `optisigns` or `optibot`) as specified in the assignment. This prevents other candidates from finding the codebase through search engines.
- **Strict Secret Prevention:** Developers must review the git diff prior to committing to ensure no active `.env` files or hardcoded credentials are included.
