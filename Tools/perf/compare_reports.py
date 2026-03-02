#!/usr/bin/env python3

import argparse
import json
import sys


def load_report(path):
  with open(path, "r") as f:
    return json.load(f)


def flatten_summary(report):
  summary = report.get("summary", {})
  flattened = {}
  for key, values in summary.items():
    flattened[key] = {
      "avg_seconds": float(values.get("avg_seconds", 0.0)),
      "runs_per_second": float(values.get("runs_per_second", 0.0)),
      "completed_runs": int(values.get("completed_runs", 0)),
    }
  return flattened


def percent_change(old_value, new_value):
  if old_value == 0.0:
    return 0.0
  return ((new_value - old_value) / old_value) * 100.0


def main():
  parser = argparse.ArgumentParser(description="Compare two PPSSPP perf reports")
  parser.add_argument("--baseline", required=True, help="Baseline perf-report JSON")
  parser.add_argument("--candidate", required=True, help="Candidate perf-report JSON")
  parser.add_argument("--max-avg-seconds-regression-pct", type=float, default=None, help="Fail if avg_seconds regression exceeds this percent")
  parser.add_argument("--max-rps-regression-pct", type=float, default=None, help="Fail if runs_per_second regression exceeds this percent")
  args = parser.parse_args()

  baseline = flatten_summary(load_report(args.baseline))
  candidate = flatten_summary(load_report(args.candidate))

  common_keys = sorted(set(baseline.keys()) & set(candidate.keys()))
  missing_from_candidate = sorted(set(baseline.keys()) - set(candidate.keys()))
  new_in_candidate = sorted(set(candidate.keys()) - set(baseline.keys()))

  if missing_from_candidate:
    print("Missing benchmarks in candidate:")
    for key in missing_from_candidate:
      print("  - {}".format(key))

  if new_in_candidate:
    print("New benchmarks in candidate:")
    for key in new_in_candidate:
      print("  + {}".format(key))

  failed = False
  if common_keys:
    print("Comparison:")
    for key in common_keys:
      base = baseline[key]
      cand = candidate[key]
      avg_delta_pct = percent_change(base["avg_seconds"], cand["avg_seconds"])
      rps_delta_pct = percent_change(base["runs_per_second"], cand["runs_per_second"])
      print("  {}: avg_seconds {:+.2f}% ({:.6f} -> {:.6f}), runs_per_second {:+.2f}% ({:.3f} -> {:.3f})".format(
        key,
        avg_delta_pct,
        base["avg_seconds"],
        cand["avg_seconds"],
        rps_delta_pct,
        base["runs_per_second"],
        cand["runs_per_second"],
      ))

      if args.max_avg_seconds_regression_pct is not None and avg_delta_pct > args.max_avg_seconds_regression_pct:
        print("    REGRESSION: avg_seconds delta {:+.2f}% exceeds +{:.2f}%".format(avg_delta_pct, args.max_avg_seconds_regression_pct))
        failed = True
      if args.max_rps_regression_pct is not None and (-rps_delta_pct) > args.max_rps_regression_pct:
        print("    REGRESSION: runs_per_second delta {:+.2f}% exceeds -{:.2f}%".format(rps_delta_pct, args.max_rps_regression_pct))
        failed = True

  if failed:
    return 2
  return 0


if __name__ == "__main__":
  sys.exit(main())
