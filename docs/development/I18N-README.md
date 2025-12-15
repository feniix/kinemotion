# Internationalization (i18n) Implementation Guide

**⚠️ IMPORTANT**: This guide covers **future work** - internationalization of backend validation messages.

**Currently Completed**: Frontend UI i18n for user-facing strings (English, Spanish, French). See `frontend/` components for current implementation.

______________________________________________________________________

## Document Index

This documentation is for implementing **backend validation message i18n** (future roadmap item).

### 1. **Summary** - Start Here

📄 **File**: `i18n-summary.md`

**What to read**: Executive overview, implementation scope, timeline
**Time to read**: 10 minutes
**Key sections**:

- Why Option B (Structured Data) is recommended
- What gets implemented (backend + frontend)
- Implementation scope and effort estimate
- JSON response example
- Backward compatibility guarantee

**Best for**: Understanding the overall approach and getting buy-in from stakeholders

______________________________________________________________________

### 2. **Specification** - Complete Technical Reference

📄 **File**: `i18n-validation-messages-specification.md`

**What to read**: Detailed technical specs, data models, implementation details
**Time to read**: 30-45 minutes
**Key sections**:

- Architecture decision rationale (Option A vs B)
- Data model changes (ValidationIssue, ValidationResult)
- Message key naming convention
- Backend implementation (step-by-step code changes)
- Frontend implementation (i18next setup, components)
- Testing strategy with code examples
- Migration checklist
- Complete message key reference

**Best for**: Developers implementing the feature, code reviewers, QA engineers

______________________________________________________________________

### 3. **Quick Start Guide** - Step-by-Step Implementation

📄 **File**: `i18n-quick-start-guide.md`

**What to read**: Actionable implementation steps, code templates
**Time to read**: 20-30 minutes for overview, reference during implementation
**Key sections**:

- Phase 1: Backend implementation (6 steps)
- Phase 2: Frontend implementation (5 steps)
- Phase 3: Integration testing
- Detailed code examples for each step
- Testing code snippets
- Implementation checklist
- Deployment steps
- Rollback plan

**Best for**: Developers actually implementing the feature (use as a guide)

______________________________________________________________________

### 4. **Architecture Diagram** - Visual Guide

📄 **File**: `i18n-architecture-diagram.md`

**What to read**: Visual representations of data flow, component architecture
**Time to read**: 15-20 minutes
**Key sections**:

- Data flow from video upload to rendered UI
- Component architecture diagram
- Message key resolution flow
- Message key namespace structure
- Backward compatibility timeline
- Language auto-detection strategy
- Testing strategy matrix

**Best for**: Understanding how components interact, architectural decisions, planning

______________________________________________________________________

### 5. **Cheat Sheet** - Quick Reference

📄 **File**: `i18n-cheat-sheet.md`

**What to read**: Quick reference during implementation
**Time to read**: 5-10 minutes (for quick lookup)
**Key sections**:

- Quick reference code snippets
- Message key patterns
- JSON response fields
- Translation template placeholders
- Code changes summary
- Time estimates
- Common mistakes to avoid
- Validation checklist

**Best for**: Developers implementing the feature (bookmark and print!)

______________________________________________________________________

## Reading Recommendations

### For Developers

1. Start with **Summary** (10 min) - understand the approach
1. Read **Quick Start Guide** (30 min) - get implementation steps
1. Keep **Cheat Sheet** open during implementation (reference as needed)
1. Reference **Specification** (30 min) - for detailed info on specific changes

### For Project Managers

1. Start with **Summary** (10 min) - understand scope and timeline
1. Review **Quick Start Guide** checklist (5 min) - track progress

### For QA/Testing Engineers

1. Start with **Summary** (10 min) - understand the feature
1. Read **Specification** testing strategy section (10 min) - understand test approach
1. Reference **Quick Start Guide** testing section (10 min) - test code examples
1. Use **Cheat Sheet** validation checklist (5 min) - test execution

### For Code Reviewers

1. Read **Summary** (10 min) - understand the approach
1. Read **Specification** sections 1-2 (15 min) - understand data model changes
1. Reference **Specification** code implementation sections (as needed)
1. Use **Cheat Sheet** common mistakes (5 min) - what to look for

### For Architects/Decision Makers

1. Read **Summary** (10 min)
1. Review **Architecture Diagram** (15 min)
1. Check **Backward Compatibility** section (5 min)

______________________________________________________________________

## Key Facts at a Glance

| Aspect              | Detail                                                  |
| ------------------- | ------------------------------------------------------- |
| **Approach**        | Option B: Structured Data + Frontend Translation        |
| **Breaking Change** | No - Fully backward compatible                          |
| **New Version**     | v0.60.0 (minor version bump)                            |
| **Effort**          | 14-20 hours (backend 4-6h, frontend 6-8h, testing 4-6h) |
| **Files to Change** | 5 backend + 10 frontend files                           |
| **Message Keys**    | ~45-50 (organized by metric)                            |
| **Languages**       | 5 (en, es, fr, de, ja)                                  |
| **Tests**           | 10-20 new tests (backend + frontend)                    |
| **Backward Compat** | Yes - message field still works                         |

