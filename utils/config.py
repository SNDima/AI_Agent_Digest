import yaml
from pathlib import Path
from typing import Dict, Any


def load_config(config_path: str) -> Dict[str, Any]:
    """Load and validate YAML configuration file."""
    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")
    
    with open(path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    
    if not config:
        raise ValueError(f"Invalid config file: empty or malformed YAML in {config_path}")
    
    return config


def get_database_file(config_path: str) -> str:
    """Load database file name from database configuration."""
    config = load_config(config_path)
    
    if "database" not in config:
        raise ValueError(f"Invalid database config file: missing 'database' key in {config_path}")
    
    db_file = config["database"].get("file")
    if not db_file:
        raise ValueError(f"Invalid database config file: missing 'database.file' in {config_path}")
    
    return db_file


def get_sources_config(config_path: str) -> Dict[str, Any]:
    """Load sources configuration and validate it."""
    config = load_config(config_path)
    
    if "sources" not in config:
        raise ValueError(f"Invalid config file: missing 'sources' key in {config_path}")
    
    if not isinstance(config["sources"], list) or len(config["sources"]) == 0:
        raise ValueError(f"Invalid config file: 'sources' must be a non-empty list in {config_path}")
    
    if not any(source.get("enabled", False) for source in config["sources"]):
        raise ValueError(f"Invalid config file: at least one source must be enabled in {config_path}")
    
    return config
