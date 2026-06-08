#!/usr/bin/env python3
"""Build initial GF180MCU-D gm/ID LUT assets from Sizing backup sweeps.

The RFPA repo currently ships raw room-temperature, typical-corner ngspice
tech-sweep files under Sizing/backup.  AnalogAgent/scripts/lut_lookup.py
expects processed files under AnalogAgent/asset_gf180mcuD, so this script
bridges that gap.

This is a starting LUT, not a full PVT characterization:
  - corner: typical
  - temp: 25C
  - width: 5 um, matching the backup schematics
  - VDS slice: configurable, default 1.65 V
  - VSB branch: configurable, default near 0 V
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd


WIDTH_UM_DEFAULT = 5.0
DEVICE_MAP = {
    "nmos": ("nfet_03v3", "techsweep_gf180mcu_nmos_3v3.txt.gz"),
    "pmos": ("pfet_03v3", "techsweep_gf180mcu_pmos_3v3.txt.gz"),
}
OUTPUT_COLUMNS = [
    "gm_id",
    "gm_gds",
    "id_w",
    "ft",
    "cgg_w",
    "cgd_w",
    "cgs_w",
    "cdb_w",
    "vgs",
    "vth",
    "vdsat",
]


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def spice_col(df: pd.DataFrame, name: str) -> str:
    matches = [col for col in df.columns if f"[{name}]" in col]
    if not matches:
        raise KeyError(f"Column for [{name}] not found in sweep file")
    return matches[0]


def nearest(values: pd.Series, target: float) -> float:
    idx = (values - target).abs().argsort().iloc[0]
    return float(values.iloc[idx])


def build_device_luts(
    sweep_path: Path,
    output_root: Path,
    device: str,
    corner: str,
    temp: str,
    width_um: float,
    vds_target: float,
    vbs_target: float,
    vbs_tolerance: float,
) -> list[Path]:
    df = pd.read_csv(sweep_path, sep=r"\s+", compression="gzip")
    cols = {name: spice_col(df, name) for name in [
        "l", "vgs", "vds", "vbs", "vth", "vdsat",
        "id", "gm", "gds", "cgg", "cgd", "cgs", "cdd",
    ]}

    width_m = width_um * 1e-6
    out_dir = output_root / device / corner / temp / "processed"
    out_dir.mkdir(parents=True, exist_ok=True)

    written: list[Path] = []
    for length_m in sorted(df[cols["l"]].unique()):
        length_df = df[np.isclose(df[cols["l"]], length_m)]
        vds_selected = nearest(length_df[cols["vds"]], vds_target)
        slice_df = length_df[
            np.isclose(length_df[cols["vds"]], vds_selected, atol=1e-6)
            & ((length_df[cols["vbs"]] - vbs_target).abs() <= vbs_tolerance)
        ].copy()

        if slice_df.empty:
            continue

        id_abs = slice_df[cols["id"]].abs()
        gm_abs = slice_df[cols["gm"]].abs()
        gds_abs = slice_df[cols["gds"]].abs()
        cgg_abs = slice_df[cols["cgg"]].abs()

        valid = (id_abs > 0) & (gm_abs > 0) & (gds_abs > 0) & (cgg_abs > 0)
        slice_df = slice_df[valid].copy()
        if slice_df.empty:
            continue

        id_abs = slice_df[cols["id"]].abs()
        gm_abs = slice_df[cols["gm"]].abs()
        gds_abs = slice_df[cols["gds"]].abs()
        cgg_abs = slice_df[cols["cgg"]].abs()

        processed = pd.DataFrame(
            {
                "gm_id": gm_abs / id_abs,
                "gm_gds": gm_abs / gds_abs,
                "id_w": id_abs / width_m,
                "ft": gm_abs / (2.0 * np.pi * cgg_abs),
                "cgg_w": cgg_abs / width_m,
                "cgd_w": slice_df[cols["cgd"]].abs() / width_m,
                "cgs_w": slice_df[cols["cgs"]].abs() / width_m,
                "cdb_w": slice_df[cols["cdd"]].abs() / width_m,
                "vgs": slice_df[cols["vgs"]].abs(),
                "vth": slice_df[cols["vth"]].abs(),
                "vdsat": slice_df[cols["vdsat"]].abs(),
            }
        )
        processed = processed.replace([np.inf, -np.inf], np.nan).dropna()
        processed = processed.sort_values("vgs")

        length_nm = int(round(length_m * 1e9))
        out_path = out_dir / f"gmid_{device}_L{length_nm}n.txt"
        with out_path.open("w", encoding="utf-8") as file_obj:
            file_obj.write(
                "# Generated from Sizing/backup GF180MCU-D room-temp sweep\n"
                f"# source={sweep_path.name} corner={corner} temp={temp} "
                f"width_um={width_um:g} vds_selected={vds_selected:g} "
                f"vbs_target={vbs_target:g} vbs_tolerance={vbs_tolerance:g}\n"
                "# columns: "
                + " ".join(OUTPUT_COLUMNS)
                + "\n"
            )
            processed.to_csv(
                file_obj,
                sep=" ",
                header=False,
                index=False,
                float_format="%.9e",
                columns=OUTPUT_COLUMNS,
            )
        written.append(out_path)

    return written


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--sizing-root",
        type=Path,
        default=repo_root() / "Sizing" / "backup",
        help="Directory containing techsweep_gf180mcu_*_3v3.txt.gz files.",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=repo_root() / "AnalogAgent" / "asset_gf180mcuD",
        help="Output asset_gf180mcuD directory.",
    )
    parser.add_argument("--corner", default="typical")
    parser.add_argument("--temp", default="25C")
    parser.add_argument("--width-um", type=float, default=WIDTH_UM_DEFAULT)
    parser.add_argument("--vds", type=float, default=1.65)
    parser.add_argument("--vbs", type=float, default=0.0)
    parser.add_argument("--vbs-tolerance", type=float, default=0.05)
    args = parser.parse_args()

    all_written: list[Path] = []
    for _, (device, filename) in DEVICE_MAP.items():
        sweep_path = args.sizing_root / filename
        if not sweep_path.is_file():
            raise FileNotFoundError(f"Missing sweep file: {sweep_path}")
        all_written.extend(
            build_device_luts(
                sweep_path=sweep_path,
                output_root=args.output_root,
                device=device,
                corner=args.corner,
                temp=args.temp,
                width_um=args.width_um,
                vds_target=args.vds,
                vbs_target=args.vbs,
                vbs_tolerance=args.vbs_tolerance,
            )
        )

    print(f"Wrote {len(all_written)} LUT files under {args.output_root}")
    for path in all_written:
        print(path)


if __name__ == "__main__":
    main()
