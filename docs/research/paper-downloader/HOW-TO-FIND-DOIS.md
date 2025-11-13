# How to Find DOIs for Research Papers

## What is a DOI?

A **DOI (Digital Object Identifier)** is a unique permanent identifier for a research paper, like a social security number for academic articles.

**Format:** `10.XXXX/identifier`
**Example:** `10.3389/fphys.2016.00677`

## Where to Find DOIs

### 1. From the Paper Itself (Most Reliable)

**On the first page of any research paper**, usually in the header or footer:

```
DOI: 10.3389/fphys.2016.00677
https://doi.org/10.3389/fphys.2016.00677
```

**Look for:**

- Near the title
- In the copyright/citation section
- Bottom of first page
- Header of subsequent pages

### 2. From PubMed

Go to https://pubmed.ncbi.nlm.nih.gov and search for your paper:

**Example search:**

```
Jimenez-Reyes force velocity profiling 2016
```

On the paper's page, look for:

```
DOI: 10.3389/fphys.2016.00677
```

**Quick tip:** The DOI is always shown in the right sidebar under "Full text links"

### 3. From Google Scholar

Search on https://scholar.google.com:

**Example:**

```
"Effectiveness of individualized training force-velocity"
```

**Finding the DOI:**

1. Click on the paper title
1. Look at the URL of the publisher's page
1. OR click "Cite" → "BibTeX" and the DOI is in the citation

**Example BibTeX:**

```bibtex
@article{jimenez2016effectiveness,
  title={Effectiveness of an individualized training...},
  doi={10.3389/fphys.2016.00677},  ← HERE!
  ...
}
```

### 4. From the Journal Website

If you're on a journal article page (e.g., Frontiers, MDPI, Nature):

**Look for:**

- Top of the article
- "Cite this article" section
- Metadata section
- Right sidebar with article details

**Example from a journal page:**

```
Cite this article:
Jiménez-Reyes P, et al. (2016) Front. Physiol. 7:677
DOI: 10.3389/fphys.2016.00677  ← HERE!
```

### 5. From CrossRef (DOI Lookup Service)

If you have partial information, use https://search.crossref.org:

**Search by:**

- Title
- Author + year
- Journal + year

The results will show the DOI.

### 6. From the URL

Many publisher URLs contain the DOI:

**Example URLs:**

```
https://doi.org/10.3389/fphys.2016.00677
                  ^^^^^^^^^^^^^^^^^^^^^ This is the DOI

https://journals.sagepub.com/doi/10.1177/0363546518793657
                                 ^^^^^^^^^^^^^^^^^^^^^^^^ This is the DOI

https://www.frontiersin.org/articles/10.3389/fphys.2016.00677/full
                                      ^^^^^^^^^^^^^^^^^^^^^ This is the DOI
```

## Common DOI Prefixes by Publisher

This helps you recognize DOIs:

| Publisher        | DOI Prefix       | Example                      |
| ---------------- | ---------------- | ---------------------------- |
| Frontiers        | 10.3389          | 10.3389/fphys.2016.00677     |
| PLOS             | 10.1371          | 10.1371/journal.pone.0161356 |
| Nature/Springer  | 10.1038, 10.1007 | 10.1007/s40279-016-0479-z    |
| Wiley            | 10.1111          | 10.1111/sms.12678            |
| Taylor & Francis | 10.1080          | 10.1080/02640414.2014.996184 |
| SAGE             | 10.1177          | 10.1177/0363546518793657     |
| MDPI             | 10.3390          | 10.3390/sports6030063        |
| Human Kinetics   | 10.1123          | 10.1123/jab.2016-0104        |

## Practical Examples

### Example 1: You have a PDF

1. Open the PDF
1. Look at the top of the first page
1. Find text like "DOI: 10.xxxx/xxxxx"
1. Copy just the DOI part (not "DOI:" prefix)

### Example 2: You have a paper title

1. Search on PubMed or Google Scholar
1. Click on the result
1. Look for DOI in the metadata
1. Copy it

### Example 3: You have a citation

```
Jiménez-Reyes P, et al. (2016)
"Effectiveness of individualized training..."
Frontiers in Physiology, 7:677
```

Search on CrossRef or PubMed:

- "Jiménez-Reyes 2016 Frontiers Physiology"
- Find DOI: `10.3389/fphys.2016.00677`

## Using DOIs with the Paper Downloader

Once you have a DOI, use it with the downloader:

### Single paper:

```bash
uv run python download.py --doi 10.3389/fphys.2016.00677 --topic jump-performance
```

### Multiple papers (add to dois.txt):

```bash
echo "10.3389/fphys.2016.00677" >> dois.txt
echo "10.1371/journal.pone.0161356" >> dois.txt
uv run python download.py
```

## DOI Best Practices

✓ **Copy-paste DOIs** - Don't type them manually (easy to make mistakes)
✓ **Include the prefix** - Always include the `10.xxxx/` part
✓ **No extra spaces** - DOIs are case-insensitive but no spaces allowed
✓ **Works with or without https://doi.org/** - Just the DOI itself is fine

❌ **Don't include:**

- "DOI:" prefix
- Surrounding quotes
- URLs (unless specifically asked for)

## Quick Test

Try finding the DOI for this paper:
**"The validity and reliability of an iPhone app for measuring vertical jump performance"**

**Answer:** `10.1080/02640414.2014.996184`

**How to find it:**

1. Search on PubMed: "Balsalobre-Fernandez iPhone vertical jump 2015"
1. Open the result
1. DOI is shown in the article metadata

______________________________________________________________________

Now you can find and download any research paper you need!
