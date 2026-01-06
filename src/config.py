import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent
CREDENTIALS_DIR = BASE_DIR / "credentials"

# Google Sheets
GOOGLE_CREDENTIALS_PATH = os.getenv("GOOGLE_CREDENTIALS_PATH", str(CREDENTIALS_DIR / "credentials.json"))
GOOGLE_TOKEN_PATH = os.getenv("GOOGLE_TOKEN_PATH", str(CREDENTIALS_DIR / "token.json"))
GOOGLE_SHEET_ID = os.getenv("GOOGLE_SHEET_ID")
GOOGLE_SHEET_NAME = os.getenv("GOOGLE_SHEET_NAME", "Logs")

# Metrics & Logs Source
SOURCE_LOG_DIR = os.getenv("SOURCE_LOG_DIR", os.path.expanduser("~/logs_estacao"))

# OpenTelemetry
OTEL_SERVICE_NAME = os.getenv("OTEL_SERVICE_NAME", "estacao-meteorologica")
OTEL_SERVICE_VERSION = os.getenv("OTEL_SERVICE_VERSION", "1.0.0")

# Exporter
BATCH_SIZE = int(os.getenv("BATCH_SIZE", "100"))
EXPORT_INTERVAL_SECONDS = int(os.getenv("EXPORT_INTERVAL_SECONDS", "60"))
MAX_RETRY_ATTEMPTS = int(os.getenv("MAX_RETRY_ATTEMPTS", "3"))

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
