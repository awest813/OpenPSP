#!/usr/bin/env python3

import argparse
import csv
import json
import os
import subprocess
import sys
from datetime import datetime, timezone


DEFAULT_CONFIG = "Tools/perf/benchmarks.json"
DEFAULT_OUTPUT = "perf-report.json"


def load_config(config_path):
  with open(config_path, "r") as f:
    return json.load(f)


def selected_profiles(config, selected_ids, config_path):
  profiles = config.get("profiles", [])
  if not selected_ids:
    return profiles

  selected = []
  by_id = {profile.get("id"): profile for profile in profiles}
  for profile_id in selected_ids:
    if profile_id not in by_id:
      raise ValueError("Unknown profile '{}' in {}".format(profile_id, config_path))
    selected.append(by_id[profile_id])
  return selected


def ensure_directory(path):
  directory = os.path.dirname(path)
  if directory and not os.path.exists(directory):
    os.makedirs(directory)


def run_profile(config_path, profile, bench_runs, repetitions):
  profile_id = profile.get("id", "unknown-profile")
  profile_output = "perf-report-{}.json".format(profile_id)
  cmd = [
    sys.executable,
    "test.py",
    "--bench",
    "--bench-config={}".format(config_path),
    "--bench-output={}".format(profile_output),
    "--bench-runs={}".format(bench_runs),
    "--bench-repetitions={}".format(repetitions),
  ]
  cmd.extend(profile.get("args", []))

  print("Running profile '{}': {}".format(profile_id, " ".join(cmd)))
  completed = subprocess.run(cmd, check=False)

  profile_report = None
  if os.path.exists(profile_output):
    with open(profile_output, "r") as f:
      profile_report = json.load(f)

  return {
    "id": profile_id,
    "description": profile.get("description", ""),
    "args": profile.get("args", []),
    "returncode": completed.returncode,
    "output_file": profile_output,
    "report": profile_report,
  }


def percentile(values, p):
  if not values:
    return 0.0
  sorted_values = sorted(values)
  if len(sorted_values) == 1:
    return float(sorted_values[0])
  rank = (p / 100.0) * (len(sorted_values) - 1)
  lower = int(rank)
  upper = min(lower + 1, len(sorted_values) - 1)
  fraction = rank - lower
  return (sorted_values[lower] * (1.0 - fraction)) + (sorted_values[upper] * fraction)


def summarize(profile_results):
  summary = {}
  for profile_result in profile_results:
    report = profile_result.get("report") or {}
    grouped = {}
    for result in report.get("results", []):
      key = "{}::{}".format(profile_result["id"], result.get("test_id", result.get("requested_test", "unknown")))
      grouped.setdefault(key, []).append(result)

    for key, samples in grouped.items():
      count = float(len(samples))
      avg_seconds_samples = [float(sample.get("avg_seconds", 0.0)) for sample in samples]
      runs_per_second_samples = [float(sample.get("runs_per_second", 0.0)) for sample in samples]
      summary[key] = {
        "avg_seconds": sum(avg_seconds_samples) / count,
        "p95_seconds": percentile(avg_seconds_samples, 95.0),
        "p99_seconds": percentile(avg_seconds_samples, 99.0),
        "runs_per_second": sum(runs_per_second_samples) / count,
        "completed_runs": int(sum(int(sample.get("completed_runs", 0)) for sample in samples) / count),
        "thread_enqueued_delta": sum(float(sample.get("thread_enqueued_delta", 0.0)) for sample in samples) / count,
        "thread_dispatched_private_delta": sum(float(sample.get("thread_dispatched_private_delta", 0.0)) for sample in samples) / count,
        "thread_dispatched_global_delta": sum(float(sample.get("thread_dispatched_global_delta", 0.0)) for sample in samples) / count,
        "thread_worker_waits_delta": sum(float(sample.get("thread_worker_waits_delta", 0.0)) for sample in samples) / count,
        "thread_worker_wait_time_us_delta": sum(float(sample.get("thread_worker_wait_time_us_delta", 0.0)) for sample in samples) / count,
      }
  return summary

