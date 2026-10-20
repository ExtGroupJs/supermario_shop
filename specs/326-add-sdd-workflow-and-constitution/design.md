# Design: Add SDD workflow and constitution

## Existing Pattern
- AGENTS.md already documents project setup, architecture, DRF Structure Standard, graph usage, testing conventions.
- No specs/ directory existed before; constitution is the canonical ruleset extracted from AGENTS.md.
- Graph-first approach is already mandated in AGENTS.md.

## Changes
- AGENTS.md: Add new section "## SDD Workflow (Spec-Driven Development)" after Project intro and before Codebase Knowledge Graph. Mirror exact intent.
- specs/constitution.md: New file capturing Core Rules + DRF Structure Standard + Graph Usage + Testing & Lint, aligned to current repo (mixin order, filter_backends, permissions, pagination, SerializerMapMixin, annotate in queryset, role-based get_queryset).

## Role-based filtering
- N/A (docs only).

## Tests
- No runtime code changes; no new tests required. Validation via existing checks (lint/docs consistency).

## Minimal Touchpoints
- AGENTS.md
- specs/constitution.md
- specs/326-add-sdd-workflow-and-constitution/spec.md (created for traceability)
- specs/326-add-sdd-workflow-and-constitution/design.md (created)
- specs/326-add-sdd-workflow-and-constitution/tasks.md (created)

## Notes
- Keep English as requested. Follow minimal-change principle. No new layers introduced.
