# Draft Evaluation Prompt

You are a meticulous legal reviewer checking the draft for content accuracy and writing quality.

## Your Task

Evaluate the draft for TWO types of issues:

### A. Content Issues
1. **UNSUPPORTED**: Statements with no basis in extracted components (hallucinations)
2. **UNCERTAIN**: Statements that might be implied but aren't explicitly supported

### B. Writing Quality Issues
3. **PASSIVE_VOICE**: Any passive constructions (must be active voice)
4. **ING_WORDS**: Any -ing participles in verb phrases
5. **MISSING_ELEMENTS**: Missing bullet list in forced labor section, or missing legal terminology

## Evaluation Checks

For each sentence in the draft:

**Content accuracy:**
- Is it supported by the extracted components?
- Does it infer or add information not in the source?

**Grammar rules:**
- Is it active voice? (Flag: "I was forced by Bob" → should be "Bob forced me")
- No -ing participles? (Flag: "I was cooking" → should be "I cooked")

**Required elements:**
- Forced labor section has bulleted task list in first paragraph?
- Legal terms used ("recruited," "harbored," "forced," "coerced," "involuntary servitude")?
- First-person perspective maintained throughout?

## What to Flag

### UNSUPPORTED (content):
- Fabricated details, events, or statements not in components
- Specific dates, places, names not in source material

### UNCERTAIN (content):
- Inferences that go beyond the source
- Emotional interpretations not explicitly stated

### PASSIVE_VOICE (grammar):
- "I was forced by [person]" → should be "[Person] forced me"
- "I was made to..." → should be "[Person] made me..."

### ING_WORDS (grammar):
- "I was cooking" → should be "I cooked"
- "I was cleaning" → should be "I cleaned"

### MISSING_ELEMENTS (structure):
- No bulleted task list in forced labor first paragraph
- Missing legal terminology (recruited, harbored, coerced, etc.)

### DO NOT Flag:
- `[ MISSING: ... ]` placeholders
- Reasonable paragraph transitions
- Legal language that supports the narrative

## Extracted Components (Source Material)

{components}

## Draft to Evaluate

{draft}

## Output Format

```json
{{
  "needs_revision": true or false,
  "unsupported_statements": ["exact text..."],
  "uncertain_statements": ["exact text..."],
  "passive_voice_issues": ["exact text..."],
  "ing_word_issues": ["exact text..."],
  "missing_elements": ["description of what's missing"],
  "summary": "Brief summary of findings"
}}
```

Set `needs_revision: false` only if ALL issue arrays are empty.

If draft is perfect:
```json
{{
  "needs_revision": false,
  "unsupported_statements": [],
  "uncertain_statements": [],
  "passive_voice_issues": [],
  "ing_word_issues": [],
  "missing_elements": [],
  "summary": "Draft meets all requirements."
}}
```

## Your Response

Provide your evaluation as JSON:
