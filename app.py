import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator, AutoMinorLocator

st.set_page_config(page_title="FALAK Electrospray Model", layout="centered")

st.markdown("<h1 style='text-align:center; letter-spacing:1px;'>FALAK Electrospray Onset Model</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#7fa8c9; font-size:14px;'>Pre-hardware Taylor cone onset prediction and propellant screening</p>", unsafe_allow_html=True)
st.markdown("---")

eps0 = 8.854e-12
theta = np.radians(49.3)
cos_theta = np.cos(theta)

def onset_voltage(gamma, r_c, d):
    return np.sqrt((r_c * gamma * cos_theta) / (2 * eps0)) * np.log(4 * d / r_c)

propellants = {
    'EMI-BF4':   {'gamma': 0.0452,  'K': 1.4,  'color': '#4fd1ff'},
    'EMI-GaCl4': {'gamma': 0.0486,  'K': 2.2,  'color': '#7fffb2'},
    'EMI-Tf2N':  {'gamma': 0.0349,  'K': 0.88, 'color': '#ff9d5c'},
    'EMI-BETI':  {'gamma': 0.02875, 'K': 0.34, 'color': '#ff6b9d'}
}

plt.style.use('dark_background')
SPACE_BG = "#0a0e1a"

col1, col2 = st.columns(2)
with col1:
    rc_um = st.slider("Emitter tip radius (micrometers)", 2, 30, 10)
with col2:
    d_mm = st.slider("Electrode gap (mm)", 0.5, 5.0, 2.0)

rc = rc_um * 1e-6
d = d_mm * 1e-3

names = list(propellants.keys())
volts = [onset_voltage(propellants[n]['gamma'], rc, d) / 1000 for n in names]
colors = [propellants[n]['color'] for n in names]

st.subheader("Predicted onset voltage by propellant")
fig, ax = plt.subplots(facecolor=SPACE_BG)
ax.set_facecolor(SPACE_BG)
ax.bar(names, volts, color=colors, edgecolor="white", linewidth=0.6)
ax.set_ylabel("Onset voltage (kV)")
ax.set_ylim(0, 6)
ax.yaxis.set_major_locator(MultipleLocator(0.5))
ax.yaxis.set_minor_locator(AutoMinorLocator(5))
ax.yaxis.set_major_formatter('{x:.1f}')
ax.grid(axis='y', which='major', linestyle='-', alpha=0.25, color="#4fd1ff")
ax.grid(axis='y', which='minor', linestyle=':', alpha=0.12, color="#4fd1ff")
for spine in ax.spines.values():
    spine.set_color("#2a3550")
st.pyplot(fig)

st.subheader("Model inputs and predictions")
table_data = {
    "Propellant": names,
    "Surface tension (N/m)": [propellants[n]['gamma'] for n in names],
    "Conductivity (S/m)": [propellants[n]['K'] for n in names],
    "Predicted onset voltage (kV)": [round(v, 3) for v in volts]
}
st.dataframe(pd.DataFrame(table_data), use_container_width=True)

st.subheader("Onset voltage vs tip radius (log-log)")
radii_um = np.logspace(np.log10(2), np.log10(30), 300)

fig2, ax2 = plt.subplots(facecolor=SPACE_BG)
ax2.set_facecolor(SPACE_BG)
for name in names:
    props = propellants[name]
    v_sweep = [onset_voltage(props['gamma'], r * 1e-6, d) / 1000 for r in radii_um]
    ax2.loglog(radii_um, v_sweep, label=name, color=props['color'], linewidth=2.2)
ax2.set_xlabel("Tip radius (micrometers)")
ax2.set_ylabel("Onset voltage (kV)")
ax2.legend(facecolor=SPACE_BG, edgecolor="#2a3550", labelcolor="white")
ax2.grid(True, which="major", linestyle="--", alpha=0.3, color="#4fd1ff")
ax2.grid(True, which="minor", linestyle=":", alpha=0.15, color="#4fd1ff")
for spine in ax2.spines.values():
    spine.set_color("#2a3550")
