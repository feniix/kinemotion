# Research Papers - Downloaded Collection

This directory contains downloaded research papers referenced in the Kinemotion project, organized by topic for easy access and searchability.

## Download Summary

**Total Papers Downloaded:** 39/43 PDFs (~36MB)
**Download Date:** 2025-11-13
**Download Method:** Sci-Hub via custom Python script (paper-downloader/)
**Success Rate:** ~91%

## Directory Organization

Papers are organized by research topic:

### `/athlete-monitoring/` (3 papers)

- HRV and recovery monitoring
- Training camp observations
- Individual athlete tracking

### `/injury-prevention/` (15 papers)

- Neuromuscular risk factors
- Hamstring injury prevention
- Landing mechanics
- Flexibility/ROM assessment
- Hip/groin/shoulder injuries

### `/jump-performance/` (9 papers)

- Force-velocity profiling
- Vertical jump assessment
- Reactive strength testing
- Countermovement jump mechanics

### `/running-biomechanics/` (9 papers)

- Running economy
- Gait mechanics
- Sprint mechanics assessment
- Stiffness measurement
- Running styles

### `/smartphone-technology/` (2 papers)

- iPhone/smartphone apps for jump measurement
- Mobile technology validation studies

### `/velocity-based-training/` (5 papers)

- Load-velocity relationships
- Barbell velocity measurement
- VBT for programming

## File Naming Convention

Files are named using URL-encoded DOIs for precise identification:

- Format: `{URL-encoded-DOI}.pdf`
- Example: `10.3389%2Ffphys.2016.00677.pdf`

To decode a filename to its DOI, use URL decoding:

- `10.3389%2Ffphys.2016.00677` → `10.3389/fphys.2016.00677`

## Papers Not Downloaded (4 papers)

Some papers were not available on Sci-Hub:

1. `10.2478/hukin-2022-0098` - Bishop 2022 (My Jump Lab validation)
1. `10.1080/14763141.2020.1869458` - Wells 2022 (Golf CMJ)
1. `10.1519/JSC.0000000000004337` - Balsalobre-Fernandez 2023 (AI barbell)
1. Paper #9 - Unpublished Substack blog

These can be accessed via institutional library or the links in `online-references-for-papers.md`.

## Searching the Collection

### By Topic

```bash
ls thirdparty/injury-prevention/
```

### By Author (using DOI)

```bash
find thirdparty -name "*morin*" -o -name "*balsalobre*"
```

### By Year (check DOI or use pdfinfo)

```bash
pdfinfo thirdparty/jump-performance/10.3389%2Ffphys.2016.00677.pdf | grep CreationDate
```

### Full-text search (requires pdfgrep)

```bash
pdfgrep -r "force-velocity" thirdparty/
```

## Verification

All downloaded files are validated as PDF documents:

```bash
find thirdparty -name "*.pdf" -exec file {} \; | grep "PDF document"
```

## Re-downloading

To re-run the downloader:

```bash
cd docs/research/paper-downloader
uv run python download.py
```

The script will:

- Log progress for each DOI
- Try multiple Sci-Hub mirrors
- Show success/failure for each paper
- Display file sizes

## Legal Note

Papers were downloaded from Sci-Hub for personal research and education purposes. Users are responsible for compliance with local copyright laws and institutional policies. Open access alternatives are listed in `online-references-for-papers.md`.

## Related Files

- `../online-references-for-papers.md` - Complete citation list with DOIs and open access links
- `../list-of-papers-about-sports-science-biomechanics.md` - Original paper list
- `../paper-downloader/` - Download scripts and configuration

______________________________________________________________________

*Last updated: 2025-11-13*
*Papers auto-downloaded using paper-downloader script*
