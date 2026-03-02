#!/usr/bin/env python3

import argparse
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


def selected_profiles(config, selected_ids):
  profiles = config.get("profiles", [])
  if not selected_ids:
    return profiles

  selected = []
  by_id = {profile.get("id"): profile for profile in profiles}
  for profile_id in selected_ids:
    if profile_id not in by_id:
      raise ValueError("Unknown profile '{}' in {}".format(profile_id, DEFAULT_CONFIG))
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


def summarize(profile_results):
  summary = {}
  for profile_result in profile_results:
    report = profile_result.get("report") or {}
    for result in report.get("results", []):
      key = "{}::{}".format(profile_result["id"], result.get("test_id", result.get("requested_test", "unknown")))
      summary[key] = {
        "avg_seconds": result.get("avg_seconds"),
        "runs_per_second": result.get("runs_per_second"),
        "completed_runs": result.get("completed_runs"),
      }
  return summary


def main():
  parser = argparse.ArgumentParser(description="Run PPSSPP benchmark profiles and generate report")
  parser.add_argument("--config", default=DEFAULT_CONFIG, help="Benchmark config JSON path")
  parser.add_argument("--output", default=DEFAULT_OUTPUT, help="Combined output report path")
  parser.add_argument("--profile", action="append", default=[], help="Profile id to run (repeatable)")
  parser.add_argument("--bench-runs", type=int, default=None, help="Override bench run count")
  parser.add_argument("--bench-repetitions", type=int, default=None, help="Override bench repetitions")
  args = parser.parse_args()

  config = load_config(args.config)
  profiles = selected_profiles(config, args.profile)
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
    if profile_result["returncode"] != 0:
      overall_returncode = profile_result["returncode"]

  combined = {
    "schema": "ppsspp_perf_report_v1",
    "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    "config": args.config,
    "bench_runs": bench_runs,
    "bench_repetitions": repetitions,
    "profiles": profile_results,
    "summary": summarize(profile_results),
  }

  ensure_directory(args.output)
  with open(args.output, "w") as f:
    json.dump(combined, f, indent=2, sort_keys=True)

  print("Wrote combined report to {}".format(args.output))
  return overall_returncode


if __name__ == "__main__":
  sys.exit(main())
