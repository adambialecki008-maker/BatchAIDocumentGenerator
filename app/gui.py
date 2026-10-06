import ctypes
import sys
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from app.bootstrap import (
    AISetupError,
    MODEL_NAME,
    ensure_ai_ready,
)
from app.client_repository import (
    MissingRequiredColumnsError,
    load_clients,
)
from app.content_generator import OllamaGenerator
from app.document_renderer import DocxRenderer
from app.pipeline import (
    REPORT_FILENAME,
    process_clients_documents,
)

APP_USER_MODEL_ID = "BatchAIDocumentGenerator"


def resource_root() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS)

    return Path(__file__).resolve().parent.parent


PROJECT_ROOT = resource_root()

RESUME_TEMPLATE = PROJECT_ROOT / "templates" / "resume_template.docx"

COVER_LETTER_TEMPLATE = PROJECT_ROOT / "templates" / "cover_letter_template.docx"

APP_ICON_ICO = PROJECT_ROOT / "assets" / "app.ico"

APP_ICON_PNG = PROJECT_ROOT / "assets" / "app.png"


class BatchAIDocumentGeneratorApp:
    def __init__(
        self,
        root: tk.Tk,
    ) -> None:
        self.root = root

        self.root.title("Batch AI Document Generator")

        self.root.geometry("650x270")

        self.root.resizable(
            False,
            False,
        )

        self.input_path = tk.StringVar()
        self.output_path = tk.StringVar()

        self.status = tk.StringVar(value=("Select an Excel file " "and output folder."))

        self._build_ui()

    def _build_ui(
        self,
    ) -> None:
        frame = ttk.Frame(
            self.root,
            padding=20,
        )

        frame.pack(
            fill="both",
            expand=True,
        )

        ttk.Label(
            frame,
            text="Candidate Excel file",
        ).grid(
            row=0,
            column=0,
            sticky="w",
        )

        ttk.Entry(
            frame,
            textvariable=self.input_path,
            width=58,
        ).grid(
            row=1,
            column=0,
            padx=(0, 10),
            pady=(4, 14),
        )

        ttk.Button(
            frame,
            text="Browse...",
            command=self._select_input,
        ).grid(
            row=1,
            column=1,
            pady=(4, 14),
        )

        ttk.Label(
            frame,
            text="Output folder",
        ).grid(
            row=2,
            column=0,
            sticky="w",
        )

        ttk.Entry(
            frame,
            textvariable=self.output_path,
            width=58,
        ).grid(
            row=3,
            column=0,
            padx=(0, 10),
            pady=(4, 18),
        )

        ttk.Button(
            frame,
            text="Browse...",
            command=self._select_output,
        ).grid(
            row=3,
            column=1,
            pady=(4, 18),
        )

        self.generate_button = ttk.Button(
            frame,
            text="Generate Documents",
            command=self._start_generation,
        )

        self.generate_button.grid(
            row=4,
            column=0,
            sticky="w",
        )

        self.progress = ttk.Progressbar(
            frame,
            mode="indeterminate",
            length=250,
        )

        self.progress.grid(
            row=4,
            column=0,
            padx=(180, 0),
            sticky="w",
        )

        self.progress.grid_remove()

        ttk.Label(
            frame,
            textvariable=self.status,
            wraplength=590,
        ).grid(
            row=5,
            column=0,
            columnspan=2,
            sticky="w",
            pady=(20, 0),
        )

    def _select_input(
        self,
    ) -> None:
        path = filedialog.askopenfilename(
            title="Select candidate Excel file",
            filetypes=[
                (
                    "Excel files",
                    "*.xlsx",
                ),
            ],
        )

        if path:
            self.input_path.set(path)

    def _select_output(
        self,
    ) -> None:
        path = filedialog.askdirectory(title="Select output folder")

        if path:
            self.output_path.set(path)

    def _start_generation(
        self,
    ) -> None:
        if not self.input_path.get():
            messagebox.showerror(
                "Missing input",
                "Select an Excel file.",
            )
            return

        if not self.output_path.get():
            messagebox.showerror(
                "Missing output",
                "Select an output folder.",
            )
            return

        self.generate_button.config(state="disabled")

        self.progress.grid()
        self.progress.start(10)

        self.status.set("Validating Excel...")

        thread = threading.Thread(
            target=self._generate,
            daemon=True,
        )

        thread.start()

    def _generate(
        self,
    ) -> None:
        try:
            input_path = Path(self.input_path.get())

            output_path = Path(self.output_path.get())

            self._validate_input(input_path)

            self._validate_templates()

            self._set_status_from_worker("Validating Excel...")

            load_result = load_clients(input_path)

            renderer = DocxRenderer(
                RESUME_TEMPLATE,
                COVER_LETTER_TEMPLATE,
            )

            generator = OllamaGenerator(MODEL_NAME)

            if load_result.clients:
                ensure_ai_ready(self._set_status_from_worker)

                self._set_status_from_worker("Generating documents...")

            summary = process_clients_documents(
                load_result.clients,
                generator,
                renderer,
                output_path,
                skipped_records=(load_result.skipped_records),
            )

            self.root.after(
                0,
                lambda: self._generation_finished(
                    summary,
                    output_path,
                ),
            )

        except (
            MissingRequiredColumnsError,
            ValueError,
            FileNotFoundError,
        ) as exc:
            self.root.after(
                0,
                lambda error=str(exc): self._generation_error(
                    "Input validation error",
                    error,
                ),
            )

        except AISetupError as exc:
            self.root.after(
                0,
                lambda error=str(exc): self._generation_error(
                    "AI setup error",
                    error,
                ),
            )

        except Exception as exc:
            self.root.after(
                0,
                lambda error=str(exc): self._generation_error(
                    "Generation error",
                    error,
                ),
            )

    def _validate_input(
        self,
        input_path: Path,
    ) -> None:
        if not input_path.exists():
            raise FileNotFoundError(("Input file does not exist:\n" f"{input_path}"))

        if not input_path.is_file():
            raise ValueError("Selected input is not a file.")

        if input_path.suffix.lower() != ".xlsx":
            raise ValueError("Input file must be an .xlsx Excel file.")

    def _validate_templates(
        self,
    ) -> None:
        if not RESUME_TEMPLATE.exists():
            raise FileNotFoundError("Resume template is missing.")

        if not COVER_LETTER_TEMPLATE.exists():
            raise FileNotFoundError("Cover letter template is missing.")

    def _set_status_from_worker(
        self,
        message: str,
    ) -> None:
        self.root.after(
            0,
            lambda: self.status.set(message),
        )

    def _generation_finished(
        self,
        summary,
        output_path: Path,
    ) -> None:
        self.progress.stop()
        self.progress.grid_remove()

        self.generate_button.config(state="normal")

        if summary.failed or summary.skipped:
            self.status.set(
                (
                    "Completed with issues. "
                    f"{summary.succeeded} generated, "
                    f"{summary.skipped} skipped, "
                    f"{summary.failed} failed."
                )
            )

            details = []

            if summary.skipped_records:
                details.append("Skipped records:")

                for record in summary.skipped_records:
                    if record.client_id:
                        identifier = f"{record.client_id} " f"(row {record.row_number})"
                    else:
                        identifier = f"Row {record.row_number}"

                    details.append((f"{identifier}: " f"{record.error}"))

            if summary.failures:
                if details:
                    details.append("")

                details.append("Generation failures:")

                for failure in summary.failures:
                    details.append((f"{failure.client_id}: " f"{failure.error}"))

            details_text = "\n".join(details)

            messagebox.showwarning(
                "Completed with issues",
                (
                    f"Processed: {summary.processed}\n"
                    f"Succeeded: {summary.succeeded}\n"
                    f"Skipped: {summary.skipped}\n"
                    f"Failed: {summary.failed}\n\n"
                    f"{details_text}\n\n"
                    f"See {REPORT_FILENAME} "
                    "for full details."
                ),
            )

            return

        self.status.set(
            ("Done. Generated documents for " f"{summary.succeeded} candidates.")
        )

        messagebox.showinfo(
            "Generation complete",
            (
                f"Processed: {summary.processed}\n"
                f"Succeeded: {summary.succeeded}\n"
                f"Skipped: {summary.skipped}\n"
                f"Failed: {summary.failed}\n\n"
                "Files saved to:\n"
                f"{output_path}"
            ),
        )

    def _generation_error(
        self,
        title: str,
        message: str,
    ) -> None:
        self.progress.stop()
        self.progress.grid_remove()

        self.generate_button.config(state="normal")

        self.status.set("Generation failed.")

        messagebox.showerror(
            title,
            message,
        )


def _configure_windows_app_id() -> None:
    if sys.platform != "win32":
        return

    try:
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(APP_USER_MODEL_ID)
    except Exception:
        pass


def _configure_window_icon(
    root: tk.Tk,
) -> None:
    if APP_ICON_ICO.exists():
        try:
            root.iconbitmap(str(APP_ICON_ICO))
        except tk.TclError:
            pass

    if APP_ICON_PNG.exists():
        try:
            icon_image = tk.PhotoImage(file=str(APP_ICON_PNG))

            root.iconphoto(
                True,
                icon_image,
            )

            root._icon_image = icon_image

        except tk.TclError:
            pass


def run_gui() -> None:
    _configure_windows_app_id()

    root = tk.Tk()

    _configure_window_icon(root)

    BatchAIDocumentGeneratorApp(root)

    root.mainloop()
