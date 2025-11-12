import json
from string import Template


def generate_report(stats, report_size, template_file, report_path):
    """
      Генерирует отчет на основе собранной статистики.
      """
    top_stats = stats[:report_size]
    table_json = json.dumps(top_stats, ensure_ascii=False, indent=2)

    with open(template_file, "r", encoding="utf-8") as f:
        template = Template(f.read())

    report_content = template.safe_substitute(table_json=table_json)

    report_path.parent.mkdir(parents=True, exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_content)
