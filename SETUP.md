# Setup Guide - Affidavit Writing Assistant
## For Windows

## Prerequisites

Before starting, download and install:

1. **Python 3.12** from https://www.python.org/downloads/
   - ✅ **Important:** Check "Add Python to PATH" during installation

2. **Git** from https://git-scm.com/downloads
   - Use default settings during installation

## Installation Steps

### 1. Clone the Repository

Open Command Prompt (Windows) or Terminal (Mac/Linux) and run:

```bash
# Navigate to where you want to install (e.g., Documents folder)
cd Documents

# Clone the repository
git clone <REPOSITORY_URL>

# Navigate into the project
cd affadavit
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv
```

### 3. Activate Virtual Environment

```bash
venv\Scripts\activate
```

You should see `(venv)` appear at the start of your command prompt.

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

This will install the required packages (anthropic, python-docx).

## First Run

### Option 1: Use Launcher Script (Easiest)

Double-click `run.bat`

### Option 2: Manual Run

```bash
# Make sure virtual environment is activated first
python main.py
```

### Enter API Key

On first run, you'll see a dialog asking for your Anthropic API key:

1. Go to https://console.anthropic.com/
2. Sign in and navigate to API Keys
3. Copy your API key (starts with `sk-ant-`)
4. Paste it into the dialog
5. Click "Save"

The key will be saved locally and you won't need to enter it again.

## Usage

1. **Launch the application**
   - Double-click `run.bat`
   
2. **Enter or load interview notes**
   - Type directly into the text area, or
   - Click "Load from File" to load from a .txt file
   
3. **Choose output location**
   - Default is the `output` folder
   - Click "Browse" to change
   
4. **Generate Affidavit**
   - Click "Generate Affidavit"
   - The process runs in the background
   - You can close the window - processing continues
   
5. **Find your output**
   - Check the output folder for two .docx files:
     - `affidavit_draft_[timestamp].docx` - The affidavit body
     - `affidavit_report_[timestamp].docx` - Extraction report

## Updating the Application

When updates are available, just double-click `update.bat`

Or manually:
```bash
# Navigate to project folder
cd Documents\affadavit

# Pull latest changes
git pull

# Activate virtual environment
venv\Scripts\activate

# Update dependencies (if needed)
pip install -r requirements.txt
```

## Troubleshooting

### "Python not found"
- Reinstall Python and make sure "Add to PATH" is checked
- Restart your terminal/command prompt

### "pip not found"
- Run: `python -m pip install -r requirements.txt`


### API key issues
- Delete `config/.api_key` file to re-enter your key
- Or manually edit the file with a text editor

### Application won't start
- Check `logs/` folder for error messages
- Make sure virtual environment is activated

## Cost Information

- Each document costs approximately $0.05-0.10 to generate
- Uses Claude Sonnet model (~15-20K tokens per document)
- Check your Anthropic console for usage tracking

## Support

For issues or questions, check the logs in the `logs/` folder for detailed error information.
