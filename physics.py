import numpy as np


# ============================================================
# Fundamental constants
# ============================================================

EPS0 = 8.8541878128e-12

# Taylor-cone half angle used in the original FALAK model.
THETA = np.radians(49.3)


# ============================================================
# Propellant properties
# ============================================================

PROPPELLANTS = {

    "EMI-BF4": {
        "surface_tension": 0.0452,
        "conductivity": 1.40,
    },

    "EMI-GaCl4": {
        "surface_tension": 0.0486,
        "conductivity": 2.20,
    },

    "EMI-Tf2N": {
        "surface_tension": 0.0349,
        "conductivity": 0.88,
    },

    "EMI-BETI": {
        "surface_tension": 0.02875,
        "conductivity": 0.34,
    },
}


# ============================================================
# Taylor-cone onset
# ============================================================

def onset_voltage(
    surface_tension,
    tip_radius,
    electrode_gap,
):
    """
    Taylor-cone onset voltage relation used by the
    original FALAK model.

    Parameters
    ----------
    surface_tension : float
        N/m

    tip_radius : float
        m

    electrode_gap : float
        m

    Returns
    -------
    float
        Voltage in volts.
    """

    return (
        np.sqrt(
            (
                tip_radius
                * surface_tension
                * np.cos(THETA)
            )
            /
            (
                2 * EPS0
            )
        )
        *
        np.log(
            4
            * electrode_gap
            / tip_radius
        )
    )


# ============================================================
# Cluster masses
# ============================================================

# EMI+ mass
M_MONOMER = (
    111.16e-3
    /
    6.02214076e23
)

# EMI+ + one EMI-BF4
M_DIMER = (
    (111.16 + 197.97)
    * 1e-3
    /
    6.02214076e23
)

# EMI+ + two EMI-BF4
M_TRIMER = (
    (111.16 + 2 * 197.97)
    * 1e-3
    /
    6.02214076e23
)


# ============================================================
# Published stopping-potential relationships
# ============================================================

def stopping_potential_dimer(
    fragmentation_potential,
    initial_potential,
):
    """
    Dimer fragmentation relationship.

    u_s = u_d
        + (m_m / m_d)
        * (V0 - u_d)
    """

    return (
        fragmentation_potential
        +
        (
            M_MONOMER
            /
            M_DIMER
        )
        *
        (
            initial_potential
            -
            fragmentation_potential
        )
    )


def stopping_potential_trimer_once(
    fragmentation_potential,
    initial_potential,
):
    """
    First trimer fragmentation:

    trimer -> dimer + neutral
    """

    return (
        fragmentation_potential
        +
        (
            M_DIMER
            /
            M_TRIMER
        )
        *
        (
            initial_potential
            -
            fragmentation_potential
        )
    )


def stopping_potential_trimer_twice(
    first_fragmentation_potential,
    second_fragmentation_potential,
    initial_potential,
):
    """
    Sequential trimer fragmentation relationship.

    trimer
       ↓
    dimer
       ↓
    monomer
    """

    return (
        second_fragmentation_potential
        +
        (
            M_MONOMER
            /
            M_DIMER
        )
        *
        (
            first_fragmentation_potential
            -
            second_fragmentation_potential
        )
        +
        (
            M_MONOMER
            /
            M_TRIMER
        )
        *
        (
            initial_potential
            -
            first_fragmentation_potential
        )
    )
