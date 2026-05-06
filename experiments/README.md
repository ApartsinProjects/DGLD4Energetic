# experiments/

One subfolder per paper experiment. Each subfolder holds the launcher
scripts (`*.py`, `*.sh`), a `results/` dir with JSON summaries, and
optional notes. Large `.pt` checkpoints are stripped; results stay.

| Subfolder                   | Paper claim                                                | Notes |
|-----------------------------|------------------------------------------------------------|-------|
| `t1_bde/`                   | T1: bond dissociation energy audit on 12 leads             | Modal A100 |
| `t2_density/`               | T2: GFN2-xTB density audit                                 | Modal A100 |
| `t3_seed_variance/`         | T3: denoiser seed variance (3 seeds)                       | Modal A100; checkpoints on Zenodo |
| `t4_oxatriazole/`           | T4: oxatriazole anchor case study                          | CPU |
| `dft_audit/`                | 12 DFT-confirmed leads + DNTF 7th anchor                   | Modal A100 |
| `multi_seed_sampling/`      | m6 multi-seed sampling stability                           | Modal L4 |
| `m7_pool_fusion/`           | m7 100k pool fusion                                        | Modal L4 |
| `cj_validation/`            | Chapman-Jouguet validation vs Cantera                      | CPU |
| `h50_sensitivity/`          | H50 impact-sensitivity surrogate                           | CPU |
| `baselines_distribution/`   | FCD baselines vs DGLD                                      | CPU |
| `baselines_lstm/`           | SMILES-LSTM multi-seed baseline                            | Modal L4 |
| `baselines_reinvent/`       | REINVENT 4 multi-seed + Uni-Mol scoring                    | Modal L4 |
| `baselines_selfies_ga/`     | SELFIES-GA baseline (40k pool)                             | Modal L4 |
| `aizynth_retro/`            | AiZynthFinder retrosynthetic feasibility (12 leads + DNTF) | CPU |
| `gaussian_control/`         | Gaussian-latent ablation (post-hoc 40k pool)               | Modal L4 |
| `tier_gate_ablation/`       | Tier-gate ablation                                         | Modal L4 |

## Conventions

- `*.py` files are launchers; `modal_*.py` runs on Modal, plain `*.py` runs locally.
- `results/*.json` is the canonical machine-readable artefact.
- `LAUNCH*.md` (when present) documents the original Modal command line.
- Old per-run dirs (`results_apr28/`, `results_modal/`, etc.) are NOT migrated; only
  the canonical `results/` from the `submission_ready` tag.
