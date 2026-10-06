import os
import shutil
import subprocess
import time
from pathlib import Path
from typing import Callable

MODEL_NAME = "qwen2.5:3b"

StatusCallback = Callable[[str], None]

CREATE_NO_WINDOW = getattr(
    subprocess,
    "CREATE_NO_WINDOW",
    0,
)


class AISetupError(RuntimeError):
    pass


def ensure_ai_ready(
    status_callback: StatusCallback | None = None,
) -> Path:
    _status(
        status_callback,
        "Checking AI engine...",
    )

    ollama_path = find_ollama()

    if ollama_path is None:
        _status(
            status_callback,
            "Installing Ollama. This is required only once...",
        )

        install_ollama()

        ollama_path = find_ollama()

        if ollama_path is None:
            raise AISetupError(
                "Ollama installation completed, but " "ollama.exe could not be found."
            )

    _status(
        status_callback,
        "Starting Ollama...",
    )

    ensure_ollama_server(ollama_path)

    if not model_is_installed(
        ollama_path,
        MODEL_NAME,
    ):
        _status(
            status_callback,
            (f"Downloading AI model {MODEL_NAME}. " "This is required only once..."),
        )

        pull_model(
            ollama_path,
            MODEL_NAME,
        )

    _status(
        status_callback,
        "AI engine is ready.",
    )

    return ollama_path


def find_ollama() -> Path | None:
    executable = shutil.which("ollama")

    if executable:
        return Path(executable)

    local_app_data = os.environ.get("LOCALAPPDATA")

    if local_app_data:
        candidate = Path(local_app_data) / "Programs" / "Ollama" / "ollama.exe"

        if candidate.exists():
            return candidate

    return None


def install_ollama() -> None:
    winget = shutil.which("winget")

    if winget is None:
        raise AISetupError(
            "Windows Package Manager (winget) is not available. "
            "Install Microsoft App Installer or install Ollama manually."
        )

    result = subprocess.run(
        [
            winget,
            "install",
            "--id",
            "Ollama.Ollama",
            "-e",
            "--silent",
            "--accept-package-agreements",
            "--accept-source-agreements",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        creationflags=CREATE_NO_WINDOW,
    )

    if result.returncode != 0:
        message = (
            result.stderr.strip() or result.stdout.strip() or "Unknown winget error."
        )

        raise AISetupError(f"Could not install Ollama.\n\n{message}")


def ensure_ollama_server(
    ollama_path: Path,
) -> None:
    if ollama_server_is_running(ollama_path):
        return

    subprocess.Popen(
        [
            str(ollama_path),
            "serve",
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=CREATE_NO_WINDOW,
    )

    for _ in range(30):
        if ollama_server_is_running(ollama_path):
            return

        time.sleep(1)

    raise AISetupError(
        "Ollama was installed, but its local server " "could not be started."
    )


def ollama_server_is_running(
    ollama_path: Path,
) -> bool:
    try:
        result = subprocess.run(
            [
                str(ollama_path),
                "list",
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=5,
            creationflags=CREATE_NO_WINDOW,
        )

        return result.returncode == 0

    except (
        subprocess.TimeoutExpired,
        OSError,
    ):
        return False


def model_is_installed(
    ollama_path: Path,
    model: str,
) -> bool:
    result = subprocess.run(
        [
            str(ollama_path),
            "show",
            model,
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=CREATE_NO_WINDOW,
    )

    return result.returncode == 0


def pull_model(
    ollama_path: Path,
    model: str,
) -> None:
    result = subprocess.run(
        [
            str(ollama_path),
            "pull",
            model,
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        text=True,
        creationflags=CREATE_NO_WINDOW,
    )

    if result.returncode != 0:
        message = result.stderr.strip() or "Unknown Ollama error."

        raise AISetupError((f"Could not download AI model " f"'{model}'.\n\n{message}"))


def _status(
    callback: StatusCallback | None,
    message: str,
) -> None:
    if callback is not None:
        callback(message)
