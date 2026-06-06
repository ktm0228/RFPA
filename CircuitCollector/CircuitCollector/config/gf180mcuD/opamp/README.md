# GF180 Opamp Configs

Create GF180-specific TOML configs in this directory.

Suggested starting point:
1. Copy the closest GF180 config already in this directory and adapt it for your topology.
2. Change `[tech].name` to `gf180mcuD`.
3. Change `[tech_lib].pdk_path` to `PDK/gf180mcuD`.
4. Replace `device_prefix` with the prefix emitted by your GF180 simulator's
   operating-point variables.
5. Replace transistor type labels and parameter ranges with values derived from
   the GF180 PDK and your characterized LUT set.

Do not reuse Sky130 width/length ranges without verification.
