# Baseline generators

The four no-diffusion baselines from the head-to-head comparison (paper §4
"Baseline generators", Table 8). All are run through the *same* downstream
validation pipeline (canonicalisation, chemistry filters, Uni-Mol 3D-CNN
surrogate scoring, novelty window) on the *same* training corpus, so any
difference reflects the generator, not the evaluation.

| Baseline | Script(s) | Model | Sampling | Seeds | DFT? |
|---|---|---|---|---|---|
| SMILES-LSTM | `smiles_lstm_baseline.py`, `modal_multiseed_lstm.py` | 2-layer char LSTM, 512 hidden, ~6M params, trained from scratch on the 326k corpus (5 epochs, AdamW 1e-3) | 10k SMILES, temperature 1.0 | 1, 2, 3 | no (surrogate + FCD) |
| SELFIES-GA | `baseline_selfies_ga.py`, `modal_baseline_selfies_ga.py`, `modal_baseline_selfies_ga_40k.py`, `modal_selfies_ga_competitor_dft.py` | GA over SELFIES (`selfies` 2.1.1), optimises the DGLD Pareto composite | pop 2000 x 30 gen (40k x 15 compute-matched), seed 42 | 42 | **yes** (40k best-novel) |
| MolMIM 70M | `molmim_generate.py`, `smoke_molmim.py` (encode smoke), `MolMIMGuide.md` | NVIDIA `molmim_70m_24_3.nemo`, BioNeMo 1.5, pretrained (no fine-tune) | greedy-perturbate, scaled_radius 1.0 | 1 | no |
| REINVENT 4 | `modal_reinvent_40k.py`, `modal_reinvent_unimol_score.py`, `modal_multiseed_reinvent.py` | REINVENT 4 (v4.4.12), RL on built-in prior, N-fraction reward | 40k target, 8000 RL steps (40k) / 2000 staged (multiseed) | 42, 1, 2 | no (surrogate post hoc) |

## Notes and caveats (carried into the paper)

- **Evaluation parity.** Every baseline is scored on the same Uni-Mol 3D-CNN
  surrogate. Only SELFIES-GA's 40k best-novel candidate was carried to the full
  DFT audit (`modal_selfies_ga_competitor_dft.py`), where it collapsed from a
  surrogate D = 9.74 to a DFT D = 6.28 km/s.
- **Composite scores are within-method only.** SELFIES-GA's composite is
  generator-internal (viability = 0.5, novelty = 1.0 assumed during search);
  REINVENT's is an N-fraction proxy; MolMIM's is on an uncalibrated scale.
- **MolMIM** is run in the BioNeMo container (`MolMIMGuide.md`); `molmim_generate.py`
  drives the greedy-perturbate sampling (scaled_radius 1.0). The sample set
  (`molmim_samples.txt`) and its scored result (`molmim_post.json`) are archived
  with the Zenodo record.
- **REINVENT version.** `LAUNCH.md` pins `reinvent==4.4.12`, but the Modal images
  install from the MolecularAI GitHub HEAD; treat 4.4.12 as the reference tag.
- **Modal / vast launchers.** The `modal_*.py` scripts are cloud-execution
  wrappers (Modal/vast.ai); the generator/eval logic is in the non-`modal_`
  files where present.
