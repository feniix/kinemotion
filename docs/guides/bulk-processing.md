# Bulk Video Processing with Kinemotion

This guide covers different approaches for processing large batches of videos using kinemotion as a library.

> **Note:** Some code examples in this guide use low-level API calls and may reference the removed `drop_height` parameter. For production use, prefer the high-level `process_dropjump_video()` and `process_cmj_video()` functions with `quality` presets (`"fast"`, `"balanced"`, or `"accurate"`) instead. See the [API documentation](../api/overview.md) for current best practices.

## Table of Contents

- [Quick Start: Local Parallel Processing](#quick-start-local-parallel-processing)
- [Cloud Platform: Modal.com](#cloud-platform-modalcom)
- [Cloud Platform: AWS Batch](#cloud-platform-aws-batch)
- [Cloud Platform: Google Cloud Run](#cloud-platform-google-cloud-run)
- [Jupyter Notebook Examples](#jupyter-notebook-examples)
- [Performance Comparison](#performance-comparison)
- [GPU Acceleration: Why Not?](#gpu-acceleration-why-not)

______________________________________________________________________

## Quick Start: Local Parallel Processing

The simplest approach uses Python's built-in multiprocessing to analyze multiple videos in parallel.

### Basic Example

```python
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from kinemotion.core import VideoProcessor, PoseTracker
from kinemotion.dropjump import (
    detect_ground_contact,
    calculate_drop_jump_metrics,
    compute_average_foot_position
)
from kinemotion.core.auto_tuning import auto_tune_parameters

def analyze_video(video_path: str, quality: str = "balanced") -> dict:
    """Analyze a single drop jump video."""
    try:
        # Use the high-level API which handles auto-tuning
        from kinemotion import process_dropjump_video

        metrics = process_dropjump_video(
            video_path,
            quality=quality,
            verbose=False
        )

        return {
            "video": video_path,
            "success": True,
            **metrics.to_dict()
        }
    except Exception as e:
        return {
            "video": video_path,
            "success": False,
            "error": str(e)
        }

# Process videos in parallel
video_dir = Path("./videos")
video_files = list(video_dir.glob("*.mp4"))

with ProcessPoolExecutor(max_workers=8) as executor:
    results = list(executor.map(
        lambda p: analyze_video(str(p), "balanced"),
        video_files
    ))

# Print summary
successful = sum(1 for r in results if r["success"])
print(f"Processed {successful}/{len(results)} videos successfully")
```

### Performance

- **8 cores**: ~30x faster than sequential processing
- **16 cores**: ~50x faster
- **Cost**: $0 (local machine) or ~$50/month (cloud VM)

______________________________________________________________________

## Cloud Platform: Modal.com

[Modal](https://modal.com) is a Python-native serverless platform that makes it easy to run batch processing jobs in the cloud with automatic scaling.

### Why Modal?

- **Simple Python API**: Decorators turn functions into cloud jobs
- **Auto-scaling**: Automatically scales to 100s of parallel workers
- **No infrastructure**: No Docker, Kubernetes, or server management
- **Pay per use**: Only pay for compute time used
- **Fast cold starts**: Jobs start in seconds

### Installation

```bash
pip install modal
modal setup  # Configure API key (free tier available)
```

### Complete Example

Create a file `batch_processor.py`:

```python
"""
Bulk video processing with Kinemotion on Modal.com

Usage:
    # Process videos from URLs
    modal run batch_processor.py --video-list videos.txt --quality balanced

    # Process videos from S3 bucket
    modal run batch_processor.py --s3-bucket my-videos --quality accurate
"""

import modal
from pathlib import Path

# Define the Modal app
app = modal.App("kinemotion-bulk-processor")

# Define the container image with dependencies
image = (
    modal.Image.debian_slim()
    .apt_install("ffmpeg")  # Required for video processing
    .pip_install(
        "kinemotion",
        "opencv-python-headless",  # Headless version for cloud
        "mediapipe",
        "numpy",
        "scipy",
        "boto3",  # For S3 support
    )
)

@app.function(
    image=image,
    cpu=4,  # 4 CPU cores per job
    memory=8192,  # 8GB RAM
    timeout=900,  # 15 minute timeout
    retries=2,  # Retry failed jobs twice
)
def process_single_video(
    video_url: str,
    drop_height: float = 0.40,
    quality: str = "balanced",
    output_json: bool = False
) -> dict:
    """
    Process a single video and return metrics.

    Args:
        video_url: URL to video file (http://, https://, or s3://)
        drop_height: Drop box height in meters
        quality: Quality preset (fast/balanced/accurate)
        output_json: Whether to save JSON output

    Returns:
        Dictionary with analysis results
    """
    import tempfile
    import urllib.request
    import json
    from kinemotion.core import VideoProcessor, PoseTracker
    from kinemotion.dropjump import (
        detect_ground_contact,
        calculate_drop_jump_metrics,
        compute_average_foot_position
    )
    from kinemotion.core.auto_tuning import auto_tune_parameters

    print(f"Processing: {video_url}")

    try:
        # Download video to temporary file
        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as tmp:
            if video_url.startswith('s3://'):
                # Download from S3
                import boto3
                bucket, key = video_url.replace('s3://', '').split('/', 1)
                s3 = boto3.client('s3')
                s3.download_file(bucket, key, tmp.name)
            else:
                # Download from HTTP(S)
                urllib.request.urlretrieve(video_url, tmp.name)

            video_path = tmp.name

        # Auto-tune parameters
        params = auto_tune_parameters(video_path, quality_preset=quality)
        print(f"  FPS: {params['fps']}, Quality: {quality}")

        # Process video
        video = VideoProcessor(video_path)
        tracker = PoseTracker(
            detection_confidence=params["detection_confidence"],
            tracking_confidence=params["tracking_confidence"]
        )

        # Extract landmarks
        landmarks = []
        frame_count = 0
        for frame in video.read_frames():
            pose_result = tracker.process_frame(frame)
            if pose_result:
                landmarks.append(pose_result)
            frame_count += 1
            if frame_count % 100 == 0:
                print(f"  Processed {frame_count} frames...")

        print(f"  Total frames: {frame_count}")

        # Detect contact states
        foot_positions = [compute_average_foot_position(lm) for lm in landmarks]
        contact_states = detect_ground_contact(
            foot_positions,
            video.fps,
            velocity_threshold=params["velocity_threshold"],
            min_contact_frames=params["min_contact_frames"],
            visibility_threshold=params["visibility_threshold"]
        )

        # Calculate metrics
        metrics = calculate_drop_jump_metrics(
            landmarks=landmarks,
            contact_states=contact_states,
            fps=video.fps,
            drop_height_m=drop_height
        )

        result = {
            "video_url": video_url,
            "success": True,
            "fps": video.fps,
            "frame_count": frame_count,
            **metrics.to_dict()
        }

        # Save JSON if requested
        if output_json:
            json_path = video_path.replace('.mp4', '_metrics.json')
            with open(json_path, 'w') as f:
                json.dump(result, f, indent=2)
            print(f"  Saved: {json_path}")

        print(f"  ✓ Success - Contact: {metrics.ground_contact_time_ms}ms, "
              f"Jump: {metrics.jump_height_m:.3f}m")

        return result

    except Exception as e:
        print(f"  ✗ Error: {e}")
        return {
            "video_url": video_url,
            "success": False,
            "error": str(e)
        }

@app.local_entrypoint()
def main(
    video_list: str = None,
    s3_bucket: str = None,
    s3_prefix: str = "",
    drop_height: float = 0.40,
    quality: str = "balanced",
    output_dir: str = None
):
    """
    Process multiple videos in parallel.

    Args:
        video_list: Path to text file with video URLs (one per line)
        s3_bucket: S3 bucket name to process all videos from
        s3_prefix: S3 prefix/folder to filter videos
        drop_height: Drop box height in meters
        quality: Quality preset (fast/balanced/accurate)
        output_dir: Directory to save results CSV
    """
    import json
    from datetime import datetime

    # Collect video URLs
    video_urls = []

    if video_list:
        # Load from file
        with open(video_list) as f:
            video_urls = [line.strip() for line in f if line.strip()]
        print(f"Loaded {len(video_urls)} videos from {video_list}")

    elif s3_bucket:
        # List from S3 bucket
        import boto3
        s3 = boto3.client('s3')
        paginator = s3.get_paginator('list_objects_v2')

        for page in paginator.paginate(Bucket=s3_bucket, Prefix=s3_prefix):
            for obj in page.get('Contents', []):
                key = obj['Key']
                if key.endswith(('.mp4', '.mov', '.avi')):
                    video_urls.append(f"s3://{s3_bucket}/{key}")

        print(f"Found {len(video_urls)} videos in s3://{s3_bucket}/{s3_prefix}")

    else:
        raise ValueError("Must provide --video-list or --s3-bucket")

    if not video_urls:
        print("No videos to process!")
        return

    # Process all videos in parallel
    print(f"\nProcessing {len(video_urls)} videos with quality={quality}, "
          f"drop_height={drop_height}m...")
    print(f"Modal will auto-scale to process videos in parallel.\n")

    start_time = datetime.now()

    # Map processes all videos in parallel (Modal handles scaling)
    results = list(process_single_video.map(
        video_urls,
        [drop_height] * len(video_urls),
        [quality] * len(video_urls),
        [False] * len(video_urls)  # output_json
    ))

    elapsed = (datetime.now() - start_time).total_seconds()

    # Print summary
    successful = sum(1 for r in results if r["success"])
    failed = len(results) - successful

    print(f"\n{'='*70}")
    print(f"PROCESSING COMPLETE")
    print(f"{'='*70}")
    print(f"Total videos: {len(results)}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print(f"Time: {elapsed:.1f}s ({elapsed/len(results):.1f}s per video average)")
    print(f"{'='*70}\n")

    # Save results to CSV
    if output_dir:
        import csv
        from pathlib import Path

        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)

        csv_file = output_path / f"results_{datetime.now():%Y%m%d_%H%M%S}.csv"

        with open(csv_file, 'w', newline='') as f:
            if results:
                writer = csv.DictWriter(f, fieldnames=results[0].keys())
                writer.writeheader()
                writer.writerows(results)

        print(f"Results saved to: {csv_file}")

    # Print failures
    if failed > 0:
        print("\nFailed videos:")
        for r in results:
            if not r["success"]:
                print(f"  - {r['video_url']}: {r.get('error', 'Unknown error')}")
```

### Usage Examples

```bash
# Process videos from URLs in a text file
modal run batch_processor.py \
    --video-list videos.txt \
    --drop-height 0.40 \
    --quality balanced \
    --output-dir results/

# Process all videos in an S3 bucket
modal run batch_processor.py \
    --s3-bucket my-training-videos \
    --s3-prefix "athletes/2024/" \
    --drop-height 0.60 \
    --quality accurate

# Fast processing for quick analysis
modal run batch_processor.py \
    --video-list videos.txt \
    --drop-height 0.40 \
    --quality fast
```

### Creating videos.txt

```text
https://example.com/videos/athlete1.mp4
https://example.com/videos/athlete2.mp4
s3://my-bucket/video1.mp4
s3://my-bucket/video2.mp4
```

### Cost Estimation

Modal pricing (as of 2024):

- **CPU**: $0.000025 per core-second
- **Memory**: $0.000003 per GB-second
- **Free tier**: 30 free GPU-hours per month

Example calculation for 100 videos (30 seconds each):

- Processing time per video: ~60 seconds (4 cores)
- Total compute: 100 videos × 60s × 4 cores = 24,000 core-seconds
- Cost: 24,000 × $0.000025 = **$0.60 for 100 videos**
- Plus memory: 24,000 × 8GB × $0.000003 = **$0.58**
- **Total: ~$1.20 for 100 videos**

### Monitoring

Modal provides a web dashboard to monitor jobs:

```bash
# View running jobs
modal app list

# View logs
modal app logs kinemotion-bulk-processor

# Stop all jobs
modal app stop kinemotion-bulk-processor
```

______________________________________________________________________

## Cloud Platform: AWS Batch

For organizations already using AWS, AWS Batch provides a fully managed batch processing service.

### Setup Overview

1. **Create Docker image with kinemotion**
1. **Push to Amazon ECR**
1. **Create AWS Batch job definition**
1. **Submit jobs via boto3 or AWS CLI**

### Dockerfile

Create `Dockerfile`:

```dockerfile
FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir \
    kinemotion \
    opencv-python-headless \
    mediapipe \
    boto3

# Copy processing script
COPY process_video.py /app/process_video.py
WORKDIR /app

ENTRYPOINT ["python", "process_video.py"]
```

### Processing Script

Create `process_video.py`:

```python
#!/usr/bin/env python3
"""
AWS Batch job for processing a single video.

Environment variables:
    VIDEO_URL: S3 URL of video to process
    DROP_HEIGHT: Drop height in meters
    QUALITY: Quality preset (fast/balanced/accurate)
    OUTPUT_BUCKET: S3 bucket for results
"""

import os
import sys
import json
import tempfile
import boto3
from kinemotion.core import VideoProcessor, PoseTracker
from kinemotion.dropjump import (
    detect_ground_contact,
    calculate_drop_jump_metrics,
    compute_average_foot_position
)
from kinemotion.core.auto_tuning import auto_tune_parameters

def main():
    # Get parameters from environment
    video_url = os.environ['VIDEO_URL']
    drop_height = float(os.environ.get('DROP_HEIGHT', '0.40'))
    quality = os.environ.get('QUALITY', 'balanced')
    output_bucket = os.environ['OUTPUT_BUCKET']

    print(f"Processing: {video_url}")
    print(f"Drop height: {drop_height}m, Quality: {quality}")

    # Parse S3 URL
    bucket, key = video_url.replace('s3://', '').split('/', 1)

    # Download video
    s3 = boto3.client('s3')
    with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as tmp:
        print(f"Downloading from S3...")
        s3.download_file(bucket, key, tmp.name)
        video_path = tmp.name

    # Process video
    params = auto_tune_parameters(video_path, quality_preset=quality)

    video = VideoProcessor(video_path)
    tracker = PoseTracker(
        detection_confidence=params["detection_confidence"],
        tracking_confidence=params["tracking_confidence"]
    )

    landmarks = []
    for frame in video.read_frames():
        pose_result = tracker.process_frame(frame)
        if pose_result:
            landmarks.append(pose_result)

    foot_positions = [compute_average_foot_position(lm) for lm in landmarks]
    contact_states = detect_ground_contact(
        foot_positions,
        video.fps,
        velocity_threshold=params["velocity_threshold"],
        min_contact_frames=params["min_contact_frames"],
        visibility_threshold=params["visibility_threshold"]
    )

    metrics = calculate_drop_jump_metrics(
        landmarks=landmarks,
        contact_states=contact_states,
        fps=video.fps,
        drop_height_m=drop_height
    )

    # Upload results to S3
    result = {
        "video_url": video_url,
        "success": True,
        **metrics.to_dict()
    }

    output_key = key.replace('.mp4', '_metrics.json')
    s3.put_object(
        Bucket=output_bucket,
        Key=output_key,
        Body=json.dumps(result, indent=2),
        ContentType='application/json'
    )

    print(f"Results uploaded to s3://{output_bucket}/{output_key}")
    print(f"Contact time: {metrics.ground_contact_time_ms}ms")
    print(f"Jump height: {metrics.jump_height_m:.3f}m")

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
```

### Submit Jobs

```python
import boto3

batch = boto3.client('batch')
s3 = boto3.client('s3')

# List videos to process
videos = []
paginator = s3.get_paginator('list_objects_v2')
for page in paginator.paginate(Bucket='my-videos', Prefix='dropjumps/'):
    for obj in page.get('Contents', []):
        if obj['Key'].endswith('.mp4'):
            videos.append(f"s3://my-videos/{obj['Key']}")

# Submit batch jobs
job_ids = []
for video_url in videos:
    response = batch.submit_job(
        jobName=f"kinemotion-{video_url.split('/')[-1]}",
        jobQueue='video-processing-queue',
        jobDefinition='kinemotion-processor:1',
        containerOverrides={
            'environment': [
                {'name': 'VIDEO_URL', 'value': video_url},
                {'name': 'DROP_HEIGHT', 'value': '0.40'},
                {'name': 'QUALITY', 'value': 'balanced'},
                {'name': 'OUTPUT_BUCKET', 'value': 'my-results'},
            ]
        }
    )
    job_ids.append(response['jobId'])

print(f"Submitted {len(job_ids)} jobs")
```

______________________________________________________________________

## Cloud Platform: Google Cloud Run

Google Cloud Run Jobs provide a simpler alternative to AWS Batch.

### Create Container

Same Dockerfile as AWS Batch section.

### Deploy Job

```bash
# Build and push container
gcloud builds submit --tag gcr.io/PROJECT_ID/kinemotion-processor

# Create job
gcloud run jobs create kinemotion-batch \
    --image gcr.io/PROJECT_ID/kinemotion-processor \
    --tasks 100 \
    --max-retries 2 \
    --task-timeout 15m \
    --cpu 4 \
    --memory 8Gi \
    --set-env-vars DROP_HEIGHT=0.40,QUALITY=balanced
```

### Execute Job

```bash
# Execute with environment variables
gcloud run jobs execute kinemotion-batch \
    --set-env-vars VIDEO_URL=gs://bucket/video1.mp4

# Or use task parallelism
gcloud run jobs execute kinemotion-batch \
    --tasks 50 \
    --set-env-vars VIDEO_LIST=gs://bucket/videos.txt
```

______________________________________________________________________

## Jupyter Notebook Examples

Perfect for exploratory analysis and visualization.

### Basic Batch Analysis

```python
# notebook.ipynb
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
from kinemotion.dropjump import analyze_video

# Process videos
video_dir = Path("./videos")
videos = list(video_dir.glob("*.mp4"))

with ProcessPoolExecutor(max_workers=8) as executor:
    results = list(executor.map(
        lambda p: analyze_video(str(p), drop_height=0.40),
        videos
    ))

# Create DataFrame
df = pd.DataFrame([r.to_dict() for r in results if r])
df['filename'] = [v.name for v in videos]

# Display results
display(df[['filename', 'ground_contact_time_ms', 'flight_time_ms', 'jump_height_m']])

# Visualize
fig, axes = plt.subplots(1, 3, figsize=(15, 5))

sns.histplot(df['ground_contact_time_ms'], ax=axes[0], kde=True)
axes[0].set_title('Ground Contact Time')
axes[0].set_xlabel('Time (ms)')

sns.histplot(df['flight_time_ms'], ax=axes[1], kde=True)
axes[1].set_title('Flight Time')
axes[1].set_xlabel('Time (ms)')

sns.histplot(df['jump_height_m'], ax=axes[2], kde=True)
axes[2].set_title('Jump Height')
axes[2].set_xlabel('Height (m)')

plt.tight_layout()
plt.show()

# Export
df.to_csv('results.csv', index=False)
df.to_excel('results.xlsx', index=False)
```

______________________________________________________________________

## Performance Comparison

Based on typical 30fps, 10-second videos (~300 frames):

| Method                    | Setup Time | Processing Time (100 videos) | Cost      | Scalability |
| ------------------------- | ---------- | ---------------------------- | --------- | ----------- |
| Sequential (1 core)       | 0 min      | ~30 min                      | $0        | Poor        |
| Local Parallel (8 cores)  | 0 min      | ~4 min                       | $0        | Limited     |
| Local Parallel (16 cores) | 0 min      | ~2 min                       | $50/mo VM | Limited     |
| Modal.com                 | 10 min     | ~1-2 min                     | ~$1.20    | Excellent   |
| AWS Batch                 | 60 min     | ~1-2 min                     | ~$2-5     | Excellent   |
| Google Cloud Run          | 30 min     | ~1-2 min                     | ~$2-5     | Excellent   |

**Recommendation**: Start with local parallel processing, move to Modal.com when you need cloud scale.

______________________________________________________________________

## GPU Acceleration: Why Not?

You might think GPU acceleration would speed up video processing. Here's why it won't:

### MediaPipe GPU Reality

1. **Python package limitations**: pip-installed MediaPipe doesn't include GPU support
1. **Complex setup**: Requires custom build with OpenGL/CUDA
1. **Limited speedup**: Benchmarks show 1.5-2x at best, sometimes SLOWER:
   - CPU: 19ms per frame
   - GPU: 23ms per frame (overhead from data transfer)
1. **Batch size**: MediaPipe processes one frame at a time, negating GPU batch benefits

### CPU Parallelism is Superior

- **8x CPU cores**: 8x speedup (trivial to implement)
- **GPU acceleration**: 1.5-2x speedup (complex, unreliable)
- **Result**: CPU parallelism is 4-5x better!

### When GPU Might Help

GPU acceleration could theoretically help if:

- You're processing 4K/8K videos (larger frames)
- You're using batch-optimized models (MediaPipe isn't)
- You have 100+ videos queued per GPU (amortize overhead)

But even then, the complexity rarely justifies the marginal gains.

### Recommendation

**Stick with CPU parallelism**. It's simpler, faster, and more cost-effective for kinemotion.

______________________________________________________________________

## Best Practices

### Error Handling

Always wrap video processing in try-except to handle corrupt videos:

```python
def process_video_safe(video_path: str) -> dict:
    try:
        result = analyze_video(video_path)
        return {"success": True, **result.to_dict()}
    except Exception as e:
        return {
            "success": False,
            "video": video_path,
            "error": str(e)
        }
```

### Progress Tracking

Use tqdm for progress bars:

```python
from tqdm import tqdm
from concurrent.futures import ProcessPoolExecutor, as_completed

with ProcessPoolExecutor(max_workers=8) as executor:
    futures = {
        executor.submit(analyze_video, str(p)): p
        for p in video_files
    }

    results = []
    for future in tqdm(as_completed(futures), total=len(futures)):
        results.append(future.result())
```

### Memory Management

For large batches, process in chunks to avoid memory issues:

```python
def process_in_chunks(videos, chunk_size=100):
    all_results = []

    for i in range(0, len(videos), chunk_size):
        chunk = videos[i:i + chunk_size]
        print(f"Processing chunk {i//chunk_size + 1}...")

        with ProcessPoolExecutor(max_workers=8) as executor:
            results = list(executor.map(analyze_video, chunk))

        all_results.extend(results)

    return all_results
```

### Result Validation

Check for common issues:

```python
def validate_results(results):
    issues = []

    for r in results:
        if not r["success"]:
            issues.append(f"Failed: {r['video']}")
        elif r.get("ground_contact_time_ms", 0) < 50:
            issues.append(f"Suspiciously short contact: {r['video']}")
        elif r.get("jump_height_m", 0) > 1.0:
            issues.append(f"Suspiciously high jump: {r['video']}")

    return issues
```

______________________________________________________________________

## Troubleshooting

### "Too many open files" error

Increase file descriptor limit:

```bash
ulimit -n 4096
```

Or in Python:

```python
import resource
resource.setrlimit(resource.RLIMIT_NOFILE, (4096, 4096))
```

### Memory issues

Reduce max_workers or use chunked processing:

```python
# Instead of max_workers=16, use fewer
with ProcessPoolExecutor(max_workers=4) as executor:
    ...
```

### Slow S3 downloads

Use concurrent downloads:

```python
import concurrent.futures

def download_from_s3(url):
    # Download logic
    pass

with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
    local_paths = list(executor.map(download_from_s3, s3_urls))
```

______________________________________________________________________

## Summary

**For most users:**

1. Start with local parallel processing (free, immediate)
1. Scale to Modal.com when you need cloud processing (easiest)
1. Skip GPU acceleration (not worth the complexity)

**For enterprise:**

1. Use AWS Batch or Google Cloud Run for integration with existing infrastructure
1. Set up monitoring and error handling
1. Implement retry logic and result validation

The beauty of kinemotion being a library is its flexibility - choose the approach that fits your needs and infrastructure!
