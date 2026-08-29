import numpy as np

from physics import PROPPELLANTS, onset_voltage


def calculate_operating_point(
    propellant_name,
    tip_radius_um,
    electrode_gap_mm,
):

    if propellant_name not in PROPPELLANTS:
        raise ValueError(
            f"Unknown propellant: {propellant_name}"
        )

    propellant = PROPPELLANTS[
        propellant_name
    ]

    tip_radius_m = (
        tip_radius_um * 1e-6
    )

    electrode_gap_m = (
        electrode_gap_mm * 1e-3
    )

    onset_v = onset_voltage(
        propellant["surface_tension"],
        tip_radius_m,
        electrode_gap_m,
    )

    return {
        "onset_voltage_V": onset_v,
        "onset_voltage_kV": onset_v / 1000.0,
        "tip_radius_um": tip_radius_um,
        "electrode_gap_mm": electrode_gap_mm,
    }


def create_field_map(
    applied_voltage,
    electrode_gap_mm,
    radial_extent_mm=3.0,
    radial_points=180,
    axial_points=180,
):

    gap_m = (
        electrode_gap_mm * 1e-3
    )

    radial_extent_m = (
        radial_extent_mm * 1e-3
    )

    x = np.linspace(
        -radial_extent_m,
        radial_extent_m,
        radial_points,
    )

    y = np.linspace(
        0.0,
        gap_m,
        axial_points,
    )

    X, Y = np.meshgrid(
        x,
        y,
    )

    uniform_field = (
        applied_voltage
        / gap_m
    )

    radial_factor = (
        1.0
        + 0.65
        * np.exp(
            -(
                X
                / (
                    0.45
                    * radial_extent_m
                )
            ) ** 2
        )
    )

    axial_factor = (
        0.75
        + 0.25
        * np.cos(
            np.pi
            * Y
            / gap_m
        )
    )

    E = (
        uniform_field
        * radial_factor
        * axial_factor
    )

    return X, Y, E