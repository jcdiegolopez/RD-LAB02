#!/usr/bin/env python3
"""Genera las gráficas del reporte a partir de pruebas/resultados/raw_results.csv.

Uso:
    python3 pruebas/generar_graficas.py
"""
from __future__ import annotations

import csv
import statistics
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

RESULTS_DIR = Path(__file__).resolve().parent / "resultados"
CSV_PATH = RESULTS_DIR / "raw_results.csv"
GRAPHS_DIR = RESULTS_DIR / "graficas"

COLORS = {"HAMMING": "#2563eb", "CRC32": "#f97316"}
ALGOS = ["HAMMING", "CRC32"]


def load_rows() -> list[dict]:
    with CSV_PATH.open(newline="") as fh:
        reader = csv.DictReader(fh)
        rows = list(reader)
    for row in rows:
        row["probability"] = float(row["probability"])
        row["size_chars"] = int(row["size_chars"])
        row["size_bits"] = int(row["size_bits"])
        row["flipped_bits"] = int(row["flipped_bits"])
        row["overhead_bits"] = int(row["overhead_bits"])
        row["overhead_pct"] = float(row["overhead_pct"])
        row["message_correct"] = int(row["message_correct"])
        row["silent_corruption"] = int(row["silent_corruption"])
    return rows


def rate(rows: list[dict], key: str) -> float:
    if not rows:
        return 0.0
    return statistics.fmean(r[key] for r in rows)


def status_rate(rows: list[dict], status: str) -> float:
    if not rows:
        return 0.0
    return sum(1 for r in rows if r["status"] == status) / len(rows)


