# models/

This directory holds **sidecar pointer files** only. Actual checkpoint
binaries live on Zenodo (DOI 10.5281/zenodo.19821953); the repo never
commits files larger than ~10 MB.

Total checkpoint size on Zenodo: ~5 GB.

## Sidecar format

Each sidecar is a plain-text file named `<filename>.sidecar`:

```
filename:   denoiser_dgld_h.pt
size_mb:    682
sha256:     <64-hex-digit>
zenodo_doi: 10.5281/zenodo.19821953
url:        https://zenodo.org/record/19821953/files/denoiser_dgld_h.pt
download:   wget -O models/denoiser_dgld_h.pt <url>
```

`sha256` fields read `TODO_BEFORE_PUBLIC` until binaries are uploaded to
Zenodo. They are filled in lockstep with the public-visibility flip.

## Inventory

| File                               | Size | Role                                             |
|------------------------------------|------|--------------------------------------------------|
| `limo_vae.pt`                      | 388 MB | LIMO VAE (encoder + decoder)                  |
| `denoiser_dgld_h.pt`               | 682 MB | Production denoiser, hazard-aware (v4b)       |
| `denoiser_dgld_p.pt`               | 682 MB | Predecessor denoiser (v3)                     |
| `denoiser_v4b_seed1.pt`            | 681 MB | T3 multi-seed denoiser (seed 1)               |
| `denoiser_v4b_seed2.pt`            | 681 MB | T3 multi-seed denoiser (seed 2)               |
| `denoiser_v4b_seed42.pt`           | 681 MB | T3 multi-seed denoiser (seed 42)              |
| `score_model_6head.pt`             |  30 MB | Production score model (6 heads)              |
| `score_model_5head.pt`             |  30 MB | Predecessor score model (5 heads)             |
| `random_forest_viability.pkl`      |   5 MB | RF viability classifier                       |
| `smoke_ensemble_fold1.pt`          | 200 MB | Smoke-test ensemble fold 1                    |
| `smoke_ensemble_fold2.pt`          | 200 MB | Smoke-test ensemble fold 2                    |

## Bulk download

```bash
bash ../scripts/download_assets.sh
```
