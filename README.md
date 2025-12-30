# Affidavit Writing Assistant

A tool that transforms interview notes into draft affidavit bodies with zero-hallucination tolerance.

## Quick Start

### Prerequisites

- Python 3.11 or higher
- Anthropic API key

### Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set your API key:
```bash
export ANTHROPIC_API_KEY="your-api-key-here"
```

### Usage

Simply run:
```bash
python main.py
```

This will open the GUI where you can:
1. Paste or load interview notes
2. Choose output location
3. Click "Generate Affidavit"
4. Close the window - the process continues in the background

The output will be saved as a `.docx` file with:
- The affidavit body draft
- Component extraction report
- Evaluation summary
- Processing log

## Customizing Prompts

All prompts are stored as markdown files in `prompts/`:

- `01-extraction.md` - Component extraction from notes
- `02-writing.md` - Affidavit body writing (includes component definitions)
- `03-evaluation.md` - Draft verification
- `04-revision.md` - Draft revision based on feedback

Simply edit these files in any text editor. Changes take effect immediately.

## Configuration

Edit `config/settings.py` to adjust:
- `MAX_ITERATIONS` - Max write-evaluate-revise loops (default: 3)
- `CLAUDE_MODEL` - Claude model to use
- `LOG_LEVEL` - Logging verbosity

## Project Structure

```
affidavit/
├── main.py              # Entry point: python main.py
├── prompts/             # All prompts (easy to edit)
│   ├── 01-extraction.md
│   ├── 02-writing.md
│   ├── 03-evaluation.md
│   └── 04-revision.md
├── pipeline/            # Core pipeline logic
│   ├── core.py
│   ├── llm_client.py
│   └── steps/
├── gui/                 # Tkinter interface
├── output/              # Document generation
├── logs/                # Execution logs
└── config/              # Settings
```

## Logs

Each run creates a timestamped log file in `logs/` with detailed execution information.

## Cost

Approximately $0.05-0.10 per document using Claude Sonnet (~15-20K tokens).
