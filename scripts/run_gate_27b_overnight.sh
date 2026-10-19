#!/usr/bin/env bash
# Week-1 gate sweep, unattended. Usage: scripts/run_gate_27b_overnight.sh [config] [model label]
# Default config is the 27B budgeted-thinking pass (see the config header); the 8B gate is
# scripts/run_gate_27b_overnight.sh configs/c0_gate_8b_think.yaml Qwen3-8B-4bit
# Runs under caffeinate so the Mac does not sleep (the 2,000-cap pass lost a night to sleep:
# one cell logged 15 h of wall time).
# Safe to rerun: cached completions are reused. Writes runs/<config stem>/, a summary CSV,
# and reports/figures/c0_<config stem>.png.
set -euo pipefail
cd "$(dirname "$0")/.."
cfg="${1:-configs/c0_gate_27b_think.yaml}"
label="${2:-Qwen3.5-27B-4bit}"
stem="$(basename "$cfg" .yaml)"
mkdir -p runs
{
  echo "=== start $(date)  config=$cfg"
  caffeinate -i .venv/bin/efa run "$cfg"
  echo "=== run done $(date)"
  .venv/bin/efa summarize "runs/$stem" --csv
  .venv/bin/efa plot "runs/$stem" --name "c0_${stem}.png" --title "$label, oracle similarity sweep ($stem)"
  echo "=== all done $(date)"
} 2>&1 | tee -a "runs/${stem}.log"
