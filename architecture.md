# Architecture & Technical Approach

## Tech Stack

| Layer | Technology | Rationale |
|-------|------------|-----------|
| Language | Python 3.11+ | Simple, good library support, easy packaging |
| LLM | Claude API (Sonnet) | Strong instruction-following, good at structured output |
| GUI | Tkinter | No extra dependencies, built into Python |
| Packaging | PyInstaller | Single .exe output, no user installation |
| Output | python-docx | Native Word document generation |

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         GUI LAYER                               │
│  ┌───────────────┐  ┌───────────────┐  ┌───────────────────┐   │
│  │ Party Mapping │  │ Notes Input   │  │ Progress Display  │   │
│  │ (anonymize)   │  │ (paste/file)  │  │ (status + errors) │   │
│  └───────────────┘  └───────────────┘  └───────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      PROCESSING PIPELINE                        │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ STEP 0: Anonymization                                   │   │
│  │ - Apply party mappings to raw notes                     │   │
│  │ - Store reverse mapping for later                       │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              │                                  │
│                              ▼                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ STEP 1: Component Extraction                            │   │
│  │ - Parse notes against required component list           │   │
│  │ - Output: { component_id: content | MISSING }           │   │
│  │ - Flag incomplete components with specific gaps         │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              │                                  │
│                              ▼                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ STEP 2: Draft Generation                                │   │
│  │ - Write each section using ONLY extracted components    │   │
│  │ - Insert [ MISSING: X ] placeholders for gaps           │   │
│  │ - No inference or creative gap-filling                  │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              │                                  │
│                              ▼                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ STEP 3: Evaluation Pass                                 │   │
│  │ - Compare each draft sentence to source components      │   │
│  │ - Flag: SUPPORTED | UNSUPPORTED | UNCERTAIN             │   │
│  │ - Generate structured evaluation report                 │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              │                                  │
│                              ▼                                  │
│                    ┌─────────────────┐                         │
│                    │  Any flags?     │                         │
│                    └────────┬────────┘                         │
│                      No     │     Yes                          │
│                       │     │      │                           │
│                       ▼     │      ▼                           │
│                    [Done]   │  ┌──────────────────────────┐    │
│                             │  │ STEP 4: Revision Pass    │    │
│                             │  │ - Remove UNSUPPORTED     │    │
│                             │  │ - Mark UNCERTAIN         │    │
│                             │  │ - Preserve SUPPORTED     │    │
│                             │  └──────────────────────────┘    │
│                             │               │                  │
│                             │               ▼                  │
│                             │      [Loop max 2-3 times]        │
│                             │               │                  │
│                             └───────────────┘                  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                       OUTPUT LAYER                              │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ - Generate .docx with draft body                        │   │
│  │ - Include extraction report (what was found/missing)    │   │
│  │ - Include evaluation summary                            │   │
│  │ - Save to designated output folder                      │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

## File Structure

```
affidavit-assistant/
├── src/
│   ├── main.py              # Entry point, GUI initialization
│   ├── gui/
│   │   ├── app.py           # Main window
│   │   └── widgets.py       # Reusable components
│   ├── pipeline/
│   │   ├── anonymizer.py    # Party mapping logic
│   │   ├── extractor.py     # Component extraction (LLM)
│   │   ├── writer.py        # Draft generation (LLM)
│   │   └── evaluator.py     # Verification pass (LLM)
│   ├── output/
│   │   └── docx_builder.py  # Word document generation
│   └── config/
│       ├── components.py    # Affidavit component definitions
│       └── prompts.py       # LLM prompt templates
├── docs/
│   ├── overview.md
│   └── architecture.md
├── tests/
├── requirements.txt
└── build.py                 # PyInstaller build script
```

## Key Design Decisions

### Why Tkinter over Streamlit/Web?
- No browser dependency
- Runs as true background process
- Simpler packaging to single .exe
- Lower resource footprint

### Why separate Extract → Write → Evaluate steps?
- Extraction creates auditable intermediate artifact
- Separation allows targeted debugging (extraction wrong? writing wrong? eval wrong?)
- Evaluation prompt can be simpler when comparing two artifacts vs. notes-to-prose

### Why cap iterations at 2-3?
- If hallucinations persist after revision, the issue is structural (bad notes, unclear components)
- Prevents infinite loops and runaway API costs
- Forces human review for genuinely ambiguous cases

## API Cost Considerations

Estimated per-document (rough):
- Extraction: ~2K input tokens, ~1K output
- Writing: ~3K input tokens, ~2K output  
- Evaluation: ~4K input tokens, ~1K output
- Revision (if needed): ~4K input, ~2K output

**Total: ~15-20K tokens per document ≈ $0.05-0.10 with Sonnet**

## Dependencies

```
anthropic>=0.30.0
python-docx>=1.0.0
```

Tkinter ships with Python standard library.
