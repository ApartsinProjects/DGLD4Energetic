#!/usr/bin/env python
"""MolMIM-70M baseline generator.

Perturb-and-decodes energetic seed molecules with MolMIM-70M to produce the
MolMIM baseline sample set used in the head-to-head comparison (paper Table 8):
greedy-perturbate latent decoding with scaled_radius = 1.0, canonicalised and
deduplicated to a target sample count.

Environment (per MolMIMGuide.md):
  image : nvcr.io/nvidia/clara/bionemo-framework:1.5
  pins  : huggingface_hub<0.20, transformers<4.38
  ckpt  : molmim_70m_24_3.nemo  (NVIDIA MolMIM, ~70M params)

Usage (inside the container):
  python molmim_generate.py \
      --nemo /workspace/data/molmim_70m_24_3.nemo \
      --seeds seeds_energetic.smi \
      --n-target 6000 --num-samples 16 --scaled-radius 1.0 \
      --out molmim_samples.txt
"""
import argparse, sys, time
from pathlib import Path

# Default energetic seeds: the two headline leads plus a few reference anchors,
# perturbed to explore MolMIM's drug-domain latent around energetic chemotypes.
DEFAULT_SEEDS = [
    "O=[N+]([O-])c1noc([N+](=O)[O-])c1[N+](=O)[O-]",       # L1, 3,4,5-trinitro-1,2-isoxazole
    "O=[N+]([O-])c1nonc1[N+](=O)[O-]",                     # 4-nitro-oxatriazole seed (E1 family)
    "O=C1N([N+](=O)[O-])CN([N+](=O)[O-])CN1[N+](=O)[O-]",  # RDX anchor
    "[O-][N+](=O)N1CN([N+](=O)[O-])CN([N+](=O)[O-])CN([N+](=O)[O-])C1",  # HMX anchor
]


def canonical(smi):
    try:
        from rdkit import Chem
        m = Chem.MolFromSmiles(smi)
        return Chem.MolToSmiles(m) if m is not None else None
    except Exception:
        return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--nemo", default="/workspace/data/molmim_70m_24_3.nemo")
    ap.add_argument("--infer-yaml",
                    default="/workspace/bionemo/examples/molecule/molmim/conf/infer.yaml")
    ap.add_argument("--seeds", default=None,
                    help="File of seed SMILES (one per line); defaults to the built-in energetic seeds.")
    ap.add_argument("--n-target", type=int, default=6000, help="Stop after this many unique canonical SMILES.")
    ap.add_argument("--num-samples", type=int, default=16, help="Samples per sample() call (per seed, per round).")
    ap.add_argument("--scaled-radius", type=float, default=1.0)
    ap.add_argument("--sampling-method", default="greedy-perturbate")
    ap.add_argument("--max-rounds", type=int, default=2000)
    ap.add_argument("--out", default="molmim_samples.txt")
    args = ap.parse_args()

    seeds = (Path(args.seeds).read_text().split() if args.seeds else DEFAULT_SEEDS)
    print(f"[molmim] {len(seeds)} seed SMILES; target {args.n_target} unique", flush=True)

    from omegaconf import OmegaConf
    from bionemo.model.molecule.molmim.infer import MolMIMInference
    cfg = OmegaConf.load(args.infer_yaml)
    cfg.model.downstream_task.restore_from_path = args.nemo
    infer = MolMIMInference(cfg=cfg.model, interactive=True,
                            restore_path=cfg.model.downstream_task.restore_from_path)

    seen, out = set(), []
    t0 = time.time()
    for r in range(args.max_rounds):
        # one sample() call per seed each round
        batches = infer.sample(num_samples=args.num_samples, seqs=seeds,
                                sampling_method=args.sampling_method,
                                scaled_radius=args.scaled_radius)
        for per_seed in batches:                      # list-of-lists, one per seed
            for smi in per_seed:
                c = canonical(smi)
                if c and c not in seen:
                    seen.add(c); out.append(c)
        if len(out) >= args.n_target:
            break
        if r % 25 == 0:
            print(f"[molmim] round {r}: {len(out)} unique, {time.time()-t0:.0f}s", flush=True)

    Path(args.out).write_text("\n".join(out[:args.n_target]) + "\n")
    print(f"[molmim] wrote {min(len(out), args.n_target)} SMILES to {args.out} "
          f"in {time.time()-t0:.0f}s", flush=True)


if __name__ == "__main__":
    main()
