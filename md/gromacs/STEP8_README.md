# Step 8 — Energy minimization

## What was done

The Packmol-packed box from Step 7 (emim_bf4_box.gro, 12,000 atoms,
500 EMIM+ / 500 BF4-) was energy-minimized using GROMACS steepest-descent
minimization to remove the residual atomic strain that packing alone
cannot fully resolve (Packmol only guarantees no hard overlaps, not a
low-energy configuration).

## Method

- Integrator: steep (steepest descent)
- Tolerance (Fmax): 500 kJ/mol/nm
- Max steps: 5000
- Cutoffs: 1.2 nm (Coulomb and van der Waals, plain cutoff -- adequate for
  minimization; production runs should switch to PME electrostatics)
- Same topology (EMIM_BF4.top) and force field as Steps 6-7, unchanged

## Result

- Converged to Fmax < 500 in 1015 steps (did not need the full 5000)
- Potential energy: -80,973.9 kJ/mol (started around -51,548 kJ/mol after
  a shorter first attempt at looser tolerance -- the drop confirms real
  relaxation, not a fluke)
- Output structure: emim_bf4_minimized.gro, same 12,000 atoms, same box,
  relaxed positions

## What this does and doesn't prove

Energy minimization only confirms the structure is now in a local energy
minimum given the force field -- it removes unphysical strain from the
packing process. It does NOT mean the liquid is equilibrated, does NOT
give a meaningful density yet (the box size is still fixed at the Step 7
estimate), and does NOT give meaningful dynamics. Temperature and pressure
equilibration (Step 9, NVT then NPT) is what actually lets the system find
its real density and relax into a genuine liquid structure. Treat this
minimized box as a clean starting point for Step 9, nothing more.
