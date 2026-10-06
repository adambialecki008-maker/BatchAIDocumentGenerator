from app.models import ClientInput, RunSummary, ClientFailure
from app.document_renderer import DocxRenderer
from app.content_generator import ContentGenerator
from app.document_service import render_client_documents
from pathlib import Path
from app.client_repository import load_clients
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
    failures = []
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
        except Exception as exc:
            failed += 1
            failures.append(
                ClientFailure(
                    client_id=client.client_id,
                    error=str(exc),
                )
            )

    summary = RunSummary(
        processed=processed,
        succeeded=succeeded,
        failed=failed,
        skipped=skipped,
        failures=failures,
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


def process_excel_batch(
    input_path: Path,
    generator: ContentGenerator,
    renderer: DocxRenderer,
    output_dir: Path,
) -> RunSummary:
    clients = load_clients(input_path)

    return process_clients_documents(
        clients,
        generator,
        renderer,
        output_dir,
    )
