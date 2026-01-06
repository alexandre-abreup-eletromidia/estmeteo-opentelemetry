import logging
import datetime
from typing import Sequence
from opentelemetry.sdk.logs.export import LogExporter, LogExportResult, LogData
from googleapiclient.discovery import build
from src.utils.auth import get_google_credentials
from src import config

class GoogleSheetsLogExporter(LogExporter):
    """Custom OpenTelemetry exporter for Google Sheets."""
    
    def __init__(self):
        self.spreadsheet_id = config.GOOGLE_SHEET_ID
        self.sheet_name = config.GOOGLE_SHEET_NAME
        self.creds = get_google_credentials()
        self.service = build('sheets', 'v4', credentials=self.creds)
        self.logger = logging.getLogger(__name__)
        
    def export(self, batch: Sequence[LogData]) -> LogExportResult:
        """Export logs to Google Sheets in batches."""
        if not self.spreadsheet_id:
             self.logger.error("GOOGLE_SHEET_ID is not configured.")
             return LogExportResult.FAILURE

        rows = []
        for log in batch:
            record = log.log_record
            
            # Timestamp to YYYY-MM-DD HH:MM:SS
            timestamp_ns = record.timestamp
            dt = datetime.datetime.fromtimestamp(timestamp_ns / 1e9, datetime.timezone.utc)
            timestamp_str = dt.strftime('%Y-%m-%d %H:%M:%S')

            attrs = record.attributes or {}
            
            row = [
                timestamp_str,
                str(attrs.get("station_id", "")),
                record.severity_text or "INFO",
                str(attrs.get("category", "")),
                str(record.body),
                str(attrs.get("temperature", "")),
                str(attrs.get("humidity", "")),
                str(attrs.get("pressure", "")),
                str(attrs.get("rain", "")),
                str(attrs.get("api_status", "")),
                str(attrs.get("response_time_ms", "")),
                str(attrs.get("offline_cache_size", "")),
                format(record.trace_id, '032x') if record.trace_id else ""
            ]
            rows.append(row)

        if not rows:
             return LogExportResult.SUCCESS

        try:
            self.service.spreadsheets().values().append(
                spreadsheetId=self.spreadsheet_id,
                range=f"{self.sheet_name}!A:M",
                valueInputOption="USER_ENTERED",
                body={"values": rows}
            ).execute()
            return LogExportResult.SUCCESS
        except Exception as e:
            self.logger.error(f"Failed to export to Sheets: {e}")
            return LogExportResult.FAILURE

    def shutdown(self):
        pass
