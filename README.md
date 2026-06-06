# GF180MCU-D RF Power Amplifier Skill

This is a shareable LLM/AI-agent skill bundle for GF180MCU-D RF power amplifier
design. It combines RFPA design guidance with a CircuitCollector/ngspice
simulation backend.

The intended workflow is simple: open the setup notebook locally, connect it to
the IIC-OSIC-TOOLS container's Jupyter kernel, run the notebook, then ask your
agent to design and review the RFPA using the running API.

## Quick Start

1. Start the IIC-OSIC-TOOLS Docker/Jupyter environment.

2. Place this folder under the host designs directory:

```text
/Users/<user_name>/eda/designs/share_RFPA
```

The container should see it at:

```text
/foss/designs/share_RFPA
```

3. Open this notebook from your local file browser:

```text
share_RFPA/notebooks/setup_and_run_rfpa_gf180mcuD.ipynb
```

4. Connect the notebook to the container's Jupyter kernel.

5. Run the notebook cells in order. The notebook links the GF180 PDK, installs
CircuitCollector in the container Python environment, starts the API, checks
`/health`, and runs an RFPA smoke test.

6. After the notebook reports a healthy API, open your coding agent from the
`share_RFPA` folder and give it the prompt below.

## Agent Prompt

Use this as a compact starting prompt:

```text
I want to design and review a GF180MCU-D RF power amplifier.

Container: <container_id_or_name>
CircuitCollector API: http://localhost:8001/simulate/

Run all simulations in the container environment. Do not run ngspice or
CircuitCollector from the host Python environment.

Use this nominal starting spec:
- Design scope: on-chip core only
- Process: GF180MCU-D
- VDD: 3.3 V
- f0: 250 MHz
- Load: 50 ohm
- Target Pout: 2 mW
- PA_class: auto
- Max DC power: 33 mW
- Max total DC current: 10 mA
- Max output RMS current: 10 mA
- Max output peak current: 10 mA
- Max device voltage: 3.3 V
- Passive scope: finite-Q schematic passives only; no EM/layout signoff
```

If the agent is already running inside the container-backed notebook
environment, the container ID is just a note; the API URL and container-visible
path are the important handles.

## Environment

This bundle was tested with the IEEE SSCS Chipathon IIC-OSIC-TOOLS
Docker/Jupyter environment:

```text
https://github.com/sscs-ose/sscs-chipathon-2026/tree/main/resources/IIC-OSIC-TOOLS
```

That environment mounts the host designs directory into the container. This is
why `/Users/<user_name>/eda/designs/share_RFPA` appears as
`/foss/designs/share_RFPA` from the connected notebook kernel.

## What's Included

- `AnalogAgent/skills/rf-power-amplifier/`: RFPA design workflow, GF180 process
  notes, topology guidance, backend adapter, and helper scripts.
- `AnalogAgent/rf-pa-spec-form-template.md`: full RFPA spec template.
- `AnalogAgent/rf-pa-onchip-core-spec-form-template.md`: on-chip-core spec
  template.
- `CircuitCollector/`: FastAPI simulation service and CircuitCollector Python
  package.
- `CircuitCollector/CircuitCollector/config/gf180mcuD/rfpa/`: RFPA TOML
  configs.
- `CircuitCollector/CircuitCollector/circuits/rfpa/`: RFPA netlist templates.
- `CircuitCollector/CircuitCollector/spec_lib/rfpa/`: RFPA testbench templates.
- `notebooks/setup_and_run_rfpa_gf180mcuD.ipynb`: setup and smoke-test
  notebook.

The GF180 PDK is not included. The setup notebook links the container's PDK into:

```text
/foss/designs/share_RFPA/CircuitCollector/CircuitCollector/PDK/gf180mcuD
```

## Notebook Notes

The first setup cell prints:

```text
kernel cwd
share root
CircuitCollector repo
RFPA skill root
```

The share root should resolve to:

```text
/foss/designs/share_RFPA
```

If it does not, set `SHARE_ROOT` manually in the first setup cell:

```python
SHARE_ROOT = Path("/foss/designs/share_RFPA")
```

The PDK cell auto-detects common IIC-OSIC-TOOLS locations such as:

```text
/foss/pdks/ciel/gf180mcu/versions/*/gf180mcuD
```

If auto-detection fails, set `PDK_SRC` manually in the first setup cell:

```python
PDK_SRC = Path("/container/path/to/gf180mcuD")
```

A valid PDK path must contain:

```text
libs.tech/ngspice/design.ngspice
libs.tech/ngspice/sm141064.ngspice
```

Before starting a fresh API, the notebook stops old uvicorn processes whose
command line contains `CircuitCollector.api.main:app`. This avoids stale
CircuitCollector servers from previous notebooks.

## Optional Checks

Backend coverage:

```bash
cd /foss/designs/share_RFPA/AnalogAgent
python3 skills/rf-power-amplifier/scripts/check_backend_coverage.py \
  --backend-root /foss/designs/share_RFPA/CircuitCollector/CircuitCollector
```

Quick RFPA smoke test:

```bash
cd /foss/designs/share_RFPA/AnalogAgent
python3 skills/rf-power-amplifier/scripts/smoke_test_backend.py \
  --backend-root /foss/designs/share_RFPA/CircuitCollector/CircuitCollector \
  --api-url http://localhost:8001/simulate/ \
  --quick \
  --topology two_stage_single_ended
```

Expected smoke-test behavior: at least `two_stage_single_ended` should run and
return parsed large-signal metrics such as `pout_w`, `pout_dbm`, `pdc_w`,
`idc_total`, `drain_efficiency`, `iout_rms`, and `iout_pk_est`.

## Troubleshooting

If the API is not healthy, inspect:

```text
/foss/designs/share_RFPA/circuitcollector_api.log
```

To manually stop old API servers in the container:

```bash
pgrep -af 'CircuitCollector.api.main:app'
pkill -f 'uvicorn.*CircuitCollector.api.main:app'
```

To verify the API:

```bash
curl http://localhost:8001/health
```

Expected response:

```json
{"status":"ok"}
```

## Notes

- Do not commit GF180 PDK contents into this folder.
- Some RFPA backend templates are idealized seeds. They are useful for topology
  exploration and API validation; final signoff still needs layout, passive, EM,
  and reference-plane closure appropriate to the design scope.

## Acknowledgements

This work is based on and extends the AnalogAgent/CircuitCollector flow from:

```text
https://github.com/jiyuanduan001-oss/LLM_Amplifier_Sizing
```

The original project provides the LLM-assisted analog sizing framework,
CircuitCollector FastAPI simulation backend, and procedural skill-stack
approach. The RFPA/GF180MCU-D files in this bundle adapt that flow for
on-chip-core RF power amplifier exploration.
