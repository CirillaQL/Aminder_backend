import yaml
from pathlib import Path
from pydantic import BaseModel
from typing import Dict, Any

class DatabaseConfig(BaseModel):
    host: str
    port: int
    user: str
    password: str
    name: str
    pool_size: int = 5
    max_overflow: int = 10
    pool_timeout: int = 30
    pool_recycle: int = 1800

class AppConfig(BaseModel):
    debug: bool
    title: str

class Settings(BaseModel):
    database: DatabaseConfig
    app: AppConfig

    @classmethod
    def load_from_yaml(cls, path: str = "config.yaml") -> "Settings":
        config_path = Path(path)
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found at {path}")
        
        with open(config_path, "r") as f:
            config_data = yaml.safe_load(f)
            
        return cls(**config_data)

# Create a global settings instance
try:
    settings = Settings.load_from_yaml()
except Exception as e:
    print(f"Error loading configuration: {e}")
    # Fallback or exit depending on requirements. 
    # For now, we'll let it fail if config is missing as it's critical.
    raise
