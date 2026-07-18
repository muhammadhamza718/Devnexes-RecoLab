---
id: 001
title: Project Constitution Creation
stage: constitution
date: 2026-07-16
surface: agent
model: claude-sonnet-4.5
feature: none
branch: main
user: Muhammad Hamza Samad
command: constitution
labels: ["constitution","documentation","standards"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
 - .specify/memory/constitution.md
tests:
 - none
---

## Prompt

Hi.

I want you to put these rules in a constitutions file. and in the CLAUDE.md, AGENT.md file keeping their own rules same as it is in the files. 

"""
You will be given enough time to complete each task, so please use it properly for research, planning, development, and testing.

This may be your first professional project, and that is completely fine. However, you are expected to put in your best effort and develop it in a clean, organized, and professional way.

You may use AI tools for guidance, but make sure you understand, review, and test everything before submission. Keep your code well-structured, push progress regularly to GitHub, and do not wait until the final deadline.

The goal is not just to complete the project, but to learn properly and build something you can confidently add to your portfolio.
"""

The following constitution file is from other projects. 
But its has some improtant rules. 
I want you to adapt these rules in this current project. 
And leave that projects instructions.

"""
# SmartServe AI Vendor System Constitution

**Project**: SmartServe AI Vendor Dashboard  
**Owner**: Muhammad Hamza Samad  
**Version**: 2.0.0 | **Ratified**: 2026-07-09 | **Last Amended**: 2026-07-13

---

## Core Principles

### I. Quality-First Development
Every feature must meet strict quality standards before being considered complete. Quality is not optional or an afterthought—it is a fundamental requirement of every development task.

### II. Spec-Driven Development (SDD)
All development follows the Spec-Driven Development lifecycle: **Spec → Plan → Tasks → Implementation**. No implementation work begins without approved specifications, plans, and tasks.

### III. Test-Driven Development (TDD)
Tests are written before implementation. The Red-Green-Refactor cycle is strictly enforced for all critical business logic and shared components.

### IV. Blast-Radius Awareness
Every change must consider its impact on the entire codebase. Internal impact research identifies all consumers before any symbol is modified.

### V. Security & Performance Standards
Security and performance are non-negotiable requirements. All code must follow security best practices and meet defined performance benchmarks.

### VI. Incremental Delivery
Work is delivered in small, testable increments. One task = one commit. Changes are revertable in isolation.

---

## Quality & Prevention Rules

### Forbidden Patterns (NON-NEGOTIABLE)

1. **No `any` types** (except debug files with explicit ESLint override comment)
   - Rationale: `any` defeats TypeScript's type safety and defeats the purpose of using TypeScript
   - Exception: Debug files may use `any` with `// eslint-disable-next-line @typescript-eslint/no-explicit-any` 

2. **No `require()` imports** (except config/debug files)
   - Rationale: ES6 imports provide better tree-shaking and type inference
   - Exception: Configuration files and debug utilities may use `require()` 

3. **No unused variables/imports**
   - Rationale: Unused code indicates incomplete refactoring or dead code
   - Action: Remove unused imports immediately, comment out unused variables with TODO if intentional

4. **No synchronous `setState` in `useEffect`**
   - Rationale: Causes infinite loops and performance issues
   - Action: Use functional updates or dependency arrays correctly

5. **No empty interfaces** (unless extending single base for contracts)
   - Rationale: Empty interfaces provide no type safety
   - Exception: Extending a single base interface for contract compliance

### Code Quality Standards

1. **Type Safety**: All functions must have explicit return types. All parameters must have types.
2. **Error Handling**: All async operations must have try-catch blocks. All API calls must handle errors.
3. **Naming**: Use descriptive names. No abbreviations unless widely understood (e.g., `id`, `url`).
4. **Code Organization**: Follow the established project structure. No arbitrary file placement.
5. **Comments**: Add comments for complex logic. No comments for obvious code.

---

## Test Quality Rules

### Test Coverage Requirements

1. **Unit Tests**: Required for all business logic, utility functions, and custom hooks
2. **Component Tests**: Required for all React components using React Testing Library
3. **Integration Tests**: Required for API routes and database operations
4. **E2E Tests**: Required for critical user flows (login, booking, payment)

### Test Standards

1. **Test Naming**: Tests must describe what they test and the expected outcome
2. **Test Independence**: Tests must not depend on each other. Each test must be runnable in isolation.
3. **Test Speed**: Unit tests must complete in < 100ms. Integration tests in < 1s.
4. **Test Maintenance**: Tests must be updated alongside implementation changes

### Test Failure Remediation

1. **Detect Early**: Run tests after every task completion
2. **Fix Alongside**: Fix failed tests in the same task/commit (never separate)
3. **Root Cause First**: Diagnose why tests failed before fixing (regression? outdated? missing?)
4. **Document**: Add test fixes to task's Implementation Steps/Acceptance Criteria
5. **Re-Verify**: Re-run all verification gates after fixing tests

---

## Verification Command Reference

### Tier 1 Verification (Every Task)
Run these commands after every task completion:

```bash
# Type checking
npx tsc --noEmit

# Linting
npm run lint

# Format checking
npm run format:check

# Build verification
npm run build

# Unit tests
npm test
npm test -- --ci

# Database schema validation
npx prisma validate
```

### Tier 2 Verification (Before Integration Merge)
Run these commands before merging into integration branch:

```bash
# Integration tests
npm run test:integration

# E2E tests
npx playwright test
```

### Pre-Implementation Hard Gate
Before starting any implementation work:

1. Run all Tier 1 verification commands
2. Capture baseline results
3. If issues exist: STOP and present to user
4. User must approve/fix before proceeding

### Post-Implementation Full Verification Gate
After ALL tasks complete:

1. Run ALL verification commands (Tier 1 + Tier 2)
2. Confirm zero new issues vs baseline
3. Only mark as done if ALL checks pass

---

## Development Workflow

### Branching Strategy

1. **Main Branch**: `hamza` - Production-ready code
2. **Feature Branches**: `feature/<phase>-<description>` - Isolated feature work
3. **Integration Branch**: `feature/phase2-phase3-completion` - Long-lived integration point
4. **Commit Discipline**: One task = one commit. Never batch multiple tasks.

### Spec-Driven Development Lifecycle

1. **Specification**: Create detailed spec.md with requirements, constraints, and success criteria
2. **Planning**: Create plan.md with architecture, blast radius map, and implementation strategy
3. **Tasks**: Create tasks.md with testable tasks, consumer impact, and acceptance criteria
4. **Implementation**: Execute tasks one by one, verifying after each
5. **ADR**: Document architectural decisions when needed
6. **PHR**: Create Prompt History Record for every session

### Code Review Process

1. **Self-Review**: Review your own code against constitution rules
2. **Verification**: Run all verification commands
3. **Documentation**: Update inline comments and API docs
4. **Cleanup**: Remove console.log, unused code, temporary files

---

## Security & Performance Standards

### Security Requirements

1. **Authentication**: JWT tokens with proper expiration and refresh mechanism
2. **Authorization**: Role-based access control (RBAC) for all protected routes
3. **Input Validation**: All user inputs must be validated and sanitized
4. **SQL Injection**: Use parameterized queries (Prisma ORM)
5. **XSS Prevention**: Sanitize all user-generated content (DOMPurify)
6. **Secrets Management**: Never hardcode secrets. Use environment variables.

### Performance Requirements

1. **API Latency**: p95 < 500ms for all API endpoints
2. **Page Load**: P95 < 3s for all dashboard pages
3. **Database Queries**: Optimize queries, use indexes, avoid N+1 queries
4. **Bundle Size**: Keep JavaScript bundles under 200KB gzipped
5. **Image Optimization**: Compress images, use modern formats (WebP)

---

## Governance

### Constitution Authority

This constitution supersedes all other practices and guidelines. All development work must comply with these rules.

### Amendment Process

1. Any amendment must be documented with rationale
2. Amendments require approval from project owner
3. Migration plan required for breaking changes
4. All team members must be notified of amendments

### Compliance Verification

1. All PRs must verify compliance with constitution rules
2. All merges must pass verification gates
3. Non-compliant code will be rejected
4. Complexity must be justified with clear rationale

### Runtime Guidance

For specific implementation guidance during development, refer to:
- `.workflows/deep-research-spec-plan-workflow.md` - Workflow procedures
- `phases.md` - Project phases and deliverables
- `AGENTS.md` - Agent-specific guidelines
- Design documents in `docs/superpowers/specs/` - Detailed design specs
"""


Organize everything we needed to build and each and everything must be documented and well organized. 
And the purpose is to make the well-organize structure + system of record. 

## Response snapshot

I successfully created a comprehensive project constitution file at `.specify/memory/constitution.md` that combines:

1. **Your Core Philosophy**: Time management, professional development standards, AI tool usage guidelines, and portfolio-quality expectations
2. **Adapted SmartServe Rules**: Quality-first development, SDD lifecycle, TDD requirements, forbidden patterns, testing standards, verification commands, and security/performance standards
3. **Project-Specific Adaptations**: Removed project-specific references, made branching strategy generic, adapted technical requirements to be broadly applicable

The constitution includes:
- Project philosophy & core values
- Development principles (Quality-First, SDD, TDD, Blast-Radius Awareness, Security & Performance, Incremental Delivery)
- Quality & prevention rules with forbidden patterns
- Test quality rules and coverage requirements
- Verification command reference (Tier 1 & Tier 2)
- Development workflow and branching strategy
- Security & performance standards
- Documentation & organization standards
- Governance and compliance verification
- Professional development standards
- Success criteria
- Project structure template

The CLAUDE.md and AGENTS.md files were kept unchanged as requested, maintaining their existing agent-specific rules and PHR creation processes.

## Outcome

- ✅ Impact: Created comprehensive project constitution establishing quality standards, development workflow, and documentation requirements for all internship projects
- 🧪 Tests: No tests run (documentation task)
- 📁 Files: Created `.specify/memory/constitution.md` (335 lines) and corresponding PHR record
- 🔁 Next prompts: User may want to review constitution, suggest amendments, or begin applying it to specific projects
- 🧠 Reflection: Successfully combined user's philosophy with adapted best practices while maintaining agent guideline compatibility

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A (documentation task)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A (constitution accepted as foundational document)
