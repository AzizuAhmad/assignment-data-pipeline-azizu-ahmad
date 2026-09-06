import os
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_PATH = os.path.join(BASE_DIR, "documentation", "data-flow-diagram.png")

steps = [
    ("Raw Dataset", "data/raw/automobileEDA_dirty_training.csv", "#d9d9d9"),
    ("Load Data", "load_data() - baca CSV dengan pandas", "#c6e0f5"),
    ("Data Inspection", "show_data() - cek shape, dtype, missing, duplikat, nilai unik", "#c6e0f5"),
    ("Data Cleaning", "cleaning_data() - missing value, duplikat, standarisasi kategori, tipe data", "#c6e0f5"),
    ("Data Transformation", "transform() - min-max scaling + encoding kategorikal", "#c6e0f5"),
    ("Processed Dataset", "data/processed/automobileEDA_processed.csv", "#cfe8cf"),
]

# fase ETL: (nama, index step awal, index step akhir)
phases = [
    ("EXTRACT", 1, 1),
    ("TRANSFORM", 2, 4),
    ("LOAD", 5, 5),
]

fig, ax = plt.subplots(figsize=(10, 11))
ax.set_xlim(0, 10)
ax.set_ylim(0, 12)
ax.axis("off")

box_w, box_h = 6.0, 1.1
x_center = 5.4
y_top = 11.0
gap = 1.9

centers = []
for i, (label, desc, color) in enumerate(steps):
    y = y_top - i * gap
    centers.append(y)
    ax.add_patch(FancyBboxPatch(
        (x_center - box_w / 2, y - box_h / 2), box_w, box_h,
        boxstyle="round,pad=0.02,rounding_size=0.12",
        linewidth=1.2, edgecolor="#333333", facecolor=color,
    ))
    ax.text(x_center, y + 0.16, label, ha="center", va="center",
            fontsize=13, fontweight="bold")
    ax.text(x_center, y - 0.27, desc, ha="center", va="center", fontsize=8.5)

# panah antar step
for i in range(len(steps) - 1):
    ax.add_patch(FancyArrowPatch(
        (x_center, centers[i] - box_h / 2),
        (x_center, centers[i + 1] + box_h / 2),
        arrowstyle="-|>", mutation_scale=20, linewidth=1.4, color="#333333",
    ))

# bracket fase ETL di sisi kiri
x_bracket = x_center - box_w / 2 - 0.5
for name, i0, i1 in phases:
    y0 = centers[i1] - box_h / 2 - 0.15
    y1 = centers[i0] + box_h / 2 + 0.15
    ax.plot([x_bracket, x_bracket], [y0, y1], color="#888888", linewidth=1.5)
    ax.plot([x_bracket, x_bracket + 0.18], [y0, y0], color="#888888", linewidth=1.5)
    ax.plot([x_bracket, x_bracket + 0.18], [y1, y1], color="#888888", linewidth=1.5)
    ax.text(x_bracket - 0.2, (y0 + y1) / 2, name, ha="center", va="center",
            rotation=90, fontsize=10, fontweight="bold", color="#555555")

ax.text(x_center, 11.8, "Data Flow - Pipeline Pengolahan Dataset Automobile",
        ha="center", va="center", fontsize=14, fontweight="bold")

plt.tight_layout()
plt.savefig(OUT_PATH, dpi=150, bbox_inches="tight")
print(f"Diagram disimpan: {OUT_PATH}")
