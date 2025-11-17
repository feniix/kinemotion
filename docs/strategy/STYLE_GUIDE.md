# Documentation Style Guide

**For:** docs/strategy/ directory
**Purpose:** Ensure consistent formatting across all strategic and assessment documents
**Status:** Active - Apply to all files

______________________________________________________________________

## 📐 Header Structure

### Rule 1: One H1 Per Document

```markdown
# Document Title

Only ONE H1 at the very beginning of the file.
Never use H1 for subsections.
```

### Rule 2: H2 for Major Sections

```markdown
## Section Name

Use H2 (##) for all major section breaks.
Examples: Executive Summary, Key Findings, Timeline, etc.
```

### Rule 3: H3 for Subsections

```markdown
### Subsection Name

Use H3 (###) for subsections within major sections.
Maximum depth: H3. Do not use H4+ unless absolutely necessary.
```

### Rule 4: Avoid Mixed Heading Styles

```markdown
✅ CORRECT:
# Document Title
## Section
### Subsection

❌ WRONG:
# Document Title
#### Subsection (skipped H2 and H3)
```

______________________________________________________________________

## 📝 Metadata & Document Start

### Standard Header Format

Every document starts with:

```markdown
# Document Title

**Date:** November 17, 2025 | **Status:** Ready | **Audience:** Leadership/Architects/Developers

---

## [First Section]
```

### Metadata Template

Use inline bold formatting:

- `**Date:** November 17, 2025`
- `**Status:** [Ready/In Progress/Draft]`
- `**Audience:** [Who should read this]`
- `**Owner:** [Person/Team responsible]`
- `**Duration:** [How long to read]`

### Separators

Use `---` (three hyphens) between major sections for visual clarity.

______________________________________________________________________

## 📊 Lists & Formatting

### Unordered Lists - Use Hyphens

```markdown
✅ CORRECT:
- Item one
- Item two
- Item three

❌ WRONG:
* Item one
+ Item two
- Item three (mixing symbols)
```

### Ordered Lists - Use Numbers

```markdown
1. First item
2. Second item
3. Third item
```

### Bold & Italics

- **Bold:** Use for emphasis on key terms
- `**term**` for bold
- *Italic:* Use sparingly
- `*term*` for italic

### Code & Technical Terms

- `backticks` for inline code
- Triple backticks for code blocks with language tag
- No backticks for file paths or command names in prose

______________________________________________________________________

## 📋 Tables

### Format

```markdown
| Column 1 | Column 2 | Column 3 |
|----------|----------|----------|
| Data | Data | Data |
| Data | Data | Data |
```

### Rules

- Align pipes `|` vertically for readability
- Use `---` (at least 3 hyphens) for column separators
- Always include header row
- Maximum 5 columns (readability)
- Break into multiple tables if >5 columns needed

______________________________________________________________________

## 🎯 Emoji Usage

### Approved Emojis (Consistent Throughout)

**Status Indicators:**

- ✅ = Complete/Approved/Yes
- ⚠️ = Warning/Caution/Maybe
- 🔴 = Critical/No/Blocked
- 🟡 = Medium/In Progress
- 🟢 = Low/OK

**Section Headers:**

- 📊 = Data/Metrics/Tables
- 📋 = Lists/Checklists/Details
- 🎯 = Goals/Objectives/Focus
- 📈 = Growth/Timeline/Progress
- 🔑 = Key Points/Important
- ⚡ = Important/Critical
- 🚀 = Launch/Next Steps
- 🎓 = Learning/Education

### Rules

- Use consistently (same emoji for same concept)
- Max 1-2 emojis per heading
- Never use in body paragraphs
- Use for scanning/navigation, not content

______________________________________________________________________

## 📐 Spacing & Whitespace

### Blank Lines

- One blank line between sections
- One blank line after heading before content
- Two blank lines after major section header
- No more than 2 consecutive blank lines

```markdown
# Title

**Metadata here**

---

## Section 1

Content here.

### Subsection 1.1

More content.

---

## Section 2

Content continues.
```

### Line Length

- Target: \<100 characters (matches project standard)
- OK: \<120 characters
- Break long lines at logical points (not mid-word)

