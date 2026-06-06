# GF180MCU-D RF Power Amplifier Skill

This folder is a shareable RF power amplifier design bundle for GF180MCU-D. It
is intended for the workflow where the repository is visible on the host, but
the notebook kernel is connected to the IIC-OSIC-TOOLS Docker container.

## Expected Workflow

1. Start the IIC-OSIC-TOOLS Docker/Jupyter environment.
2. Copy or place this folder directly under the mounted designs directory on the host, for example:

```text
/Users/<user_name>/eda/designs/share_RFPA
```

The IIC-OSIC-TOOLS container should then see the same folder through its mounted designs path, commonly:

```text
/foss/designs/share_RFPA
```

3. Open the setup notebook from that local folder.
4. Connect the notebook to the Jupyter kernel served by the Docker container.
5. Run the setup notebook. The code executes inside the container even though
   the files are visible locally.
6. The notebook starts and verifies the CircuitCollector API in the container.
7. Tell the agent to use this RFPA skill and to run simulations through the
   container environment/API.

The important point: place `share_RFPA` in the host designs directory that is
already mounted into the container. There is no separate container copy step.

## Environment

This bundle was tested with the IEEE SSCS Chipathon IIC-OSIC-TOOLS
Docker/Jupyter environment:

```text
https://github.com/sscs-ose/sscs-chipathon-2026/tree/main/resources/IIC-OSIC-TOOLS
```

That environment mounts the host designs directory into the container, which is
why placing this folder at `/Users/<user_name>/eda/designs/share_RFPA` makes it
available at `/foss/designs/share_RFPA` from the connected notebook kernel.

## Contents

- `AnalogAgent/skills/rf-power-amplifier/`: RFPA design workflow, topology
  guidance, GF180 process notes, backend adapter, and smoke-test scripts.
- `AnalogAgent/rf-pa-spec-form-template.md`: full RFPA spec template.
- `AnalogAgent/rf-pa-onchip-core-spec-form-template.md`: on-chip-core-focused
  spec template.
- `CircuitCollector/`: FastAPI simulation service and CircuitCollector Python
  package.
- `CircuitCollector/CircuitCollector/config/gf180mcuD/rfpa/`: RFPA TOML configs.
- `CircuitCollector/CircuitCollector/circuits/rfpa/`: RFPA netlist templates.
- `CircuitCollector/CircuitCollector/spec_lib/rfpa/`: RFPA testbench templates.
- `notebooks/setup_and_run_rfpa_gf180mcuD.ipynb`: RFPA-focused setup notebook.

The GF180 PDK is not included. It must be available inside the container and
linked at:

```text
/foss/designs/share_RFPA/CircuitCollector/CircuitCollector/PDK/gf180mcuD
```

## Path Mapping

There are two paths to keep straight:

```text
Host path:
/Users/<user_name>/eda/designs/share_RFPA

Container path:
/foss/designs/share_RFPA
```

Use the container path in commands that run from the notebook kernel, API, or
agent simulation tools. The host path is just where you browse and edit files.

In a notebook cell, confirm the container path with:

```python
from pathlib import Path
print(Path.cwd())
```

If the notebook is opened from `share_RFPA/notebooks`, the share root is usually:

```python
SHARE_ROOT = Path.cwd().parent
```

If the notebook starts from the repository root, use:

```python
SHARE_ROOT = Path.cwd() / "share_RFPA"
```

## Run the RFPA Setup Notebook

Open this notebook from the local file browser and connect it to the container
Jupyter kernel:

```text
share_RFPA/notebooks/setup_and_run_rfpa_gf180mcuD.ipynb
```

Before running all cells, update these values in the first setup cell if needed:

```python
SHARE_ROOT = Path.cwd().parent
PDK_SRC = None  # or Path("/container/path/to/gf180mcuD")
API_URL = "http://localhost:8001"
```

The first setup cell prints `kernel cwd`, `share root`, and `CircuitCollector
repo`. Check these before running the install cell. The CircuitCollector repo
should end with:

```text
share_RFPA/CircuitCollector
```

If it prints a path such as `/foss/designs/CircuitCollector`, the notebook
kernel started outside the repository and did not find `share_RFPA`. Set
`SHARE_ROOT` manually in the first setup cell to the container-visible path of
this folder, for example:

```python
SHARE_ROOT = Path("/foss/designs/share_RFPA")
```

