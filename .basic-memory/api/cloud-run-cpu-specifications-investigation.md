---
title: Cloud Run CPU Specifications Investigation
type: note
permalink: api/cloud-run-cpu-specifications-investigation
tags:
- cloud-run
- infrastructure
- cpu-specs
---

## Cloud Run 1 CPU & 4GB RAM Configuration

### Key Finding: Cloud Run Abstracts Infrastructure Details

Cloud Run does **not** publicly expose specific CPU processor details (family, generation, clock speed) for its container instances. This is by design - Cloud Run prioritizes abstraction over infrastructure visibility.

### What We Know:
- **Default CPU limit**: 1 CPU
- **Max memory with 1 CPU**: 4 GiB (matches user config)
- **Allocation model**: vCPU (virtual CPU, not pinned to physical core)
- **Underlying platform**: Runs on Google Cloud infrastructure (likely shares hardware with Compute Engine)

### Compute Engine CPU Options (for reference):
Cloud Run doesn't let you choose, but Compute Engine uses:
- **Intel Xeon processors** (Skylake through Granite Rapids generations)
  - Base frequencies: 1.9 - 3.1 GHz depending on generation
  - Turbo frequencies: 2.6 - 4.2 GHz
- **AMD EPYC processors** (Rome through Turin generations)
  - Base frequencies: 2.25 - 2.7 GHz
  - Max boost: 3.3 - 4.1 GHz

### To Determine Actual Hardware:
1. **CPU info from OS**: `lscpu` or `/proc/cpuinfo` inside container (reveals actual hypervisor CPU)
2. **Runtime profiling**: Use CPU benchmarks to infer processor type
3. **Google docs**: No official specification available - intentionally abstracted

### Practical Implication:
You cannot guarantee a specific processor family or clock speed in Cloud Run. Google allocates based on availability and load balancing across their infrastructure.
