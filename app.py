import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from scipy.constants import epsilon_0, elementary_charge

st.set_page_config(
    page_title="Electrospray Model",
    layout="wide",
)

st.markdown(
    """
    <style>
    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    .falak-title {
        text-align: center;
        font-size: 42px;
        font-weight: 700;
        letter-spacing: 2px;
    }

    .falak-subtitle {
        text-align: center;
        color: #7fa8c9;
        font-size: 16px;
        margin-bottom: 30px;
    }

    .metric-card {
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #26324a;
        background: #0d1424;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="falak-title">FALAK Electrospray Model</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="falak-subtitle">'
    'Multiscale electrospray simulation and analysis'
    '</div>',
    unsafe_allow_html=True,
)

st.divider()

# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("Simulation Controls")

model = st.sidebar.selectbox(
    "Model",
    [
        "Taylor Cone Onset",
        "Molecular System",
        "Electric Field",
        "RPA Analysis",
    ],
)

st.sidebar.markdown("---")

st.sidebar.caption(
    "Current validated research target:"
)

st.sidebar.info(
    "EMIM-BF₄\n\n"
    "Initial force-field basis: OPLS-2009IL / "
    "0.8-scaled OPLS-2009IL."
)

# ============================================================
# PROPELLANT
# ============================================================

propellant = "EMIM-BF4"

gamma = 0.0452  # N/m
conductivity = 1.4  # S/m

# ============================================================
# TAYLOR-CONE MODEL
# ============================================================


def onset_voltage(gamma, r_c, d):
    """
    Reduced-order Taylor-cone onset relation used
    by the original FALAK prototype.

    This is an onset model only.

    It is NOT the molecular-dynamics model.
    """

    theta = np.radians(49.3)

    return (
        np.sqrt(
            (r_c * gamma * np.cos(theta))
            / (2 * epsilon_0)
        )
        * np.log(4 * d / r_c)
    )


if model == "Taylor Cone Onset":

    st.header("Taylor Cone Onset")

    col1, col2, col3 = st.columns(3)

    with col1:
        radius_um = st.slider(
            "Emitter tip radius (μm)",
            2.0,
            30.0,
            10.0,
        )

    with col2:
        gap_mm = st.slider(
            "Emitter–extractor gap (mm)",
            0.5,
            5.0,
            2.0,
        )

    with col3:
        st.metric(
            "Propellant",
            propellant,
        )

    radius_m = radius_um * 1e-6
    gap_m = gap_mm * 1e-3

    voltage = onset_voltage(
        gamma,
        radius_m,
        gap_m,
    )

    st.metric(
        "Predicted onset voltage",
        f"{voltage / 1000:.3f} kV",
    )

    radii = np.logspace(
        np.log10(2),
        np.log10(30),
        300,
    )

    voltages = [
        onset_voltage(
            gamma,
            r * 1e-6,
            gap_m,
        ) / 1000
        for r in radii
    ]

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=radii,
            y=voltages,
            mode="lines",
            name="EMIM-BF4",
        )
    )

    fig.update_layout(
        title="Onset Voltage vs Emitter Tip Radius",
        xaxis_title="Tip radius (μm)",
        yaxis_title="Onset voltage (kV)",
        template="plotly_dark",
        height=550,
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )

    st.warning(
        "This is the reduced-order onset model. "
        "It is not yet coupled to molecular dynamics."
    )

# ============================================================
# MOLECULAR SYSTEM
# ============================================================

elif model == "Molecular System":

    st.header("EMIM-BF₄ Molecular System")

    st.write(
        "This view represents the atomistic system used "
        "by the molecular-dynamics layer."
    )

    st.info(
        "The molecular coordinates shown here must eventually "
        "come from the validated EMIM-BF₄ topology/trajectory. "
        "No synthetic trajectory is being presented as experimental data."
    )

    # Simple structural schematic.
    # These coordinates are only a visualization placeholder,
    # NOT a molecular-dynamics result.

    atoms = pd.DataFrame(
        {
            "element": [
                "N",
                "C",
                "C",
                "C",
                "B",
                "F",
                "F",
                "F",
                "F",
            ],
            "x": [
                -1.0,
                0.0,
                1.0,
                0.0,
                3.0,
                4.2,
                3.0,
                3.0,
                1.8,
            ],
            "y": [
                0.0,
                0.8,
                0.0,
                -0.8,
                0.0,
                0.0,
                1.2,
                -1.2,
                0.0,
            ],
            "z": [
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.8,
                0.0,
                0.0,
                -0.8,
            ],
        }
    )

    fig = go.Figure()

    fig.add_trace(
        go.Scatter3d(
            x=atoms["x"],
            y=atoms["y"],
            z=atoms["z"],
            mode="markers+text",
            text=atoms["element"],
            textposition="top center",
            marker=dict(
                size=9,
            ),
        )
    )

    fig.update_layout(
        title="Atomistic EMIM-BF₄ Structure",
        template="plotly_dark",
        height=650,
        scene=dict(
            xaxis_title="x",
            yaxis_title="y",
            zaxis_title="z",
        ),
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )

    st.caption(
        "Visualization scaffold only. Replace with coordinates "
        "from the validated force-field topology/trajectory."
    )

# ============================================================
# ELECTRIC FIELD
# ============================================================

elif model == "Electric Field":

    st.header("Electrospray Electric Field")

    col1, col2 = st.columns(2)

    with col1:

        voltage_kv = st.slider(
            "Extractor voltage (kV)",
            0.1,
            10.0,
            2.0,
        )

    with col2:

        gap_mm = st.slider(
            "Emitter–extractor gap (mm)",
            0.5,
            10.0,
            2.0,
        )

    gap_m = gap_mm * 1e-3

    E = voltage_kv * 1000 / gap_m

    st.metric(
        "Uniform-field estimate",
        f"{E / 1e6:.3f} MV/m",
    )

    x = np.linspace(
        -2,
        2,
        20,
    )

    y = np.linspace(
        -2,
        2,
        20,
    )

    X, Y = np.meshgrid(x, y)

    U = np.zeros_like(X)
    V = np.ones_like(Y)

    fig = go.Figure()

    fig.add_trace(
        go.Heatmap(
            x=x,
            y=y,
            z=V,
            colorbar=dict(
                title="Relative E",
            ),
        )
    )

    fig.add_trace(
        go.Streamline(
            x=x,
            y=y,
            z=V,
        )
        if False
        else go.Scatter(
            x=X.flatten(),
            y=Y.flatten(),
            mode="markers",
            marker=dict(
                size=2,
                opacity=0.35,
            ),
            name="Field samples",
        )
    )

    fig.update_layout(
        title="Electric-Field Visualization",
        template="plotly_dark",
        height=600,
        xaxis_title="x",
        yaxis_title="y",
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )

    st.caption(
        "The current field view is a visualization of the "
        "uniform-field estimate. The production model will "
        "replace this with the actual electrode geometry and "
        "electrostatic solution."
    )

# ============================================================
# RPA
# ============================================================

elif model == "RPA Analysis":

    st.header("Retarding Potential Analysis")

    st.write(
        "Upload an experimental or simulated RPA dataset."
    )

    uploaded = st.file_uploader(
        "RPA CSV",
        type=["csv"],
    )

    if uploaded is None:

        st.info(
            "Expected columns:\n\n"
            "`stopping_potential_V,current_A`\n\n"
            "or\n\n"
            "`stopping_potential_V,normalized_current`"
        )

    else:

        data = pd.read_csv(uploaded)

        st.subheader("Dataset")

        st.dataframe(
            data,
            use_container_width=True,
        )

        required_voltage = "stopping_potential_V"

        if required_voltage not in data.columns:

            st.error(
                "The CSV must contain "
                "`stopping_potential_V`."
            )

        else:

            current_column = None

            for candidate in [
                "current_A",
                "normalized_current",
                "current",
            ]:
                if candidate in data.columns:
                    current_column = candidate
                    break

            if current_column is None:

                st.error(
                    "Could not find a current column. "
                    "Use `current_A` or "
                    "`normalized_current`."
                )

            else:

                fig = go.Figure()

                fig.add_trace(
                    go.Scatter(
                        x=data[required_voltage],
                        y=data[current_column],
                        mode="lines+markers",
                        name="RPA data",
                    )
                )

                fig.update_layout(
                    title="Retarding Potential Analysis",
                    xaxis_title="Retarding potential (V)",
                    yaxis_title=current_column,
                    template="plotly_dark",
                    height=550,
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True,
                )

                st.success(
                    "RPA dataset loaded successfully."
                )

# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "FALAK Electrospray Model — research prototype. "
    "Simulation results are only reported when generated "
    "from documented computational or experimental data."
)
