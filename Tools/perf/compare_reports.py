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
      "p95_seconds": float(values.get("p95_seconds", 0.0)),
      "p99_seconds": float(values.get("p99_seconds", 0.0)),
      "runs_per_second": float(values.get("runs_per_second", 0.0)),
      "completed_runs": int(values.get("completed_runs", 0)),
      "thread_enqueued_delta": float(values.get("thread_enqueued_delta", 0.0)),
      "thread_worker_wait_time_us_delta": float(values.get("thread_worker_wait_time_us_delta", 0.0)),
    }
  return flattened

def fallback_count(report, key):
  values = report.get(key, [])
  if isinstance(values, list):
    return len(values)
  return 0


def percent_change(old_value, new_value):
  if old_value == 0.0:
    return 0.0
  return ((new_value - old_value) / old_value) * 100.0


def main():
  parser = argparse.ArgumentParser(description="Compare two PPSSPP perf reports")
  parser.add_argument("--baseline", required=True, help="Baseline perf-report JSON")
  parser.add_argument("--candidate", required=True, help="Candidate perf-report JSON")
  parser.add_argument("--max-avg-seconds-regression-pct", type=float, default=None, help="Fail if avg_seconds regression exceeds this percent")
  parser.add_argument("--max-p95-seconds-regression-pct", type=float, default=None, help="Fail if p95_seconds regression exceeds this percent")
  parser.add_argument("--max-p99-seconds-regression-pct", type=float, default=None, help="Fail if p99_seconds regression exceeds this percent")
  parser.add_argument("--max-rps-regression-pct", type=float, default=None, help="Fail if runs_per_second regression exceeds this percent")
  parser.add_argument("--max-thread-enqueued-regression-pct", type=float, default=None, help="Fail if thread_enqueued_delta regression exceeds this percent")
  parser.add_argument("--max-thread-wait-us-regression-pct", type=float, default=None, help="Fail if thread_worker_wait_time_us_delta regression exceeds this percent")
  parser.add_argument("--max-completed-runs-drop", type=int, default=None, help="Fail if completed_runs drops by more than this count")
  parser.add_argument("--max-backend-fallback-increase", type=int, default=None, help="Fail if backend fallback sample count increases by more than this value")
  parser.add_argument("--max-cpu-fallback-increase", type=int, default=None, help="Fail if CPU fallback sample count increases by more than this value")
  parser.add_argument("--require-no-missing-benchmarks", action="store_true", help="Fail if candidate report is missing baseline benchmark keys")
  parser.add_argument("--require-no-new-benchmarks", action="store_true", help="Fail if candidate report contains benchmark keys absent in baseline")
  args = parser.parse_args()

  baseline_report = load_report(args.baseline)
  candidate_report = load_report(args.candidate)
  baseline = flatten_summary(baseline_report)
  candidate = flatten_summary(candidate_report)

  common_keys = sorted(set(baseline.keys()) & set(candidate.keys()))
  missing_from_candidate = sorted(set(baseline.keys()) - set(candidate.keys()))
  new_in_candidate = sorted(set(candidate.keys()) - set(baseline.keys()))
  failed = False

  if missing_from_candidate:
    print("Missing benchmarks in candidate:")
    for key in missing_from_candidate:
      print("  - {}".format(key))
    if args.require_no_missing_benchmarks:
      print("    REGRESSION: candidate report is missing benchmark keys.")
      failed = True

  if new_in_candidate:
    print("New benchmarks in candidate:")
    for key in new_in_candidate:
      print("  + {}".format(key))
    if args.require_no_new_benchmarks:
      print("    REGRESSION: candidate report contains unexpected benchmark keys.")
      failed = True

  if common_keys:
    print("Comparison:")
    for key in common_keys:
      base = baseline[key]
      cand = candidate[key]
      avg_delta_pct = percent_change(base["avg_seconds"], cand["avg_seconds"])
      p95_delta_pct = percent_change(base["p95_seconds"], cand["p95_seconds"])
      p99_delta_pct = percent_change(base["p99_seconds"], cand["p99_seconds"])
      rps_delta_pct = percent_change(base["runs_per_second"], cand["runs_per_second"])
      enqueued_delta_pct = percent_change(base["thread_enqueued_delta"], cand["thread_enqueued_delta"])
      wait_us_delta_pct = percent_change(base["thread_worker_wait_time_us_delta"], cand["thread_worker_wait_time_us_delta"])
      completed_runs_drop = base["completed_runs"] - cand["completed_runs"]
      print("  {}: avg_seconds {:+.2f}% ({:.6f} -> {:.6f}), p95_seconds {:+.2f}% ({:.6f} -> {:.6f}), p99_seconds {:+.2f}% ({:.6f} -> {:.6f}), runs_per_second {:+.2f}% ({:.3f} -> {:.3f}), completed_runs {:+d} ({} -> {}), thread_enqueued_delta {:+.2f}% ({:.3f} -> {:.3f}), thread_wait_us_delta {:+.2f}% ({:.3f} -> {:.3f})".format(
        key,
        avg_delta_pct,
        base["avg_seconds"],
        cand["avg_seconds"],
        p95_delta_pct,
        base["p95_seconds"],
        cand["p95_seconds"],
        p99_delta_pct,
        base["p99_seconds"],
        cand["p99_seconds"],
        rps_delta_pct,
        base["runs_per_second"],
        cand["runs_per_second"],
        -completed_runs_drop,
        base["completed_runs"],
        cand["completed_runs"],
        enqueued_delta_pct,
        base["thread_enqueued_delta"],
        cand["thread_enqueued_delta"],
        wait_us_delta_pct,
        base["thread_worker_wait_time_us_delta"],
        cand["thread_worker_wait_time_us_delta"],
      ))

      if args.max_avg_seconds_regression_pct is not None and avg_delta_pct > args.max_avg_seconds_regression_pct:
        print("    REGRESSION: avg_seconds delta {:+.2f}% exceeds +{:.2f}%".format(avg_delta_pct, args.max_avg_seconds_regression_pct))
        failed = True
      if args.max_p95_seconds_regression_pct is not None and p95_delta_pct > args.max_p95_seconds_regression_pct:
        print("    REGRESSION: p95_seconds delta {:+.2f}% exceeds +{:.2f}%".format(p95_delta_pct, args.max_p95_seconds_regression_pct))
        failed = True
      if args.max_p99_seconds_regression_pct is not None and p99_delta_pct > args.max_p99_seconds_regression_pct:
        print("    REGRESSION: p99_seconds delta {:+.2f}% exceeds +{:.2f}%".format(p99_delta_pct, args.max_p99_seconds_regression_pct))
        failed = True
      if args.max_rps_regression_pct is not None and (-rps_delta_pct) > args.max_rps_regression_pct:
        print("    REGRESSION: runs_per_second delta {:+.2f}% exceeds -{:.2f}%".format(rps_delta_pct, args.max_rps_regression_pct))
        failed = True
      if args.max_completed_runs_drop is not None and completed_runs_drop > args.max_completed_runs_drop:
        print("    REGRESSION: completed_runs drop {} exceeds {}".format(completed_runs_drop, args.max_completed_runs_drop))
        failed = True
      if args.max_thread_enqueued_regression_pct is not None and enqueued_delta_pct > args.max_thread_enqueued_regression_pct:
        print("    REGRESSION: thread_enqueued_delta {:+.2f}% exceeds +{:.2f}%".format(enqueued_delta_pct, args.max_thread_enqueued_regression_pct))
        failed = True
      if args.max_thread_wait_us_regression_pct is not None and wait_us_delta_pct > args.max_thread_wait_us_regression_pct:
        print("    REGRESSION: thread_worker_wait_time_us_delta {:+.2f}% exceeds +{:.2f}%".format(wait_us_delta_pct, args.max_thread_wait_us_regression_pct))
        failed = True

  baseline_backend_fallbacks = fallback_count(baseline_report, "backend_fallbacks")
  candidate_backend_fallbacks = fallback_count(candidate_report, "backend_fallbacks")
  backend_fallback_delta = candidate_backend_fallbacks - baseline_backend_fallbacks
  print("Fallbacks: backend {} -> {} (delta {:+d})".format(
    baseline_backend_fallbacks,
    candidate_backend_fallbacks,
    backend_fallback_delta,
  ))
  if args.max_backend_fallback_increase is not None and backend_fallback_delta > args.max_backend_fallback_increase:
    print("    REGRESSION: backend fallback delta {:+d} exceeds +{:d}".format(backend_fallback_delta, args.max_backend_fallback_increase))
    failed = True

  baseline_cpu_fallbacks = fallback_count(baseline_report, "cpu_fallbacks")
  candidate_cpu_fallbacks = fallback_count(candidate_report, "cpu_fallbacks")
  cpu_fallback_delta = candidate_cpu_fallbacks - baseline_cpu_fallbacks
  print("Fallbacks: cpu {} -> {} (delta {:+d})".format(
    baseline_cpu_fallbacks,
    candidate_cpu_fallbacks,
    cpu_fallback_delta,
  ))
  if args.max_cpu_fallback_increase is not None and cpu_fallback_delta > args.max_cpu_fallback_increase:
    print("    REGRESSION: CPU fallback delta {:+d} exceeds +{:d}".format(cpu_fallback_delta, args.max_cpu_fallback_increase))
    failed = True

  if failed:
    return 2
  return 0


if __name__ == "__main__":
  sys.exit(main())
