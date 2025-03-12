import json
from pathlib import Path
import csv

import structlog

logger = structlog.get_logger(__name__)


def load_json(file_path: Path) -> dict:
    """Read the JSON file."""
    with file_path.open() as f:
        return json.load(f)


def append_to_csv(csv_file: str, data):
    with open(csv_file, 'a', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=data.keys())

    # Write the header only if the file is empty
    if file.tell() == 0:
        writer.writeheader()

    # Write the single row
    writer.writerow(data)

    # Todo: add error handling


def save_json(contents: dict, file_path: Path) -> None:
    """Save json files to specified path."""

    with file_path.open("w") as f:
        json.dump(contents, f, indent=4)
    logger.info("Data has been saved.", file_path=file_path)
