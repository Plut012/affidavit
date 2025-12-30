"""
Evaluation step - verifies draft against extracted components.
"""
import json
import logging
from pipeline.core import PipelineStep, PipelineState, ErrorSeverity
from pipeline.llm_client import ClaudeClient, PromptLoader

logger = logging.getLogger(__name__)


class EvaluatorStep(PipelineStep):
    """Evaluates draft affidavit against source components."""

    def __init__(self, client: ClaudeClient, prompt_loader: PromptLoader):
        self.client = client
        self.prompt_loader = prompt_loader

    @property
    def name(self) -> str:
        return "Evaluating draft against sources"

    def execute(self, state: PipelineState) -> PipelineState:
        """
        Evaluate draft for unsupported statements.

        Updates state.evaluation_report with findings.
        """
        # Check prerequisites
        if not state.draft_text:
            state.add_error(
                self.name,
                ErrorSeverity.CRITICAL,
                "Cannot evaluate: no draft text available"
            )
            return state

        if not state.extracted_components:
            state.add_error(
                self.name,
                ErrorSeverity.CRITICAL,
                "Cannot evaluate: no extracted components available"
            )
            return state

        try:
            # Format inputs
            components_json = json.dumps(state.extracted_components, indent=2)

            # Load and format prompt
            prompt = self.prompt_loader.format(
                "03-evaluation",
                components=components_json,
                draft=state.draft_text
            )

            # Call LLM
            response = self.client.generate(prompt, max_tokens=4096)

            # Parse evaluation report
            evaluation = self._parse_response(response)

            # Store evaluation
            state.evaluation_report = evaluation
            state.step_outputs[f'evaluation_{state.iteration_count}'] = evaluation

            # Log findings
            if not evaluation.get('needs_revision', True):
                logger.info("Draft is perfect - no issues found!")
            else:
                unsupported = len(evaluation.get('unsupported_statements', []))
                uncertain = len(evaluation.get('uncertain_statements', []))
                passive = len(evaluation.get('passive_voice_issues', []))
                ing = len(evaluation.get('ing_word_issues', []))
                missing = len(evaluation.get('missing_elements', []))
                logger.warning(
                    f"Issues found - unsupported: {unsupported}, uncertain: {uncertain}, "
                    f"passive voice: {passive}, -ing words: {ing}, missing elements: {missing}"
                )

        except json.JSONDecodeError as e:
            state.add_error(
                self.name,
                ErrorSeverity.ERROR,
                f"Failed to parse evaluation JSON: {str(e)}",
                e
            )
            # Create a safe default to allow pipeline to continue
            state.evaluation_report = {
                'needs_revision': True,
                'unsupported_statements': [],
                'uncertain_statements': [],
                'passive_voice_issues': [],
                'ing_word_issues': [],
                'missing_elements': [],
                'error': str(e)
            }
        except Exception as e:
            state.add_error(
                self.name,
                ErrorSeverity.CRITICAL,
                f"Evaluation failed: {str(e)}",
                e
            )

        return state

    def _parse_response(self, response: str) -> dict:
        """Parse LLM evaluation response to extract JSON."""
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
