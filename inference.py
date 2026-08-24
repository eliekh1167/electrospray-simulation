import numpy as np

from rpa import (
    simulate_rpa,
    normalize_curve,
)


def fit_rpa_curve(
    experimental_voltage,
    experimental_current,
    operating_voltage,
    candidates=50,
    particle_count=2000,
    seed=42,
):
    """
    Search over candidate initial beam compositions and
    compare simulated RPA curves with an experimental RPA curve.

    This is parameter fitting, not machine learning.

    The fitting metric is normalized L2 error.
    """

    rng = np.random.default_rng(
        seed
    )

    experimental_voltage = np.asarray(
        experimental_voltage,
        dtype=float,
    )

    experimental_current = np.asarray(
        experimental_current,
        dtype=float,
    )

    # --------------------------------------------------------
    # Clean and normalize experimental curve
    # --------------------------------------------------------

    valid = (
        np.isfinite(
            experimental_voltage
        )
        &
        np.isfinite(
            experimental_current
        )
    )

    experimental_voltage = (
        experimental_voltage[valid]
    )

    experimental_current = (
        experimental_current[valid]
    )

    if len(experimental_voltage) < 3:
        raise ValueError(
            "Experimental RPA curve needs at least 3 valid points."
        )

    order = np.argsort(
        experimental_voltage
    )

    experimental_voltage = (
        experimental_voltage[order]
    )

    experimental_current = (
        experimental_current[order]
    )

    experimental_current -= (
        experimental_current.min()
    )

    max_current = (
        experimental_current.max()
    )

    if max_current > 0:
        experimental_current /= max_current

    results = []

    # --------------------------------------------------------
    # Candidate beam compositions
    # --------------------------------------------------------

    for _ in range(candidates):

        composition = (
            rng.dirichlet(
                [
                    4.0,
                    3.0,
                    2.0,
                ]
            )
        )

        simulated_voltage, species = (
            simulate_rpa(
                operating_voltage=operating_voltage,
                fractions=composition,
                particle_count=particle_count,
                seed=int(
                    rng.integers(
                        0,
                        2**32 - 1,
                    )
                ),
            )
        )

        simulated_curve, edges = (
            normalize_curve(
                simulated_voltage,
                operating_voltage,
                bins=150,
            )
        )

        simulated_centers = (
            edges[:-1]
            +
            edges[1:]
        ) / 2

        # Interpolate simulation onto experimental voltage grid.
        simulated_current = np.interp(
            experimental_voltage,
            simulated_centers,
            simulated_curve,
            left=0.0,
            right=0.0,
        )

        error = np.mean(
            (
                experimental_current
                -
                simulated_current
            )
            ** 2
        )

        results.append(
            {
                "error": float(error),

                "monomer_fraction": float(
                    composition[0]
                ),

                "dimer_fraction": float(
                    composition[1]
                ),

                "trimer_fraction": float(
                    composition[2]
                ),
            }
        )

    results.sort(
        key=lambda x: x["error"]
    )

    return __import__("pandas").DataFrame(
        results
    )