______________________________________________________________________

## 🎨 Callout Boxes & Emphasis

### Important Notes

Use blockquote format:

```markdown
> **Important:** This is a key point everyone should know.
```

### Definitions

```markdown
> **Term:** Definition of the term goes here.
```

### Code Examples

Use fenced code blocks:

````markdown
```python
def example():
    return "code"
```
````

______________________________________________________________________

## 📑 Document Sections Order

Recommended structure for all strategic documents:

1. **Title** (H1)
1. **Metadata** (Date, Status, Audience)
1. **Separator** (---)
1. **Executive Summary** (H2) - if applicable
1. **Key Findings** (H2) - if applicable
1. **Detailed Content** (H2 sections)
1. **Next Steps** (H2) - if applicable
1. **Questions?** (H2) - if applicable
1. **Footer** - Last Updated date

______________________________________________________________________

## ✅ Checklist Before Publishing

- [ ] One H1 only (document title)
- [ ] All major sections are H2
- [ ] All subsections are H3 (max)
- [ ] Metadata formatted consistently
- [ ] Lists use hyphens for bullets
- [ ] Code in backticks
- [ ] Tables properly aligned
- [ ] Emojis used consistently
- [ ] No lines >100 characters
- [ ] Proper spacing (1-2 blank lines max)
- [ ] Related documents linked at bottom
- [ ] Last Updated date present
- [ ] Spelling & grammar checked

______________________________________________________________________

## 🔗 Cross-References

### Linking to Other Docs

```markdown
[Document Name](./path/to/document.md)
[Agent Assessment](../BIOMECHANICS/01-executive-summary.md)
[Master Index](../README.md)
```

### Linking Within Doc

```markdown
## Table of Contents
- [Section 1](#section-1)
- [Section 2](#section-2)

...

## Section 1
```

______________________________________________________________________

## 📌 Common Patterns

### Verdict Statements

```markdown
✅ **VERDICT NAME** | **Risk Level** | **Confidence Level**

[Description of verdict]
```

### Timeline Blocks

```markdown
**This Week:**
- [ ] Action item 1
- [ ] Action item 2

**Next Week:**
- [ ] Action item 1
```

### Decision Points

```markdown
### Decision Name

**Options:**
- Option A: Description
- Option B: Description (Recommended)

**Recommendation:** Option B
```

______________________________________________________________________

## 🚫 What NOT to Do

- ❌ Multiple H1 headers per document
- ❌ Using H4, H5, H6 (max H3)
- ❌ Mixing bullet styles (\* - +)
- ❌ Long paragraphs (break at logical points)
- ❌ All caps except acronyms
- ❌ Excessive emoji use
- ❌ Inconsistent date formatting
- ❌ Links without descriptive text
- ❌ Tables with >5 columns
- ❌ Metadata scattered throughout document

______________________________________________________________________

## 📖 Examples

### Good Example

```markdown
# Agent Assessment - Biomechanics

**Date:** November 17, 2025 | **Status:** Complete | **Owner:** Biomechanics Specialist

---

## Executive Summary

Verdict here.

---

## Key Findings

- Finding 1
- Finding 2

## Detailed Analysis

### Ankle Angle Issue

Description and analysis.

### CMJ Metrics

More analysis.

---

## Next Steps

- [ ] Action 1
- [ ] Action 2

**Last Updated:** November 17, 2025
```

### Bad Example

```markdown
# Agent Assessment

## Biomechanics

Date: November 17, 2025 (inconsistent formatting)

#### Executive Summary (wrong header level)

Verdict here.

* Finding 1 (inconsistent bullets)
- Finding 2

Lots of text without breaks. More text. Even more text running on and on without organization or spacing making it hard to read and understand.

******* (excessive separator)

### Final thoughts (misplaced section)
```

______________________________________________________________________

## 🎯 Apply This Guide To

- ✅ All files in `docs/strategy/`
- ✅ All agent assessment files
- ✅ All consolidated documents
- ✅ All README files
- ✅ All decision/risk/timeline documents

______________________________________________________________________

**Last Updated:** November 17, 2025
**Version:** 1.0 - Official Style Guide for Strategic Documentation
