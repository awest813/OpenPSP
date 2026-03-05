# Performance Fixes & Issues Roadmap

## Objectives
- Improve frame pacing consistency (reduce stutter and frametime spikes).
- Lower CPU overhead in emulation, rendering, and UI paths.
- Reduce GPU stalls and overdraw in common gameplay and menu flows.
- Build repeatable profiling and regression checks so performance does not drift.

## Current Performance Issues (to validate and track)
1. **Frame pacing instability**
   - Symptoms: uneven frametimes despite acceptable average FPS.
   - Likely areas: sync timing, queue depth, shader compilation hitches.

2. **CPU hotspots in emulation loops**
   - Symptoms: high core utilization on mid-tier devices and battery drain.
   - Likely areas: interpreter/JIT transitions, memory access checks, tight loops.

3. **GPU pipeline stalls**
   - Symptoms: periodic drops when effects/state changes are heavy.
   - Likely areas: frequent pipeline state switches, synchronous resource uploads.

4. **UI thread contention**
   - Symptoms: menu lag while background tasks (asset scan/network/save) run.
   - Likely areas: synchronous file I/O and expensive list redraws.

5. **Asset loading hitches**
   - Symptoms: pauses during scene/game transition and texture warm-up.
   - Likely areas: blocking decode and upload on critical frame boundaries.

6. **Performance regressions not caught early**
   - Symptoms: improvements are lost between releases.
   - Likely areas: no standardized benchmark scenes + thresholds in CI/nightly checks.

## Roadmap

### Phase 0 — Baseline & Instrumentation (Week 1-2)
- Define performance targets by tier:
  - 16.7 ms/frame target for 60 FPS paths.
  - 33.3 ms/frame cap for fallback-heavy scenarios.
- Add lightweight telemetry markers around:
  - Emulation step, render submission, frame present, asset load jobs, UI update.
- Create a reproducible benchmark set:
  - 3 gameplay scenes (CPU-bound, GPU-bound, mixed), 2 UI stress scenes.
- Output a single benchmark report format (avg FPS, P95/P99 frametime, CPU%, GPU time, memory).

**Deliverables**
- Baseline dashboard/report committed with reference runs.
- Profiling capture guide for contributors.

### Phase 1 — Quick Wins (Week 3-4)
- Cache frequently recomputed state in hot paths.
- Reduce redundant draw/state updates in UI and renderer.
- Move non-critical synchronous I/O off the main thread.
- Add prewarming for common shaders and texture formats during non-interactive windows.

**Exit criteria**
- 10-15% reduction in P99 frametime spikes in benchmark scenes.
- No UI interaction block over 100 ms during background operations.

### Phase 2 — Core Runtime Optimizations (Week 5-8)
- Optimize emulation loop hotspots identified in profiling captures.
- Minimize JIT/interpreter boundary overhead.
- Improve memory locality in high-frequency data paths.
- Batch GPU resource updates and avoid per-frame allocations.
- Reduce pipeline/state thrash by sorting/batching where safe.

**Exit criteria**
- 15-25% CPU time reduction in CPU-bound benchmark.
- 20% fewer GPU stall events in GPU-bound benchmark.

### Phase 3 — Streaming & Asset Pipeline (Week 9-10)
- Introduce asynchronous decode/upload queues with frame-budget-aware scheduling.
- Add asset cache policy tuning (lifetime, eviction, warm sets).
- Prioritize visible/near-future assets to reduce transition hitches.

**Exit criteria**
- 50% fewer transition-related frame spikes.
- No single asset operation blocks the main thread > 8 ms in normal flow.

### Phase 4 — Guardrails & Continuous Verification (Week 11-12)
- Add automated benchmark runs in CI/nightly for target platforms.
- Define fail thresholds for key metrics (P95/P99 frametime, CPU budget, load stutter count).
- Publish a `PERF_CHANGELOG` entry template for each optimization PR.

**Exit criteria**
- Regression alerts generated automatically for threshold breaches.
- Performance status included in release readiness checks.

## Ownership Model
- **Performance lead**: triage, metric definitions, milestone accountability.
- **Runtime owner**: emulation/JIT/memory optimizations.
- **Renderer owner**: GPU frame graph, state changes, upload scheduling.
- **UI/Platform owner**: main-thread responsiveness and I/O offloading.

## Tracking Template
For each performance issue, track:
- ID / title
- Repro scene + platform
- Baseline metrics (avg FPS, P95/P99 frametime)
- Suspected subsystem
- Fix strategy
- Validation result
- Risk / rollback plan

## Risks & Mitigations
- **Risk**: Optimization changes correctness.
  - **Mitigation**: Pair perf changes with deterministic correctness checks.
- **Risk**: Improvements on one platform hurt another.
  - **Mitigation**: Platform-specific benchmark gates and toggles.
- **Risk**: Instrumentation overhead distorts measurements.
  - **Mitigation**: Low-overhead sampling and optional compile-time switches.

## Definition of Done
A performance fix is done when:
1. It improves agreed benchmark metrics by target amounts.
2. It passes functional regression checks.
3. It includes before/after measurements.
4. It is covered by ongoing benchmark guardrails.
