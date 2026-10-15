#!/usr/bin/env bash
# Week-1 gate on the 27B, overnight (~3 h). Safe to rerun: cached completions are reused.
# Writes runs/c0_gate_27b_long, a summary CSV, and reports/figures/c0_qwen3.5_27b.png.
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p runs
{
  echo "=== start $(date)"
  .venv/bin/efa run configs/c0_gate_27b_long.yaml
  echo "=== run done $(date)"
  .venv/bin/efa summarize runs/c0_gate_27b_long --csv
  .venv/bin/efa plot runs/c0_gate_27b_long --name c0_qwen3.5_27b.png
  echo "=== all done $(date)"
} 2>&1 | tee -a runs/gate_27b_overnight.log
