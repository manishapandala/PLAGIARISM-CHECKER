#!/usr/bin/env python3
"""Generate a synthetic battery-cell tabular dataset for smoke testing."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate synthetic battery cell data.")
    parser.add_argument(
        "--output",
        default="battery_anomaly_detection/data/synthetic_cells.csv",
        help="Path to write the generated CSV file.",
    )
    parser.add_argument("--rows", type=int, default=500, help="Number of synthetic cells.")
    parser.add_argument("--seed", type=int, default=42, help="Random seed.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rng = np.random.default_rng(args.seed)
    n = args.rows

    cell_id = np.arange(1, n + 1)
    box = np.where(cell_id <= 130, 1, np.where(cell_id <= 260, 2, np.where(cell_id <= 390, 3, 4)))

    overhang = rng.normal(0.62, 0.04, size=n)
    cathode_width = rng.normal(58.10, 0.11, size=n)
    anode_width = rng.normal(58.35, 0.10, size=n)
    core_offset = rng.normal(0.02, 0.02, size=n)
    crimp_depth = rng.normal(1.45, 0.06, size=n)
    coat_thickness = rng.normal(74.2, 1.3, size=n)
    porosity = rng.normal(33.1, 1.0, size=n)
    moisture_ppm = rng.normal(42.0, 5.0, size=n)
    resistance_mohm = rng.normal(16.0, 0.5, size=n)
    capacity_0p2c = rng.normal(4.94, 0.05, size=n)

    # Subtle lot shifts to mimic manufacturing build variation.
    box3 = box == 3
    late_lot = cell_id >= 391

    overhang[box3] -= 0.025
    cathode_width[box3] += 0.06
    core_offset[box3] += 0.01

    overhang[late_lot] += 0.015
    cathode_width[late_lot] -= 0.04
    crimp_depth[late_lot] += 0.03
    resistance_mohm[late_lot] += 0.2
    capacity_0p2c[late_lot] -= 0.03

    df = pd.DataFrame(
        {
            "cell_id": cell_id,
            "shipping_box": box,
            "overhang_mm": overhang,
            "cathode_width_mm": cathode_width,
            "anode_width_mm": anode_width,
            "core_offset_mm": core_offset,
            "crimp_depth_mm": crimp_depth,
            "coat_thickness_um": coat_thickness,
            "porosity_pct": porosity,
            "moisture_ppm": moisture_ppm,
            "resistance_mohm": resistance_mohm,
            "capacity_0p2c_ah": capacity_0p2c,
        }
    )

    for col in [
        "overhang_mm",
        "cathode_width_mm",
        "crimp_depth_mm",
        "moisture_ppm",
    ]:
        missing_idx = rng.choice(n, size=max(3, int(0.02 * n)), replace=False)
        df.loc[missing_idx, col] = np.nan

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"Wrote synthetic dataset to: {output_path.resolve()}")


if __name__ == "__main__":
    main()
