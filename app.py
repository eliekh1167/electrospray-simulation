import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from physics import (
    EPS0,
    PROPPELLANTS,
    onset_voltage,
    stopping_potential_dimer,
    stopping_potential_trimer_once,
    stopping_potential_trimer_twice,
)

from rpa import simulate_rpa, normalize_curve
from inference import fit_rpa_curve


st.set_page_config(
    page_title="FALAK Electrospray Model",
    page_icon="🚀",
    layout="wide",
)

st.title("FALAK Electrospray Emission & RPA Model")

st.markdown(
    """
    **Taylor-cone onset → cluster emission → fragmentation → stopping potential → RPA**

    This is a reduced-order electrospray model based on the published
    electrospray/RPA methodology. It does **not** perform molecular dynamics.
    """
)

st.divider()


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.header("Emitter")

propellant_name = st.sidebar.selectbox(
    "Propellant",
    list(PROPPELLANTS.keys())
)

tip_radius_um = st.sidebar.slider(
    "Emitter tip radius (µm)",
    min_value=2.0,
    max_value=30.0,
    value=10.0,
    step=0.5,
)

gap_mm = st.sidebar.slider(
    "Electrode gap (mm)",
    min_value=0.5,
    max_value=5.0,
    value=2.0,
    step=0.1,
)

tip_radius = tip_radius_um * 1e-6
gap = gap_mm * 1e-3

props = PROPPELLANTS[propellant_name]

V_onset = onset_voltage(
    props["surface_tension"],
    tip_radius,
    gap,
)

st.sidebar.metric(
    "Predicted onset voltage",
    f"{V_onset / 1000:.3f} kV",
)


# ============================================================
# TABS
# ============================================================

tab_onset, tab_rpa, tab_inference, tab_about = st.tabs(
    [
        "Onset Model",
        "RPA Simulation",
        "RPA Inference",
        "Model Documentation",
    ]
)


# ============================================================
# ONSET MODEL
# ============================================================

with tab_onset:

    st.header("Taylor-cone onset")

    st.write(
        "The onset model estimates the voltage at which the applied "
        "electrostatic stress reaches the surface-tension scale used "
        "by the original FALAK model."
    )

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Surface tension",
        f"{props['surface_tension']:.5f} N/m",
    )

    col2.metric(
        "Tip radius",
        f"{tip_radius_um:.1f} µm",
    )

    col3.metric(
        "Electrode gap",
        f"{gap_mm:.2f} mm",
    )

    st.metric(
        "Predicted onset voltage",
        f"{V_onset / 1000:.3f} kV",
    )

    st.subheader("Propellant comparison")

    propellant_names = list(PROPPELLANTS.keys())

    onset_values = []

    for name in propellant_names:

        p = PROPPELLANTS[name]

        value = onset_voltage(
            p["surface_tension"],
            tip_radius,
            gap,
        )

        onset_values.append(value / 1000)

    fig, ax = plt.subplots(figsize=(9, 4))

    ax.bar(
        propellant_names,
        onset_values,
    )

    ax.set_ylabel("Onset voltage (kV)")
    ax.set_title("Predicted electrospray onset")

    ax.grid(
        axis="y",
        alpha=0.25,
    )

    st.pyplot(fig)

    st.subheader("Tip-radius sensitivity")

    radii = np.logspace(
        np.log10(2e-6),
        np.log10(30e-6),
        300,
    )

    fig, ax = plt.subplots(figsize=(9, 4))

    for name in propellant_names:

        p = PROPPELLANTS[name]

        values = [
            onset_voltage(
                p["surface_tension"],
                radius,
                gap,
            ) / 1000
            for radius in radii
        ]

        ax.plot(
            radii * 1e6,
            values,
            label=name,
        )

    ax.set_xlabel("Tip radius (µm)")
    ax.set_ylabel("Onset voltage (kV)")
    ax.set_title("Onset voltage vs emitter radius")

    ax.legend()
    ax.grid(alpha=0.25)

    st.pyplot(fig)


# ============================================================
# RPA
# ============================================================

