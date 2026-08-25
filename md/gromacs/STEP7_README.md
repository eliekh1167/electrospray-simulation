# Step 7 — EMIM-BF4 initial coordinates

## What's in this folder

- `emim_bf4_box.gro` — GROMACS coordinate file: 500 EMIM+ and 500 BF4- ions
  packed into a 5.045 nm cube (12,000 atoms total), matching the 500/500
  molecule counts already specified in EMIM_BF4.top.
- `EMIM.pdb`, `BF4.pdb` — the individual ion structures this box was built
  from, sourced unmodified from github.com/orlandoacevedo/IL (PDB/ folder).
- `pack_emim_bf4.inp` — the exact Packmol input script used to build the box,
  included so the box generation is fully reproducible from source files,
  not a black box.

## How the box size was chosen

500 ion pairs x 197.995 g/mol (EMI+ = 111.192, BF4- = 86.803) at the
literature EMIM-BF4 density of 1.28 g/cm3 (Garoz et al. 2007) gives a target
volume of 128.43 nm^3, i.e. a 5.045 nm cube. This was verified against the
actual packed box: gmx editconf reports a final box volume of 128.41 nm^3,
matching the calculation.

## How this was verified

The resulting emim_bf4_box.gro was tested against md/gromacs/EMIM_BF4.top
using `gmx grompp` with a minimal energy-minimization .mdp. It completed with
zero errors (two standard advisory notes only, about Verlet list frequency
and electrostatics method), confirming the topology and coordinate file are
mutually consistent -- 12,000 atoms in both, same molecule order (EMI first,
then BF4).

## Where this box is NOT yet valid

This is a freshly packed box, not an equilibrated liquid. Packmol only
guarantees no atomic overlaps -- it says nothing about correct density,
correct energy, or correct liquid structure. That is exactly what Steps 8
(energy minimization) and 9 (NVT/NPT equilibration) are for. Do not treat
any property measured from this raw box (density, RDFs, etc.) as
meaningful yet.