st.pyplot(fig2)

st.markdown("---")
st.subheader("Model validation against published data")
st.write("Enter a measured onset voltage from a literature source to check how well the model predicts real experimental results.")

val_col1, val_col2 = st.columns(2)
with val_col1:
    validation_liquid = st.selectbox("Propellant to validate", names)
with val_col2:
    published_v = st.number_input("Published onset voltage (kV)", min_value=0.0, value=0.0, step=0.1)

predicted_v = volts[names.index(validation_liquid)]

if published_v > 0:
    error_pct = abs(predicted_v - published_v) / published_v * 100
    st.metric(
        label=f"{validation_liquid}: predicted vs published",
        value=f"{predicted_v:.2f} kV",
        delta=f"{error_pct:.1f}% from published {published_v:.2f} kV"
    )
    if error_pct < 15:
        st.success("Prediction within 15 percent of published value. Model treated as validated for this regime.")
    else:
        st.warning("Prediction differs from published value by more than 15 percent. Geometry assumptions or property values may need review before treating this as validated.")
else:
    st.info("Enter a published onset voltage above to run the validation check.")

st.markdown("---")
st.caption(
    "Propellant properties: Garoz et al., Taylor cones of ionic liquids from capillary tubes as sources of pure ions, "
    "Journal of Applied Physics 102, 064913 (2007), Table I. "
    "Onset voltage model: Taylor cone equilibrium, G.I. Taylor, Proceedings of the Royal Society A 280, 383 to 397, 1964, "
    "combined with a capillary electrode field approximation."
)
st.caption("FALAK Aerospace and Engineering Program")

st.markdown("---")
st.header("Molecular dynamics: EMIM-BF4 bulk liquid")
st.write(
    "Below is real GROMACS output from an EMIM-BF4 simulation box "
    "(500 EMIM+ / 500 BF4- ions, 12000 atoms), built from the OPLS-AA "
    "ionic liquid force field (Doherty et al. 2017), packed with Packmol, "
    "energy minimized, then equilibrated at 298.15 K and 1 bar."
)

NPT_TIME_PS = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.4, 1.6, 1.8, 2.0, 2.2, 2.4, 2.6, 2.8, 3.0, 3.2, 3.4, 3.6, 3.8, 4.0, 4.2, 4.4, 4.6, 4.8, 5.0, 5.2, 5.4, 5.6, 5.8, 6.0, 6.2, 6.4, 6.6, 6.8, 7.0, 7.2, 7.4, 7.6, 7.8, 8.0, 8.2, 8.4, 8.6, 8.8, 9.0, 9.2, 9.4, 9.6, 9.8, 10.0, 10.2, 10.4, 10.6, 10.8, 11.0, 11.2, 11.4, 11.6, 11.8, 12.0, 12.2, 12.4, 12.6, 12.8, 13.0, 13.2, 13.4, 13.6, 13.8, 14.0, 14.2, 14.4, 14.6, 14.8, 15.0, 15.2, 15.4, 15.6, 15.8, 16.0, 16.2, 16.4, 16.6, 16.8, 17.0, 17.2, 17.4, 17.6, 17.8, 18.0, 18.2, 18.4, 18.6, 18.8, 19.0, 19.2, 19.4, 19.6, 19.8, 20.0]

