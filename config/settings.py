"""
Configuration settings for affidavit assistant.
"""
import os
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
PROMPTS_DIR = PROJECT_ROOT / "prompts"
LOGS_DIR = PROJECT_ROOT / "logs"
OUTPUT_DIR = PROJECT_ROOT / "output"
CONFIG_DIR = PROJECT_ROOT / "config"

# Ensure directories exist
LOGS_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

# API key configuration file
API_KEY_FILE = CONFIG_DIR / ".api_key"


def get_api_key() -> str:
    """
    Get API key from environment variable or config file.

    Priority:
    1. ANTHROPIC_API_KEY environment variable
    2. .api_key file in config directory
    3. Empty string (will prompt user)
    """
    # Try environment variable first
    key = os.getenv("ANTHROPIC_API_KEY", "").strip()
    if key:
        return key

    # Try config file
    if API_KEY_FILE.exists():
        try:
            key = API_KEY_FILE.read_text().strip()
            if key:
                return key
        except Exception:
            pass

    return ""


def save_api_key(key: str) -> None:
    """
    Save API key to config file.

    Args:
        key: Anthropic API key to save
    """
    API_KEY_FILE.write_text(key.strip())
    # Set restrictive permissions (owner read/write only)
    try:
        API_KEY_FILE.chmod(0o600)
    except Exception:
        # Windows doesn't support chmod the same way
        pass


# API settings
ANTHROPIC_API_KEY = get_api_key()
CLAUDE_MODEL = "claude-sonnet-4-20250514"

# Pipeline settings
MAX_ITERATIONS = 3  # Maximum write-evaluate-revise loops
LLM_TEMPERATURE = 0.0  # Deterministic output
MAX_TOKENS = 4096

# Logging
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
