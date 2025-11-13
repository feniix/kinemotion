# Paper Downloader

Standalone utility to download research papers from DOIs using multiple sources including Sci-Hub.

## Features

- ✓ Downloads papers from DOIs
- ✓ Tries multiple Sci-Hub mirrors automatically
- ✓ Detailed progress logging for each paper
- ✓ Organizes downloads by research topic
- ✓ Handles click-through websites
- ✓ No dependencies added to main Kinemotion project

## Quick Start

### Download papers from DOI list

```bash
cd docs/research/paper-downloader
uv run python download.py
```

### Download a single paper

```bash
uv run python download.py --doi 10.1234/example.doi --topic velocity-based-training
```

### Download from custom DOI file

```bash
uv run python download.py --file my-papers.txt
```

## Configuration

### Method 1: Edit dois.txt (Simple)

Add DOIs to `dois.txt`, one per line:

```text
10.1234/your.doi.here
10.5678/another.doi
```

Then run:

```bash
uv run python download.py
```

### Method 2: Command-line arguments (Flexible)

Download a single paper to a specific topic:

```bash
uv run python download.py \
  --doi 10.1234/example.doi \
  --topic running-biomechanics \
  --output ../thirdparty
```

### Method 3: Custom DOI file

Create a file with DOIs and download:

```bash
echo "10.1234/paper1.doi" > my-papers.txt
echo "10.5678/paper2.doi" >> my-papers.txt

uv run python download.py --file my-papers.txt --topic misc
```

## Topic Directories

Available topic directories:

- `athlete-monitoring`
- `injury-prevention`
- `jump-performance`
- `running-biomechanics`
- `smartphone-technology`
- `velocity-based-training`
- `misc` (for uncategorized papers)

## Output

The script provides detailed logging:

```text
[1/5] Processing DOI: 10.1234/example.doi
  Topic: velocity-based-training

[10.1234/example.doi]
  → Trying Sci-Hub...
    Trying https://sci-hub.st...
    Found PDF link: https://2024.sci-hub.st/...
  ✓ SUCCESS: Downloaded (523.4 KB)
```

## How It Works

1. Reads DOIs from `dois.txt` or command-line
1. For each DOI, tries multiple Sci-Hub mirrors
1. Parses HTML to find embedded PDF link
1. Downloads PDF and saves to topic directory
1. Validates download (size > 10KB)
1. Reports success/failure

## Sci-Hub Mirrors

The script tries these mirrors in order:

- <https://sci-hub.st> (primary)
- <https://sci-hub.se> (fallback)
- <https://sci-hub.ru> (fallback)

## Dependencies

Installed automatically via `uv sync`:

- PyPaperBot >= 1.2.7 (for Sci-Hub access)
- requests (HTTP client)

## Troubleshooting

**No papers downloading?**

- Check internet connection
- Sci-Hub mirrors may be blocked in your region
- Try a VPN if needed

**Download fails with 403 error?**

- This is normal for some publishers
- Script automatically tries fallback mirrors

**Want to add more sources?**

- Edit `download.py` to add more download methods
- Can add Unpaywall, ResearchGate, institutional repos, etc.

## Example: Download New Papers

```bash
# Add DOIs to dois.txt
echo "10.1145/3375633" >> dois.txt
echo "10.1038/nature12373" >> dois.txt

# Run downloader
uv run python download.py

# Papers will be organized by topic based on doi_topics mapping in download.py
```

## Advanced: Modify Topic Mapping

Edit the `doi_topics` dictionary in `download.py`:

```python
doi_topics = {
    '10.1234/your.doi': 'your-topic-directory',
    '10.5678/another': 'running-biomechanics',
    # Add more mappings...
}
```

Papers not in the mapping go to the default topic specified in the script.

______________________________________________________________________

*Built for Kinemotion research documentation*
*Uses Sci-Hub for academic research purposes*
