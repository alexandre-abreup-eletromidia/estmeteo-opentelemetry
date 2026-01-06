import logging
from opentelemetry import logs
from opentelemetry.sdk.logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk.logs.export import BatchLogProcessor, ConsoleLogExporter
from opentelemetry.sdk.resources import Resource

from src import config
from src.exporters.google_sheets import GoogleSheetsLogExporter

def setup_opentelemetry():
    """Configure OpenTelemetry logging with Google Sheets and Console exporters."""
    
    # Create resource with service details
    resource = Resource.create(attributes={
        "service.name": config.OTEL_SERVICE_NAME,
        "service.version": config.OTEL_SERVICE_VERSION,
    })

    logger_provider = LoggerProvider(resource=resource)
    
    # Add Google Sheets Exporter
    try:
        sheets_exporter = GoogleSheetsLogExporter()
        sheets_processor = BatchLogProcessor(
            sheets_exporter,
            max_export_batch_size=config.BATCH_SIZE,
            schedule_delay_millis=config.EXPORT_INTERVAL_SECONDS * 1000
        )
        logger_provider.add_log_record_processor(sheets_processor)
        print("[INFO] Google Sheets exporter initialized.")
    except Exception as e:
        print(f"[ERROR] Failed to initialize Google Sheets exporter: {e}")

    # Add Console Exporter for debugging
    console_exporter = ConsoleLogExporter()
    console_processor = BatchLogProcessor(console_exporter)
    logger_provider.add_log_record_processor(console_processor)

    # Set global logger provider
    logs.set_logger_provider(logger_provider)
    
    # Return a handler to attach to python logging
    return LoggingHandler(level=logging.NOTSET, logger_provider=logger_provider)
