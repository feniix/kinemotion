#!/bin/bash
# Test-Retest Determinism Test
# Runs the same video 100 times and verifies identical results

set -e  # Exit on error

VIDEO="samples/cmjs/cmj.mp4"
TEST_DIR="data/determinism_test"
VIDEOS_DIR="$TEST_DIR/videos"
RESULTS_DIR="$TEST_DIR/results"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
# shellcheck disable=SC2034
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "=========================================="
echo "KINEMOTION DETERMINISM TEST"
echo "=========================================="
echo ""

# Check video exists
if [ ! -f "$VIDEO" ]; then
    echo -e "${RED}❌ Error: Test video not found: $VIDEO${NC}"
    exit 1
fi

# Setup
echo "Setting up test environment..."
rm -rf "$TEST_DIR"
mkdir -p "$VIDEOS_DIR" "$RESULTS_DIR"

# Create 100 symlinks to same video
echo "Creating 100 symlinks to $VIDEO..."
for i in $(seq -f "%03g" 1 100); do
    ln -s "../../../$VIDEO" "$VIDEOS_DIR/test_${i}.mp4"
done

echo -e "${GREEN}✓${NC} Created 100 test videos (symlinks)"
echo ""

# Process all with batch mode
echo "Processing 100 videos with batch mode (4 workers)..."
echo "This tests both algorithm determinism AND batch processing stability"
echo ""

uv run kinemotion cmj-analyze "$VIDEOS_DIR"/*.mp4 \
    --batch \
    --workers 8 \
    --json-output-dir "$RESULTS_DIR" \
    --quality balanced

echo ""
echo "Batch processing complete. Comparing results..."
echo ""

# Compare results with Python
python3 << 'PYTHON'
import json
from pathlib import Path
import sys

results_dir = Path("data/determinism_test/results")
json_files = sorted(results_dir.glob("test_*.json"))

if len(json_files) == 0:
    print("❌ Error: No result files found")
    sys.exit(1)

print(f"Comparing {len(json_files)} result files...")

# Load baseline (first result - extract DATA section only)
with open(json_files[0]) as f:
    baseline_full = json.load(f)
    baseline_data = baseline_full['data']

# Compare all others to baseline (DATA section only)
# Metadata (timestamps, processing_time, source_path) should vary
mismatches = []
for i, file in enumerate(json_files[1:], start=2):
    with open(file) as f:
        current_full = json.load(f)
        current_data = current_full['data']

    if current_data != baseline_data:
        mismatches.append((i, file.name))

# Report results
print("=" * 60)
if mismatches:
    print(f"❌ FAILED: Found {len(mismatches)} mismatches out of {len(json_files)} runs")
    print("\nNon-deterministic! Files differ:")
    for run_num, filename in mismatches[:5]:  # Show first 5
        print(f"  - Run #{run_num}: {filename}")

    if len(mismatches) > 5:
        print(f"  ... and {len(mismatches) - 5} more")

    print("\n⚠️  Investigation needed:")
    print("  - Check for random number generators")
    print("  - Look for uninitialized variables")
    print("  - Verify no timestamps in calculations")
    print("  - Test MediaPipe stability")
    sys.exit(1)
else:
    print(f"✅ SUCCESS: All {len(json_files)} runs produced identical results")
    print("")
    print("Algorithm is DETERMINISTIC!")
    print("")
    print("This means:")
    print("  ✓ Same input always produces same output")
    print("  ✓ Results are reproducible")
    print("  ✓ No random variation")
    print("  ✓ Reliable for validation studies")
    print("")
    print("=" * 60)
    sys.exit(0)
PYTHON

exit_code=$?

if [ $exit_code -eq 0 ]; then
    echo ""
    echo -e "${GREEN}Next step: Document results in docs/validation/determinism-test.md${NC}"
fi

exit $exit_code