The PDK cell auto-detects common IIC-OSIC-TOOLS locations such as
`/foss/pdks/ciel/gf180mcu/versions/*/gf180mcuD`. If auto-detection fails, set
`PDK_SRC` manually to the GF180MCU-D PDK path as seen inside the container. A
valid PDK link should make these files exist:

```text
CircuitCollector/CircuitCollector/PDK/gf180mcuD/libs.tech/ngspice/design.ngspice
CircuitCollector/CircuitCollector/PDK/gf180mcuD/libs.tech/ngspice/sm141064.ngspice
```

The notebook installs CircuitCollector in the container Python environment,
starts the FastAPI server, checks `/health`, and can run a quick RFPA smoke
test.

If the health check fails, inspect the printed `circuitcollector_api.log` tail.
The notebook starts the API with the active kernel Python executable, so rerun
the first setup cell and the install cell after changing kernels or restarting
Jupyter. Before starting a new server, the notebook stops old uvicorn processes
whose command line contains `CircuitCollector.api.main:app`, then starts a fresh
API on `127.0.0.1:8001`.

## Manual API Commands

Use these only if you want to do the notebook steps manually inside a container
terminal or notebook cell.

```bash
export SHARE_ROOT=<container path to share_RFPA>
export GF180_PDK=/path/to/gf180mcuD

cd "$SHARE_ROOT/CircuitCollector/CircuitCollector"
mkdir -p PDK
ln -sfn "$GF180_PDK" PDK/gf180mcuD
test -f PDK/gf180mcuD/libs.tech/ngspice/sm141064.ngspice
```

Install and start the API:

```bash
cd "$SHARE_ROOT/CircuitCollector"
python3 -m pip install -e . uvicorn httpx

export PATH=/foss/tools/ngspice/bin:/foss/tools/bin:$PATH
export LD_LIBRARY_PATH=/foss/tools/ngspice/lib:${LD_LIBRARY_PATH:-}
python3 -m uvicorn CircuitCollector.api.main:app --host 0.0.0.0 --port 8001
```

To manually stop old CircuitCollector API servers in the container:

```bash
pgrep -af 'CircuitCollector.api.main:app'
pkill -f 'uvicorn.*CircuitCollector.api.main:app'
```

Verify from the same container kernel or terminal:

```bash
curl http://localhost:8001/health
```

Expected response:

```json
{"status":"ok"}
```

## Check RFPA Backend Coverage

Run this inside the container environment:

```bash
cd "$SHARE_ROOT/AnalogAgent"
python3 skills/rf-power-amplifier/scripts/check_backend_coverage.py \
  --backend-root "$SHARE_ROOT/CircuitCollector/CircuitCollector"
```

This verifies that each RFPA topology has its expected TOML config and netlist
template.

## Run a Quick RFPA Smoke Test

With the API already running in the container:

```bash
cd "$SHARE_ROOT/AnalogAgent"
python3 skills/rf-power-amplifier/scripts/smoke_test_backend.py \
  --backend-root "$SHARE_ROOT/CircuitCollector/CircuitCollector" \
  --api-url http://localhost:8001/simulate/ \
  --quick \
  --topology two_stage_single_ended
```

To smoke test all RFPA topology configs, omit `--topology two_stage_single_ended`.

## Prompt the Agent

After the setup notebook confirms the API is healthy, tell the agent something
like this. Replace the placeholders with your active container and API details.
If your agent is already running inside the container-backed notebook
environment, the container ID can be left as a note rather than used directly.

```text
I want to design and review a GF180MCU-D RF power amplifier using this shared
RFPA bundle.

Container:
<container_id_or_name>

Container-visible share root:
/foss/designs/share_RFPA

CircuitCollector API:
http://localhost:8001/simulate/

Use the RFPA skill/docs and the local CircuitCollector GF180MCU-D backend from
this share root. Run all simulations in the container environment; do not run
ngspice or CircuitCollector from the host Python environment.

Nominal starting spec:
- Process: GF180MCU-D
- Device family: nfet_03v3 / pfet_03v3 as needed
- Design scope: on-chip core only
- Reference plane: schematic output node
- Passive scope: finite-Q schematic passives only; no EM/layout signoff
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

Please check backend coverage, run a quick smoke test, select a runnable local
topology, iterate sizing through the API if needed, and return an RF PA design
review with active pass/fail specs and residual risks.
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
