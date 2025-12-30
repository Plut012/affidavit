"""
Revision step - revises draft based on evaluation feedback.
"""
import json
import logging
from pipeline.core import PipelineStep, PipelineState, ErrorSeverity
from pipeline.llm_client import ClaudeClient, PromptLoader

logger = logging.getLogger(__name__)


class ReviserStep(PipelineStep):
    """Revises draft based on evaluation feedback."""

    def __init__(self, client: ClaudeClient, prompt_loader: PromptLoader):
        self.client = client
        self.prompt_loader = prompt_loader

    @property
    def name(self) -> str:
        return "Revising draft based on feedback"

    def execute(self, state: PipelineState) -> PipelineState:
        """
        Revise draft to fix unsupported/uncertain statements.

        Updates state.draft_text with revised version.
        Increments state.iteration_count.
        """
        # Check if revision is needed
        if not state.evaluation_report:
            logger.info("No evaluation report - skipping revision")
            return state

        if not state.evaluation_report.get('needs_revision', True):
            logger.info("No issues found - no revision needed")
            state.final_text = state.draft_text
            return state

        logger.info("=" * 60)
        logger.info(f"STEP 4: REVISING DRAFT (Iteration {state.iteration_count + 1})")
        logger.info("=" * 60)

        # Check prerequisites
        if not state.draft_text or not state.extracted_components:
            logger.error("ERROR: Cannot revise - missing draft or components")
            state.add_error(
                self.name,
                ErrorSeverity.ERROR,
                "Cannot revise: missing draft or components"
            )
            return state

        try:
            # Format inputs
            components_json = json.dumps(state.extracted_components, indent=2)
            evaluation_json = json.dumps(state.evaluation_report, indent=2)

            # Load and format prompt
            logger.info("Fixing identified issues...")
            prompt = self.prompt_loader.format(
                "04-revision",
                components=components_json,
                draft=state.draft_text,
                evaluation=evaluation_json,
                case_specifics=state.case_specifics or "None provided"
            )

            # Call LLM
            response = self.client.generate(prompt, max_tokens=4096)

            # Update draft with revised version
            old_word_count = len(state.draft_text.split())
            new_word_count = len(response.split())

            state.draft_text = response.strip()
            state.iteration_count += 1
            state.step_outputs[f'revision_{state.iteration_count}'] = response.strip()

            logger.info("")
            logger.info("REVISION COMPLETE:")
            logger.info(f"  Words: {old_word_count} → {new_word_count}")
            logger.info(f"  Will evaluate again to check if issues are fixed")
            logger.info("")

        except Exception as e:
            state.add_error(
                self.name,
                ErrorSeverity.ERROR,
                f"Revision failed: {str(e)}",
                e
            )

        return state
