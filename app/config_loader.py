import yaml
from pathlib import Path

CONFIGS_DIR = Path(__file__).parent.parent / "configs"

def load_config(name: str) -> dict:
    path = CONFIGS_DIR / f"{name}.yaml"
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)