def plot_success_vs_probability(rows: list[dict]) -> None:
    data = [r for r in rows if r["experiment"] == "B_vs_probabilidad"]
    probs = sorted({r["probability"] for r in data})

    fig, ax = plt.subplots(figsize=(8, 5))
    for algo in ALGOS:
        ys = []
        for p in probs:
            subset = [r for r in data if r["algorithm"] == algo and r["probability"] == p]
            ys.append(rate(subset, "message_correct") * 100)
        ax.plot(probs, ys, marker="o", label=algo, color=COLORS[algo])

    ax.set_xlabel("Probabilidad de error por bit")
    ax.set_ylabel("Mensajes recibidos correctamente (%)")
    ax.set_title(f"Tasa de éxito vs. probabilidad de error\n(mensaje fijo de 32 caracteres, 200 pruebas por punto)")
    ax.set_xscale("symlog", linthresh=0.001)
    ax.set_ylim(-5, 105)
    ax.grid(alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(GRAPHS_DIR / "01_exito_vs_probabilidad.png", dpi=150)
    plt.close(fig)


def plot_silent_corruption_vs_probability(rows: list[dict]) -> None:
    data = [r for r in rows if r["experiment"] == "B_vs_probabilidad"]
    probs = sorted({r["probability"] for r in data})

    fig, ax = plt.subplots(figsize=(8, 5))
    for algo in ALGOS:
        ys = []
        for p in probs:
            subset = [r for r in data if r["algorithm"] == algo and r["probability"] == p]
            ys.append(rate(subset, "silent_corruption") * 100)
        ax.plot(probs, ys, marker="o", label=algo, color=COLORS[algo])

    ax.set_xlabel("Probabilidad de error por bit")
    ax.set_ylabel("Corrupción silenciosa (%)")
    ax.set_title(
        "Corrupción silenciosa vs. probabilidad de error\n"
        "(mensaje reportado como OK/CORRECTED pero incorrecto)"
    )
    ax.set_xscale("symlog", linthresh=0.001)
    ax.grid(alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(GRAPHS_DIR / "02_corrupcion_silenciosa_vs_probabilidad.png", dpi=150)
    plt.close(fig)


def plot_overhead_vs_size(rows: list[dict]) -> None:
    data = [r for r in rows if r["experiment"] == "A_overhead"]
    sizes = sorted({r["size_bits"] for r in data})

    fig, ax = plt.subplots(figsize=(8, 5))
    for algo in ALGOS:
        ys = []
        for s in sizes:
            subset = [r for r in data if r["algorithm"] == algo and r["size_bits"] == s]
            ys.append(statistics.fmean(r["overhead_pct"] for r in subset))
        ax.plot(sizes, ys, marker="o", label=algo, color=COLORS[algo])

    ax.set_xlabel("Tamaño del mensaje original (bits)")
    ax.set_ylabel("Overhead (%) respecto al mensaje original")
    ax.set_title("Overhead de redundancia vs. tamaño del mensaje")
    ax.set_xscale("log", base=2)
    ax.grid(alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(GRAPHS_DIR / "03_overhead_vs_tamano.png", dpi=150)
    plt.close(fig)


def plot_success_vs_size(rows: list[dict]) -> None:
    data = [r for r in rows if r["experiment"] == "C_vs_tamano"]
    sizes = sorted({r["size_bits"] for r in data})

    fig, ax = plt.subplots(figsize=(8, 5))
    for algo in ALGOS:
        ys = []
        for s in sizes:
            subset = [r for r in data if r["algorithm"] == algo and r["size_bits"] == s]
            ys.append(rate(subset, "message_correct") * 100)
        ax.plot(sizes, ys, marker="o", label=algo, color=COLORS[algo])

    ax.set_xlabel("Tamaño del mensaje original (bits)")
    ax.set_ylabel("Mensajes recibidos correctamente (%)")
    ax.set_title("Tasa de éxito vs. tamaño del mensaje\n(probabilidad de error fija = 0.01, 150 pruebas por punto)")
    ax.set_xscale("log", base=2)
    ax.set_ylim(-5, 105)
    ax.grid(alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(GRAPHS_DIR / "04_exito_vs_tamano.png", dpi=150)
    plt.close(fig)


def plot_status_breakdown(rows: list[dict]) -> None:
    data = [r for r in rows if r["experiment"] == "B_vs_probabilidad"]
    probs = sorted({r["probability"] for r in data})
    statuses = ["OK", "CORRECTED", "ERROR_DETECTED"]
    status_colors = {"OK": "#16a34a", "CORRECTED": "#2563eb", "ERROR_DETECTED": "#dc2626"}

    fig, axes = plt.subplots(1, 2, figsize=(13, 5), sharey=True)
    for ax, algo in zip(axes, ALGOS):
        bottoms = [0.0] * len(probs)
        for status in statuses:
            ys = []
            for p in probs:
                subset = [r for r in data if r["algorithm"] == algo and r["probability"] == p]
                ys.append(status_rate(subset, status) * 100)
            ax.bar([str(p) for p in probs], ys, bottom=bottoms, label=status, color=status_colors[status])
            bottoms = [b + y for b, y in zip(bottoms, ys)]
        ax.set_title(algo)
        ax.set_xlabel("Probabilidad de error por bit")
        ax.tick_params(axis="x", rotation=45)
    axes[0].set_ylabel("Proporción de pruebas (%)")
    axes[0].legend(loc="lower left")
    fig.suptitle("Composición de resultados por estado reportado (OK / CORRECTED / ERROR_DETECTED)")
    fig.tight_layout()
    fig.savefig(GRAPHS_DIR / "05_desglose_estados.png", dpi=150)
    plt.close(fig)


def main() -> None:
    GRAPHS_DIR.mkdir(parents=True, exist_ok=True)
    rows = load_rows()
    plot_success_vs_probability(rows)
    plot_silent_corruption_vs_probability(rows)
    plot_overhead_vs_size(rows)
    plot_success_vs_size(rows)
    plot_status_breakdown(rows)
    print(f"Gráficas generadas en {GRAPHS_DIR}")


if __name__ == "__main__":
    main()
