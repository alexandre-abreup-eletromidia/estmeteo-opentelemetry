import time
import logging
import re
import glob
import os
import sys
from datetime import datetime

from opentelemetry import logs
from opentelemetry.sdk.logs import LogRecord

from src import config
from src.otel_setup import setup_opentelemetry

# Regex Patterns
BASE_PATTERN = re.compile(r'^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\s+(\w+)\s+\[(.*?)\]\s+(.*)$')
SENSOR_PATTERN = re.compile(r'Temp:\s*([\d.]+)°C,\s*Umid:\s*([\d.]+)%,\s*Press:\s*([\d.]+)hPa,\s*Rain:\s*([\d.]+)mm')
API_PATTERN = re.compile(r'API Response:\s*(\d+)\s+OK\s+\(latency:\s*(\d+)ms\)')
CACHE_PATTERN = re.compile(r'pendencias:\s*(\d+)')

SEVERITY_MAP = {
    "DEBUG": 5,
    "INFO": 9,
    "WARNING": 13,
    "ERROR": 17,
    "CRITICAL": 21, 
    "FATAL": 21
}

# Configure local logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("main")

def get_latest_log_file():
    """Find the latest log file in the source directory."""
    try:
        if not os.path.exists(config.SOURCE_LOG_DIR):
             # Just return None if dir doesn't exist yet
             return None
             
        search_path = os.path.join(config.SOURCE_LOG_DIR, "estacao_*.log")
        files = glob.glob(search_path)
        if not files:
            return None
        return max(files, key=os.path.getmtime)
    except Exception as e:
        logger.error(f"Error finding log file: {e}")
        return None

def parse_and_emit(otel_logger, line):
    line = line.strip()
    if not line:
        return

    match = BASE_PATTERN.match(line)
    if not match:
        # Emit as raw log if pattern doesn't match
        otel_logger.emit(LogRecord(
            timestamp=time.time_ns(),
            body=line,
            severity_number=9, # INFO
            severity_text="INFO",
            attributes={"category": "UNSTRUCTURED"}
        ))
        return

    ts_str, level, station_id, message = match.groups()
    
    # Parse Timestamp
    try:
        dt = datetime.strptime(ts_str, '%Y-%m-%d %H:%M:%S')
        timestamp_ns = int(dt.timestamp() * 1e9)
    except Exception:
        timestamp_ns = time.time_ns()

    attributes = {
        "station_id": station_id,
        "category": "SYSTEM"
    }

    # Extract Metrics
    sensor_match = SENSOR_PATTERN.search(message)
    if sensor_match:
        attributes.update({
            "category": "SENSOR_READ",
            "temperature": float(sensor_match.group(1)),
            "humidity": float(sensor_match.group(2)),
            "pressure": float(sensor_match.group(3)),
            "rain": float(sensor_match.group(4))
        })
    
    api_match = API_PATTERN.search(message)
    if api_match:
        attributes.update({
            "category": "API_SEND",
            "api_status": int(api_match.group(1)),
            "response_time_ms": int(api_match.group(2))
        })
        
    cache_match = CACHE_PATTERN.search(message)
    if cache_match:
        attributes.update({
            "category": "OFFLINE_CACHE",
            "offline_cache_size": int(cache_match.group(1))
        })

    severity_num = SEVERITY_MAP.get(level.upper(), 9)
    
    otel_logger.emit(LogRecord(
        timestamp=timestamp_ns,
        observed_timestamp=time.time_ns(),
        body=message,
        severity_text=level,
        severity_number=severity_num,
        attributes=attributes
    ))

def tail_file(otel_logger, filepath):
    logger.info(f"Tailing file: {filepath}")
    try:
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            f.seek(0, 2) # Start at end
            
            while True:
                line = f.readline()
                if not line:
                    time.sleep(1)
                    # Check for rotation
                    latest = get_latest_log_file()
                    if latest and os.path.abspath(latest) != os.path.abspath(filepath):
                        logger.info("Log rotation detected.")
                        return # Return to main loop to switch file
                    if not os.path.exists(filepath):
                         logger.warning("File disappeared.")
                         return
                    continue
                
                try:
                    parse_and_emit(otel_logger, line)
                except Exception as e:
                    logger.error(f"Error parsing line: {e}")
                    
    except Exception as e:
        logger.error(f"Error handling file {filepath}: {e}")
        time.sleep(5)

def main():
    logger.info("Initializing estmeteo-opentelemetry agent...")
    _ = setup_opentelemetry()
    otel_logger = logs.get_logger("estacao.log_shipper")
    
    logger.info(f"Log Source Directory: {config.SOURCE_LOG_DIR}")
    
    while True:
        try:
            latest_file = get_latest_log_file()
            
            if latest_file:
                logger.info(f"Active log file: {latest_file}")
                tail_file(otel_logger, latest_file)
            else:
                logger.warning(f"No log files found in {config.SOURCE_LOG_DIR}. Retrying in 10s...")
                time.sleep(10)
                
        except KeyboardInterrupt:
            logger.info("Stopping agent...")
            sys.exit(0)
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
