#!/usr/bin/env python3
"""Convert all PDFs in pdfs/ directory to markdown in markdown/ directory."""

import subprocess
import sys
from pathlib import Path


def convert_pdf_to_markdown(pdf_path: Path, output_path: Path) -> bool:
    """Convert a single PDF to markdown using pymupdf4llm."""
    try:
        # Import pymupdf4llm
        import pymupdf4llm

        # Convert PDF to markdown
        md_text = pymupdf4llm.to_markdown(str(pdf_path))

        # Write to output file
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(md_text, encoding="utf-8")

        return True
    except ImportError:
        print("Error: pymupdf4llm not installed. Installing...")
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "pymupdf4llm"],
            check=True,
            capture_output=True,
        )
        # Retry after installation
        import pymupdf4llm

        md_text = pymupdf4llm.to_markdown(str(pdf_path))
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(md_text, encoding="utf-8")
        return True
    except Exception as e:
        print(f"Error converting {pdf_path.name}: {e}")
        return False


def main():
    """Convert all PDFs to markdown."""
    base_dir = Path(__file__).parent
    pdfs_dir = base_dir / "pdfs"
    markdown_dir = base_dir / "markdown"

    # Find all PDFs
    pdf_files = sorted(pdfs_dir.rglob("*.pdf"))

    print(f"Found {len(pdf_files)} PDF files to convert")
    print()

    success_count = 0
    fail_count = 0

    for pdf_path in pdf_files:
        # Determine output path (preserve directory structure)
        relative_path = pdf_path.relative_to(pdfs_dir)
        output_path = markdown_dir / relative_path.with_suffix(".md")

        print(f"Converting: {relative_path}")

        if convert_pdf_to_markdown(pdf_path, output_path):
            print(f"  ✓ Saved to: {output_path.relative_to(base_dir)}")
            success_count += 1
        else:
            print("  ✗ Failed")
            fail_count += 1
        print()

    print("=" * 60)
    print("Conversion complete!")
    print(f"Success: {success_count}")
    print(f"Failed: {fail_count}")
    print(f"Total: {len(pdf_files)}")


if __name__ == "__main__":
    main()
