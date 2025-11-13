# Manual Download Guide for Missing Papers

## Papers to Download Manually

### Paper #17 - Balsalobre-Fernández et al. 2020

**FULL TITLE:**
"Validity and reliability of a computer-vision-based smartphone app for measuring barbell trajectory during the snatch"

**AUTHORS:**
Balsalobre-Fernández, C., Geiser, G., Krzyszkowski, J., and Kipp, K.

**YEAR:** 2020
**JOURNAL:** Journal of Sports Sciences

**WHERE TO DOWNLOAD:**

- PubMed: https://pubmed.ncbi.nlm.nih.gov/32079484/
- Check PubMed page for DOI and full-text links

**SAVE AS:**
`2020_Balsalobre-Fernandez_Barbell-Trajectory-Snatch.pdf`

**SAVE TO:**
`docs/research/thirdparty/pdfs/velocity-based-training/`

______________________________________________________________________

### Paper #22 - Buchheit et al. 2015

**FULL TITLE:**
"Assessing Stride Variables and Vertical Stiffness with GPS-Embedded Accelerometers: Preliminary Insights for the Monitoring of Neuromuscular Fatigue on the Field"

**AUTHORS:**
Buchheit, M., Gray, A., and Morin, J-B.

**YEAR:** 2015
**JOURNAL:** Journal of Sport Science & Medicine, 14: 698–701

**WHERE TO DOWNLOAD:**

- PMC (Open Access): https://pmc.ncbi.nlm.nih.gov/articles/PMC4657410/
- Direct PDF: https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4657410/pdf/jssm-14-698.pdf
- PubMed: https://pubmed.ncbi.nlm.nih.gov/26664264/

**SAVE AS:**
`2015_Buchheit_GPS-Accelerometers-Stride-Stiffness.pdf`

**SAVE TO:**
`docs/research/thirdparty/pdfs/athlete-monitoring/`

______________________________________________________________________

### Paper #32 - Foster et al. 2001

**FULL TITLE:**
"A New Approach to Monitoring Exercise Training"

**AUTHORS:**
Foster, C., Florhaug, J.A., Franklin, J., Gottschall, L., Hrovatin, L.A., Parker, S., Doleshal, P., and Dodge, C.

**YEAR:** 2001
**JOURNAL:** Journal of Strength and Conditioning Research, 15(1), 109–115

**WHERE TO DOWNLOAD:**

- PubMed: https://pubmed.ncbi.nlm.nih.gov/11708692/
- DOI: https://doi.org/10.1519/00124278-200102000-00019
- ResearchGate: https://www.researchgate.net/publication/11645805

**SAVE AS:**
`2001_Foster_Session-RPE-Training-Monitoring.pdf`

**SAVE TO:**
`docs/research/thirdparty/pdfs/athlete-monitoring/`

______________________________________________________________________

## After Downloading

### Step 1: Place PDFs in correct directories (as shown above)

### Step 2: Convert to markdown

```bash
cd docs/research/thirdparty

# Convert the new PDFs
pdftotext pdfs/athlete-monitoring/2015_Buchheit_GPS-Accelerometers-Stride-Stiffness.pdf - > markdown/athlete-monitoring/2015_Buchheit_GPS-Accelerometers-Stride-Stiffness.md

pdftotext pdfs/athlete-monitoring/2001_Foster_Session-RPE-Training-Monitoring.pdf - > markdown/athlete-monitoring/2001_Foster_Session-RPE-Training-Monitoring.md

pdftotext pdfs/velocity-based-training/2020_Balsalobre-Fernandez_Barbell-Trajectory-Snatch.pdf - > markdown/velocity-based-training/2020_Balsalobre-Fernandez_Barbell-Trajectory-Snatch.md
```

### Step 3: Update online-references-for-papers.md

Add these lines to the appropriate paper sections:

**For Paper #17:**

```markdown
**Local PDF:** [2020_Balsalobre-Fernandez_Barbell-Trajectory-Snatch.pdf](./pdfs/velocity-based-training/2020_Balsalobre-Fernandez_Barbell-Trajectory-Snatch.pdf)
**Local Markdown:** [2020_Balsalobre-Fernandez_Barbell-Trajectory-Snatch.md](./markdown/velocity-based-training/2020_Balsalobre-Fernandez_Barbell-Trajectory-Snatch.md)
```

**For Paper #22:**

```markdown
**Local PDF:** [2015_Buchheit_GPS-Accelerometers-Stride-Stiffness.pdf](./pdfs/athlete-monitoring/2015_Buchheit_GPS-Accelerometers-Stride-Stiffness.pdf)
**Local Markdown:** [2015_Buchheit_GPS-Accelerometers-Stride-Stiffness.md](./markdown/athlete-monitoring/2015_Buchheit_GPS-Accelerometers-Stride-Stiffness.md)
```

**For Paper #32:**

```markdown
**Local PDF:** [2001_Foster_Session-RPE-Training-Monitoring.pdf](./pdfs/athlete-monitoring/2001_Foster_Session-RPE-Training-Monitoring.pdf)
**Local Markdown:** [2001_Foster_Session-RPE-Training-Monitoring.md](./markdown/athlete-monitoring/2001_Foster_Session-RPE-Training-Monitoring.md)
```

______________________________________________________________________

**Once complete, you'll have 41/43 papers (95% complete)!**
*(Only #9 Substack blog is not a formal paper)*
