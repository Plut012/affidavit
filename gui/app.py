"""
Tkinter GUI for Affidavit Writing Assistant.
"""
import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
from pathlib import Path
import logging

from gui.runner import PipelineRunner
from config import settings

logger = logging.getLogger(__name__)


class AffidavitApp:
    """Main application window."""

    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Affidavit Writing Assistant")
        self.window.geometry("800x600")

        # Check for API key on startup
        if not settings.ANTHROPIC_API_KEY:
            self._prompt_for_api_key()

        self.runner = PipelineRunner()
        self._build_ui()

    def _build_ui(self):
        """Build the user interface."""
        # Main container with padding
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure grid weights for resizing
        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)

        # Title
        title_label = ttk.Label(
            main_frame,
            text="Affidavit Writing Assistant",
            font=("Arial", 16, "bold")
        )
        title_label.grid(row=0, column=0, pady=(0, 10))

        # Notes input section
        notes_frame = ttk.LabelFrame(main_frame, text="Interview Notes", padding="10")
        notes_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        notes_frame.columnconfigure(0, weight=1)
        notes_frame.rowconfigure(0, weight=3)
        notes_frame.rowconfigure(2, weight=1)

        # Text area for notes
        self.notes_text = scrolledtext.ScrolledText(
            notes_frame,
            wrap=tk.WORD,
            width=70,
            height=12,
            font=("Arial", 10)
        )
        self.notes_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Case specifics section
        ttk.Label(
            notes_frame,
            text="Case Specifics (optional instructions/guidance):",
            font=("Arial", 9)
        ).grid(row=1, column=0, sticky=tk.W, pady=(10, 2))

        self.case_specifics_text = scrolledtext.ScrolledText(
            notes_frame,
            wrap=tk.WORD,
            width=70,
            height=3,
            font=("Arial", 9)
        )
        self.case_specifics_text.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Buttons frame
        button_frame = ttk.Frame(notes_frame)
        button_frame.grid(row=1, column=0, pady=(5, 0))

        load_button = ttk.Button(
            button_frame,
            text="Load from File",
            command=self._load_notes_file
        )
        load_button.grid(row=0, column=0, padx=5)

        clear_button = ttk.Button(
            button_frame,
            text="Clear",
            command=self._clear_notes
        )
        clear_button.grid(row=0, column=1, padx=5)

        clear_specifics_button = ttk.Button(
            button_frame,
            text="Clear Specifics",
            command=self._clear_specifics
        )
        clear_specifics_button.grid(row=0, column=2, padx=5)

        # Output path section
        output_frame = ttk.LabelFrame(main_frame, text="Output", padding="10")
        output_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=5)
        output_frame.columnconfigure(1, weight=1)

        # Case/file name
        ttk.Label(output_frame, text="Case Name:").grid(row=0, column=0, padx=(0, 5), sticky=tk.W)

        self.case_name_var = tk.StringVar()
        case_name_entry = ttk.Entry(
            output_frame,
            textvariable=self.case_name_var,
            width=50
        )
        case_name_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5)

        # Output directory
        ttk.Label(output_frame, text="Save to:").grid(row=1, column=0, padx=(0, 5), pady=(5, 0), sticky=tk.W)

        self.output_path_var = tk.StringVar(value=str(settings.OUTPUT_DIR))
        output_entry = ttk.Entry(
            output_frame,
            textvariable=self.output_path_var,
            width=50
        )
        output_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=5, pady=(5, 0))

        browse_button = ttk.Button(
            output_frame,
            text="Browse...",
            command=self._browse_output
        )
        browse_button.grid(row=1, column=2, pady=(5, 0))

        # Progress section
        progress_frame = ttk.LabelFrame(main_frame, text="Status", padding="10")
        progress_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=5)
        progress_frame.columnconfigure(0, weight=1)

        self.status_label = ttk.Label(
            progress_frame,
            text="Ready to generate affidavit",
            font=("Arial", 9)
        )
        self.status_label.grid(row=0, column=0, sticky=tk.W)

        self.progress_bar = ttk.Progressbar(
            progress_frame,
            mode='determinate',
            length=300
        )
        self.progress_bar.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(5, 0))

        # Generate button
        self.generate_button = ttk.Button(
            main_frame,
            text="Generate Affidavit",
            command=self._start_generation,
            style="Accent.TButton"
        )
        self.generate_button.grid(row=4, column=0, pady=10)

        # Info label
        info_label = ttk.Label(
            main_frame,
            text="This process runs in the background. You can close this window after clicking Generate.",
            font=("Arial", 8),
            foreground="gray"
        )
        info_label.grid(row=5, column=0)

    def _load_notes_file(self):
        """Load notes from a text file."""
        filename = filedialog.askopenfilename(
            title="Select Interview Notes File",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.notes_text.delete(1.0, tk.END)
                self.notes_text.insert(1.0, content)
                logger.info(f"Loaded notes from: {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load file: {str(e)}")

    def _clear_notes(self):
        """Clear the notes text area."""
        self.notes_text.delete(1.0, tk.END)

    def _clear_specifics(self):
        """Clear the case specifics text area."""
        self.case_specifics_text.delete(1.0, tk.END)

    def _browse_output(self):
        """Browse for output directory."""
        directory = filedialog.askdirectory(
            title="Select Output Directory",
            initialdir=self.output_path_var.get()
        )
        if directory:
            self.output_path_var.set(directory)

    def _start_generation(self):
        """Start the affidavit generation process."""
        # Validate inputs
        notes = self.notes_text.get(1.0, tk.END).strip()
        if not notes:
            messagebox.showwarning("No Notes", "Please enter or load interview notes.")
            return

        case_name = self.case_name_var.get().strip()
        if not case_name:
            messagebox.showwarning("No Case Name", "Please enter a case name for organizing the output files.")
            return

        output_path = self.output_path_var.get().strip()
        if not output_path:
            messagebox.showwarning("No Output Path", "Please specify an output location.")
            return

        # Get case specifics (optional)
        case_specifics = self.case_specifics_text.get(1.0, tk.END).strip()

        # Check if runner is already running
        if self.runner.is_running:
            messagebox.showinfo("Already Running", "Pipeline is already running in the background.")
            return

        # Disable generate button
        self.generate_button.config(state='disabled')
        self.progress_bar['value'] = 0
        self.status_label.config(text="Starting pipeline...")

        # Start pipeline in background
        self.runner.start(
            notes=notes,
            output_path=output_path,
            case_name=case_name,
            case_specifics=case_specifics,
            progress_callback=self._on_progress,
            completion_callback=self._on_completion
        )

        logger.info("Pipeline started")

    def _on_progress(self, message: str, progress: int):
        """
        Handle progress updates from pipeline.

        Note: Called from background thread, use thread-safe updates.
        """
        # Schedule GUI update in main thread
        self.window.after(0, self._update_progress, message, progress)

    def _update_progress(self, message: str, progress: int):
        """Update progress in main thread (thread-safe)."""
        self.status_label.config(text=message)
        if progress >= 0:
            self.progress_bar['value'] = progress
        logger.debug(f"Progress: {progress}% - {message}")

    def _on_completion(self, message: str, success: bool):
        """
        Handle pipeline completion.

        Note: Called from background thread, use thread-safe updates.
        """
        # Schedule GUI update in main thread
        self.window.after(0, self._handle_completion, message, success)

    def _handle_completion(self, message: str, success: bool):
        """Handle completion in main thread (thread-safe)."""
        self.generate_button.config(state='normal')
        self.progress_bar['value'] = 100 if success else 0
        self.status_label.config(text=message)

        # Show message box
        if success:
            messagebox.showinfo("Success", message)
        else:
            messagebox.showerror("Error", message)

        logger.info(f"Pipeline completed: {message}")

    def _prompt_for_api_key(self):
        """Prompt user to enter API key on first run."""
        # Create a simple dialog
        dialog = tk.Toplevel(self.window)
        dialog.title("API Key Required")
        dialog.geometry("500x200")
        dialog.transient(self.window)
        dialog.grab_set()

        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (500 // 2)
        y = (dialog.winfo_screenheight() // 2) - (200 // 2)
        dialog.geometry(f"500x200+{x}+{y}")

        # Content
        frame = ttk.Frame(dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(
            frame,
            text="Anthropic API Key Required",
            font=("Arial", 12, "bold")
        ).pack(pady=(0, 10))

        ttk.Label(
            frame,
            text="Please enter your Anthropic API key.\nYou can find it at: https://console.anthropic.com/",
            justify=tk.LEFT
        ).pack(pady=(0, 10))

        # API key entry
        key_var = tk.StringVar()
        key_entry = ttk.Entry(frame, textvariable=key_var, width=60, show="*")
        key_entry.pack(pady=5)
        key_entry.focus()

        # Button frame
        button_frame = ttk.Frame(frame)
        button_frame.pack(pady=10)

        def save_key():
            key = key_var.get().strip()
            if not key:
                messagebox.showwarning("Empty Key", "Please enter an API key.")
                return
            if not key.startswith("sk-ant-"):
                if not messagebox.askyesno(
                    "Confirm Key",
                    "The API key doesn't look correct (should start with 'sk-ant-').\nSave anyway?"
                ):
                    return

            try:
                settings.save_api_key(key)
                settings.ANTHROPIC_API_KEY = key
                messagebox.showinfo("Success", "API key saved successfully!")
                dialog.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save API key: {str(e)}")

        def cancel():
            if messagebox.askyesno(
                "Exit",
                "The application requires an API key to function.\nExit without saving?"
            ):
                self.window.destroy()
                dialog.destroy()

        ttk.Button(button_frame, text="Save", command=save_key).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=cancel).pack(side=tk.LEFT, padx=5)

        # Handle window close
        dialog.protocol("WM_DELETE_WINDOW", cancel)

        # Wait for dialog to close
        self.window.wait_window(dialog)

    def run(self):
        """Start the application."""
        logger.info("Starting GUI")
        self.window.mainloop()
