# Xschem Netlist Package

This folder is grouped for Xschem/ngspice verification of the selected RFPA.

## What is here

- `two_stage_single_ended_subckt.spice`: selected PA subcircuit.
- `two_stage_single_ended_tb.spice`: simple transient verification deck using the local GF180MCU-D PDK path.
- `two_stage_single_ended_full_generated.cir`: exact CircuitCollector-generated deck from the final-selected run.

## Can Xschem open it as a schematic?

Not directly. CircuitCollector generated SPICE, not an Xschem `.sch` schematic.
Xschem can include and simulate these netlists, but it will not reverse-convert
the SPICE into an editable schematic drawing automatically.

For a true editable view, the next step is to create an Xschem `.sch` manually
using GF180 symbols and attach the same values:

- driver NMOS: `l=0.28u`, `w=3.36u`, `m=20`
- output NMOS: `l=0.28u`, `w=7.56u`, `m=80`
- driver current source: `0.8mA`
- output current source: `8mA`
- `CIN=2pF`, `CINTER=2pF`, `RGOUT=10ohm`
- output network/traps as listed in `two_stage_single_ended_subckt.spice`

## Quick ngspice check

From this folder:

```sh
ngspice two_stage_single_ended_tb.spice
```

The deck uses this PDK path:

```text
/Users/tkong/Documents/GitHub/RFPA/CircuitCollector/CircuitCollector/PDK/gf180mcuD
```
