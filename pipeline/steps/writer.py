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
        logger.info("=" * 60)
        logger.info("STEP 2: WRITING FORCED LABOR SECTION")
        logger.info("=" * 60)

        # Check prerequisites
        if not state.extracted_components:
            logger.error("ERROR: Cannot write - no components extracted")
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
            logger.info("Generating section using AI...")
            prompt = self.prompt_loader.format(
                "02-writing",
                components=components_json
            )

            # Call LLM
            response = self.client.generate(prompt, max_tokens=4096)

            # Store draft
            state.draft_text = response.strip()
            state.step_outputs['writing'] = response.strip()

            # Count words and paragraphs
            word_count = len(response.split())
            para_count = len([p for p in response.split('\n\n') if p.strip()])

            logger.info("")
            logger.info("DRAFT COMPLETE:")
            logger.info(f"  Words: {word_count}")
            logger.info(f"  Paragraphs: {para_count}")
            logger.info("")

        except Exception as e:
            state.add_error(
                self.name,
                ErrorSeverity.CRITICAL,
                f"Draft generation failed: {str(e)}",
                e
            )

        return state
