import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

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

fig, ax = plt.subplots()
ax.bar(names, volts, color=colors)
ax.set_ylabel("Onset voltage (kV)")
st.pyplot(fig)

st.write("Data source: Garoz et al., J. Appl. Phys. 102, 064913 (2007)")
