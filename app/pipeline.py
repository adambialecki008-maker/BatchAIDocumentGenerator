import json
from pathlib import Path

from app.client_repository import load_clients
from app.content_generator import ContentGenerator
from app.document_renderer import DocxRenderer
from app.document_service import render_client_documents
from app.models import (
    ClientFailure,
    ClientInput,
    RunSummary,
    SkippedRecord,
)

REPORT_FILENAME = "batch_report.json"


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
    skipped_records: list[SkippedRecord] | None = None,
) -> RunSummary:
    if skipped_records is None:
        skipped_records = []

    succeeded = 0
    failed = 0

    failures: list[ClientFailure] = []

    for client in clients:
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
        processed=(len(clients) + len(skipped_records)),
        succeeded=succeeded,
        failed=failed,
        skipped=len(skipped_records),
        failures=failures,
        skipped_records=skipped_records,
    )

    save_batch_report(
        summary,
        output_dir,
    )

    return summary


def save_batch_report(
    summary: RunSummary,
    output_dir: Path,
) -> None:
    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    report_path = output_dir / REPORT_FILENAME

    report_path.write_text(
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
    load_result = load_clients(input_path)

    return process_clients_documents(
        load_result.clients,
        generator,
        renderer,
        output_dir,
        skipped_records=(load_result.skipped_records),
    )
