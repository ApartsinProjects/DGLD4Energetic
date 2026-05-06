"""DGLD4Energetic: Domain-Gated Latent Diffusion for Energetic Materials.

This package collects the LIMO encoder/decoder, the domain-gated latent
denoiser, the multi-head score model, and the guided sampler used in the
companion paper.

Module map
----------
- ``limo_model``      LIMO VAE encoder/decoder.
- ``model``           Latent denoiser architecture (UNet over latent codes).
- ``train_multihead_latent``  Score-model training entry point.
- ``guided_v2_sampler``       Guided sampling with multi-head guidance.
- ``m1_anneal_clamp``         Anneal+clamp guidance fix (paper Sec. 5).
- ``aizynth_run``             AiZynthFinder retro-synthesis wrapper.

Checkpoints (LIMO VAE, denoisers, score model) are NOT shipped in the repo
and must be downloaded from Zenodo: see ``../models/*.sidecar`` for URLs.
"""

__version__ = "1.0.0"
