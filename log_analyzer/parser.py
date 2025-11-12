import gzip
import os
import re
from collections import namedtuple
from datetime import datetime
from pathlib import Path


LogFile = namedtuple("LogFile", ["path", "date", "extension"])

LOG_PATTERN = re.compile(r"nginx-access-ui\.log-(\d{8})\.(gz|log)$")


def find_latest_log(log_dir):
    """
    Находит самый последний файл логов в указанной директории.
    """
    latest_date = None
    latest_file = None
    for filename in os.listdir(log_dir):
        match = LOG_PATTERN.match(filename)
        if match:
            date_str, ext = match.groups()
            date = datetime.strptime(date_str, "%Y%m%d")
            if latest_date is None or date > latest_date:
                latest_date = date
                latest_file = LogFile(Path(log_dir) / filename, date, ext)
    return latest_file


def parse_log(log_path, extension):
    """
    Парсит лог-файл и извлекает информацию о запросах.
    """
    opener = gzip.open if extension == "gz" else open
    with opener(log_path, "rt", encoding="utf-8") as f:
        for line in f:
            try:
                parts = line.strip().split()
                if len(parts) < 12:
                    yield None
                    continue
                request = (
                    parts[5] + " " + parts[6] + " " + parts[7]
                )
                url = parts[6]
                request_time = float(parts[-1])
                yield {"url": url, "request_time": request_time}
            except (ValueError, IndexError):
                yield None
