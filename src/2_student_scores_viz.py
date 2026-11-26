"""
Fetch student test scores, calculate statistical metrics, and render a performance bar chart.
"""

from __future__ import annotations

import logging
import statistics
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import requests

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("student_scores_viz")

FALLBACK_STUDENTS: List[Dict[str, Any]] = [
    {"name": "Alice Johnson", "score": 94.0},
    {"name": "Bob Martinez", "score": 78.5},
    {"name": "Charlie Lee", "score": 88.0},
    {"name": "Diana Patel", "score": 96.5},
    {"name": "Evan Davis", "score": 83.0},
    {"name": "Fiona Clark", "score": 71.5},
    {"name": "George Brown", "score": 89.0},
    {"name": "Hannah White", "score": 91.5},
    {"name": "Ian Wright", "score": 67.0},
    {"name": "Julia Chen", "score": 98.0},
]

MOCK_API_URL = "https://raw.githubusercontent.com/datasets/sample-student-scores/main/scores.json"


def get_default_output_path() -> Path:
    base_dir = Path(__file__).resolve().parent.parent
    out_dir = base_dir / "outputs"
    out_dir.mkdir(parents=True, exist_ok=True)
    return out_dir / "student_scores.png"


def fetch_student_scores(
    api_url: str = MOCK_API_URL, timeout_seconds: float = 3.0
) -> Tuple[List[Dict[str, Any]], str]:
    logger.info(f"Fetching student scores from: {api_url}")
    try:
        response = requests.get(
            api_url,
            timeout=timeout_seconds,
            headers={"User-Agent": "ScoreProcessor/1.0"},
        )
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list) and len(data) > 0 and "score" in data[0]:
                logger.info(f"Retrieved {len(data)} student scores.")
                return data, "external_api"
    except Exception as exc:
        logger.info(f"Endpoint unavailable ({exc}); using fallback score set.")

    return FALLBACK_STUDENTS, "fallback"


def compute_summary_metrics(scores: List[float]) -> Dict[str, float]:
    if not scores:
        raise ValueError("Cannot compute metrics on an empty list of scores.")

    avg_score = float(statistics.mean(scores))
    med_score = float(statistics.median(scores))
    min_score = float(min(scores))
    max_score = float(max(scores))
    std_dev = float(statistics.stdev(scores)) if len(scores) > 1 else 0.0

    return {
        "count": len(scores),
        "average": round(avg_score, 2),
        "median": round(med_score, 2),
        "min": round(min_score, 2),
        "max": round(max_score, 2),
        "std_dev": round(std_dev, 2),
    }


def print_summary_metrics(metrics: Dict[str, float], source_desc: str = "") -> None:
    print("\n" + "=" * 54)
    print(f" Student Scores Summary ({source_desc})")
    print("=" * 54)
    print(f"  Count        : {int(metrics['count'])}")
    print(f"  Average      : {metrics['average']:.2f}")
    print(f"  Median       : {metrics['median']:.2f}")
    print(f"  Min Score    : {metrics['min']:.2f}")
    print(f"  Max Score    : {metrics['max']:.2f}")
    print(f"  Std. Dev     : {metrics['std_dev']:.2f}")
    print("=" * 54 + "\n")


def generate_bar_chart(
    students: List[str],
    scores: List[float],
    output_path: Path | str,
    metrics: Dict[str, float] | None = None,
    dpi: int = 300,
) -> Path:
    out_file = Path(output_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)

    if metrics is None:
        metrics = compute_summary_metrics(scores)

    colors = []
    for s in scores:
        if s >= 90:
            colors.append("#2E7D32")
        elif s >= 80:
            colors.append("#1976D2")
        elif s >= 70:
            colors.append("#F57C00")
        else:
            colors.append("#D32F2F")

    fig, ax = plt.subplots(figsize=(11, 6.5), dpi=dpi)

    bars = ax.bar(
        students,
        scores,
        color=colors,
        edgecolor="#222222",
        linewidth=1.2,
        width=0.62,
        zorder=3,
    )

    for bar in bars:
        height = bar.get_height()
        ax.annotate(
            f"{height:.1f}",
            xy=(bar.get_x() + bar.get_width() / 2, height),
            xytext=(0, 5),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=10,
            fontweight="bold",
            color="#222222",
        )

    avg_val = metrics["average"]
    ax.axhline(
        y=avg_val,
        color="#C62828",
        linestyle="--",
        linewidth=2.0,
        zorder=4,
        label=f"Average ({avg_val:.2f})",
    )

    med_val = metrics["median"]
    ax.axhline(
        y=med_val,
        color="#6A1B9A",
        linestyle=":",
        linewidth=1.8,
        zorder=4,
        label=f"Median ({med_val:.2f})",
    )

    ax.set_title(
        "Student Test Scores & Performance Distribution",
        fontsize=14,
        fontweight="bold",
        pad=16,
        color="#1A237E",
    )
    ax.set_xlabel("Student Name", fontsize=11, fontweight="bold", labelpad=8)
    ax.set_ylabel("Test Score (Scale 0-100)", fontsize=11, fontweight="bold", labelpad=8)
    ax.set_ylim(0, 110)
    ax.set_yticks(range(0, 110, 10))
    ax.grid(axis="y", linestyle="--", alpha=0.45, zorder=0)
    ax.set_axisbelow(True)

    plt.xticks(rotation=25, ha="right", fontsize=10)
    plt.yticks(fontsize=10)
    ax.legend(loc="upper left", frameon=True, framealpha=0.9, facecolor="#F8F9FA", edgecolor="#CCCCCC")

    plt.tight_layout()
    plt.savefig(str(out_file), dpi=dpi, bbox_inches="tight")
    plt.close(fig)

    logger.info(f"Bar chart exported to: {out_file}")
    return out_file


def main() -> None:
    output_path = get_default_output_path()
    data, source = fetch_student_scores()
    students = [item["name"] for item in data]
    scores = [float(item["score"]) for item in data]

    metrics = compute_summary_metrics(scores)
    print_summary_metrics(metrics, source_desc=source)
    generate_bar_chart(students, scores, output_path, metrics=metrics)
    print(f"[OK] Chart saved at: {output_path}\n")


if __name__ == "__main__":
    main()