with tab_rpa:

    st.header("Retarding Potential Analysis")

    st.warning(
        "The RPA model is only activated for EMI-BF4 because the "
        "cluster/fragmentation model implemented here is tied to "
        "the published EMI-BF4 study. Do not transfer these "
        "fragmentation parameters to other ionic liquids without data."
    )

    if propellant_name != "EMI-BF4":

        st.error(
            "Select EMI-BF4 to run the paper-linked cluster/RPA model."
        )

    else:

        operating_voltage_kv = st.slider(
            "Operating voltage (kV)",
            min_value=V_onset / 1000,
            max_value=5.0,
            value=max(1.5, V_onset / 1000),
            step=0.05,
        )

        operating_voltage = operating_voltage_kv * 1000

        st.subheader("Initial beam composition")

        c1, c2, c3 = st.columns(3)

        monomer = c1.slider(
            "Monomer (%)",
            0,
            100,
            45,
        )

        dimer = c2.slider(
            "Dimer (%)",
            0,
            100,
            35,
        )

        trimer = c3.slider(
            "Trimer (%)",
            0,
            100,
            20,
        )

        total = monomer + dimer + trimer

        if total == 0:

            st.error(
                "At least one species must have a non-zero fraction."
            )

        else:

            fractions = np.array(
                [
                    monomer,
                    dimer,
                    trimer,
                ],
                dtype=float,
            )

            fractions /= fractions.sum()

            st.write(
                f"Normalized beam composition: "
                f"{fractions[0]*100:.1f}% monomer, "
                f"{fractions[1]*100:.1f}% dimer, "
                f"{fractions[2]*100:.1f}% trimer."
            )

            st.subheader("RPA parameters")

            particle_count = st.slider(
                "Monte-Carlo particles",
                1000,
                50000,
                10000,
                1000,
            )

            bins = st.slider(
                "RPA bins",
                50,
                300,
                150,
                10,
            )

            seed = st.number_input(
                "Random seed",
                min_value=0,
                max_value=999999,
                value=42,
            )

            if st.button(
                "Run RPA simulation",
                type="primary",
            ):

                with st.spinner(
                    "Running RPA Monte-Carlo simulation..."
                ):

                    stopping_potentials, species = simulate_rpa(
                        operating_voltage=operating_voltage,
                        fractions=fractions,
                        particle_count=particle_count,
                        seed=int(seed),
                    )

                curve, edges = normalize_curve(
                    stopping_potentials,
                    operating_voltage,
                    bins,
                )

                centers = (
                    edges[:-1] +
                    edges[1:]
                ) / 2

                st.subheader(
                    "Simulated RPA curve"
                )

                fig, ax = plt.subplots(
                    figsize=(10, 5)
                )

                ax.plot(
                    centers / 1000,
                    curve,
                    linewidth=2,
                )

                ax.set_xlabel(
                    "Retarding potential (kV)"
                )

                ax.set_ylabel(
                    "Normalized current"
                )

                ax.set_title(
                    "Simulated Retarding Potential Analysis"
                )

                ax.grid(alpha=0.25)

                st.pyplot(fig)

                st.subheader(
                    "Detected species distribution"
                )

                species_counts = (
                    pd.Series(species)
                    .value_counts()
                    .reindex(
                        [
                            "monomer",
                            "dimer",
                            "trimer",
                        ],
                        fill_value=0,
                    )
                )

                species_percent = (
                    species_counts /
                    species_counts.sum()
                    * 100
                )

                result = pd.DataFrame(
                    {
                        "Species": species_percent.index,
                        "Fraction (%)": species_percent.values,
                    }
                )

                st.dataframe(
                    result,
                    use_container_width=True,
                )


# ============================================================
# INFERENCE
# ============================================================

with tab_inference:

    st.header(
        "Infer emission characteristics from experimental RPA"
    )

    st.write(
        """
        Upload an experimental RPA curve as CSV.

        Required columns:

        `stopping_potential_V`

        `normalized_current`
        """
    )

    uploaded_file = st.file_uploader(
        "Experimental RPA CSV",
        type=["csv"],
    )

    if uploaded_file is not None:

        data = pd.read_csv(
            uploaded_file
        )

        required_columns = {
            "stopping_potential_V",
            "normalized_current",
        }

        if not required_columns.issubset(
            data.columns
        ):

            st.error(
                "CSV must contain the columns: "
                "stopping_potential_V and normalized_current"
            )

        else:

            st.dataframe(
                data.head(),
                use_container_width=True,
            )

            if propellant_name != "EMI-BF4":

                st.warning(
                    "Inference is currently restricted to EMI-BF4."
                )

            else:

                particle_count = st.slider(
                    "Particles per candidate",
                    500,
                    10000,
                    2000,
                    500,
                )

                candidates = st.slider(
                    "Candidate models",
                    10,
                    500,
                    50,
                    10,
                )

                if st.button(
                    "Fit model to experimental RPA",
                    type="primary",
                ):

                    with st.spinner(
                        "Searching candidate emission distributions..."
                    ):

                        result = fit_rpa_curve(
                            experimental_voltage=data[
                                "stopping_potential_V"
                            ].to_numpy(),

                            experimental_current=data[
                                "normalized_current"
                            ].to_numpy(),

                            operating_voltage=operating_voltage
                            if "operating_voltage" in locals()
                            else 2000.0,

                            candidates=candidates,

                            particle_count=particle_count,
                        )

                    st.subheader(
                        "Best-fit emission characteristics"
                    )

                    best = result.iloc[0]

                    c1, c2, c3 = st.columns(3)

                    c1.metric(
                        "Monomer",
                        f"{best['monomer_fraction']*100:.1f}%",
                    )

                    c2.metric(
                        "Dimer",
                        f"{best['dimer_fraction']*100:.1f}%",
                    )

                    c3.metric(
                        "Trimer",
                        f"{best['trimer_fraction']*100:.1f}%",
                    )

                    st.metric(
                        "Fit error",
                        f"{best['error']:.5g}",
                    )

                    st.subheader(
                        "Candidate solutions"
                    )

                    st.dataframe(
                        result.head(20),
                        use_container_width=True,
                    )


# ============================================================
# DOCUMENTATION
# ============================================================

with tab_about:

    st.header("Scientific scope")

    st.markdown(
        """
### Implemented

**Taylor-cone onset**

The original FALAK onset equation is retained.

**Cluster species**

The RPA model represents emitted charged species as
monomers, dimers and trimers.

**Fragmentation**

The model uses the published stopping-potential relationships
for fragmented clusters.

**RPA**

The model converts simulated stopping potentials into an
RPA-like normalized current curve.

**Inference**

Experimental RPA data can be compared against candidate
beam-composition models.

### Not implemented

This project does **not** claim to perform molecular dynamics.

It also does not claim to solve the complete
electrohydrodynamic field around an emitter.

Those are separate research modules that would require:

- an actual molecular-dynamics engine,
- a validated ionic-liquid force field,
- experimentally/MD-derived fragmentation data,
- and a validated electrohydrodynamic field solution.

Therefore the scientifically accurate description is:

> **Reduced-order electrospray emission and RPA model
> informed by published molecular-dynamics results.**
        """
    )

    st.info(
        "For research use, every empirical parameter should be "
        "linked to its source in the repository documentation."
    )
