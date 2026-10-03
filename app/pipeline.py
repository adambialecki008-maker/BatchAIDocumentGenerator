from app.models import ClientInput, RunSummary
from app.document_renderer import DocxRenderer
from app.content_generator import ContentGenerator
from app.document_service import render_client_documents
from pathlib import Path
import json


def process_client_documents(
    client: ClientInput,
    generator: ContentGenerator,
    renderer: DocxRenderer,
    output_dir: Path,
) -> None:
    content = generator.generate(client)
    render_client_documents(
        client,
        content,
        renderer,
        output_dir,
    )


def process_clients_documents(
    clients: list[ClientInput],
    generator: ContentGenerator,
    renderer: DocxRenderer,
    output_dir: Path,
) -> RunSummary:
    processed = 0
    succeeded = 0
    failed = 0
    skipped = 0
    for client in clients:
        processed += 1
        try:
            process_client_documents(
                client,
                generator,
                renderer,
                output_dir,
            )
            succeeded += 1
        except Exception:
            failed += 1
    summary = RunSummary(
        processed=processed,
        succeeded=succeeded,
        failed=failed,
        skipped=skipped,
    )
    save_run_summary(
        summary,
        output_dir,
    )
    return summary


def save_run_summary(
    summary: RunSummary,
    output_dir: Path,
) -> None:
    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    summary_path = output_dir / "run_summary.json"

    summary_path.write_text(
        json.dumps(
            summary.model_dump(),
            indent=2,
        ),
        encoding="utf-8",
    )
