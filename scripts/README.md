# Validation Scripts

Scripts for validating kinemotion accuracy and reliability.

______________________________________________________________________

## Quick Start

### Test Determinism (Task 1.3)

**Purpose:** Verify algorithm produces identical results for identical inputs

```bash
# Run complete test (100 runs, ~3-5 minutes)
./scripts/test_determinism.sh

# Analyze variance in detail
./scripts/analyze_determinism_variance.py
```

**What it does:**

1. Creates 100 symlinks to same video
1. Processes all with batch mode (4 workers)
1. Compares all results for identity
1. Reports variance statistics

**Expected result:**

```text
✅ SUCCESS: All 100 runs produced identical results
Algorithm is DETERMINISTIC!
```

______________________________________________________________________

## Available Scripts

### `setup-google-oauth.sh`

**Purpose:** Automate Google Cloud OAuth setup for Supabase authentication

**Idempotent:** ✅ Yes - safe to run multiple times. Checks for existing configuration and allows skipping steps.

**Usage:**

```bash
# Basic usage (uses defaults)
./scripts/setup-google-oauth.sh

# With environment variables
GCP_PROJECT_ID=my-project \
SUPABASE_PROJECT_ID=abc123 \
FRONTEND_URL=https://myapp.vercel.app \
./scripts/setup-google-oauth.sh
```

**What it does:**

1. Checks/installs gcloud CLI
1. Authenticates with Google Cloud
1. Creates/selects Google Cloud project
1. Enables required APIs
1. Guides through OAuth consent screen setup
1. Guides through OAuth client creation
1. Collects credentials for Supabase configuration

**Configuration:**

- `GCP_PROJECT_ID` - Google Cloud project ID (default: `kinemotion-backend`)
- `APP_NAME` - Application name (default: `Kinemotion`)
- `SUPABASE_PROJECT_ID` - Supabase project ID (prompted if not set)
- `FRONTEND_URL` - Production frontend URL (default: `https://kinemotion.vercel.app`)
- `LOCAL_PORT` - Local development port (default: `5173`)

**Requirements:**

- `gcloud` CLI installed and authenticated
- Google Cloud account with billing enabled (for OAuth)

**Output:**

- OAuth Client ID and Client Secret
- Instructions for configuring Supabase Dashboard
- Direct links to Google Cloud Console

**See also:**

- `.basic-memory/authentication/Supabase Google OAuth Setup Guide.md`

______________________________________________________________________

### `test_determinism.sh`

#### Test-retest determinism validation

- Runs same video 100 times
- Uses batch processing (realistic usage)
- Compares all outputs for identity
- **Time:** ~5 minutes
- **Output:** `data/determinism_test/results/`

**Exit codes:**

- `0` - Success (deterministic)
- `1` - Failure (non-deterministic or error)

______________________________________________________________________

### `analyze_determinism_variance.py`

#### Detailed variance analysis

- Calculates mean, std, range for all metrics
- Identifies which fields vary (if any)
- Distinguishes floating point vs real variance
- **Time:** \<1 minute
- **Requires:** Results from `test_determinism.sh`

**Output example:**

```text
Jump Height (m):
  Mean:  0.4540739478
  Std:   0.000000000000000
  Range: 0.000000000000000
  ✅ PERFECT: Zero variance
```

______________________________________________________________________

## Future Scripts (Planned)

### `test_known_heights.py` (Task 1.4)

Drop objects from measured heights, validate timing accuracy

### `parameter_sensitivity.py` (Task 1.5)

Test how algorithm parameters affect results

### `compare_to_manual.py` (Task 2.1)

Compare automated detection vs manual frame selection

______________________________________________________________________

## Validation Workflow

```text
1. Test Determinism     ← ./scripts/test_determinism.sh
   ↓ (if pass)
2. Known Heights        ← ./scripts/test_known_heights.py (future)
   ↓ (if pass)
3. Parameter Sensitivity ← ./scripts/parameter_sensitivity.py (future)
   ↓ (if pass)
4. Manual Comparison    ← ./scripts/compare_to_manual.py (future)
   ↓ (if pass)
5. Technical Report     ← Write validation report
```

______________________________________________________________________

## Requirements

**All scripts require:**

- Python 3.10+
- kinemotion installed (`uv sync`)
- Test videos in `samples/` directory

**Platform:**

- macOS, Linux, Windows (WSL)

______________________________________________________________________

## Output Directories

Validation data stored in `data/` (gitignored):

```text
data/
├── determinism_test/
│   ├── videos/          # 100 symlinks to test video
│   └── results/         # 100 JSON outputs
├── known_heights/       # (future)
├── parameter_sweep/     # (future)
└── manual_comparison/   # (future)
```

______________________________________________________________________

## Documentation

Results documented in `docs/validation/`:

- **determinism-test.md** - This test's results
- **known-height-validation.md** - (future)
- **parameter-sensitivity.md** - (future)
- **manual-comparison-study.md** - (future)

______________________________________________________________________

## Getting Help

If tests fail:

1. Check `docs/validation/determinism-test.md` for troubleshooting
1. Run variance analysis: `./scripts/analyze_determinism_variance.py`
1. Open issue with test results

______________________________________________________________________

## Contributing

When adding new validation scripts:

1. Follow naming: `test_*.sh` or `*_validation.py`
1. Make executable: `chmod +x scripts/your_script.sh`
1. Document in this README
1. Add results template to `docs/validation/`
1. Update validation roadmap if needed

______________________________________________________________________

See `docs/development/validation-roadmap.md` for complete validation plan.
