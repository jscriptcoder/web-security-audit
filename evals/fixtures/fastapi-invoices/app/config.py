from pathlib import Path

import yaml
from pydantic import BaseModel


class Settings(BaseModel):
    database_url: str
    jwt_secret: str
    jwt_issuer: str = "https://invoices.example.com"
    jwt_audience: str = "invoices-api"
    web_origin: str = "https://app.invoices.example.com"
    payments_webhook_secret: str
    pdf_dir: Path = Path("/var/lib/invoices/pdf")


def load_settings(path: Path = Path("/etc/invoices/settings.yaml")) -> Settings:
    with path.open("rb") as handle:
        data = yaml.safe_load(handle) or {}
    return Settings.model_validate(data)


settings = load_settings()