NPT_DENSITY_KGM3 = [1280.24, 1262.41, 1252.71, 1248.5, 1228.4, 1223.77, 1227.59, 1219.08, 1229.98, 1229.55, 1219.89, 1231.31, 1224.45, 1220.16, 1226.13, 1216.57, 1214.45, 1220.29, 1208.12, 1214.88, 1215.31, 1209.22, 1217.78, 1214.93, 1209.42, 1219.02, 1215.14, 1213.81, 1223.61, 1219.25, 1223.96, 1222.44, 1219.16, 1219.66, 1220.86, 1211.01, 1215.02, 1216.24, 1209.39, 1212.9, 1216.46, 1208.36, 1217.83, 1211.24, 1210.92, 1215.1, 1208.77, 1207.08, 1212.71, 1209.73, 1214.02, 1214.52, 1216.82, 1216.42, 1219.21, 1211.23, 1216.56, 1217.63, 1211.17, 1214.51, 1216.67, 1207.85, 1213.45, 1211.1, 1208.58, 1211.38, 1216.86, 1211.87, 1219.36, 1218.82, 1216.6, 1215.48, 1214.02, 1218.02, 1212.06, 1215.36, 1219.36, 1210.24, 1215.84, 1213.28, 1202.55, 1210.47, 1210.07, 1201.98, 1212.32, 1217.43, 1207.07, 1213.9, 1215.04, 1210.6, 1209.54, 1215.98, 1211.69, 1213.59, 1212.19, 1215.89, 1212.56, 1217.41, 1215.87, 1217.82, 1220.32]

NPT_TEMPERATURE_K = [298.55, 295.13, 294.1, 296.58, 295.65, 299.07, 298.99, 295.74, 299.0, 300.27, 298.26, 295.4, 297.15, 298.04, 300.26, 304.04, 297.14, 300.86, 297.29, 302.23, 302.09, 297.3, 295.73, 296.93, 294.01, 295.44, 296.5, 292.8, 297.83, 296.31, 299.65, 301.36, 303.3, 297.46, 294.33, 295.34, 297.08, 302.4, 294.97, 300.21, 299.71, 297.42, 298.52, 299.81, 295.54, 296.0, 294.98, 295.09, 294.69, 299.87, 300.5, 298.47, 294.36, 299.55, 298.4, 297.9, 298.62, 301.54, 300.38, 300.87, 302.49, 301.58, 299.21, 298.97, 300.75, 295.01, 301.09, 299.59, 298.53, 299.76, 298.56, 297.81, 298.45, 298.81, 300.82, 301.68, 300.8, 297.96, 298.57, 303.64, 300.79, 296.07, 295.67, 300.41, 295.68, 299.97, 296.96, 297.51, 294.24, 298.75, 299.49, 300.4, 293.93, 298.65, 296.98, 299.48, 294.6, 297.05, 299.55, 297.92, 299.79]

density_mean = sum(NPT_DENSITY_KGM3) / len(NPT_DENSITY_KGM3)
temp_mean = sum(NPT_TEMPERATURE_K) / len(NPT_TEMPERATURE_K)
literature_density = 1240.0
density_error_pct = abs(density_mean - literature_density) / literature_density * 100

col1, col2, col3 = st.columns(3)
col1.metric("Simulated density (mean)", f"{density_mean:.1f} kg/m3")
col2.metric("Simulated temperature (mean)", f"{temp_mean:.1f} K", delta="target 298.15 K")
col3.metric("Density vs literature", f"{density_error_pct:.1f}% difference", delta=f"lit. value {literature_density:.0f} kg/m3")

fig3, ax3 = plt.subplots(facecolor=SPACE_BG)
ax3.set_facecolor(SPACE_BG)
ax3.plot(NPT_TIME_PS, NPT_DENSITY_KGM3, color="#4fd1ff", linewidth=1.5)
ax3.axhline(y=literature_density, linestyle="--", color="white", linewidth=1, label=f"Literature ({literature_density:.0f} kg/m3)")
ax3.set_xlabel("Time (ps)")
ax3.set_ylabel("Density (kg/m3)")
ax3.legend(facecolor=SPACE_BG, edgecolor="#2a3550", labelcolor="white")
for spine in ax3.spines.values():
    spine.set_color("#2a3550")
st.pyplot(fig3)
st.caption("NPT density relaxing from the initial packed value toward equilibrium. Run length: 20 ps (demonstration scale, not production length).")

