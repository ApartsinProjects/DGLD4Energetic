# scripts/

Top-level entry points for figure regeneration, training, sampling, and
asset download.

## Figure scripts

| Script             | Produces                                       |
|--------------------|------------------------------------------------|
| `plot_fig1.py`     | Fig 1 -- novelty vs detonation velocity        |
| `plot_fig19.py`    | Fig 19 -- lead cards grid                      |
| `plot_fig21.py`    | Fig 21 -- DFT dumbbell                         |
| `plot_fig22.py`    | Fig 22 -- baseline forest plot                 |
| `plot_fig23.py`    | Fig 23 -- quadrant scatter (D vs Tanimoto)     |

All figure scripts read from `../experiments/<exp>/results/*.json` and write
to `../figures/`.

## Asset download

`download_assets.sh` (TBD) wraps `wget` over the sidecars in `../models/` to
fetch checkpoints from Zenodo. Reads each `.sidecar`, follows the URL,
verifies SHA-256 (once placeholders are filled).

## Training entry points (TBD wrappers)

- `train_limo.py` -- LIMO VAE pre-training.
- `train_denoiser.py` -- Latent denoiser training (matches paper Section 4).
- `train_score_model.py` -- Multi-head score-model training.
- `sample.py` -- Wrapper over `dgld.guided_v2_sampler`.

These are stub names; concrete wrappers ship in v1.0.x patch releases.
