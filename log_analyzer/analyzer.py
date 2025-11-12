import statistics
from collections import defaultdict


def analyze_logs(parsed_lines):
    """
    Анализирует строки логов для сбора статистики по запросам на URL.
    """
    url_stats = defaultdict(lambda: {"times": [], "count": 0})
    total_requests = 0
    total_time = 0.0

    for line in parsed_lines:
        if line:
            url = line["url"]
            time_val = line["request_time"]
            url_stats[url]["times"].append(time_val)
            url_stats[url]["count"] += 1
            total_requests += 1
            total_time += time_val

    stats = []
    for url, data in url_stats.items():
        times = data["times"]
        count = data["count"]
        time_sum = sum(times)
        time_avg = time_sum / count
        time_max = max(times)
        time_med = statistics.median(times)
        count_perc = ((count / total_requests) * 100) \
            if total_requests > 0 else 0
        time_perc = (time_sum / total_time) * 100 if total_time > 0 else 0
        stats.append(
            {
                "url": url,
                "count": count,
                "count_perc": round(count_perc, 2),
                "time_sum": round(time_sum, 3),
                "time_perc": round(time_perc, 2),
                "time_avg": round(time_avg, 3),
                "time_max": round(time_max, 3),
                "time_med": round(time_med, 3),
            }
        )

    stats.sort(key=lambda x: x["time_sum"], reverse=True)
    return stats
