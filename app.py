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
