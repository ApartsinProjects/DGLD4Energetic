# models/

This directory holds **sidecar pointer files** only. Actual checkpoint
binaries live on Zenodo (DOI 10.5281/zenodo.19821952); the repo never
commits files larger than ~10 MB.

Total checkpoint size on Zenodo: ~5 GB.

## Sidecar format

Each sidecar is a plain-text file named `<filename>.sidecar`:

```
filename:   denoiser_dgld_h.pt
size_mb:    682
sha256:     <64-hex-digit>
zenodo_doi: 10.5281/zenodo.19821952
url:        https://zenodo.org/record/21708802/files/denoiser_dgld_h.pt
download:   wget -O models/denoiser_dgld_h.pt <url>
```

`sha256` fields read `TODO_BEFORE_PUBLIC` until binaries are uploaded to
Zenodo. They are filled in lockstep with the public-visibility flip.

## Inventory

| File | Size | Role |
|---|---|---|
| `limo_best.pt` | 406 MB | LIMO SELFIES-VAE (encoder + decoder) |
| `v3_best.pt` | 715 MB | Conditional latent denoiser, v3 (DGLD-P predecessor) |
| `v4b_best.pt` | 715 MB | Production conditional latent denoiser, v4b (DGLD-H) |
| `score_model_v3e.pt` | 31 MB | Multi-task latent score model, v3e (5-head predecessor) |
| `score_model_v3f.pt` | 32 MB | Production multi-task latent score model, v3f (6-head) |
| `vocab.json` | 1 MB | SELFIES token vocabulary |
| `meta.json` | 1 MB | Run metadata |

Data archives (CSVs, hard-negative latents, code/results zips) are in the same Zenodo record; see the paper's Data Availability Statement.
