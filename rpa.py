import numpy as np

from physics import (
    M_MONOMER,
    M_DIMER,
    M_TRIMER,
    stopping_potential_dimer,
    stopping_potential_trimer_once,
    stopping_potential_trimer_twice,
)


def simulate_rpa(
    operating_voltage,
    fractions,
    particle_count=10000,
    seed=42,
):
    """
    Monte-Carlo RPA model.

    IMPORTANT:

    This function does NOT invent an electric-field trajectory
    or molecular-dynamics fragmentation lifetime.

    Instead, it represents the emission beam as a population of
    monomers, dimers and trimers and applies the published
    stopping-potential relationships to generate an RPA
    distribution.

    fractions:
        [monomer_fraction,
         dimer_fraction,
         trimer_fraction]
    """

    rng = np.random.default_rng(seed)

    fractions = np.asarray(
        fractions,
        dtype=float,
    )

    if fractions.sum() <= 0:
        raise ValueError(
            "Beam fractions must sum to a positive value."
        )

    fractions /= fractions.sum()

    emitted_species = rng.choice(
        [
            "monomer",
            "dimer",
            "trimer",
        ],
        size=particle_count,
        p=fractions,
    )

    stopping_potentials = np.zeros(
        particle_count
    )

    final_species = np.empty(
        particle_count,
        dtype=object,
    )

    # --------------------------------------------------------
    # Monomers
    # --------------------------------------------------------

    monomer_mask = (
        emitted_species
        ==
        "monomer"
    )

    stopping_potentials[
        monomer_mask
    ] = operating_voltage

    final_species[
        monomer_mask
    ] = "monomer"

    # --------------------------------------------------------
    # Dimers
    # --------------------------------------------------------

    dimer_mask = (
        emitted_species
        ==
        "dimer"
    )

    dimer_count = np.sum(
        dimer_mask
    )

    if dimer_count > 0:

        # The stopping potential for a dimer that fragments
        # at an unknown location is not uniquely determined
        # without the fragmentation-position / lifetime model.
        #
        # Therefore this implementation samples a fragmentation
        # potential explicitly as a model parameter.
        #
        # It is NOT presented as an MD-derived distribution.
        fragmentation_potential = rng.uniform(
            0.0,
            operating_voltage,
            dimer_count,
        )

        stopping_potentials[
            dimer_mask
        ] = stopping_potential_dimer(
            fragmentation_potential,
            operating_voltage,
        )

        final_species[
            dimer_mask
        ] = "monomer"

    # --------------------------------------------------------
    # Trimers
    # --------------------------------------------------------

    trimer_mask = (
        emitted_species
        ==
        "trimer"
    )

    trimer_count = np.sum(
        trimer_mask
    )

    if trimer_count > 0:

        first_fragmentation = rng.uniform(
            0.0,
            operating_voltage,
            trimer_count,
        )

        second_fragmentation = rng.uniform(
            0.0,
            operating_voltage,
            trimer_count,
        )

        # Ensure the second fragmentation occurs after
        # the first in potential-space.
        low = np.minimum(
            first_fragmentation,
            second_fragmentation,
        )

        high = np.maximum(
            first_fragmentation,
            second_fragmentation,
        )

        first_fragmentation = low
        second_fragmentation = high

        stopping_potentials[
            trimer_mask
        ] = stopping_potential_trimer_twice(
            first_fragmentation,
            second_fragmentation,
            operating_voltage,
        )

        final_species[
            trimer_mask
        ] = "monomer"

    return (
        stopping_potentials,
        final_species,
    )


def normalize_curve(
    stopping_potentials,
    operating_voltage,
    bins=150,
):
    """
    Convert stopping-potential samples into a normalized
    RPA-like distribution.
    """

    histogram, edges = np.histogram(
        stopping_potentials,
        bins=bins,
        range=(
            0,
            operating_voltage,
        ),
    )

    histogram = histogram.astype(float)

    if histogram.max() > 0:
        histogram /= histogram.max()

    return (
        histogram,
        edges,
    )
