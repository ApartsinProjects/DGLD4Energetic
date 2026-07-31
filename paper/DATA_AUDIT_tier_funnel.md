# Data audit: tier counts and 40k funnel (for author reconciliation)

Generated during the consistency audit. These items were **verified against the
committed experiment data across five repos** but **not applied** to the paper,
because doing so correctly requires an authoring decision (see each item).

## 1. Four-tier label counts — CORRECTED (2026) to the committed data

**Status: applied.** Table 1, Table A.1 (long paper + NMI), and the NMI tier
prose now read **A ~19,200 / B ~1,900 / C ~12,000 / D ~47,000** (rows carrying
>=1 label at that tier, per `apply_4tier_system.py` on the committed
65,980-row master), with a caption noting the counts do not partition the master
and that only ~3,000 rows carry a trusted A/B label on the target detonation
channels. **Author check still needed on the source->citation attributions in
Table A.1** (see below): the row descriptions were updated to the actual tiering
sources (cm4c01978 XRD densities for A; EXPLO5 train/test for B; cm4c01978 K-J
for C; 3D-CNN + generative-model predictions for D), but the *citation keys*
([60]/[15]/[62]) were kept as-is and should be verified against those sources.

### Original discrepancy (for the record)

The manuscript previously reported **Tier-A ~3,000 / B ~9,000 / C ~25,000 /
D ~30,000** in both `Table 1` and `Table A.1`. These numbers:

- appear **only in the prose** — no script, log, JSON, or notebook computes them;
- are **internally flagged** as unreconciled in
  `EnergeticDiffusion2/PAPER_AUDIT_LINEBYLINE.md:76` (they sum to 67k, but the
  master is 65,980);
- **do not match** the committed 65,980-row master.

Authoritative tiering: `EnergeticDiffusion2/scripts/apply_4tier_system.py`
(`tier_for()`, whose output is the committed `labeled_master.csv`). Computed on
that master:

| Tier | Source (per code) | rows with >=1 property at tier | perf-channels only (excl. bulk density) |
|---|---|---|---|
| A (experimental) | EXPLO5 train/test density, cm4c01978 density, misc | ~19,200 | ~725 |
| B (DFT / EXPLO5 non-density) | EXPLO5 train/test non-density | ~1,900 | ~1,925 |
| C (Kamlet-Jacobs) | cm4c01978, kj_from_explo5_hof | ~12,000 | ~12,000 |
| D (surrogate) | 3D-CNN + all generators | ~47,000 | ~47,000 |

Row-level "most-reliable tier" partition: A=19,200, B=3, C=5, D=46,772 (rows with
experimental density get Tier-A regardless of their performance-label tier).

**Why not auto-applied:** (a) the two tables are entangled — A.1 attributes counts
to specific citations (e.g. "Casey et al. 2020 = ~9,000" for Tier-B) that do not
map to the tiering code's source columns without per-source enumeration; (b) A.1
is pre-dedup and Table 1 is post-dedup, so a post-dedup Tier-A of ~19,000 would
logically exceed A.1's pre-dedup ~3,000 (impossible); (c) the abstract's "~3,000"
is defensible if it means **trusted (A/B) labels on the target detonation channels
(D, P, HOF)** ≈ 2,650, which is a different quantity than any single tier count.

**Recommended reconciliation (author):** decide the counting convention (per-tier
row presence vs. performance-channel trusted vs. row-level partition), then update
Table 1 **and** Table A.1 **and** the per-source citations together. If helpful, a
per-source enumeration pass on the committed master can produce the citation-level
counts to fill A.1 consistently.

## 2. 40k funnel keep-rate (Table F.5 / Fig 14) — NOT an error

Cross-checked and **consistent**: pool=40k -> ~1,800 chem-pass after Stage 1+2
(4.6% keep) -> 966 full-filter survivors -> top-100 -> 12 DFT-validated leads.
The two numbers ("~1,800 @ 4.6%" and "966 @ 2.4%") are different filter stages,
not a contradiction. The five-lane 100k pool-fusion -> 4,639 is confirmed by
`experiments/m7_pool_fusion/results/m7_post.json` (`n_validated=4639`).
No change needed.

## 3. Applied fixes (verified, already in the source)

- SELFIES-GA rediscovery **75% (75/100)**, not 74% (`selfies_ga_top100.json`).
- **11 unique** DFT-confirmed leads (**12 lead cards**; L3 and L16 are the same
  compound C3H2N6O6, identical to 6 sig figs in `m2_lead_L3/L16.json`).
- AiZynth state score standardized to **0.049** (`aizynth_results.json`: 0.0491).
- Abstract scarcity phrasing aligned to the NMI version ("~66k CHNO molecules with
  reported detonation properties, only ~3,000 carry trustworthy experimental or
  quantum-chemistry values").
