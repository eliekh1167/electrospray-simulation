import os

import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Ellipse, Rectangle

try:
    import py3Dmol
    from stmol import showmol
    MOLECULAR_VIEW_AVAILABLE = True
except ImportError:
    MOLECULAR_VIEW_AVAILABLE = False

from physics import PROPPELLANTS, onset_voltage

try:
    from electric_field import (
        calculate_operating_point,
        create_field_map,
    )
    ELECTRIC_FIELD_AVAILABLE = True
except ImportError:
    ELECTRIC_FIELD_AVAILABLE = False


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="FALAK Electrospray Model",
    layout="centered",
)


# ============================================================
# SCIENTIFIC / LIGHT THEME
# ============================================================

st.markdown(
    """
    <style>

    html, body, [class*="css"] {
        font-family: "Times New Roman", Times, serif;
    }

    .stApp {
        background-color: #f7f9fc;
        color: #111827;
    }

    h1, h2, h3, h4, h5, h6 {
        color: #0b1f3a !important;
        font-family: "Times New Roman", Times, serif !important;
        font-weight: 600 !important;
    }

    p, label, div, span {
        font-family: "Times New Roman", Times, serif;
    }

    .stMarkdown,
    .stText,
    .stCaption {
        color: #172033;
    }

    .stSlider label,
    .stNumberInput label,
    .stSelectbox label,
    .stTextInput label {
        color: #0b1f3a !important;
        font-weight: 600 !important;
        font-size: 16px !important;
    }

    .stSlider [data-baseweb="slider"] {
        color: #0b1f3a;
    }

    .stMetric label {
        color: #0b1f3a !important;
        font-family: "Times New Roman", Times, serif !important;
        font-weight: 600 !important;
    }

    .stMetric [data-testid="stMetricValue"] {
        color: #0b1f3a !important;
        font-family: "Times New Roman", Times, serif !important;
    }

    .stMetric [data-testid="stMetricDelta"] {
        color: #344054 !important;
    }

    .stDataFrame {
        color: #111827;
    }

    .stCaption {
        color: #475467 !important;
        font-family: "Times New Roman", Times, serif !important;
    }

    hr {
        border-color: #d7dee8;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# TITLE
# ============================================================

st.markdown(
    "<h1 style='text-align:center; letter-spacing:0.5px;'>"
    "FALAK Electrospray Onset Model"
    "</h1>",
    unsafe_allow_html=True,
)

st.markdown(
    "<p style='text-align:center; color:#344054; font-size:16px;'>"
    "EMIM-BF4 electrospray modeling from Taylor-cone onset "
    "to molecular dynamics"
    "</p>",
    unsafe_allow_html=True,
)

st.markdown("---")


# ============================================================
# VISUAL SETTINGS
# ============================================================

SPACE_BG = "#f7f9fc"
NAVY = "#0b1f3a"
BLUE = "#1f5f8b"
LIGHT_BLUE = "#6ea6c7"
ORANGE = "#b85c00"
GRID = "#cbd5e1"
DARK_GRAY = "#344054"


# ============================================================
# EMIM-BF4 PROPELLANT
# ============================================================

EMIM_BF4 = {
    "name": "EMI-BF4",
    "gamma": PROPPELLANTS["EMI-BF4"]["surface_tension"],
    "K": PROPPELLANTS["EMI-BF4"]["conductivity"],
}


# ============================================================
# ELECTROSPRAY ONSET MODEL
# ============================================================

st.header("EMIM-BF4 Taylor-cone onset")

st.write(
    "Predict the approximate voltage required to reach the "
    "Taylor-cone onset condition for the EMIM-BF4 ionic liquid."
)

col1, col2 = st.columns(2)

with col1:
    rc_um = st.slider(
        "Emitter tip radius (µm)",
        min_value=2,
        max_value=30,
        value=10,
    )

with col2:
    d_mm = st.slider(
        "Electrode gap (mm)",
        min_value=0.5,
        max_value=5.0,
        value=2.0,
    )

rc = rc_um * 1e-6
d = d_mm * 1e-3

predicted_onset_v = onset_voltage(
    EMIM_BF4["gamma"],
    rc,
    d,
)

predicted_onset_kv = predicted_onset_v / 1000.0


metric1, metric2, metric3 = st.columns(3)

metric1.metric(
    "Propellant",
    "EMIM-BF4",
)

metric2.metric(
    "Predicted onset",
    f"{predicted_onset_kv:.3f} kV",
)

metric3.metric(
    "Surface tension",
    f"{EMIM_BF4['gamma']:.4f} N/m",
)


# ============================================================
# MODEL INPUTS
# ============================================================

st.subheader("Model inputs")

table_data = {
    "Parameter": [
        "Propellant",
        "Surface tension",
        "Conductivity",
        "Emitter tip radius",
        "Electrode gap",
        "Predicted onset voltage",
    ],
    "Value": [
        "EMIM-BF4",
        f"{EMIM_BF4['gamma']:.4f} N/m",
        f"{EMIM_BF4['K']:.2f} S/m",
        f"{rc_um} µm",
        f"{d_mm:.2f} mm",
        f"{predicted_onset_kv:.3f} kV",
    ],
}

st.dataframe(
    pd.DataFrame(table_data),
    use_container_width=True,
    hide_index=True,
)


# ============================================================
# ONSET VOLTAGE VS TIP RADIUS
# ============================================================

st.subheader("Onset voltage vs tip radius")

radii_um = np.logspace(
    np.log10(2),
    np.log10(30),
    300,
)

v_sweep = [
    onset_voltage(
        EMIM_BF4["gamma"],
        r * 1e-6,
        d,
    ) / 1000.0
    for r in radii_um
]

fig2, ax2 = plt.subplots(
    figsize=(8, 5),
    facecolor=SPACE_BG,
)

ax2.set_facecolor(SPACE_BG)

ax2.loglog(
    radii_um,
    v_sweep,
    color=BLUE,
    linewidth=2.2,
    label="EMIM-BF4",
)

ax2.scatter(
    [rc_um],
    [predicted_onset_kv],
    color=NAVY,
    s=55,
    zorder=5,
    label="Current operating point",
)

ax2.set_xlabel("Tip radius (µm)", color=NAVY)
ax2.set_ylabel("Onset voltage (kV)", color=NAVY)

ax2.tick_params(
    axis="both",
    colors=DARK_GRAY,
)

ax2.legend(
    facecolor=SPACE_BG,
    edgecolor=GRID,
)

ax2.grid(
    True,
    which="major",
    linestyle="--",
    alpha=0.35,
    color=GRID,
)

ax2.grid(
    True,
    which="minor",
    linestyle=":",
    alpha=0.18,
    color=GRID,
)

for spine in ax2.spines.values():
    spine.set_color(GRID)

st.pyplot(fig2)


# ============================================================
# EXPERIMENTAL VALIDATION
# ============================================================

st.markdown("---")
st.subheader("Model validation against published data")

st.write(
    "Enter a measured EMIM-BF4 onset voltage from a literature "
    "source to compare the analytical prediction with experiment."
)

published_v = st.number_input(
    "Published EMIM-BF4 onset voltage (kV)",
    min_value=0.0,
    value=0.0,
    step=0.1,
)

if published_v > 0:

    error_pct = (
        abs(predicted_onset_kv - published_v)
        / published_v
        * 100.0
    )

    st.metric(
        label="Predicted onset voltage",
        value=f"{predicted_onset_kv:.3f} kV",
        delta=f"{error_pct:.1f}% difference from published value",
    )

    if error_pct < 15:

        st.success(
            "The prediction is within 15% of the supplied experimental "
            "value. This is a numerical comparison, not a complete "
            "experimental validation."
        )

    else:

        st.warning(
            "The prediction differs by more than 15%. Geometry assumptions, "
            "experimental conditions, or liquid properties should be "
            "investigated before claiming agreement."
        )

else:

    st.info(
        "Enter a published EMIM-BF4 onset voltage above to perform "
        "the comparison."
    )


# ============================================================
# MOLECULAR DYNAMICS
# ============================================================

st.markdown("---")
st.header("Molecular dynamics: EMIM-BF4 bulk liquid")

st.write(
    "This section summarizes the GROMACS EMIM-BF4 simulation developed "
    "by FALAK. The system contains 500 EMIM+ ions and 500 BF4- ions "
    "(12,000 atoms), using the documented ionic-liquid force-field "
    "parameters, followed by energy minimization and NVT/NPT equilibration."
)


# ============================================================
# NPT DATA
# ============================================================

NPT_TIME_PS = [
    0.0, 0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.4, 1.6, 1.8,
    2.0, 2.2, 2.4, 2.6, 2.8, 3.0, 3.2, 3.4, 3.6, 3.8,
    4.0, 4.2, 4.4, 4.6, 4.8, 5.0, 5.2, 5.4, 5.6, 5.8,
    6.0, 6.2, 6.4, 6.6, 6.8, 7.0, 7.2, 7.4, 7.6, 7.8,
    8.0, 8.2, 8.4, 8.6, 8.8, 9.0, 9.2, 9.4, 9.6, 9.8,
    10.0, 10.2, 10.4, 10.6, 10.8, 11.0, 11.2, 11.4, 11.6, 11.8,
    12.0, 12.2, 12.4, 12.6, 12.8, 13.0, 13.2, 13.4, 13.6, 13.8,
    14.0, 14.2, 14.4, 14.6, 14.8, 15.0, 15.2, 15.4, 15.6, 15.8,
    16.0, 16.2, 16.4, 16.6, 16.8, 17.0, 17.2, 17.4, 17.6, 17.8,
    18.0, 18.2, 18.4, 18.6, 18.8, 19.0, 19.2, 19.4, 19.6, 19.8,
    20.0,
]

NPT_DENSITY_KGM3 = [
    1280.24, 1262.41, 1252.71, 1248.5, 1228.4, 1223.77, 1227.59,
    1219.08, 1229.98, 1229.55, 1219.89, 1231.31, 1224.45, 1220.16,
    1226.13, 1216.57, 1214.45, 1220.29, 1208.12, 1214.88, 1215.31,
    1209.22, 1217.78, 1214.93, 1209.42, 1219.02, 1215.14, 1213.81,
    1223.61, 1219.25, 1223.96, 1222.44, 1219.16, 1219.66, 1220.86,
    1211.01, 1215.02, 1216.24, 1209.39, 1212.9, 1216.46, 1208.36,
    1217.83, 1211.24, 1210.92, 1215.1, 1208.77, 1207.08, 1212.71,
    1209.73, 1214.02, 1216.82, 1216.42, 1219.21, 1211.23, 1216.56,
    1217.63, 1211.17, 1214.51, 1216.67, 1207.85, 1213.45, 1211.1,
    1208.58, 1211.38, 1216.86, 1211.87, 1219.36, 1218.82, 1216.6,
    1215.48, 1214.02, 1218.02, 1212.06, 1215.36, 1219.36, 1210.24,
    1215.84, 1213.28, 1202.55, 1210.47, 1210.07, 1201.98, 1212.32,
    1217.43, 1207.07, 1213.9, 1215.04, 1210.6, 1209.54, 1215.98,
    1211.69, 1213.59, 1212.19, 1215.89, 1212.56, 1217.41, 1215.87,
    1217.82, 1220.32,
]

NPT_TEMPERATURE_K = [
    298.55, 295.13, 294.1, 296.58, 295.65, 299.07, 298.99, 295.74,
    299.0, 300.27, 298.26, 295.4, 297.15, 298.04, 300.26, 304.04,
    297.14, 300.86, 297.29, 302.23, 302.09, 297.3, 295.73, 296.93,
    294.01, 295.44, 296.5, 292.8, 297.83, 296.31, 299.65, 301.36,
    303.3, 297.46, 294.33, 295.34, 297.08, 302.4, 294.97, 300.21,
    299.71, 297.42, 298.52, 299.81, 295.54, 296.0, 294.98, 295.09,
    294.69, 299.87, 300.5, 298.47, 294.36, 299.55, 298.4, 297.9,
    298.62, 301.54, 300.38, 302.49, 301.58, 299.21, 298.97, 300.75,
    295.01, 301.09, 299.59, 298.53, 299.76, 298.56, 297.81, 298.45,
    298.81, 300.82, 301.68, 300.8, 297.96, 298.57, 303.64, 300.79,
    296.07, 295.67, 300.41, 295.68, 299.97, 296.96, 297.51, 294.24,
    298.75, 299.49, 300.4, 293.93, 298.65, 296.98, 299.48, 294.6,
    297.05, 299.55, 297.92, 299.79,
]


# ============================================================
# SAFE DATA ALIGNMENT
# ============================================================

npt_lengths = [
    len(NPT_TIME_PS),
    len(NPT_DENSITY_KGM3),
    len(NPT_TEMPERATURE_K),
]

npt_points = min(npt_lengths)

if len(set(npt_lengths)) != 1:

    st.warning(
        f"Temperature data contains {len(NPT_TEMPERATURE_K)} points "
        f"while the time array contains {len(NPT_TIME_PS)}. "
        f"The plots use only the {npt_points} matching points."
    )

time_plot = np.asarray(
    NPT_TIME_PS[:npt_points],
    dtype=float,
)

density_plot = np.asarray(
    NPT_DENSITY_KGM3[:npt_points],
    dtype=float,
)

temperature_plot = np.asarray(
    NPT_TEMPERATURE_K[:npt_points],
    dtype=float,
)

density_mean = np.mean(density_plot)
temp_mean = np.mean(temperature_plot)

literature_density = 1240.0

density_error_pct = (
    abs(density_mean - literature_density)
    / literature_density
    * 100.0
)


col1, col2, col3 = st.columns(3)

col1.metric(
    "Simulated density",
    f"{density_mean:.1f} kg/m³",
)

col2.metric(
    "Mean temperature",
    f"{temp_mean:.1f} K",
)

col3.metric(
    "Density difference",
    f"{density_error_pct:.1f}%",
)


# ============================================================
# DENSITY PLOT
# ============================================================

fig3, ax3 = plt.subplots(
    figsize=(8, 5),
    facecolor=SPACE_BG,
)

ax3.set_facecolor(SPACE_BG)

ax3.plot(
    time_plot,
    density_plot,
    color=BLUE,
    linewidth=1.5,
)

ax3.axhline(
    y=literature_density,
    linestyle="--",
    color=NAVY,
    linewidth=1,
    label=f"Literature ({literature_density:.0f} kg/m³)",
)

ax3.set_xlabel("Time (ps)", color=NAVY)
ax3.set_ylabel("Density (kg/m³)", color=NAVY)

ax3.tick_params(
    axis="both",
    colors=DARK_GRAY,
)

ax3.legend(
    facecolor=SPACE_BG,
    edgecolor=GRID,
)

ax3.grid(
    True,
    linestyle=":",
    alpha=0.35,
    color=GRID,
)

for spine in ax3.spines.values():
    spine.set_color(GRID)

st.pyplot(fig3)

st.caption(
    "NPT density relaxation during the 20 ps demonstration-scale run. "
    "This is not a production-length equilibrium simulation."
)


# ============================================================
# TEMPERATURE PLOT
# ============================================================

fig4, ax4 = plt.subplots(
    figsize=(8, 5),
    facecolor=SPACE_BG,
)

ax4.set_facecolor(SPACE_BG)

ax4.plot(
    time_plot,
    temperature_plot,
    color=ORANGE,
    linewidth=1.5,
)

ax4.axhline(
    y=298.15,
    linestyle="--",
    color=NAVY,
    linewidth=1,
    label="Target (298.15 K)",
)

ax4.set_xlabel("Time (ps)", color=NAVY)
ax4.set_ylabel("Temperature (K)", color=NAVY)

ax4.tick_params(
    axis="both",
    colors=DARK_GRAY,
)

ax4.legend(
    facecolor=SPACE_BG,
    edgecolor=GRID,
)

ax4.grid(
    True,
    linestyle=":",
    alpha=0.35,
    color=GRID,
)

for spine in ax4.spines.values():
    spine.set_color(GRID)

st.pyplot(fig4)

st.caption(
    "NPT temperature during the equilibration run."
)


# ============================================================
# 3D MOLECULAR STRUCTURE
# ============================================================

st.markdown("---")
st.header("3D structure: simulated EMIM-BF4 box")

st.write(
    "Interactive molecular visualization of the actual equilibrated "
    "GROMACS coordinate file."
)

PROJECT_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

NPT_GRO_PATH = os.path.join(
    PROJECT_DIR,
    "md",
    "gromacs",
    "npt.gro",
)

if not MOLECULAR_VIEW_AVAILABLE:

    st.warning(
        "The molecular visualization packages are not available in "
        "the current Python environment. Install py3Dmol, stmol, "
        "ipywidgets, and ipython_genutils, then restart Streamlit."
    )

elif not os.path.exists(NPT_GRO_PATH):

    st.warning(
        "npt.gro was not found at md/gromacs/npt.gro."
    )

else:

    try:

        n_pairs_to_show = st.slider(
            "Number of ion pairs to display",
            min_value=10,
            max_value=500,
            value=100,
        )

        with open(
            NPT_GRO_PATH,
            "r",
            encoding="utf-8",
        ) as f:

            gro_lines = f.readlines()

        title_line = gro_lines[0]

        n_atoms_total = int(
            gro_lines[1].strip()
        )

        atom_lines = gro_lines[
            2:2 + n_atoms_total
        ]

        box_line = gro_lines[
            2 + n_atoms_total
        ]

        emim_atom_count = 19
        bf4_atom_count = 5
        n_molecules = 500

        expected_atoms = (
            n_molecules * emim_atom_count
            + n_molecules * bf4_atom_count
        )

        if n_atoms_total < expected_atoms:

            st.error(
                f"The coordinate file contains {n_atoms_total} atoms, "
                f"but the expected EMIM-BF4 system contains "
                f"{expected_atoms} atoms."
            )

        else:

            emim_atoms = atom_lines[
                :n_molecules * emim_atom_count
            ]

            bf4_atoms = atom_lines[
                n_molecules * emim_atom_count:
                n_molecules * emim_atom_count
                + n_molecules * bf4_atom_count
            ]

            subset_emim = emim_atoms[
                :n_pairs_to_show * emim_atom_count
            ]

            subset_bf4 = bf4_atoms[
                :n_pairs_to_show * bf4_atom_count
            ]

            subset_atoms = (
                subset_emim
                + subset_bf4
            )

            mini_gro = (
                title_line
                + f"{len(subset_atoms)}\n"
                + "".join(subset_atoms)
                + box_line
            )

            view = py3Dmol.view(
                width=700,
                height=450,
            )

            view.addModel(
                mini_gro,
                "gro",
            )

            view.setStyle(
                {
                    "stick": {
                        "radius": 0.15,
                    }
                }
            )

            view.setBackgroundColor(
                "#f7f9fc"
            )

            view.zoomTo()

            showmol(
                view,
                height=450,
                width=700,
            )

            st.caption(
                f"Showing {n_pairs_to_show} of 500 ion pairs "
                "from the actual equilibrated npt.gro structure."
            )

    except (
        ValueError,
        IndexError,
    ) as exc:

        st.error(
            f"Could not parse npt.gro: {exc}"
        )


# ============================================================
# 3D TAYLOR-CONE AND ION-EMISSION VISUALIZATION
# ============================================================

st.markdown("---")
st.header("3D Taylor-cone and ion-emission visualization")

st.write(
    "Three-dimensional schematic representation of the EMIM-BF4 "
    "electrospray onset geometry, including the liquid reservoir, "
    "Taylor cone, emission jet, emitted ions, and counter-electrode."
)

if not MOLECULAR_VIEW_AVAILABLE:

    st.warning(
        "py3Dmol/stmol are not available. Install them with "
        "'python -m pip install py3Dmol stmol'."
    )

else:

    cone_col1, cone_col2 = st.columns(2)

    with cone_col1:

        cone_angle = st.slider(
            "Taylor-cone half-angle (°)",
            min_value=35.0,
            max_value=55.0,
            value=49.3,
            step=0.1,
            key="cone_angle_3d",
        )

    with cone_col2:

        jet_radius_um = st.slider(
            "Jet radius (µm)",
            min_value=1.0,
            max_value=20.0,
            value=7.0,
            step=0.5,
            key="jet_radius_3d",
        )

    emitted_pairs = st.slider(
        "Emitted ion pairs",
        min_value=2,
        max_value=20,
        value=8,
        step=1,
        key="emitted_pairs_3d",
    )

    try:

        # ----------------------------------------------------
        # CREATE VIEWER
        # ----------------------------------------------------

        view3d = py3Dmol.view(
            width=760,
            height=560,
        )

        # ----------------------------------------------------
        # GEOMETRY
        # ----------------------------------------------------

        cone_height = 3.2
        reservoir_radius = 3.0
        reservoir_depth = 0.9

        jet_length = 2.0
        jet_start = cone_height
        jet_end = jet_start + jet_length

        electrode_z = 8.2

        # ----------------------------------------------------
        # LIQUID RESERVOIR
        # ----------------------------------------------------

        view3d.addCylinder(
            {
                "start": {
                    "x": 0,
                    "y": 0,
                    "z": -reservoir_depth,
                },
                "end": {
                    "x": 0,
                    "y": 0,
                    "z": 0,
                },
                "radius": reservoir_radius,
                "color": "#315b7d",
                "opacity": 0.75,
            }
        )

        # ----------------------------------------------------
        # TAYLOR CONE
        #
        # Instead of relying on addCone(), construct the
        # surface using many thin circular rings.
        # This gives a smoother and more controllable shape.
        # ----------------------------------------------------

        angle_rad = np.deg2rad(cone_angle)

        cone_base_radius = (
            cone_height * np.tan(angle_rad)
        )

        cone_base_radius = min(
            cone_base_radius,
            reservoir_radius * 0.95,
        )

        n_rings = 32
        n_segments = 48

        for i in range(n_rings):

            z = (
                cone_height
                * i
                / (n_rings - 1)
            )

            # Radius decreases linearly toward the tip.
            radius = cone_base_radius * (
                1.0 - i / (n_rings - 1)
            )

            # Avoid zero radius at the very tip.
            radius = max(
                radius,
                0.025,
            )

            for j in range(n_segments):

                theta = (
                    2.0
                    * np.pi
                    * j
                    / n_segments
                )

                x = radius * np.cos(theta)
                y = radius * np.sin(theta)

                view3d.addSphere(
                    {
                        "center": {
                            "x": x,
                            "y": y,
                            "z": z,
                        },
                        "radius": 0.085,
                        "color": "#4fd1ff",
                        "opacity": 0.72,
                    }
                )

        # ----------------------------------------------------
        # CONE TIP
        # ----------------------------------------------------

        view3d.addSphere(
            {
                "center": {
                    "x": 0,
                    "y": 0,
                    "z": cone_height,
                },
                "radius": 0.12,
                "color": "#8ee8ff",
                "opacity": 0.95,
            }
        )

        # ----------------------------------------------------
        # EMISSION JET
        # ----------------------------------------------------

        jet_radius = jet_radius_um / 10.0

        view3d.addCylinder(
            {
                "start": {
                    "x": 0,
                    "y": 0,
                    "z": jet_start,
                },
                "end": {
                    "x": 0,
                    "y": 0,
                    "z": jet_end,
                },
                "radius": jet_radius,
                "color": "#8ee8ff",
                "opacity": 0.85,
            }
        )

        # ----------------------------------------------------
        # EMITTED IONS
        # ----------------------------------------------------

        ion_start = jet_end + 0.35
        ion_spacing = 0.45

        for i in range(emitted_pairs):

            z_position = (
                ion_start
                + i * ion_spacing
            )

            # Slight radial oscillation creates a realistic
            # emission plume rather than a perfectly straight line.
            x_offset = (
                0.10
                * np.sin(i * 1.7)
            )

            y_offset = (
                0.10
                * np.cos(i * 1.3)
            )

            # EMIM+
            emim_x = x_offset
            emim_y = y_offset

            view3d.addSphere(
                {
                    "center": {
                        "x": emim_x,
                        "y": emim_y,
                        "z": z_position,
                    },
                    "radius": 0.18,
                    "color": "#4fd1ff",
                    "opacity": 1.0,
                }
            )

            # BF4-
            bf4_x = x_offset + 0.34
            bf4_y = y_offset + 0.12

            view3d.addSphere(
                {
                    "center": {
                        "x": bf4_x,
                        "y": bf4_y,
                        "z": z_position + 0.08,
                    },
                    "radius": 0.13,
                    "color": "#7ee081",
                    "opacity": 1.0,
                    }
            )

            # Ion-pair connection
            view3d.addCylinder(
                {
                    "start": {
                        "x": emim_x,
                        "y": emim_y,
                        "z": z_position,
                    },
                    "end": {
                        "x": bf4_x,
                        "y": bf4_y,
                        "z": z_position + 0.08,
                    },
                    "radius": 0.025,
                    "color": "#b8c7d9",
                    "opacity": 0.65,
                }
            )

        # ----------------------------------------------------
        # COUNTER-ELECTRODE
        # ----------------------------------------------------

        view3d.addCylinder(
            {
                "start": {
                    "x": -3.5,
                    "y": -3.5,
                    "z": electrode_z,
                },
                "end": {
                    "x": 3.5,
                    "y": 3.5,
                    "z": electrode_z,
                },
                "radius": 0.10,
                "color": "#c7c7c7",
                "opacity": 0.95,
            }
        )

        view3d.addCylinder(
            {
                "start": {
                    "x": -3.5,
                    "y": 3.5,
                    "z": electrode_z,
                },
                "end": {
                    "x": 3.5,
                    "y": -3.5,
                    "z": electrode_z,
                },
                "radius": 0.10,
                "color": "#c7c7c7",
                "opacity": 0.95,
            }
        )

        # ----------------------------------------------------
        # ELECTRIC FIELD ARROWS
        # ----------------------------------------------------

        for x_position in [-2.0, 0.0, 2.0]:

            view3d.addArrow(
                {
                    "start": {
                        "x": x_position,
                        "y": 0,
                        "z": 5.0,
                    },
                    "end": {
                        "x": x_position,
                        "y": 0,
                        "z": 6.0,
                    },
                    "radius": 0.035,
                    "color": "#ff9d5c",
                    "opacity": 0.75,
                }
            )

        # ----------------------------------------------------
        # LABELS
        # ----------------------------------------------------

        view3d.addLabel(
            "EMIM-BF4 liquid",
            {
                "position": {
                    "x": -2.1,
                    "y": 0,
                    "z": -0.45,
                },
                "fontColor": "white",
                "backgroundColor": "#172033",
                "backgroundOpacity": 0.80,
                "fontSize": 13,
            },
        )

        view3d.addLabel(
            "Taylor cone",
            {
                "position": {
                    "x": 1.0,
                    "y": 0,
                    "z": 1.7,
                },
                "fontColor": "white",
                "backgroundColor": "#172033",
                "backgroundOpacity": 0.80,
                "fontSize": 13,
            },
        )

        view3d.addLabel(
            "Ion emission",
            {
                "position": {
                    "x": 1.0,
                    "y": 0,
                    "z": 5.4,
                },
                "fontColor": "white",
                "backgroundColor": "#172033",
                "backgroundOpacity": 0.80,
                "fontSize": 13,
            },
        )

        view3d.addLabel(
            "Counter-electrode",
            {
                "position": {
                    "x": 1.9,
                    "y": 0,
                    "z": electrode_z,
                },
                "fontColor": "white",
                "backgroundColor": "#172033",
                "backgroundOpacity": 0.80,
                "fontSize": 13,
            },
        )

        # ----------------------------------------------------
        # CAMERA / DISPLAY
        # ----------------------------------------------------

        view3d.setBackgroundColor(
            "#0a0e1a"
        )

        view3d.zoomTo()

        view3d.rotate(
            15,
            "y",
        )

        showmol(
            view3d,
            height=560,
            width=760,
        )

        st.caption(
            "Three-dimensional schematic of the electrospray "
            "emission geometry. The Taylor cone and ion plume "
            "are illustrative and are not directly extracted "
            "from the GROMACS trajectory."
        )

        st.caption(
            "Blue markers represent EMIM+; green markers "
            "represent BF4−. Orange arrows indicate the "
            "assumed electric-field direction."
        )

    except Exception as exc:

        st.error(
            f"The 3D Taylor-cone visualization could not be "
            f"generated: {exc}"
        )
# ============================================================
# ELECTRIC FIELD VISUALIZATION
# ============================================================

st.markdown("---")
st.header("Electric-field visualization")

st.write(
    "Analytical visualization of the electric field between the emitter "
    "and counter-electrode. The color map represents field magnitude, "
    "while arrows indicate the approximate field direction."
)

if not ELECTRIC_FIELD_AVAILABLE:

    st.error(
        "electric_field.py could not be imported. "
        "Create electric_field.py in the same project directory "
        "as app.py."
    )

else:

    field_col1, field_col2 = st.columns(2)

    with field_col1:

        field_voltage = st.number_input(
            "Applied voltage (kV)",
            min_value=0.1,
            max_value=30.0,
            value=5.0,
            step=0.1,
            key="field_voltage",
        )

    with field_col2:

        field_gap = st.slider(
            "Electrode gap (mm)",
            min_value=0.5,
            max_value=5.0,
            value=2.0,
            key="field_gap",
        )

    field_radius = st.slider(
        "Emitter tip radius (µm)",
        min_value=2,
        max_value=30,
        value=10,
        key="field_radius",
    )

    try:

        operating_point = calculate_operating_point(
            "EMI-BF4",
            field_radius,
            field_gap,
        )

        applied_voltage = (
            field_voltage * 1000.0
        )

        X, Y, E = create_field_map(
            applied_voltage,
            field_gap,
        )

        metric1, metric2, metric3 = st.columns(3)

        metric1.metric(
            "Predicted onset",
            f"{operating_point['onset_voltage_kV']:.3f} kV",
        )

        metric2.metric(
            "Applied voltage",
            f"{field_voltage:.2f} kV",
        )

        metric3.metric(
            "Average field",
            f"{applied_voltage / (field_gap * 1e-3) / 1e6:.2f} MV/m",
        )


        # ----------------------------------------------------
        # FIELD MAP
        # ----------------------------------------------------

        fig_field, ax_field = plt.subplots(
            figsize=(9, 6),
            facecolor=SPACE_BG,
        )

        ax_field.set_facecolor(
            SPACE_BG
        )

        field_plot = ax_field.contourf(
            X * 1000.0,
            Y * 1000.0,
            E / 1e6,
            levels=40,
            cmap="viridis",
        )

        x_min = np.min(
            X * 1000.0
        )

        x_max = np.max(
            X * 1000.0
        )

        y_min = np.min(
            Y * 1000.0
        )

        y_max = np.max(
            Y * 1000.0
        )

        arrow_x = np.linspace(
            x_min,
            x_max,
            17,
        )

        arrow_y = np.linspace(
            y_min,
            y_max,
            17,
        )

        XX, YY = np.meshgrid(
            arrow_x,
            arrow_y,
        )

        U = np.zeros_like(
            XX
        )

        V = np.ones_like(
            YY
        )

        ax_field.quiver(
            XX,
            YY,
            U,
            V,
            color="white",
            alpha=0.60,
            angles="xy",
            scale_units="xy",
            scale=35,
            width=0.002,
        )

        ax_field.scatter(
            [0],
            [0],
            s=120,
            marker="^",
            color="white",
            edgecolor=NAVY,
            linewidth=0.8,
            zorder=5,
            label="Emitter",
        )

        ax_field.set_xlabel(
            "Radial position (mm)",
            color=NAVY,
        )

        ax_field.set_ylabel(
            "Axial position (mm)",
            color=NAVY,
        )

        ax_field.set_title(
            "EMIM-BF4 analytical electric-field approximation",
            color=NAVY,
        )

        ax_field.tick_params(
            axis="both",
            colors=DARK_GRAY,
        )

        cbar = fig_field.colorbar(
            field_plot,
            ax=ax_field,
        )

        cbar.set_label(
            "Electric field magnitude (MV/m)",
            color=NAVY,
        )

        ax_field.legend(
            facecolor=SPACE_BG,
            edgecolor=GRID,
        )

        for spine in ax_field.spines.values():
            spine.set_color(GRID)

        st.pyplot(
            fig_field
        )

        st.caption(
            "Color represents the analytical field magnitude. White arrows "
            "show the assumed emitter-to-electrode field direction for "
            "visualization. This is not a finite-element electrostatic solution."
        )

    except Exception as exc:

        st.error(
            f"The electric-field model could not be calculated: {exc}"
        )


# ============================================================
# REFERENCES / MODEL SCOPE
# ============================================================

st.markdown("---")

st.caption(
    "EMIM-BF4 surface tension and conductivity are based on published "
    "ionic-liquid data. The onset model follows the Taylor-cone "
    "equilibrium framework combined with a capillary electrode-field "
    "approximation."
)

st.caption(
    "Molecular dynamics: OPLS-based ionic-liquid force-field parameters "
    "from Doherty et al. (2017), with the documented FALAK EMIM-BF4 "
    "parameter implementation. Simulations performed with GROMACS."
)

st.caption(
    "Important scope: the present FALAK implementation is an analytical "
    "electrospray onset model coupled to a bulk-liquid MD workflow. "
    "It does not yet constitute a full electrohydrodynamic or "
    "particle-in-cell electrospray simulation."
)

st.caption(
    "FALAK Aerospace and Engineering Program"
)