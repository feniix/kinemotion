# Kinemotion Presentation Demos

Demo scripts for the live presentation.

## Setup

### 1. Install Kinemotion

```bash
pip install kinemotion
```

### 2. Prepare Sample Videos

The `sample_data/` directory contains drop jump videos from a single athlete:

```bash
# Videos are already in sample_data/
# Format: IMG_XXXX.MOV files
```

### 3. Test Demos

```bash
# Test single video analysis
kinemotion dropjump-analyze sample_data/IMG_5809.MOV

# Test batch processing
python batch_processing_demo.py
```

## Demo Scripts

### Demo 1: Single Video Analysis (CLI)

**What it shows**: Basic command-line usage

```bash
# Simple analysis
kinemotion dropjump-analyze sample_data/IMG_5809.MOV

# Expected output:
# - Ground contact time
# - Flight time
# - Reactive Strength Index (RSI)
# - Jump height
```

**Talking points**:

- Processing speed (2-5 seconds)
- Automatic pose detection
- No manual marker placement needed

### Demo 2: Debug Visualization

**What it shows**: Visual feedback and pose tracking

```bash
kinemotion dropjump-analyze sample_data/IMG_5809.MOV --output debug_output.mp4
```

**Talking points**:

- 33 body landmarks tracked
- Ground contact and flight phase detection
- Velocity curves overlay
- Quality assessment

**Note**: Have the debug video ready to show if live processing is slow

### Demo 3: Batch Processing (Python API)

**What it shows**: Processing multiple videos in parallel

```bash
python batch_processing_demo.py
```

**What the script does**:

1. Finds all videos in `sample_data/`
2. Processes with 1 worker (sequential)
3. Processes with 4 workers (parallel)
4. Compares performance
5. Exports results to JSON

**Talking points**:

- Parallel processing speedup
- Team assessment workflow
- JSON export for analysis
- Error handling per video

### Demo 4: Python API Integration (Jupyter Notebook)

**What it shows**: Interactive Python API usage

```bash
# Open Jupyter notebook
jupyter notebook api_demo.ipynb
```

**What the notebook demonstrates**:

1. Single video analysis with API
2. Accessing all metrics
3. Custom team assessment workflow
4. Ranking athletes by RSI
5. CSV export for further analysis

**Talking points**:

- Interactive development environment
- Simple API for custom workflows
- Integration with existing systems
- Export to CSV for Excel/R/SPSS
- Extensibility for research

## Demo Tips

### Before Presenting

1. **Test all demos** - Run each one to verify they work
2. **Have backups** - Screenshots or pre-recorded videos
3. **Increase font size** - Terminal at 18pt minimum
4. **Clear output** - Remove old files before demo
5. **Position windows** - Terminal and slides side-by-side

### During Demo

1. **Explain first** - "This command will..."
2. **Type slowly** - People are reading along
3. **Highlight output** - Point to key metrics
4. **Pause for questions** - After each demo
5. **Have backup ready** - If demo fails, show screenshot

### If Demo Fails

1. Show pre-recorded video
2. Display screenshot of expected output
3. Explain what should happen
4. Move on confidently
5. Offer to show working version after presentation

## Troubleshooting

### Common Issues

**Videos not found**:

```bash
# Check directory
ls -la sample_data/

# Verify video format
file sample_data/*.MOV
```

**Import errors**:

```bash
# Verify installation
pip show kinemotion

# Reinstall if needed
pip install --upgrade kinemotion
```

**Processing errors**:

- Check video quality (not too dark/blurry)
- Verify full body is visible
- Ensure camera angle is correct (45° or sagittal)

## Sample Video Requirements

For best demo results, use drop jump videos with:

- ✅ Clear view of full body
- ✅ 45° or sagittal camera angle
- ✅ 30+ fps (60+ fps preferred)
- ✅ Good lighting
- ✅ 2-5 meters from subject
- ✅ Standard lens (not wide angle)
- ✅ Athlete drops from box (20-40cm height)
- ✅ Visible ground contact and takeoff

## Quick Reference

```bash
# Single video
kinemotion dropjump-analyze sample_data/IMG_5809.MOV

# With debug output
kinemotion dropjump-analyze sample_data/IMG_5809.MOV --output debug.mp4

# Batch processing
python batch_processing_demo.py

# Check version
kinemotion --version

# Get help
kinemotion dropjump-analyze --help
```

## Time Allocation

- Demo 1 (CLI): 2 minutes
- Demo 2 (Debug): 2 minutes
- Demo 3 (Batch): 3 minutes
- Demo 4 (API): 1 minute
- **Total**: 8-10 minutes (including questions)

## Success Criteria

✅ All demos run without errors
✅ Output is clearly visible on screen
✅ Audience can read terminal text
✅ Key metrics are highlighted
✅ Questions are answered confidently
