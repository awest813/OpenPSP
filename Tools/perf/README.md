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
