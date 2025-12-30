"""
Draft writing step - generates affidavit body from extracted components.
"""
import json
import logging
from pipeline.core import PipelineStep, PipelineState, ErrorSeverity
from pipeline.llm_client import ClaudeClient, PromptLoader

logger = logging.getLogger(__name__)


class WriterStep(PipelineStep):
    """Writes affidavit draft from extracted components."""

    def __init__(self, client: ClaudeClient, prompt_loader: PromptLoader):
        self.client = client
        self.prompt_loader = prompt_loader

    @property
    def name(self) -> str:
        return "Writing affidavit draft"

    def execute(self, state: PipelineState) -> PipelineState:
        """
        Generate affidavit draft from extracted components.

        Updates state.draft_text with generated affidavit body.
        """
        # Check prerequisites
        if not state.extracted_components:
            state.add_error(
                self.name,
                ErrorSeverity.CRITICAL,
                "Cannot write draft: no extracted components available"
            )
            return state

        try:
            # Format components as JSON string for prompt
            components_json = json.dumps(state.extracted_components, indent=2)

            # Load and format prompt
            # Note: Component definitions are embedded in the prompt
            prompt = self.prompt_loader.format(
                "02-writing",
                components=components_json
            )

            # Call LLM
            response = self.client.generate(prompt, max_tokens=4096)

            # Store draft
            state.draft_text = response.strip()
            state.step_outputs['writing'] = response.strip()
            logger.info(f"Generated draft ({len(response)} chars)")

        except Exception as e:
            state.add_error(
                self.name,
                ErrorSeverity.CRITICAL,
                f"Draft generation failed: {str(e)}",
                e
            )

        return state
