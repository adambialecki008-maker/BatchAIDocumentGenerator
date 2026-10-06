from pathlib import Path

import pandas as pd
from pydantic import ValidationError

from app.models import (
    ClientInput,
    ClientLoadResult,
    SkippedRecord,
)


class MissingRequiredColumnsError(ValueError):
    pass


def load_clients(
    path: Path,
) -> ClientLoadResult:
    dataframe = pd.read_excel(path)

    _validate_required_columns(dataframe)

    clients: list[ClientInput] = []

    skipped_records: list[SkippedRecord] = []

    seen_client_ids: set[str] = set()

    records = dataframe.to_dict(orient="records")

    for row_number, record in enumerate(
        records,
        start=2,
    ):
        raw_client_id = record.get("client_id")

        client_id = _normalize_client_id(raw_client_id)

        # 1. client_id has highest priority
        if client_id is None:
            skipped_records.append(
                SkippedRecord(
                    row_number=row_number,
                    client_id=None,
                    error=("field 'client_id': " "must not be blank"),
                )
            )
            continue

        # 2. duplicate client_id before any
        #    other record validation
        if client_id in seen_client_ids:
            skipped_records.append(
                SkippedRecord(
                    row_number=row_number,
                    client_id=client_id,
                    error=("duplicate client_id"),
                )
            )
            continue

        # Mark ID as seen immediately.
        # Any later occurrence is duplicate,
        # even if this record contains another
        # validation error.
        seen_client_ids.add(client_id)

        # Keep normalized ID for Pydantic
        record["client_id"] = client_id

        # 3. validate the rest of the record
        try:
            client = ClientInput(**record)

        except ValidationError as error:
            skipped_records.append(
                _validation_error_to_skipped(
                    row_number=row_number,
                    client_id=client_id,
                    record=record,
                    error=error,
                )
            )
            continue

        clients.append(client)

    return ClientLoadResult(
        total_records=len(records),
        clients=clients,
        skipped_records=(skipped_records),
    )


def _validate_required_columns(
    dataframe: pd.DataFrame,
) -> None:
    expected_columns = {
        "client_id",
        "first_name",
        "last_name",
        "email",
        "target_role",
        "years_experience",
        "skills",
        "current_company",
        "current_role",
        "location",
        "key_achievement",
        "tone",
    }

    actual_columns = set(dataframe.columns)

    missing_columns = expected_columns - actual_columns

    if missing_columns:
        raise MissingRequiredColumnsError(
            "Missing required columns: " f"{sorted(missing_columns)}"
        )


def _validation_error_to_skipped(
    row_number: int,
    client_id: str,
    record: dict,
    error: ValidationError,
) -> SkippedRecord:
    first_error = error.errors()[0]

    location = first_error["loc"]

    field = ".".join(str(part) for part in location)

    root_field = str(location[0]) if location else ""

    value = record.get(root_field)

    if _is_blank(value):
        message = "must not be blank"
    else:
        message = first_error["msg"]

    return SkippedRecord(
        row_number=row_number,
        client_id=client_id,
        error=(f"field '{field}': " f"{message}"),
    )


def _normalize_client_id(
    value,
) -> str | None:
    if _is_blank(value):
        return None

    return str(value).strip()


def _is_blank(
    value,
) -> bool:
    if value is None:
        return True

    if isinstance(value, str) and not value.strip():
        return True

    try:
        return bool(pd.isna(value))

    except (
        TypeError,
        ValueError,
    ):
        return False
