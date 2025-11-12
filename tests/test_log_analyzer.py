import json
import gzip
import tempfile
from pathlib import Path
from log_analyzer.analyzer import analyze_logs
from log_analyzer.parser import find_latest_log, parse_log
from log_analyzer.reporter import generate_report
from log_analyzer.config import DEFAULT_CONFIG
from log_analyzer.main import load_config


def test_load_config_default():
    config = load_config(None)
    assert config == DEFAULT_CONFIG


def test_load_config_override():
    config_content = 'LOG_DIR = "/new/path"\nREPORT_SIZE = 50\n'
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(config_content)
        config_path = f.name

    try:
        config = load_config(config_path)
        assert config["LOG_DIR"] == "/new/path"
        assert config["REPORT_SIZE"] == 50
        assert config["REPORT_DIR"] == DEFAULT_CONFIG["REPORT_DIR"]  # Not overridden
    finally:
        Path(config_path).unlink()


def test_find_latest_log():
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create test files
        Path(tmpdir, "nginx-access-ui.log-20210101.log").touch()
        Path(tmpdir, "nginx-access-ui.log-20210102.gz").touch()
        Path(tmpdir, "nginx-access-ui.log-20210103.log").touch()
        Path(tmpdir, "other.log").touch()

        log_file = find_latest_log(tmpdir)
        assert log_file.date.strftime("%Y%m%d") == "20210103"
        assert log_file.extension == "log"


def test_parse_log_plain():
    log_content = '127.0.0.1 - - [01/Jan/2021:00:00:00 +0000] "GET /test HTTP/1.1" 200 123 "-" "Mozilla/5.0" 0.123\n'
    with tempfile.NamedTemporaryFile(mode="w", suffix=".log", delete=False) as f:
        f.write(log_content)
        log_path = f.name

    try:
        parsed = list(parse_log(log_path, "log"))
        assert len(parsed) == 1
        assert parsed[0]["url"] == "/test"
        assert parsed[0]["request_time"] == 0.123
    finally:
        Path(log_path).unlink()


def test_parse_log_gz():
    log_content = '127.0.0.1 - - [01/Jan/2021:00:00:00 +0000] "GET /test HTTP/1.1" 200 123 "-" "Mozilla/5.0" 0.123\n'
    with tempfile.NamedTemporaryFile(suffix=".gz", delete=False) as f:
        with gzip.open(f, "wt") as gz_f:
            gz_f.write(log_content)
        log_path = f.name

    try:
        parsed = list(parse_log(log_path, "gz"))
        assert len(parsed) == 1
        assert parsed[0]["url"] == "/test"
        assert parsed[0]["request_time"] == 0.123
    finally:
        Path(log_path).unlink()


def test_analyze_logs():
    parsed_lines = [
        {"url": "/a", "request_time": 1.0},
        {"url": "/a", "request_time": 2.0},
        {"url": "/b", "request_time": 3.0},
        None,  # Invalid line
    ]
    stats = analyze_logs(parsed_lines)
    assert len(stats) == 2
    a_stat = next(s for s in stats if s["url"] == "/a")
    assert a_stat["count"] == 2
    assert a_stat["time_sum"] == 3.0
    assert a_stat["time_avg"] == 1.5
    assert a_stat["time_max"] == 2.0
    assert a_stat["time_med"] == 1.5


def test_generate_report():
    stats = [
        {
            "url": "/test",
            "count": 1,
            "count_perc": 100.0,
            "time_sum": 1.0,
            "time_perc": 100.0,
            "time_avg": 1.0,
            "time_max": 1.0,
            "time_med": 1.0,
        }
    ]
    template_content = "<html>$table_json</html>"
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".html", delete=False
    ) as template_f:
        template_f.write(template_content)
        template_path = template_f.name

    with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as report_f:
        report_path = report_f.name

    try:
        generate_report(stats, 10, template_path, Path(report_path))
        with open(report_path, "r") as f:
            content = f.read()
        assert json.loads(content.replace("<html>", "").replace("</html>", "")) == stats
    finally:
        Path(template_path).unlink()
        Path(report_path).unlink()
