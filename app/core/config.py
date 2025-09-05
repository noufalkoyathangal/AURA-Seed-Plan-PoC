from pydantic_settings import BaseSettings
from typing import List, Dict, Any

class Settings(BaseSettings):
    data_dir: str = "data"
    out_dir: str = "out"
    cors_allow_origins: List[str] = ["*"]
    swagger_ui_parameters: Dict[str, Any] = {
        "deepLinking": True,
        "displayRequestDuration": True,
        "tryItOutEnabled": True,
    }
    class Config:
        extra = "ignore"

settings = Settings()
