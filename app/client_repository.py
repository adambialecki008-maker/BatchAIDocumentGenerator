from pathlib import Path
import pandas as pd
from openpyxl import load_workbook
from app.models import ClientInput
from pydantic import ValidationError


class MissingRequiredColumnsError(Exception):
    pass


class InvalidClientRecordError(ValueError):
    pass


def load_clients(path: Path) -> list[ClientInput]:
    dataframe = pd.read_excel(path)
    clients = []
    _validate_required_columns(dataframe)
    for row_number, record in enumerate(
        dataframe.to_dict(orient="records"),
        start=2,
    ):
        try:
            client = ClientInput(**record)
            clients.append(client)
        except ValidationError as error:
            first_error = error.errors()[0]
            field = ".".join(str(part) for part in first_error["loc"])
            message = first_error["msg"]
            raise InvalidClientRecordError(
                f"Excel row {row_number}, field '{field}': {message}"
            ) from error
    return clients


def _validate_required_columns(dataframe: pd.DataFrame) -> None:
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
            f"Missing required columns: {sorted(missing_columns)}"
        )
