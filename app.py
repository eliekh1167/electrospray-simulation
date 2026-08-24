import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator, AutoMinorLocator

st.title("Electrospray onset voltage — propellant comparison")

eps0 = 8.854e-12
theta = np.radians(49.3)
cos_theta = np.cos(theta)

def onset_voltage(gamma, r_c, d):
    return np.sqrt((r_c * gamma * cos_theta) / (2 * eps0)) * np.log(4 * d / r_c)

propellants = {
    'EMI-BF4':   {'gamma': 0.0452,  'K': 1.4,  'color': '#2a78d6'},
    'EMI-GaCl4': {'gamma': 0.0486,  'K': 2.2,  'color': '#1baf7a'},
    'EMI-Tf2N':  {'gamma': 0.0349,  'K': 0.88, 'color': '#eb6834'},
    'EMI-BETI':  {'gamma': 0.02875, 'K': 0.34, 'color': '#eda100'}
}

rc_um = st.slider("Tip radius (µm)", 2, 30, 10)
d_mm = st.slider("Electrode gap (mm)", 0.5, 5.0, 2.0)

rc = rc_um * 1e-6
d = d_mm * 1e-3

names = list(propellants.keys())
volts = [onset_voltage(propellants[n]['gamma'], rc, d) / 1000 for n in names]
colors = [propellants[n]['color'] for n in names]

# --- Bar chart, with fine-grained axis ---
fig, ax = plt.subplots()
ax.bar(names, volts, color=colors)
ax.set_ylabel("Onset voltage (kV)")
ax.set_ylim(0, 6)
ax.yaxis.set_major_locator(MultipleLocator(0.5))   # major tick every 0.5 kV
ax.yaxis.set_minor_locator(AutoMinorLocator(5))     # minor ticks between those
ax.yaxis.set_major_formatter('{x:.1f}')             # show one decimal, e.g. "2.5"
ax.grid(axis='y', which='major', linestyle='-', alpha=0.3)
ax.grid(axis='y', which='minor', linestyle=':', alpha=0.15)
st.pyplot(fig)

# --- Data table ---
st.subheader("Model inputs and predictions")
table_data = {
    "Propellant": names,
    "γ (N/m)": [propellants[n]['gamma'] for n in names],
    "K (S/m)": [propellants[n]['K'] for n in names],
    "Predicted onset V (kV)": [round(v, 3) for v in volts]
}
st.dataframe(pd.DataFrame(table_data))

# --- Log-log sensitivity plot, now with real smooth curves ---
st.subheader("Onset voltage vs. tip radius (log-log)")
radii_um = np.logspace(np.log10(2), np.log10(30), 300)  # 300 points = smooth curve, not a jagged line

fig2, ax2 = plt.subplots()
for name in names:
    props = propellants[name]
    v_sweep = [onset_voltage(props['gamma'], r * 1e-6, d) / 1000 for r in radii_um]
    ax2.loglog(radii_um, v_sweep, label=name, color=props['color'], linewidth=2)

ax2.set_xlabel("Tip radius (µm)")
ax2.set_ylabel("Onset voltage (kV)")
ax2.legend()
ax2.grid(True, which="major", linestyle="--", alpha=0.4)
ax2.grid(True, which="minor", linestyle=":", alpha=0.2)
st.pyplot(fig2)

# --- Sources ---
st.caption(
    "Propellant properties (γ, K): Garoz et al., "
    "\"Taylor cones of ionic liquids from capillary tubes as sources of pure ions,\" "
    "J. Appl. Phys. 102, 064913 (2007), Table I. "
    "Onset voltage model: Taylor cone equilibrium (G.I. Taylor, Proc. Roy. Soc. A 280, 383–97, 1964) "
    "combined with capillary-electrode field approximation."
)
