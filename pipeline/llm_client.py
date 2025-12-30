"""
Claude API client wrapper with prompt loading.
"""
import os
from pathlib import Path
from typing import Dict, Optional
import logging
from anthropic import Anthropic

logger = logging.getLogger(__name__)


class PromptLoader:
    """Loads and manages prompts from markdown files."""

    def __init__(self, prompts_dir: str = "prompts"):
        """
        Initialize prompt loader.

        Args:
            prompts_dir: Directory containing prompt .md files
        """
        self.prompts_dir = Path(prompts_dir)
        self._cache: Dict[str, str] = {}

    def load(self, prompt_name: str) -> str:
        """
        Load a prompt from markdown file.

        Args:
            prompt_name: Name of prompt file (without .md extension)

        Returns:
            Prompt content as string

        Raises:
            FileNotFoundError: If prompt file doesn't exist
        """
        if prompt_name in self._cache:
            return self._cache[prompt_name]

        prompt_path = self.prompts_dir / f"{prompt_name}.md"

        if not prompt_path.exists():
            raise FileNotFoundError(f"Prompt file not found: {prompt_path}")

        with open(prompt_path, 'r', encoding='utf-8') as f:
            content = f.read()

        self._cache[prompt_name] = content
        logger.debug(f"Loaded prompt: {prompt_name}")

        return content

    def format(self, prompt_name: str, **variables) -> str:
        """
        Load and format a prompt with variables.

        Args:
            prompt_name: Name of prompt file (without .md extension)
            **variables: Variables to substitute in the prompt

        Returns:
            Formatted prompt string
        """
        template = self.load(prompt_name)
        return template.format(**variables)


class ClaudeClient:
    """Wrapper for Claude API calls."""

    def __init__(self, api_key: Optional[str] = None, model: str = "claude-sonnet-4-20250514"):
        """
        Initialize Claude client.

        Args:
            api_key: Anthropic API key (defaults to ANTHROPIC_API_KEY env var)
            model: Claude model to use
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment or constructor")

        self.model = model
        self.client = Anthropic(api_key=self.api_key)
        logger.info(f"Initialized Claude client with model: {model}")

    def generate(self, prompt: str, max_tokens: int = 4096,
                 temperature: float = 0.0, system: Optional[str] = None) -> str:
        """
        Generate text using Claude.

        Args:
            prompt: User prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0 = deterministic)
            system: Optional system prompt

        Returns:
            Generated text

        Raises:
            Exception: If API call fails
        """
        try:
            logger.debug(f"Calling Claude API (tokens: {max_tokens}, temp: {temperature})")

            kwargs = {
                "model": self.model,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "messages": [{"role": "user", "content": prompt}]
            }

            if system:
                kwargs["system"] = system

            response = self.client.messages.create(**kwargs)

            # Extract text from response
            text = response.content[0].text

            logger.debug(f"Received response ({len(text)} chars)")
            return text

        except Exception as e:
            logger.error(f"Claude API error: {str(e)}")
            raise