def collect_rows(profile_results):
  rows = []
  for profile_result in profile_results:
    report = profile_result.get("report") or {}
    meta_records = report.get("meta", [])
    meta_by_key = {}
    for meta in meta_records:
      key = (meta.get("requested_test"), meta.get("repetition"))
      meta_by_key[key] = meta

    for result in report.get("results", []):
      key = (result.get("requested_test"), result.get("repetition"))
      meta = meta_by_key.get(key, {})
      rows.append({
        "profile_id": profile_result["id"],
        "requested_test": result.get("requested_test"),
        "test_id": result.get("test_id"),
        "requested_gpu_backend": result.get("requested_gpu_backend", meta.get("requested_gpu_backend")),
        "requested_cpu_core": result.get("requested_cpu_core", meta.get("requested_cpu_core")),
        "repetition": result.get("repetition"),
        "requested_runs": result.get("requested_runs"),
        "completed_runs": result.get("completed_runs"),
        "successful_runs": result.get("successful_runs"),
        "avg_seconds": result.get("avg_seconds"),
        "runs_per_second": result.get("runs_per_second"),
        "total_seconds": result.get("total_seconds"),
        "success": result.get("success"),
        "thread_enqueued_delta": result.get("thread_enqueued_delta"),
        "thread_dispatched_private_delta": result.get("thread_dispatched_private_delta"),
        "thread_dispatched_global_delta": result.get("thread_dispatched_global_delta"),
        "thread_worker_waits_delta": result.get("thread_worker_waits_delta"),
        "thread_worker_wait_time_us_delta": result.get("thread_worker_wait_time_us_delta"),
        "thread_compute_queue_max": result.get("thread_compute_queue_max"),
        "thread_io_queue_max": result.get("thread_io_queue_max"),
        "gpu_backend": meta.get("gpu_backend", result.get("gpu_backend")),
        "cpu_core": meta.get("cpu_core", result.get("cpu_core")),
        "platform": meta.get("platform", result.get("platform")),
        "arch": meta.get("arch", result.get("arch")),
        "compiler": meta.get("compiler", result.get("compiler")),
        "build_type": meta.get("build_type", result.get("build_type")),
      })
  return rows

