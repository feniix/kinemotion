#!/usr/bin/env python3
"""
Download research papers using requests and multiple sources.
Reads DOIs from dois.txt and downloads papers to ../thirdparty/
Logs progress for each paper attempt.
"""

import time
import urllib.parse
from pathlib import Path

import requests

BASE_DIR = Path(__file__).parent.parent / "thirdparty"

# Sci-Hub mirrors to try
SCIHUB_MIRRORS = [
    "https://sci-hub.st",
    "https://sci-hub.se",
    "https://sci-hub.ru",
]


def download_from_scihub(doi, output_path):
    """Try to download from Sci-Hub mirrors."""
    for mirror in SCIHUB_MIRRORS:
        try:
            url = f"{mirror}/{doi}"
            print(f"    Trying {mirror}...")

            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
            }
            response = requests.get(url, headers=headers, timeout=30)

            if response.status_code == 200:
                # Parse HTML to find PDF link
                import re

                # Try multiple patterns that Sci-Hub uses
                patterns = [
                    r'src="(//[^"]*\.pdf[^"]*)"',  # embed src
                    r'<iframe[^>]*src="([^"]*\.pdf[^"]*)"',  # iframe src
                    r'location\.href=[\'"](.*?\.pdf.*?)[\'"]',  # location.href
                    r'<embed[^>]*src="([^"]*\.pdf[^"]*)"',  # embed tag
                ]

                for pattern in patterns:
                    match = re.search(pattern, response.text)
                    if match:
                        pdf_url = match.group(1)

                        # Fix URL if needed
                        if pdf_url.startswith("//"):
                            pdf_url = f"https:{pdf_url}"
                        elif not pdf_url.startswith("http"):
                            pdf_url = f"{mirror}{pdf_url}"

                        print(f"    Found PDF link: {pdf_url[:80]}...")

                        try:
                            pdf_response = requests.get(
                                pdf_url, headers=headers, timeout=30
                            )

                            if (
                                pdf_response.status_code == 200
                                and len(pdf_response.content) > 10000
                            ):
                                output_path.write_bytes(pdf_response.content)
                                return True
                        except Exception as e:
                            print(f"    Error downloading PDF: {e}")
                            continue

        except Exception as e:
            print(f"    Error with {mirror}: {e}")
            continue

    return False


def download_paper(doi, topic_dir):
    """Download a single paper by DOI with logging."""
    safe_doi = urllib.parse.quote(doi, safe="")
    output_path = BASE_DIR / topic_dir / f"{safe_doi}.pdf"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"\n[{doi}]")

    # Try Sci-Hub
    print("  → Trying Sci-Hub...")
    if download_from_scihub(doi, output_path):
        size_kb = output_path.stat().st_size / 1024
        print(f"  ✓ SUCCESS: Downloaded ({size_kb:.1f} KB)")
        return True

    print("  ✗ FAILED: Could not download from any source")
    return False


def main():
    """Main download function."""
    import argparse

    parser = argparse.ArgumentParser(description="Download research papers from DOIs")
    parser.add_argument("--doi", help="Single DOI to download")
    parser.add_argument(
        "--file", default="dois.txt", help="File containing DOIs (default: dois.txt)"
    )
    parser.add_argument(
        "--topic",
        default=None,
        help="Topic directory for downloads (overrides mapping)",
    )
    parser.add_argument("--output", default=None, help="Custom output directory")
    args = parser.parse_args()

    # Read DOIs
    if args.doi:
        dois = [args.doi]
    else:
        dois_file = Path(__file__).parent / args.file
        if not dois_file.exists():
            print(f"Error: File not found: {dois_file}")
            return
        dois = [
            d.strip() for d in dois_file.read_text().strip().split("\n") if d.strip()
        ]

    # Override output directory if specified
    global BASE_DIR
    if args.output:
        BASE_DIR = Path(args.output)

    # Mapping DOIs to topic directories
    doi_topics = {
        "10.1080/02640414.2014.996184": "smartphone-technology",
        "10.3389/fphys.2016.00677": "jump-performance",
        "10.1249/MSS.0b013e31822d757a": "jump-performance",
        "10.1055/s-0033-1354382": "jump-performance",
        "10.1123/ijspp.2015-0638": "jump-performance",
        "10.1007/s40279-016-0479-z": "injury-prevention",
        "10.1080/14763141.2018.1545044": "jump-performance",
        "10.2478/hukin-2022-0098": "smartphone-technology",
        "10.1080/14763141.2020.1869458": "jump-performance",
        "10.1519/JSC.0000000000004337": "velocity-based-training",
        "10.1080/02640414.2016.1260152": "velocity-based-training",
        "10.1080/02640414.2015.1090010": "velocity-based-training",
        "10.1519/JSC.0b013e3181b62c5f": "velocity-based-training",
        "10.1111/sms.12678": "velocity-based-training",
        "10.1123/jab.2016-0104": "running-biomechanics",
        "10.1123/jab.21.2.167": "running-biomechanics",
        "10.1007/s40279-016-0474-4": "running-biomechanics",
        "10.1519/JSC.0000000000001316": "running-biomechanics",
        "10.1519/SSC.0b013e31823e83db": "injury-prevention",
        "10.1177/0363546518793657": "injury-prevention",
        "10.1177/03635465241237595": "running-biomechanics",
        "10.1080/02640414.2019.1677391": "running-biomechanics",
        "10.1080/14763141.2020.1792968": "running-biomechanics",
        "10.1080/14763141.2021.1873411": "running-biomechanics",
        "10.3390/sports6030093": "athlete-monitoring",
        "10.3390/sports6030063": "athlete-monitoring",
        "10.1123/ijspp.2018-0154": "athlete-monitoring",
        "10.1123/jsr.2013-0097": "injury-prevention",
        "10.1249/MSS.0000000000001241": "injury-prevention",
        "10.1371/journal.pone.0161356": "injury-prevention",
        "10.1177/0363546511419277": "injury-prevention",
        "10.1080/02640414.2018.1494908": "injury-prevention",
        "10.1136/bjsports-2015-094602": "injury-prevention",
        "10.1177/0363546510384223": "injury-prevention",
        "10.1016/j.jsams.2016.10.002": "injury-prevention",
        "10.1016/j.arthro.2019.07.018": "injury-prevention",
        "10.2147/OAJSM.S72432": "injury-prevention",
    }

    print("=" * 80)
    print(f"Paper Downloader - Starting download of {len(dois)} papers")
    print(f"Output directory: {BASE_DIR}")
    print("=" * 80)

    successful = 0
    failed = 0

    for i, doi in enumerate(dois, 1):
        # Use command-line topic if specified, otherwise use mapping
        topic = args.topic if args.topic else doi_topics.get(doi, "misc")
        print(f"\n[{i}/{len(dois)}] Processing DOI: {doi}")
        print(f"  Topic: {topic}")

        if download_paper(doi, topic):
            successful += 1
        else:
            failed += 1

        # Be respectful between downloads
        if i < len(dois):
            time.sleep(3)

    print(f"\n{'=' * 80}")
    print("DOWNLOAD COMPLETE")
    print(f"Successful: {successful}/{len(dois)}")
    print(f"Failed: {failed}/{len(dois)}")
    print(f"Check files in: {BASE_DIR}")
    print(f"{'=' * 80}")


if __name__ == "__main__":
    main()
