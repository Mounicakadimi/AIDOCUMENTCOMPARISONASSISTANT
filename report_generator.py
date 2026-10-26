
from datetime import datetime


def build_report(file_a, file_b, result):
    report = [
        "AI DOCUMENT COMPARISON REPORT",
        "=" * 32,
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        f"DOCUMENT A: {file_a}",
        f"Word count: {result['words_a']}",
        "",
        f"DOCUMENT B: {file_b}",
        f"Word count: {result['words_b']}",
        "",
        f"Text similarity: {result['similarity']}%",
        f"Shared vocabulary: {result['overlap']}%",
        "",
        "DOCUMENT A SUMMARY",
        "-" * 24,
        result["summary_a"],
        "",
        "DOCUMENT B SUMMARY",
        "-" * 24,
        result["summary_b"],
        "",
        "COMPARISON",
        "-" * 24,
        result["comparison"],
        "",
        "WORDS SHARED BY BOTH",
        ", ".join(result["common_words"]),
        "",
        "WORDS ONLY IN DOCUMENT A",
        ", ".join(result["unique_a"]),
        "",
        "WORDS ONLY IN DOCUMENT B",
        ", ".join(result["unique_b"]),
        "",
        "LINE-BY-LINE DIFFERENCES",
        result["differences"]
    ]

    return "\n".join(report)
