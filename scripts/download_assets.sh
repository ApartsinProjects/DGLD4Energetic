#!/bin/bash
# Fetch the DGLD model checkpoints from the Zenodo record
# (concept DOI 10.5281/zenodo.19821952). Reads the pointer files in models/*.sidecar
# and downloads each binary next to its sidecar. Raw datasets and the full bundle
# are in the same Zenodo record; see the paper's Data Availability Statement.
set -eu
cd "$(dirname "$0")/.."
for sc in models/*.sidecar; do
  fn=$(awk -F': +' '/^filename:/{print $2}' "$sc")
  url=$(awk -F': +' '/^url:/{print $2}' "$sc")
  if [ -f "models/$fn" ]; then echo "[skip] models/$fn exists"; continue; fi
  echo "[get ] models/$fn"
  wget -q --show-progress -O "models/$fn" "$url"
done
echo "Done. Checkpoints in models/ ; verify md5 against each *.sidecar."
