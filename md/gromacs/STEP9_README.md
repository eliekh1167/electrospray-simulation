# Step 9 — NVT and NPT equilibration

## What was done

Starting from the energy-minimized box (Step 8), two short equilibration
runs were performed with GROMACS:

1. NVT (constant volume, constant temperature): 20 ps, V-rescale
   thermostat, target 298.15 K, velocities generated from a Maxwell
   distribution at that temperature.
2. NPT (constant pressure, constant temperature): 20 ps, continued from
   the NVT run's final velocities, C-rescale barostat, target 1 bar,
   same thermostat settings.

Both runs used h-bond constraints (LINCS), a 2 fs timestep, and the same
EMIM_BF4.top topology from Steps 6-7, unchanged.

## Results

- NVT temperature: stable around 298.5-299.4 K throughout (target 298.15 K)
- NPT temperature: 298.27 K average (target 298.15 K) -- excellent agreement
- NPT density: 1217.3 kg/m^3 average, compared to the literature EMIM-BF4
  density of ~1240 kg/m^3 (Garoz et al. 2007) -- about 1.8% difference
- NPT pressure: 199 bar average with large fluctuation (RMSD ~1061 bar) --
  expected for a run this short; pressure converges much more slowly than
  density or temperature in NPT equilibration

## Honest limitations

This is a demonstration-scale equilibration (20 ps each stage), not a
production-length one. The Acevedo group's own tutorial for the sibling
[BMIM][BF4] system used a 40 ns production run -- roughly 2000x longer than
what was run here. The density agreement (1.8%) is a genuinely encouraging
sign that the topology and force field are behaving correctly, but it
should not be reported as a converged or publication-grade result. The
pressure has clearly not equilibrated yet, and running longer (at minimum
low nanoseconds) would be needed before treating this box as production-
ready for Step 10's fuller validation (radial distribution functions,
self-diffusion, ionic conductivity) or for any Step 11 cluster analysis.

## Files

- nvt.mdp / nvt.gro / nvt.log -- NVT stage inputs and outputs
- npt.mdp / npt.gro / npt.log -- NPT stage inputs and outputs
- density.xvg / temperature.xvg / pressure.xvg -- extracted time series
  from the NPT run (gmx energy output)
