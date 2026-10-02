from pathlib import Path
import pandas as pd
from openpyxl import load_workbook
from app.models import ClientInput


class MissingRequiredColumnsError(Exception):
    pass


def load_clients(path: Path) -> list[ClientInput]:
    dataframe = pd.read_excel(path)
    clients = []
    _validate_required_columns(dataframe)
    for record in dataframe.to_dict(orient="records"):
        clients.append(ClientInput(**record))
    print(len(clients))
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
