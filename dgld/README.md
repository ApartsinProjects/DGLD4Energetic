# dgld/

Importable Python package: the LIMO encoder/decoder, the domain-gated latent
denoiser, the multi-head score model, and the guided sampler.

Install with `pip install -e .` from the repo root, then `import dgld`.

## Module layout

- `limo_model.py` -- LIMO VAE encoder and decoder. Latent dim = 1024.
- `model.py` -- Latent denoiser (UNet over 1024-dim codes).
- `train_multihead_latent.py` -- Score-model training entry point (multi-head: viability, sensitivity, hazard, ...).
- `guided_v2_sampler.py` -- Guided sampler. Supports CFG + multi-head guidance.
- `m1_anneal_clamp.py` -- Anneal-and-clamp guidance fix (paper Section 5).
- `aizynth_run.py` -- Wrapper around AiZynthFinder for retrosynthetic feasibility.
- `meta.json` -- Bundle metadata (training data hash, head order, etc.).
- `vocab.json` -- SELFIES vocabulary used by LIMO.
- `smiles_targets_L4L5.json` -- L4/L5 anchor SMILES used by paper Section 5.

## Checkpoints

The package ships **no** checkpoint binaries. Before running anything,
download from Zenodo via the sidecars in `../models/`:

```bash
bash ../scripts/download_assets.sh
```

This places `limo_vae.pt`, `denoiser_dgld_h.pt`, `denoiser_dgld_p.pt`, and
`score_model_6head.pt` under `../models/`.

## Minimal sampling example

```python
from dgld.limo_model import LimoVAE
from dgld.model import LatentDenoiser
from dgld.guided_v2_sampler import sample_guided
import torch

vae = LimoVAE.from_checkpoint("models/limo_vae.pt").eval()
denoiser = LatentDenoiser.from_checkpoint("models/denoiser_dgld_h.pt").eval()
score = torch.load("models/score_model_6head.pt", map_location="cpu")

samples = sample_guided(
    vae=vae, denoiser=denoiser, score_model=score,
    n=2048, condition="Hz-C2", seed=42, cfg_scale=2.0,
)
```
