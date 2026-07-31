# Round-2 review: data-integrity items for author resolution

These are inconsistencies in the underlying results (not the prose); each needs
your check against the source data before submission. The writing/cross-ref/
framing findings from the same review were fixed autonomously.

1. **L2 = R2 are the same molecule.** `m2_lead_L2.json` and `m2_lead_R2.json`
   both have SMILES `O=[N+]([O-])N=C1NC(O)ON=C1[N+](=O)[O-]` (C3H3N5O6, same
   rho_dft). The paper presents this molecule as BOTH a chem-pass lead (L2) and a
   SMARTS-rejected reference scaffold (R2). One classification (or the DFT-audit
   labeling) is wrong; a molecule cannot both pass and be rejected by the gate.

2. **Novelty audit: "3 rediscoveries" vs Table 3 "1% exact match".** Section 2.4
   names three labelled-master rediscoveries (dinitramide, 1,2-dinitrohydrazine,
   N,N'-dinitrocarbodiimide) but Table 3's labelled-master exact-match cell reads
   1% (= 1). Reconcile the count (3 -> 3%) or the named list.

3. **Scaffold counts disagree ~10x (Tables S18 vs S19 vs S13).** For the same C0
   unguided 10k pool: Table S18 = 125 BM scaffolds (62-165), Table S19 = 1262
   (659-1262), Table S13 = 369. The body cites 659-1262 (S19), so S18's column
   looks stale. Confirm which is correct.

4. **Top-5 MW range 147-233 Da** (Section 2.2) does not match any single lead's
   formula MW (L1-L5 span ~163-230). Verify the range/basis.
