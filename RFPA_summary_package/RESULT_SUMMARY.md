# GF180MCU-D RFPA Result Summary

This package keeps only the RFPA netlists, simulation results, and Xschem/ngspice verification files.

## Original Run Spec

- Process: `GF180MCU-D`
- Design scope: on-chip core only
- Frequency: `250 MHz`
- Supply: `VDD = 3.3 V`
- Load: `50 ohm`
- Target output power: `2 mW`
- Max DC current: `10 mA`
- Max output peak current: `10 mA`
- Starting topologies: `class_ab_single_ended`, `two_stage_single_ended`
- CircuitCollector API: `http://127.0.0.1:8001/simulate/`
- S11/S22 treatment: rough current-testbench estimates only, not signoff
- GF180 gm/ID LUT treatment: typical/25C first-pass sizing guidance only

## Preflight

For `2 mW` delivered into `50 ohm`:

- Required output voltage is about `0.316 Vrms`
- Required output voltage peak is about `0.447 Vpk`
- Ideal output peak current is about `8.94 mA`

The target is feasible at `VDD = 3.3 V`, but the output peak-current margin is tight because the ideal load current is already close to the `10 mA` limit.

## Topology Decision

Two topologies were simulated:

- `class_ab_single_ended`
- `two_stage_single_ended`

The Class-AB candidate met nominal Pout and current limits, but its rough small-signal stability estimate was poor (`K ~= 0.176`, `mu ~= 0.690`). The two-stage candidate met Pout/current and had much better rough stability (`K ~= 3.82`, `mu ~= 1.50`), so the selected result uses `two_stage_single_ended`.

## Selected Candidate

Topology: `two_stage_single_ended`

Sizing and drive:

- `rf_input_vpk = 0.118`
- Driver NMOS: `l=0.28u`, `w=3.36u`, `m=20`
- Output NMOS: `l=0.28u`, `w=7.56u`, `m=80`
- Driver current source: `0.8mA`
- Output current source: `8mA`
- `VDD = 3.3V`, `f0 = 250MHz`, `Rload = 50ohm`

Final selected metrics:

| Metric | Value |
| --- | ---: |
| `pout_w` | `2.118657e-03 W` |
| `pout_dbm` | `3.260607 dBm` |
| `idc_total` | `8.8e-03 A` |
| `pdc_w` | `2.904e-02 W` |
| `gain_db` | `17.84357 dB` |
| `pae` | `7.175783 %` |
| `drain_efficiency` | `7.295652 %` |
| `iout_rms` | `6.509466e-03 A` |
| `iout_pk_est` | `9.238073e-03 A` |
| `h2_dbc` | `-28.98179 dBc` |
| `h3_dbc` | `-33.69711 dBc` |
| rough `stability_k` | `3.821117` |
| rough `stability_mu` | `1.497428` |

S11/S22 are rough current-testbench estimates, not signoff.

## Pass / Fail Against Active Core Targets

| Requirement | Result | Status |
| --- | ---: | --- |
| `Pout >= 2 mW` | `2.118657 mW` | PASS |
| `Idc_total <= 10 mA` | `8.8 mA` | PASS |
| `Iout_pk_est <= 10 mA` | `9.238073 mA` | PASS |
| `H2/H3 < -25 dBc` | `-28.98 / -33.70 dBc` | PASS |
| rough `K > 1`, `mu > 1` | `3.82 / 1.50` | PASS |

## Main Caveats

- This is not layout, passive, EM, package, or final reference-plane signoff.
- S11/S22 are rough estimates from the current CircuitCollector testbench.
- The selected two-stage backend still uses ideal drain-bias current sources.
- Compression, AM-AM, and AM-PM were not proven by the current backend path.
- The Xschem folder is netlist-only; it is not an editable `.sch` schematic.

## Important Files

### Final Selected Two-Stage Result

- Source template: `source_templates/two_stage_single_ended/netlist.j2`
- Source config: `source_templates/two_stage_single_ended/two_stage_single_ended.toml`
- Rendered full SPICE deck: `results/selected/two_stage_single_ended/two_stage_single_ended_circuit.cir`
- Rendered PA subcircuit: `results/selected/two_stage_single_ended/temp_circuit_params.txt`
- DC result: `results/selected/two_stage_single_ended/two_stage_single_ended_DC.txt`
- Large-signal result: `results/selected/two_stage_single_ended/two_stage_single_ended_LARGE_SIGNAL.txt`
- Rough S-parameter output: `results/selected/two_stage_single_ended/two_stage_single_ended_SPARAM.txt`
- ngspice log: `results/selected/two_stage_single_ended/two_stage_single_ended.log`

### Class-AB Comparison Result

- Source template: `source_templates/class_ab_single_ended/netlist.j2`
- Source config: `source_templates/class_ab_single_ended/class_ab_single_ended.toml`
- Rendered full SPICE deck: `results/comparison/class_ab_single_ended/class_ab_single_ended_circuit.cir`
- Rendered PA subcircuit: `results/comparison/class_ab_single_ended/temp_circuit_params.txt`
- DC result: `results/comparison/class_ab_single_ended/class_ab_single_ended_DC.txt`
- Large-signal result: `results/comparison/class_ab_single_ended/class_ab_single_ended_LARGE_SIGNAL.txt`
- Rough S-parameter output: `results/comparison/class_ab_single_ended/class_ab_single_ended_SPARAM.txt`
- ngspice log: `results/comparison/class_ab_single_ended/class_ab_single_ended.log`

Class-AB comparison metrics:

| Metric | Value |
| --- | ---: |
| `pout_w` | `2.154057e-03 W` |
| `pout_dbm` | `3.332571 dBm` |
| `idc_total` | `1.0e-02 A` |
| `iout_pk_est` | `9.351648e-03 A` |
| `gain_db` | `12.33256 dB` |
| `pae` | `6.145951 %` |
| rough `stability_k` | `0.176095` |
| rough `stability_mu` | `0.689964` |

## Sweep Outputs

The bounded iteration sweep outputs are still copied under:

```text
results/sweeps/
```

Each sweep case folder contains its rendered deck, config, DC result, large-signal result, rough S-parameter result, and ngspice log.

## Xschem / ngspice Folder

Use:

```text
xschem/
```

Important files:

- `xschem/two_stage_single_ended_subckt.spice`: selected PA subcircuit.
- `xschem/two_stage_single_ended_tb.spice`: simple transient verification deck.
- `xschem/two_stage_single_ended_full_generated.cir`: exact CircuitCollector-generated final deck.
- `xschem/README.md`: instructions and Xschem caveat.

Xschem note: this is netlist-only material. It can be included/simulated from Xschem or run directly with ngspice, but it is not an editable Xschem `.sch` schematic.

Quick verification:

```sh
cd xschem
ngspice -b two_stage_single_ended_tb.spice
```
