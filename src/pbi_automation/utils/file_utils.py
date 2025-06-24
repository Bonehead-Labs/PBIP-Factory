import json
import yaml
import pandas as pd
from pathlib import Path
from typing import Any, Dict, List

def read_json(path: Path) -> Dict[str, Any]:
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def write_json(path: Path, data: Dict[str, Any]):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

def read_yaml(path: Path) -> Dict[str, Any]:
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def read_csv(path: Path) -> List[Dict[str, Any]]:
    df = pd.read_csv(path)
    return df.to_dict(orient='records') 