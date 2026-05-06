# data/

Small data tracked in the repo; large data hosted on Zenodo via sidecars.

## Files

(Initially empty -- training and validation tables move here in v1.0.x.)

## Schemas (TBD)

| File                        | Schema                                                | Rows   |
|-----------------------------|-------------------------------------------------------|--------|
| `train_chno.parquet.sidecar`| smiles, density, det_velocity, det_pressure, h50, ... | 65,980 |
| `held_out_anchors.csv`      | smiles, name, density_lit, D_lit, citation            | 12     |
| `dft_audit_inputs.csv`      | smiles, name, source, dft_method                      | 13     |

## Licenses and provenance

- Training data labels are derived from public sources, used for research
  with attribution, and redistributed under CC-BY-4.0 (see `../LICENSE-DATA`).

Public-source citations:

- Klapotke, T. M. *Chemistry of High-Energy Materials*, 5th ed. De Gruyter, 2019.
- Cooper, P. W. *Explosives Engineering*. Wiley-VCH, 1996.
- LLNL Explosives Handbook: Properties of Chemical Explosives and Explosive Simulants. UCRL-52997, 1985.
- Casey, A. D., et al. *J. Energ. Mater.* (2020).
- ZINC-15 (Sterling and Irwin, *J. Chem. Inf. Model.* 2015).

Per-row provenance is recorded in the `source` column of each table.
