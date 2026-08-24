# FALAK EMIM-BF4 Force Field

## Purpose

This directory contains the molecular mechanics force-field
files used by the FALAK electrospray molecular-dynamics model.

The initial FALAK system is:

    1-ethyl-3-methylimidazolium tetrafluoroborate

    EMIM+ + BF4-

The force-field basis is the OPLS-2009IL ionic-liquid force field
and the subsequent 0.8-scaled parameter set described by:

Doherty, B.; Zhong, X.; Gathiaka, S.; Li, B.; Acevedo, O.
"Revisiting OPLS Force Field Parameters for Ionic Liquid Simulations."
J. Chem. Theory Comput. 2017, 13, 6131-6145.

Official parameter repository:

https://github.com/orlandoacevedo/IL

## IMPORTANT

Do not manually invent or modify:

- atomic charges
- Lennard-Jones parameters
- bond parameters
- angle parameters
- dihedral parameters
- improper parameters

unless the modification is explicitly documented.

## FALAK policy

All force-field parameters must be traceable to:

1. the published force-field source,
2. the thesis being reproduced,
3. or a documented FALAK modification.

## Initial target

The first computational target is reproduction of the
EMIM-BF4 bulk-liquid validation before electric-field
fragmentation simulations are attempted.

Target validation quantities include:

- density
- radial distribution functions
- self-diffusion
- ionic conductivity

Only after the bulk model is validated should the
fragmentation simulations be used.

## Simulation hierarchy

EMIM-BF4 bulk liquid
        |
        v
electric-field emission
        |
        v
ion clusters
        |
        +--> positive dimer
        |
        +--> positive trimer
        |
        +--> negative dimer
        |
        +--> negative trimer
        |
        v
fragmentation statistics
        |
        v
RPA model
