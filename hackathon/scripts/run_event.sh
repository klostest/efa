#!/usr/bin/env bash
# Event-weekend rerun of the preregistered Qwen matrix from a cleared cache, in priority
# order (plan, "Event weekend plan", 2026-11-06). Each item writes to its own directory
# under hackathon/runs/event/, which starts without a cache, so every model call is a fresh
# sample. Safe to rerun: finished cells are skipped, and a crash mid-cell resumes from the
# cache. Runs under caffeinate so the Mac does not sleep.
#
# Usage: hackathon/scripts/run_event.sh            # everything, in order
#        hackathon/scripts/run_event.sh c2 d1_c2   # a subset of the item names below
set -uo pipefail
cd "$(dirname "$0")/../.."
EFA=.venv/bin/efa
OUT=hackathon/runs/event
mkdir -p "$OUT"

# name | config | --only filter (substring of the cell id; empty = all cells) | output stem
ITEMS=(
  "c2|configs/c2_false_beards.yaml||c2_false_beards"
  "audited|configs/d1_audited.yaml||d1_audited"
  "d2|configs/d2_secret.yaml||d2_secret"
  "d1_c2|configs/d1_costly_claim.yaml|_c2_|d1_costly_claim"
  "d1_c0.5|configs/d1_costly_claim.yaml|_c0.5_|d1_costly_claim"
  "d1_c0|configs/d1_costly_claim.yaml|_c0_|d1_costly_claim"
  "d1_c1.5|configs/d1_costly_claim.yaml|_c1.5_|d1_costly_claim"
  "d1_c1|configs/d1_costly_claim.yaml|_c1_|d1_costly_claim"
  "c0|configs/c0_gate_27b_think.yaml||c0_gate_27b_think"
  "h1|configs/c1_h1.yaml||c1_h1"
  "confound|configs/c2_confound.yaml||c2_confound"
)

wanted=("$@")
want() { [ ${#wanted[@]} -eq 0 ] && return 0; for w in "${wanted[@]}"; do [ "$w" = "$1" ] && return 0; done; return 1; }

echo "=== run_event start $(date)" | tee -a "$OUT/run_event.log"
for item in "${ITEMS[@]}"; do
  IFS='|' read -r name cfg only stem <<< "$item"
  want "$name" || continue
  log="$OUT/$stem.log"
  {
    echo "=== [$name] start $(date)  config=$cfg only=${only:-all}"
    if [ -n "$only" ]; then
      caffeinate -i "$EFA" run "$cfg" --out "$OUT/$stem" --only "$only"
    else
      caffeinate -i "$EFA" run "$cfg" --out "$OUT/$stem"
    fi
    status=$?
    echo "=== [$name] done $(date) exit=$status"
    "$EFA" summarize "$OUT/$stem" --csv || true
  } 2>&1 | tee -a "$log" | grep -v "it/s\]" >> "$OUT/run_event.log"
done
echo "=== run_event end $(date)" | tee -a "$OUT/run_event.log"
