"""
Background pipeline runner with daemon threading.
"""
import threading
import logging
from typing import Optional, Callable
from pathlib import Path

from pipeline.core import Pipeline, PipelineState
from pipeline.llm_client import ClaudeClient, PromptLoader
from pipeline.steps.extractor import ExtractorStep
from pipeline.steps.writer import WriterStep
from pipeline.steps.evaluator import EvaluatorStep
from pipeline.steps.reviser import ReviserStep
from output.docx_builder import AffidavitDocxBuilder
from config import settings

logger = logging.getLogger(__name__)


class PipelineRunner:
    """
    Manages background execution of the affidavit generation pipeline.

    Runs pipeline in daemon thread so it continues even if GUI closes.
    """

    def __init__(self):
        self.thread: Optional[threading.Thread] = None
        self.is_running = False

    def start(
        self,
        notes: str,
        output_path: str,
        case_name: str,
        case_specifics: str = "",
        progress_callback: Optional[Callable[[str, int], None]] = None,
        completion_callback: Optional[Callable[[str, bool], None]] = None
    ):
        """
        Start pipeline in background thread.

        Args:
            notes: Raw interview notes
            output_path: Path for output directory
            case_name: Name for this case (creates subdirectory)
            case_specifics: Optional case-specific instructions/guidance
            progress_callback: Optional callback(message, progress_percent)
            completion_callback: Optional callback(result_message, success)
        """
        if self.is_running:
            logger.warning("Pipeline already running")
            return

        # Create daemon thread
        self.thread = threading.Thread(
            target=self._run_pipeline,
            args=(notes, output_path, case_name, case_specifics, progress_callback, completion_callback),
            daemon=True  # Continues even if GUI closes
        )

        self.is_running = True
        self.thread.start()
        logger.info("Pipeline started in background")

    def _run_pipeline(
        self,
        notes: str,
        output_path: str,
        case_name: str,
        case_specifics: str,
        progress_callback: Optional[Callable[[str, int], None]],
        completion_callback: Optional[Callable[[str, bool], None]]
    ):
        """Internal method that runs the pipeline."""
        try:
            # Initialize components
            client = ClaudeClient(
                api_key=settings.ANTHROPIC_API_KEY,
                model=settings.CLAUDE_MODEL
            )
            prompt_loader = PromptLoader(str(settings.PROMPTS_DIR))

            # Build pipeline with write-evaluate-revise loop
            pipeline = self._build_pipeline(client, prompt_loader)

            # Create initial state
            initial_state = PipelineState(
                raw_notes=notes,
                output_path=output_path,
                case_name=case_name,
                case_specifics=case_specifics
            )

            # Run pipeline
            logger.info("Starting pipeline execution")
            final_state = pipeline.run(initial_state, progress_callback)

            # Generate output documents
            if progress_callback:
                progress_callback("Generating Word documents...", 95)

            builder = AffidavitDocxBuilder()
            main_file, report_file = builder.build(final_state)

            # Report completion
            if final_state.has_critical_error():
                message = (f"Pipeline completed with errors.\n"
                          f"Draft: {main_file}\n"
                          f"Report: {report_file}")
                success = False
                logger.warning(message)
            else:
                message = (f"Success! Documents generated:\n"
                          f"Draft: {main_file}\n"
                          f"Report: {report_file}")
                success = True
                logger.info(message)

            if completion_callback:
                completion_callback(message, success)

        except Exception as e:
            error_msg = f"Pipeline failed: {str(e)}"
            logger.error(error_msg, exc_info=True)
            if completion_callback:
                completion_callback(error_msg, False)

        finally:
            self.is_running = False

    def _build_pipeline(self, client: ClaudeClient, prompt_loader: PromptLoader) -> Pipeline:
        """
        Build the pipeline with write-evaluate-revise loop.

        Pipeline flow:
        1. Extract components
        2. Write draft
        3. Evaluate draft
        4. If issues found and iterations < max: Revise and go back to step 3
        5. Done
        """
        # Create pipeline steps
        extractor = ExtractorStep(client, prompt_loader)
        writer = WriterStep(client, prompt_loader)
        evaluator = EvaluatorStep(client, prompt_loader)
        reviser = ReviserStep(client, prompt_loader)

        # Build step sequence with iteration logic
        # The Pipeline class will handle the write-evaluate-revise loop
        # For now, we'll create a custom pipeline that handles iterations

        return IterativePipeline(
            extract_step=extractor,
            write_step=writer,
            eval_step=evaluator,
            revise_step=reviser,
            max_iterations=settings.MAX_ITERATIONS
        )


class IterativePipeline(Pipeline):
    """
    Custom pipeline that handles write-evaluate-revise iterations.
    """

    def __init__(self, extract_step, write_step, eval_step, revise_step, max_iterations=3):
        # Don't call super().__init__ - we'll override run()
        self.extract_step = extract_step
        self.write_step = write_step
        self.eval_step = eval_step
        self.revise_step = revise_step
        self.max_iterations = max_iterations

    def run(self, state: PipelineState,
            progress_callback: Optional[Callable[[str, int], None]] = None) -> PipelineState:
        """
        Run pipeline with iterative write-evaluate-revise loop.
        """
        # Step 1: Extract components (10% of progress)
        if progress_callback:
            progress_callback("Extracting components from notes...", 10)

        state = self.extract_step.execute(state)
        if state.has_critical_error():
            return state

        # Step 2: Initial write (30% of progress)
        if progress_callback:
            progress_callback("Writing initial draft...", 30)

        state = self.write_step.execute(state)
        if state.has_critical_error():
            return state

        # Steps 3-4: Evaluate and revise loop (30% - 90% of progress)
        iteration = 0
        while iteration < self.max_iterations:
            # Evaluate
            progress = 40 + (iteration * 20)
            if progress_callback:
                progress_callback(f"Evaluating draft (iteration {iteration + 1})...", progress)

            state = self.eval_step.execute(state)
            if state.has_critical_error():
                return state

            # Check if we're done (no revision needed)
            if state.evaluation_report and not state.evaluation_report.get('needs_revision', True):
                logger.info(f"Draft approved after {iteration + 1} iteration(s)")
                state.final_text = state.draft_text
                break

            # Revise if we haven't hit max iterations
            iteration += 1
            if iteration < self.max_iterations:
                progress = 50 + (iteration * 20)
                if progress_callback:
                    progress_callback(f"Revising draft (iteration {iteration})...", progress)

                state = self.revise_step.execute(state)
                if state.has_critical_error():
                    return state
            else:
                logger.warning(f"Reached max iterations ({self.max_iterations})")
                state.final_text = state.draft_text
                break

        return state
