# Tasks: Add SDD workflow and constitution

## Implementation
- [x] 1. Create specs/ directory structure if missing (already exists)
- [x] 2. Update AGENTS.md to add SDD Workflow section (graph-first, 7 steps)
- [x] 3. Create specs/constitution.md with Core Rules, DRF Structure Standard, Graph Usage, Testing & Lint
- [x] 4. Create spec/design/tasks under specs/326-add-sdd-workflow-and-constitution/ for traceability

## Verification
- [x] AGENTS.md contains "SDD Workflow (Spec-Driven Development)" section
- [x] specs/constitution.md exists and reflects repo conventions
- [x] No unrelated files modified
- [x] English only, minimal changes
- [x] ruff check . (docs only; no Python changes) - run quick check
- [x] Files readable and consistent

## Run validation
- [x] `ruff check .` (should pass; no new Python code)
