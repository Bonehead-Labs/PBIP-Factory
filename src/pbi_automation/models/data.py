from typing import Dict, Any, List
from pathlib import Path
import csv


class DataRow:
    """Represents a single row of data from the CSV file."""
    
    def __init__(self, data: Dict[str, Any]):
        self.data = data
    
    def get_folder_name(self) -> str:
        """Generate a stable project folder name.

        Prefers the explicit 'Report_Name' column when present; otherwise falls
        back to a "Name_Owner" concatenation to maintain backward compatibility.
        """
        if "Report_Name" in self.data:
            return self.data["Report_Name"]
        else:
            # Fallback to the old format
            name = self.data.get("Name", "Unknown")
            owner = self.data.get("Owner", "Unknown")
            return f"{name}_{owner}"
    
    def __getitem__(self, key: str) -> Any:
        return self.data[key]
    
    def get(self, key: str, default: Any = None) -> Any:
        return self.data.get(key, default)


def clean_column_name(column_name: str) -> str:
    """Normalize CSV column names by stripping BOM and whitespace artifacts."""
    return column_name.replace('\ufeff', '').replace('ï»¿', '').strip()


def load_data_from_csv(csv_path: Path) -> List[DataRow]:
    """Load CSV into a list of DataRow objects with basic schema validation.

    Enforces a consistent set of columns across all rows to prevent subtle
    mapping issues during generation.
    """
    parsed_rows: List[DataRow] = []
    try:
        # utf-8-sig handles potential BOM automatically
        with open(csv_path, 'r', encoding='utf-8-sig') as csv_file:
            reader = csv.DictReader(csv_file)
            expected_columns: List[str] | None = None
            for row_index, raw_row in enumerate(reader, start=1):
                cleaned_row = {clean_column_name(key): value for key, value in raw_row.items()}

                if expected_columns is None:
                    expected_columns = list(cleaned_row.keys())
                else:
                    current_columns = list(cleaned_row.keys())
                    if current_columns != expected_columns:
                        raise ValueError(f"Row {row_index} has different columns than the first row")

                parsed_rows.append(DataRow(cleaned_row))
        return parsed_rows
    except (OSError, csv.Error, ValueError) as error:
        raise RuntimeError(f"Failed to load or parse CSV: {error}")
    except Exception:
        # Re-raise unexpected exceptions to preserve traceback for callers
        raise