fig4, ax4 = plt.subplots(facecolor=SPACE_BG)
ax4.set_facecolor(SPACE_BG)
ax4.plot(NPT_TIME_PS, NPT_TEMPERATURE_K, color="#ff9d5c", linewidth=1.5)
ax4.axhline(y=298.15, linestyle="--", color="white", linewidth=1, label="Target (298.15 K)")
ax4.set_xlabel("Time (ps)")
ax4.set_ylabel("Temperature (K)")
ax4.legend(facecolor=SPACE_BG, edgecolor="#2a3550", labelcolor="white")
for spine in ax4.spines.values():
    spine.set_color("#2a3550")
st.pyplot(fig4)
st.caption("NPT temperature held at target throughout the run by the thermostat.")

st.caption(
    "Simulation details: OPLS-AA ionic liquid force field, Doherty et al., "
    "J. Chem. Theory Comput. 2017, 13, 6131-6145, parameters from "
    "github.com/orlandoacevedo/IL. Box built with Packmol, run with GROMACS "
    "2023.3. Literature density: Garoz et al., J. Appl. Phys. 102, 064913 (2007)."
)
st.markdown("---")
st.header("GROMACS pipeline: EMIM-BF4 bulk liquid build")
st.write("Summary of the actual pipeline run to build and equilibrate this system.")

pipeline_steps = [
    ("Step 6: Topology",
     "OPLS-AA bonded and nonbonded parameters (Doherty et al. 2017) assembled into a GROMACS .top file for EMIM+ and BF4-.",
     "19 EMIM atoms, 5 BF4 atoms, 500/500 molecule counts, zero invented parameters"),
    ("Step 7: Coordinates",
     "500 EMIM+ and 500 BF4- ions packed into a cubic box with Packmol, using published PDB ion structures.",
     "12,000 atoms, 5.045 nm cube, box volume 128.41 nm3 (target from density calc: 128.43 nm3)"),
    ("Step 8: Energy minimization",
     "Steepest-descent minimization to remove packing strain before dynamics.",
     "Converged in 1015 steps, potential energy -80,974 kJ/mol"),
    ("Step 9: NVT/NPT equilibration",
     "20 ps NVT then 20 ps NPT at 298.15 K and 1 bar (demonstration-scale, not production length).",
     "Density 1217.3 kg/m3 (1.8% from literature 1240 kg/m3), temperature 298.27 K")
]

for title, desc, result in pipeline_steps:
    with st.expander(title):
        st.write(desc)
        st.markdown(f"**Result:** {result}")

st.markdown("---")
st.header("3D structure: simulated EMIM-BF4 box")
st.write(
    "This renders the actual equilibrated simulation box after Steps 6-9, "
    "directly from the GROMACS coordinate file (not a stock image)."
)

try:
    import py3Dmol
    from stmol import showmol

    with open("md/gromacs/npt.gro") as f:
        gro_lines = f.readlines()

    n_pairs_to_show = st.slider("Number of ion pairs to display", 10, 500, 100)

    title_line = gro_lines[0]
    n_atoms_total = int(gro_lines[1].strip())
    atom_lines = gro_lines[2:2 + n_atoms_total]
    box_line = gro_lines[2 + n_atoms_total]

    emim_atoms = atom_lines[:500 * 19]
    bf4_atoms = atom_lines[500 * 19:500 * 19 + 500 * 5]

    subset_emim = emim_atoms[:n_pairs_to_show * 19]
    subset_bf4 = bf4_atoms[:n_pairs_to_show * 5]
    subset_atoms = subset_emim + subset_bf4

    mini_gro = title_line + f"{len(subset_atoms)}\n" + "".join(subset_atoms) + box_line

    view = py3Dmol.view(width=700, height=450)
    view.addModel(mini_gro, "gro")
    view.setStyle({"stick": {"radius": 0.15}})
    view.setBackgroundColor("#0a0e1a")
    view.zoomTo()
    showmol(view, height=450, width=700)

    st.caption(f"Showing {n_pairs_to_show} of 500 ion pairs from the actual equilibrated box (npt.gro).")

except FileNotFoundError:
    st.warning("npt.gro not found at md/gromacs/npt.gro in the repo. Upload it there to enable this view.")
except ImportError:
    st.warning("stmol and py3Dmol not installed. Check requirements.txt was updated and redeployed.")
