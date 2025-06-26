from typing import Dict, Any, List
from pathlib import Path
import csv


class DataRow:
    """Represents a single row of data from the CSV file."""
    
    def __init__(self, data: Dict[str, Any]):
        self.data = data
    
    def get_folder_name(self) -> str:
        """Generate a folder name based on the data."""
        # Use Report_Name if available, otherwise fall back to Name_Owner
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


def load_data_from_csv(csv_path: Path) -> List[DataRow]:
    """Load data from a CSV file and return a list of DataRow objects."""
    data_rows = []
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            first_row = None
            for i, row in enumerate(reader, 1):
                if first_row is None:
                    first_row = set(row.keys())
                else:
                    current_row = set(row.keys())
                    if current_row != first_row:
                        raise ValueError(f"Row {i} has different columns than the first row")
                data_rows.append(DataRow(row))
        return data_rows
    except (OSError, csv.Error, ValueError) as e:
        raise RuntimeError(f"Failed to load or parse CSV: {e}")
    except Exception as e:
        raise 