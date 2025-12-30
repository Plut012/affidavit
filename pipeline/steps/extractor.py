"""
Component extraction step - extracts structured components from interview notes.
"""
import json
from typing import Dict, Any
import logging
from pipeline.core import PipelineStep, PipelineState, ErrorSeverity
from pipeline.llm_client import ClaudeClient, PromptLoader

logger = logging.getLogger(__name__)


class ExtractorStep(PipelineStep):
    """Extracts affidavit components from raw interview notes."""

    def __init__(self, client: ClaudeClient, prompt_loader: PromptLoader):
        self.client = client
        self.prompt_loader = prompt_loader

    @property
    def name(self) -> str:
        return "Extracting components from notes"

    def execute(self, state: PipelineState) -> PipelineState:
        """
        Extract components from notes using LLM.

        Updates state.extracted_components with structured data.
        """
        try:
            # Load and format prompt
            prompt = self.prompt_loader.format(
                "01-extraction",
                notes=state.raw_notes
            )

            # Call LLM
            response = self.client.generate(prompt, max_tokens=4096)

            # Parse JSON response
            extracted = self._parse_response(response)

            # Validate extraction
            if not extracted:
                state.add_error(
                    self.name,
                    ErrorSeverity.ERROR,
                    "Extraction returned empty result"
                )
            else:
                state.extracted_components = extracted
                state.step_outputs['extraction'] = extracted
                logger.info(f"Extracted {len(extracted)} components")

        except json.JSONDecodeError as e:
            state.add_error(
                self.name,
                ErrorSeverity.ERROR,
                f"Failed to parse extraction JSON: {str(e)}",
                e
            )
        except Exception as e:
            state.add_error(
                self.name,
                ErrorSeverity.CRITICAL,
                f"Extraction failed: {str(e)}",
                e
            )

        return state

    def _parse_response(self, response: str) -> Dict[str, Any]:
        """
        Parse LLM response to extract JSON.

        Args:
            response: Raw LLM response

        Returns:
            Parsed component dictionary
        """
        # Try to extract JSON from markdown code blocks if present
        if "```json" in response:
            start = response.find("```json") + 7
            end = response.find("```", start)
            json_str = response[start:end].strip()
        elif "```" in response:
            start = response.find("```") + 3
            end = response.find("```", start)
            json_str = response[start:end].strip()
        else:
            json_str = response.strip()

        return json.loads(json_str)
