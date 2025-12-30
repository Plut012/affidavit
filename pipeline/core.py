"""
Core pipeline framework for affidavit generation.

Simple, linear pipeline with state object flowing through each step.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Callable, Optional, Any
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ErrorSeverity(Enum):
    """Error severity levels for pipeline error handling."""
    INFO = "info"           # Informational, continue
    WARNING = "warning"     # Log and continue
    ERROR = "error"         # Log and continue, but mark step as partial failure
    CRITICAL = "critical"   # Stop pipeline execution


@dataclass
class PipelineError:
    """Represents an error that occurred during pipeline execution."""
    step_name: str
    severity: ErrorSeverity
    message: str
    exception: Optional[Exception] = None


@dataclass
class PipelineState:
    """
    State object that flows through the pipeline.
    Each step reads from and writes to this state.
    """
    # Input
    raw_notes: str
    output_path: str
    case_name: str
    case_specifics: str = ""

    # Intermediate artifacts (populated as pipeline progresses)
    extracted_components: Optional[Dict[str, Any]] = None
    draft_text: Optional[str] = None
    evaluation_report: Optional[Dict[str, Any]] = None
    final_text: Optional[str] = None

    # Metadata
    iteration_count: int = 0
    errors: List[PipelineError] = field(default_factory=list)
    step_outputs: Dict[str, Any] = field(default_factory=dict)  # For debugging

    def add_error(self, step_name: str, severity: ErrorSeverity,
                  message: str, exception: Optional[Exception] = None):
        """Add an error to the state."""
        error = PipelineError(step_name, severity, message, exception)
        self.errors.append(error)
        logger.log(
            self._severity_to_log_level(severity),
            f"[{step_name}] {message}",
            exc_info=exception
        )

    def has_critical_error(self) -> bool:
        """Check if any critical errors occurred."""
        return any(e.severity == ErrorSeverity.CRITICAL for e in self.errors)

    @staticmethod
    def _severity_to_log_level(severity: ErrorSeverity) -> int:
        """Map severity to logging level."""
        mapping = {
            ErrorSeverity.INFO: logging.INFO,
            ErrorSeverity.WARNING: logging.WARNING,
            ErrorSeverity.ERROR: logging.ERROR,
            ErrorSeverity.CRITICAL: logging.CRITICAL,
        }
        return mapping[severity]


class PipelineStep(ABC):
    """
    Abstract base class for pipeline steps.
    Each step implements execute() which takes state and returns updated state.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable name for progress reporting."""
        pass

    @abstractmethod
    def execute(self, state: PipelineState) -> PipelineState:
        """
        Execute this step of the pipeline.

        Args:
            state: Current pipeline state

        Returns:
            Updated pipeline state

        Note: Should catch exceptions and add them to state.errors
              rather than raising them (unless critical).
        """
        pass


class Pipeline:
    """
    Pipeline orchestrator that runs steps sequentially.
    Handles progress callbacks and error propagation.
    """

    def __init__(self, steps: List[PipelineStep], max_iterations: int = 3):
        """
        Initialize pipeline.

        Args:
            steps: List of pipeline steps to execute
            max_iterations: Maximum write-evaluate-revise iterations
        """
        self.steps = steps
        self.max_iterations = max_iterations

    def run(self, state: PipelineState,
            progress_callback: Optional[Callable[[str, int], None]] = None) -> PipelineState:
        """
        Run the pipeline to completion.

        Args:
            state: Initial pipeline state
            progress_callback: Optional callback(message, progress_percent)

        Returns:
            Final pipeline state
        """
        total_steps = len(self.steps)

        for i, step in enumerate(self.steps):
            # Report progress
            if progress_callback:
                progress = int((i / total_steps) * 100)
                progress_callback(f"Step {i+1}/{total_steps}: {step.name}", progress)

            # Execute step
            logger.info(f"Executing step: {step.name}")
            try:
                state = step.execute(state)
            except Exception as e:
                # Unexpected exception - treat as critical
                state.add_error(
                    step.name,
                    ErrorSeverity.CRITICAL,
                    f"Unexpected error: {str(e)}",
                    e
                )

            # Check for critical errors
            if state.has_critical_error():
                logger.critical("Critical error encountered, stopping pipeline")
                if progress_callback:
                    progress_callback("Pipeline stopped due to critical error", -1)
                break

        # Final progress update
        if progress_callback and not state.has_critical_error():
            progress_callback("Pipeline complete", 100)

        return state
