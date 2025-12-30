# Affidavit Writing Assistant

## Problem Statement

Legal affidavits require precise, structured writing derived entirely from client interview notes. The process is time-consuming and repetitive, yet demands absolute accuracy—every statement must trace directly to source material. No inference, no gap-filling, no hallucination.

## Goal

Build a tool that transforms raw interview notes into draft affidavit bodies, allowing the user to initiate the process and continue other work while it runs.

## Core Requirements

### 1. Zero Hallucination Tolerance
- Every sentence in the output must be directly supported by the input notes
- When information is missing, the system must explicitly mark it: `[ MISSING: description of what's needed ]`
- The system should never attempt to infer, assume, or fill gaps

### 2. Component-Based Construction
- Break the affidavit body into discrete, well-defined components
- Extract and map notes to these components before writing
- Track which components have sufficient source material vs. which are incomplete

### 3. Iterative Write-Evaluate Loop
- Draft generation followed by verification against source components
- Multiple passes to catch and remove unsupported statements
- Capped iterations (2-3 max) to prevent infinite loops

### 4. Explicit Gap Identification
- Missing components flagged at extraction stage
- Missing information in draft marked with clear placeholders
- Final output serves as both draft AND checklist for follow-up questions

### 5. Simple User Experience
- Single executable, no installation required
- Input notes → hit run → close and continue other work
- Output delivered as file when complete

## Anonymization Approach

Manual pre-processing with standardized role names:
- User defines party mappings before processing (e.g., "Maria Garcia" → `[CLIENT]`)
- System performs find-replace before notes reach the API
- Real names never transmitted to external services
- Reverse mapping available for final document if needed

## User Profile

Single user (immigration attorney). Tool is for personal productivity, not team or client-facing use.

## Success Criteria

1. Draft output requires less revision time than writing from scratch
2. No fabricated details slip through to final review
3. Missing information is obvious and actionable
4. User can trust the tool enough to run it unattended