______________________________________________________________________

## Implementation Checklist

### Before Starting

- [ ] Read Summary (i18n-summary.md)
- [ ] Read Quick Start Guide (i18n-quick-start-guide.md)
- [ ] Print Cheat Sheet (i18n-cheat-sheet.md)
- [ ] Review Architecture (i18n-architecture-diagram.md)

### Phase 1: Backend

- [ ] Update ValidationIssue dataclass
- [ ] Update add_error/add_warning/add_info methods
- [ ] Update CMJ validator (16 methods)
- [ ] Update Drop Jump validator (6 methods)
- [ ] Update serialization (to_dict)
- [ ] Add backend tests
- [ ] Run full test suite
- [ ] Verify backward compatibility

### Phase 2: Frontend

- [ ] Create translation files (5 languages)
- [ ] Install i18next + react-i18next
- [ ] Setup i18next configuration
- [ ] Update ValidationIssue component
- [ ] Add language selector (optional)
- [ ] Add frontend tests
- [ ] Run linting and type checks

### Phase 3: Integration

- [ ] Run E2E tests
- [ ] Test all languages
- [ ] Verify number formatting
- [ ] Test language switching
- [ ] Test URL parameters
- [ ] Test localStorage persistence
- [ ] Verify message key completeness

### Pre-Release

- [ ] All tests passing (620+ backend, frontend tests)
- [ ] No type errors (pyright strict)
- [ ] No linting errors (ruff)
- [ ] Code review complete
- [ ] Documentation updated
- [ ] CHANGELOG updated

______________________________________________________________________

## FAQ

**Q: Why Option B (Structured Data) instead of Option A (Backend Translation)?**
A: See Summary section "Why This Approach?" - better separation of concerns, scalability, maintainability.

**Q: Is this a breaking change?**
A: No. The `message` field continues to work. This is backward compatible.

**Q: How long does implementation take?**
A: 14-20 hours total (backend 4-6h, frontend 6-8h, testing 4-6h).

**Q: What if I only want to support 2 languages?**
A: Just create 2 translation files. The system is flexible.

**Q: Do I need to update every validator method?**
A: Yes. All 22 validation methods should be updated for consistency.

**Q: Can I implement this incrementally?**
A: Yes. Phase 1 (backend) can be deployed as v0.60.0 with both message and message_key fields. Phase 2 (frontend) can be deployed separately.

**Q: What happens to old clients?**
A: They continue using the `message` field, which is still populated. No issues.

**Q: How do I test this locally?**
A: See Quick Start Guide section on testing.

**Q: When should I do this?**
A: Recommended for v0.60.0 release (after MVP validation).

______________________________________________________________________

## Document Sizes

| Document                     | Pages  | Read Time       |
| ---------------------------- | ------ | --------------- |
| i18n-summary.md              | 10     | 10 min          |
| i18n-specification.md        | 20     | 30-45 min       |
| i18n-quick-start-guide.md    | 15     | 20-30 min       |
| i18n-architecture-diagram.md | 12     | 15-20 min       |
| i18n-cheat-sheet.md          | 8      | 5-10 min        |
| **Total**                    | **65** | **1.5-2 hours** |

______________________________________________________________________

## Implementation Timeline

```
Week 1 (Backend Implementation)
├─ Day 1: Update core validation.py
├─ Day 2: Update CMJ validator
├─ Day 3: Update Drop Jump validator
├─ Day 4: Serialization + testing
└─ Day 5: Code review + fixes

Week 2 (Frontend Implementation)
├─ Day 1: Create translation files
├─ Day 2: Setup i18next
├─ Day 3: Update components
├─ Day 4: Testing + fixes
└─ Day 5: Integration testing

Week 3 (QA & Release)
├─ Day 1-2: Full testing cycle
├─ Day 3: Documentation
├─ Day 4: Code review
└─ Day 5: Release (v0.60.0)
```

______________________________________________________________________

## Key Contacts

- **Architecture Questions**: See i18n-architecture-diagram.md
- **Implementation Help**: See i18n-quick-start-guide.md
- **Detailed Specs**: See i18n-validation-messages-specification.md
- **Quick Reference**: See i18n-cheat-sheet.md

______________________________________________________________________

## Version History

| Version | Date       | Changes               |
| ------- | ---------- | --------------------- |
| 1.0     | 2024-12-14 | Initial specification |

______________________________________________________________________

## Related Documentation

- **Project Roadmap**: `docs/strategy/MVP_VALIDATION_CHECKPOINTS.md`
- **Testing Guide**: `docs/development/testing.md`
- **Type Hints Guide**: `docs/development/type-hints.md`
- **Agents Guide**: `docs/development/agents-guide.md`

______________________________________________________________________

## Next Steps

1. **Read Summary** (10 minutes)
1. **Share with team** for feedback
1. **Create feature branch**: `feat/i18n-validation-messages`
1. **Follow Quick Start Guide** for implementation
1. **Track progress** using implementation checklist above
1. **Request code review** following specification
1. **Deploy to production** as v0.60.0

______________________________________________________________________

**Status**: ✅ Complete
**Last Updated**: 2024-12-14
**Maintained By**: Kinemotion Development Team
