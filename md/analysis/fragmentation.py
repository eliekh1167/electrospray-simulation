"""
FALAK Electrospray
Fragmentation trajectory analysis

Purpose
-------
Analyze molecular-dynamics trajectory data and identify
fragmentation events.

This module does NOT invent fragmentation rates.

It calculates them from supplied trajectory data.

Expected input
--------------
A CSV file containing at minimum:

time_ps
cluster_distance_A

where cluster_distance_A is the distance between the
relevant fragment centers of mass.

The initial FALAK threshold follows the fragmentation
criterion used in the thesis:

approximately 30 Angstrom separation.

IMPORTANT
---------
This script is an analysis tool. It does not replace
the molecular-dynamics simulation.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd


FRAGMENTATION_DISTANCE_A = 30.0


def load_trajectory(path: str | Path) -> pd.DataFrame:
    """Load trajectory analysis data."""

    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(f"Trajectory file not found: {path}")

    df = pd.read_csv(path)

    required = {"time_ps", "cluster_distance_A"}

    missing = required - set(df.columns)

    if missing:
        raise ValueError(
            f"Missing required columns: {sorted(missing)}"
        )

    df = df.sort_values("time_ps").reset_index(drop=True)

    return df


def find_fragmentation_time(
    df: pd.DataFrame,
    threshold_A: float = FRAGMENTATION_DISTANCE_A,
) -> float | None:
    """
    Find the first time at which the cluster separation
    reaches the fragmentation threshold.
    """

    events = df[df["cluster_distance_A"] >= threshold_A]

    if events.empty:
        return None

    return float(events.iloc[0]["time_ps"])


def analyze_single_trajectory(
    path: str | Path,
    threshold_A: float = FRAGMENTATION_DISTANCE_A,
) -> dict:
    """Analyze one trajectory."""

    df = load_trajectory(path)

    fragmentation_time = find_fragmentation_time(
        df,
        threshold_A=threshold_A,
    )

    return {
        "file": str(path),
        "fragmented": fragmentation_time is not None,
        "fragmentation_time_ps": fragmentation_time,
    }


def estimate_first_order_rate(
    fragmentation_times_ps: list[float],
) -> float:
    """
    Estimate a first-order fragmentation rate from
    observed fragmentation times.

    For an exponential survival process:

        k = 1 / mean(t)

    This should only be used when the trajectories
    correspond to the same physical conditions.
    """

    if not fragmentation_times_ps:
        raise ValueError(
            "No fragmentation events were supplied."
        )

    times = np.asarray(fragmentation_times_ps, dtype=float)

    if np.any(times <= 0):
        raise ValueError(
            "Fragmentation times must be positive."
        )

    return float(1.0 / np.mean(times))


def analyze_directory(
    directory: str | Path,
    threshold_A: float = FRAGMENTATION_DISTANCE_A,
) -> pd.DataFrame:
    """
    Analyze all CSV trajectory-analysis files in a directory.
    """

    directory = Path(directory)

    if not directory.exists():
        raise FileNotFoundError(
            f"Directory not found: {directory}"
        )

    results = []

    for csv_file in sorted(directory.glob("*.csv")):
        try:
            result = analyze_single_trajectory(
                csv_file,
                threshold_A=threshold_A,
            )
            results.append(result)
        except Exception as exc:
            print(
                f"Skipping {csv_file.name}: {exc}"
            )

    return pd.DataFrame(results)


def main():
    parser = argparse.ArgumentParser(
        description="Analyze FALAK MD fragmentation trajectories."
    )

    parser.add_argument(
        "input",
        help="Trajectory CSV file or directory containing CSV files.",
    )

    parser.add_argument(
        "--threshold",
        type=float,
        default=FRAGMENTATION_DISTANCE_A,
        help="Fragmentation separation threshold in Angstrom.",
    )

    args = parser.parse_args()

    input_path = Path(args.input)

    if input_path.is_file():

        result = analyze_single_trajectory(
            input_path,
            threshold_A=args.threshold,
        )

        print("\nFALAK fragmentation analysis")
        print("----------------------------")
        print(f"Trajectory: {result['file']}")
        print(f"Fragmented: {result['fragmented']}")
        print(
            f"Fragmentation time: "
            f"{result['fragmentation_time_ps']} ps"
        )

    elif input_path.is_dir():

        results = analyze_directory(
            input_path,
            threshold_A=args.threshold,
        )

        print("\nFALAK fragmentation analysis")
        print("----------------------------")
        print(results.to_string(index=False))

    else:

        raise FileNotFoundError(
            f"Input not found: {input_path}"
        )


if __name__ == "__main__":
    main()