def write_csv_report(path, rows):
  ensure_directory(path)
  fieldnames = [
    "profile_id",
    "requested_test",
    "test_id",
    "requested_gpu_backend",
    "requested_cpu_core",
    "repetition",
    "requested_runs",
    "completed_runs",
    "successful_runs",
    "avg_seconds",
    "runs_per_second",
    "total_seconds",
    "success",
    "thread_enqueued_delta",
    "thread_dispatched_private_delta",
    "thread_dispatched_global_delta",
    "thread_worker_waits_delta",
    "thread_worker_wait_time_us_delta",
    "thread_compute_queue_max",
    "thread_io_queue_max",
    "gpu_backend",
    "cpu_core",
    "platform",
    "arch",
    "compiler",
    "build_type",
  ]
  with open(path, "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    for row in rows:
      writer.writerow(row)

def detect_backend_fallbacks(rows):
  fallbacks = []
  for row in rows:
    requested = row.get("requested_gpu_backend")
    actual = row.get("gpu_backend")
    if requested and requested != "default" and actual and requested != actual:
      fallbacks.append({
        "profile_id": row.get("profile_id"),
        "requested_test": row.get("requested_test"),
        "test_id": row.get("test_id"),
        "requested_gpu_backend": requested,
        "actual_gpu_backend": actual,
      })
  return fallbacks

def detect_cpu_fallbacks(rows):
  fallbacks = []
  for row in rows:
    requested = row.get("requested_cpu_core")
    actual = row.get("cpu_core")
    if requested and requested != "default" and actual and requested != actual:
      fallbacks.append({
        "profile_id": row.get("profile_id"),
        "requested_test": row.get("requested_test"),
        "test_id": row.get("test_id"),
        "requested_cpu_core": requested,
        "actual_cpu_core": actual,
      })
  return fallbacks


def main():
  parser = argparse.ArgumentParser(description="Run PPSSPP benchmark profiles and generate report")
  parser.add_argument("--config", default=DEFAULT_CONFIG, help="Benchmark config JSON path")
  parser.add_argument("--output", default=DEFAULT_OUTPUT, help="Combined output report path")
  parser.add_argument("--csv-output", default=None, help="Optional CSV output path for per-run benchmark rows")
  parser.add_argument("--profile", action="append", default=[], help="Profile id to run (repeatable)")
  parser.add_argument("--bench-runs", type=int, default=None, help="Override bench run count")
  parser.add_argument("--bench-repetitions", type=int, default=None, help="Override bench repetitions")
  parser.add_argument("--continue-on-profile-error", action="store_true", help="Continue and return success even if one profile fails")
  parser.add_argument("--max-backend-fallbacks", type=int, default=None, help="Fail if backend fallback sample count exceeds this value")
  parser.add_argument("--max-cpu-fallbacks", type=int, default=None, help="Fail if CPU fallback sample count exceeds this value")
  args = parser.parse_args()

  config = load_config(args.config)
  profiles = selected_profiles(config, args.profile, args.config)
  if not profiles:
    print("No profiles configured in {}".format(args.config))
    return 1

  bench_runs = args.bench_runs if args.bench_runs is not None else int(config.get("default_bench_runs", 20))
  repetitions = args.bench_repetitions if args.bench_repetitions is not None else int(config.get("default_repetitions", 1))
  bench_runs = max(1, bench_runs)
  repetitions = max(1, repetitions)

  profile_results = []
  overall_returncode = 0
  for profile in profiles:
    profile_result = run_profile(args.config, profile, bench_runs, repetitions)
    profile_results.append(profile_result)
    if profile_result["returncode"] != 0 and not args.continue_on_profile_error:
      overall_returncode = profile_result["returncode"]
    elif profile_result["returncode"] != 0:
      print("Profile '{}' failed with return code {}, continuing.".format(profile_result["id"], profile_result["returncode"]))

  combined = {
    "schema": "ppsspp_perf_report_v1",
    "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    "config": args.config,
    "bench_runs": bench_runs,
    "bench_repetitions": repetitions,
    "profiles": profile_results,
    "summary": summarize(profile_results),
  }

  rows = collect_rows(profile_results)
  combined["backend_fallbacks"] = detect_backend_fallbacks(rows)
  combined["cpu_fallbacks"] = detect_cpu_fallbacks(rows)
  combined["fallback_thresholds"] = {
    "max_backend_fallbacks": args.max_backend_fallbacks,
    "max_cpu_fallbacks": args.max_cpu_fallbacks,
  }

  ensure_directory(args.output)
  with open(args.output, "w") as f:
    json.dump(combined, f, indent=2, sort_keys=True)

  print("Wrote combined report to {}".format(args.output))
  if combined["backend_fallbacks"]:
    print("Detected {} backend fallback sample(s).".format(len(combined["backend_fallbacks"])))
  if args.max_backend_fallbacks is not None and len(combined["backend_fallbacks"]) > args.max_backend_fallbacks:
    print("Backend fallback threshold exceeded: {} > {}".format(len(combined["backend_fallbacks"]), args.max_backend_fallbacks))
    overall_returncode = overall_returncode or 3
  if combined["cpu_fallbacks"]:
    print("Detected {} CPU fallback sample(s).".format(len(combined["cpu_fallbacks"])))
  if args.max_cpu_fallbacks is not None and len(combined["cpu_fallbacks"]) > args.max_cpu_fallbacks:
    print("CPU fallback threshold exceeded: {} > {}".format(len(combined["cpu_fallbacks"]), args.max_cpu_fallbacks))
    overall_returncode = overall_returncode or 3
  if args.csv_output:
    write_csv_report(args.csv_output, rows)
    print("Wrote CSV report to {}".format(args.csv_output))
  return overall_returncode


if __name__ == "__main__":
  sys.exit(main())
