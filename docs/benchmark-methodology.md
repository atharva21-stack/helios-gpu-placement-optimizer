# Benchmark methodology

Benchmarks use a fixed fleet, workload set, and random seed. Every strategy
receives a fresh fleet snapshot. Reports include acceptance, utilization,
fragmentation, contiguous blocks, cross-rack placements, and elapsed time.

The included runner is a reproducible smoke benchmark rather than a performance
claim. Large-fleet results should record machine type, Python and OR-Tools
versions, input checksums, solver limit, and at least five repetitions.
