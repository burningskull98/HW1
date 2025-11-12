import os

DEFAULT_CONFIG = {
    "LOG_DIR": "D:\\Виктория\\Курс.Часть2\\ДЗ\\HW1\\logs",
    "REPORT_DIR": "./reports",
    "REPORT_SIZE": 1000,
    "LOG_FILE": None,
    "PARSING_ERROR_THRESHOLD": 0.1,
    "TEMPLATE_FILE": os.path.join(os.path.dirname(__file__), "report.html"),
}
