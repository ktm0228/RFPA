# RFPA Summary Package

This folder contains a compact summary package for the GF180MCU-D 250 MHz RFPA iteration.

Start here:

- `RESULT_SUMMARY.md`: selected metrics and exact file locations.
- `results/selected/two_stage_single_ended/`: final selected rendered SPICE deck and simulation outputs.
- `results/comparison/class_ab_single_ended/`: Class-AB comparison run.
- `results/sweeps/`: copied sweep outputs from the bounded iteration.
- `source_templates/`: original topology templates and configs copied for reference.
- `xschem/`: netlist-only Xschem/ngspice verification folder.

No waveform plot images, Jupyter visualization notebooks, or raw waveform dumps are included in this simplified package.

Reusable Codex skill installed at:

```text
~/.codex/skills/rfpa-summary-package
```

To regenerate this compact package from a future RFPA run:

```sh
python3 ~/.codex/skills/rfpa-summary-package/scripts/build_rfpa_summary_package.py
```
