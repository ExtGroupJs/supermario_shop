# Spec: Add SDD workflow and constitution

## Goal
Add Spec-Driven Development (SDD) workflow to AGENTS.md and create specs/constitution.md with repo conventions to standardize how issues/features are implemented.

## User Story
As a developer working on this repo, I want a documented SDD workflow and a clear constitution, so that implementations follow the existing DRF patterns consistently and with minimal deviation.

## Requirements
- MUST document SDD steps in AGENTS.md (understand, research with graph-first, create spec/design/tasks, implement task-by-task, verify).
- MUST create specs/constitution.md capturing DRF Structure Standard (models, viewsets, serializers, URLs), mixin order, permissions, filters, pagination, graph usage priority, testing/lint conventions.
- MUST follow repo rules: English in code/docstrings, minimal changes, no new layers unless justified, use graph tools first.
- MUST be consistent with existing AGENTS.md content.

## Acceptance Criteria
- [ ] AGENTS.md contains "SDD Workflow (Spec-Driven Development)" section with the 7 steps listed.
- [ ] specs/constitution.md exists with Core Rules, DRF Structure Standard sections, Graph Usage, Testing & Lint.
- [ ] Constitution matches repo conventions (GenericLogMixin first, SafeDeleteModel second, BaseModel last; 3 filter backends; CommonRolePermission; SerializerMapMixin; annotate in queryset).
- [ ] Changes are minimal and only touch AGENTS.md and specs/constitution.md (plus any necessary __init__ if creating folder, but folder created).

## Out of Scope
- Creating other specs files beyond constitution context.
- Modifying existing code behavior (models/views/serializers/urls logic).
- Changing CI/deploy or tooling configs beyond docs.

## Business Rules / Permissions
- N/A (documentation only).

## Affected Entities
- AGENTS.md (docs)
- specs/constitution.md (new)
- specs/326-add-sdd-workflow-and-constitution/ (folder for traceability)
