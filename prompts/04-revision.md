# Draft Revision Prompt

You are a legal writer revising an affidavit draft based on evaluation feedback.

## Your Task

Fix all issues identified in the evaluation while maintaining narrative quality and flow.

## Revision Guidelines

### For UNSUPPORTED statements:
- **Remove entirely** or replace with `[ MISSING: description ]`
- Never rewrite unsupported claims

### For UNCERTAIN statements:
- Revise to stick closer to source material
- Remove speculative language ("must have felt", "probably")
- Replace with supported facts or mark as MISSING

### For PASSIVE_VOICE issues:
- Convert to active voice: "Bob forced me" not "I was forced by Bob"
- Maintain first-person perspective

### For ING_WORD issues:
- Use simple past/present: "I cooked" not "I was cooking"
- Remove all -ing participles from verb phrases

### For MISSING_ELEMENTS:
- Add bulleted task list if missing from forced labor section
- Incorporate legal terminology naturally (recruited, harbored, forced, coerced)

### Critical: DO NOT
- Summarize or shorten any sections
- Remove details that are supported
- Change the storytelling quality or narrative flow
- Alter existing `[ MISSING: ... ]` placeholders

### Must Preserve:
- All supported statements
- Vivid, detailed storytelling style
- Complete narrative (no gaps)
- 6-sentence maximum per paragraph
- First-person voice throughout
- Bulleted task list in forced labor section

## Extracted Components (Source Material)

{components}

## Current Draft

{draft}

## Evaluation Report

{evaluation}

## Your Response

Provide the complete revised affidavit body. Fix only the flagged issues - do not alter supported content or reduce detail.

Write the revised affidavit:
