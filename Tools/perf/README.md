# PPSSPP Performance Benchmarks

This directory contains the Phase 0 baseline benchmarking tooling:

- `benchmarks.json`: canonical benchmark list + profile definitions
- `bench_runner.py`: profile orchestrator for local/CI benchmark runs

## Headless benchmark output schema

`PPSSPPHeadless --bench` emits machine-parseable JSON lines:

- `BENCH_META { ... }`
- `BENCH_RESULT { ... }`

Current schema id: `ppsspp_headless_bench_v1`

Each `BENCH_RESULT` record includes per-run metadata:

- `test_id`, `test_file`
- `gpu_backend`, `cpu_core`
- `build_type`, `compiler`, `platform`, `arch`
- `requested_runs`, `completed_runs`, `successful_runs`
- `total_seconds`, `avg_seconds`, `runs_per_second`
- thread scheduler deltas:
  - `thread_enqueued_delta`
  - `thread_dispatched_private_delta`
  - `thread_dispatched_global_delta`
  - `thread_worker_waits_delta`
  - `thread_worker_wait_time_us_delta`
  - `thread_compute_queue_max`
  - `thread_io_queue_max`

## Running from `test.py`

Run the default benchmark config:

```bash
python3 test.py --bench --graphics=software -j
```

Run with explicit run counts and save JSON:

```bash
python3 test.py --bench --bench-runs=30 --bench-repetitions=2 --bench-output=perf-report-software.json --graphics=software -j
```

The generated JSON includes:
- `results`: per-test benchmark samples (`BENCH_RESULT`)
- `meta`: per-run environment metadata (`BENCH_META`)
- both sections include `requested_gpu_backend` and `requested_cpu_core` so fallback/override behavior is visible in reports
- combined reports include:
  - `backend_fallbacks` (`requested_gpu_backend` vs `gpu_backend`)
  - `cpu_fallbacks` (`requested_cpu_core` vs `cpu_core`)

Select tests manually:

```bash
python3 test.py --bench cpu/cpu_alu/cpu_alu gpu/primitives/triangles --graphics=software -j
```

## Running multi-profile reports

Run all configured profiles and generate one combined report:

```bash
python3 Tools/perf/bench_runner.py --output perf-report.json --csv-output perf-report.csv
```

Run only the CI profile with reduced cost:

```bash
python3 Tools/perf/bench_runner.py --profile ci-software --bench-runs 10 --bench-repetitions 1 --output perf-report-ci.json
```

Run software + GLES candidates and keep going if one profile is unavailable:

```bash
python3 Tools/perf/bench_runner.py --profile ci-software --profile ci-gles --bench-runs 10 --bench-repetitions 1 --continue-on-profile-error --output perf-report-ci.json --csv-output perf-report-ci.csv
```

Optionally enforce maximum fallback counts in a run:

```bash
python3 Tools/perf/bench_runner.py --profile ci-software --bench-runs 10 --bench-repetitions 1 --max-backend-fallbacks 0 --max-cpu-fallbacks 0 --output perf-report-ci.json
```

## Comparing two reports

Create a baseline and candidate report, then compare:

```bash
python3 Tools/perf/compare_reports.py --baseline perf-report-baseline.json --candidate perf-report-candidate.json
```

Optionally fail on regressions beyond tolerance bands:

```bash
python3 Tools/perf/compare_reports.py --baseline perf-report-baseline.json --candidate perf-report-candidate.json --max-avg-seconds-regression-pct 5 --max-p95-seconds-regression-pct 5 --max-p99-seconds-regression-pct 5 --max-rps-regression-pct 5 --max-completed-runs-drop 0 --max-backend-fallback-increase 0 --max-cpu-fallback-increase 0 --require-no-missing-benchmarks
```

Thread scheduler pressure can also be guarded:

```bash
python3 Tools/perf/compare_reports.py --baseline perf-report-baseline.json --candidate perf-report-candidate.json --max-thread-enqueued-regression-pct 10 --max-thread-wait-us-regression-pct 10
```

Percentile frame-time deltas can also be thresholded:

```bash
python3 Tools/perf/compare_reports.py --baseline perf-report-baseline.json --candidate perf-report-candidate.json --max-p95-seconds-regression-pct 5 --max-p99-seconds-regression-pct 5
```

To emit a machine-readable comparison artifact:

```bash
python3 Tools/perf/compare_reports.py --baseline perf-report-baseline.json --candidate perf-report-candidate.json --output-json perf-compare.json
```

## Regression triage workflow

When a perf compare run fails thresholds:

1. Check `missing_benchmarks` / `new_benchmarks` first (often config/profile drift).
2. Check fallback deltas (`backend_fallbacks`, `cpu_fallbacks`) to rule out backend/core fallback effects.
3. Sort by largest `avg_seconds` / `p95_seconds` / `p99_seconds` regression.
4. Cross-check thread pressure deltas (`thread_enqueued_delta`, `thread_worker_wait_time_us_delta`) for scheduler contention clues.
5. Re-run the affected profile with higher repetitions to confirm signal before raising or tuning thresholds.
