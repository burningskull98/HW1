import structlog
import argparse
import sys
import traceback
from collections import namedtuple
from pathlib import Path
from log_analyzer.config import DEFAULT_CONFIG
from log_analyzer.parser import find_latest_log, parse_log
from log_analyzer.analyzer import analyze_logs
from log_analyzer.reporter import generate_report

LogFile = namedtuple("LogFile", ["path", "date", "extension"])


def load_config(config_path):
    """
    Загружает конфигурацию из указанного файла.
    """
    config = DEFAULT_CONFIG.copy()
    if config_path:
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                exec(f.read(), {}, config)
        except Exception as e:
            raise ValueError(f"Failed to load config from {config_path}: {e}")
    return config


def setup_logging(config):
    """
    Настраивает логирование на основе конфигурации..
    """
    if config["LOG_FILE"]:
        structlog.configure(
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.UnicodeDecoder(),
                structlog.processors.JSONRenderer(),
            ],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )
        import logging

        logging.basicConfig(filename=config["LOG_FILE"], level=logging.DEBUG)
    else:
        structlog.configure(
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.UnicodeDecoder(),
                structlog.processors.JSONRenderer(),
            ],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )
        import logging

        logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


def main():
    parser = argparse.ArgumentParser(description="Log Analyzer")
    parser.add_argument("--config", default=None, help="Path to config file")
    args = parser.parse_args()

    try:
        config = load_config(args.config)
        setup_logging(config)
        logger = structlog.get_logger()

        logger.info("Starting log analyzer", config=config)

        log_file = find_latest_log(config["LOG_DIR"])
        if not log_file:
            logger.info("No log files found")
            return

        report_path = (
            Path(config["REPORT_DIR"]) / f"report-{log_file.date.strftime('%Y.%m.%d')}.html")
        if report_path.exists():
            logger.info("Report already exists, skipping",
                        report_path=str(report_path))
            return

        parsed_lines = list(parse_log(log_file.path, log_file.extension))
        total_lines = len(parsed_lines)
        parsed_count = sum(1 for line in parsed_lines if line is not None)
        error_rate = 1 - (parsed_count / total_lines) if total_lines > 0 else 0

        if error_rate > config["PARSING_ERROR_THRESHOLD"]:
            logger.error(
                "Parsing error rate exceeded threshold",
                error_rate=error_rate,
                threshold=config["PARSING_ERROR_THRESHOLD"],
            )
            return

        stats = analyze_logs(parsed_lines)
        generate_report(
            stats, config["REPORT_SIZE"], config["TEMPLATE_FILE"], report_path
        )

        logger.info("Log analysis completed", report_path=str(report_path))

    except Exception as e:
        logger = structlog.get_logger()
        logger.error("Unexpected error",
                     error=str(e), traceback=traceback.format_exc())
        raise


if __name__ == "__main__":
    main()
