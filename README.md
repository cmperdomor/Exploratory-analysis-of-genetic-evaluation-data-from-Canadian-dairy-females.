# Regional Patterns in Canadian Dairy Genetic Evaluations

**Data source:** [Lactanet](https://www.lactanet.ca) — Canadian dairy cattle genetic evaluation service.

## Purpose

Provincial genetic reports are usually read on their own, each describing one region's elite dairy population independently. This project combined the top 400 LPI animals from all 10 provinces into a single dataset to ask a broader question: do regional differences in genetic merit go along with regional differences in the *information* supporting those evaluations? Provinces are the unit of observation here, not the subject of the study,the subject is how that information is assembled.

**Throughout this project, "information integration" means the combination of pedigree, genomic testing, and official phenotype-based records (production and classification) behind an animal's genetic evaluation.** Genomic testing is one piece of that combination, not the focus on its own.

## Two concepts worth knowing before the numbers

An **Estimated Breeding Value (EBV)** is not a direct measurement — it's a statistical prediction of an animal's genetic merit, built from whatever information is available for it. **Reliability** reflects how much confidence to place in that prediction: how close it's likely to be to the animal's true genetic merit.

An important characteristic of this dataset is that it represents a ranking rather than a fixed cohort. Each provincial dataset contains the top 400 females according to Lifetime Performance Index (LPI) at the time of each official genetic evaluation release. Consequently, high-ranking animals may appear in multiple consecutive releases if their LPI remains competitive. This persistence reflects the design of a top-ranked selection rather than incomplete data collection or missing animals. Individuals remain in the dataset until they are surpassed by newly evaluated animals with higher genetic merit.

## The conceptual framework

```
   Pedigree        Genomic testing        Official phenotype-based
                                           records (production +
                                           classification)
        │                 │                        │
        └─────────────────┴────────────────────────┘
                           │
                           ▼
                 Genetic evaluation (EBV)
                           │
                           ▼
                       Reliability
                           │
                           ▼
                  Selection decisions
```

Animals with similar LPI values may still differ substantially in the information supporting those evaluations. This project examines how much that varies across Canada, and what it's associated with.

## What's in this repo

- `genetic_analysis_Code.ipynb` — the full analysis, step by step, in a Jupyter notebook.
- `images/` — every chart from the notebook, saved as PNG.
- `methodology.md` — every statistical method used and why.
- `conclusion.md` — the full findings, discussion, and a confidence rating for each conclusion.

## What this analysis found

**Information sources differ sharply in how much confidence they support.** Pedigree alone yields the lowest average reliability (37.9% on protein); genomic testing alone already exceeds official phenotype-based records alone (81.0% vs. 56.2%); the two combined yield the highest reliability of any source (84.1%). Full breakdown in `conclusiones_generales.md`.

**That same pattern holds at the regional level.** Provinces with a higher share of genomically tested animals in their elite population tend to show higher average LPI — a measured association across all 10 provinces (r=0.73, p=0.016, confirmed stable under robustness checks), not a claim about which service causes what. It is not associated with greater consistency (r=0.01, not significant) — genomic representation predicts a higher average, not a more uniform one. This dataset can't determine *why* regions differ in this respect — nothing here speaks to producer cost, awareness, or access.

**Production and conformation are largely independent traits** — cows that produce more milk aren't meaningfully more or less likely to score well on conformation, by design in how these evaluation systems work. Good conformation's only clearly demonstrated association in this data is a mild trade-off with mastitis resistance, not a health benefit.

**Regional profiles differ in shape, not just rank.** Ontario has the highest average LPI; Quebec ranks a close 2nd but is the most internally consistent province in the dataset — a distinct strength from Ontario's. Manitoba stands apart from every other province on a conformation/health trade-off, leaning hardest toward health and fertility traits. Newfoundland & Labrador and New Brunswick are statistically tied for last, and by far the widest spread between strongest and weakest animals belongs to Newfoundland & Labrador. Several provinces sit close enough together that three pairs are statistically indistinguishable despite different raw averages, a reminder that this is one data snapshot, not a fixed hierarchy. Provinces broadly separate into three profiles by overall strength and by the conformation/health trade-off, a description of profile shape, not a ranking of genetic quality.

**Genomic testing's best-supported contribution is confidence, not magnitude.** The reliability gap between genomically tested and untested animals (Cohen's d up to 6.9) is far larger than the gap in the predicted values themselves (d up to 0.5), and reliability climbs further still when genomic testing is paired with official phenotype-based records, consistent with the integration theme running through this project.

Full detail, regional breakdowns, and the "how confident should each of these be treated" table are in `conclusiones_generales.md`.

## A quick heads-up before you read the numbers

Each province's file is only its *top 400 animals by LPI* — the best-ranked tier, not an average farm. This is a selection-bias caveat that applies to every number below: statistics computed on a top-ranked subset (means, spreads, correlations) describe that elite tier, not each province's general cattle population, and provinces with larger underlying populations have a deeper pool to draw their top 400 from than provinces with smaller ones — something this dataset can't correct for. Full discussion in `methodology.md`, Section 14.

## Things this analysis couldn't fully answer

- All 10 provinces now show a plausible pedigree-only vs. phenotype-based split — no province needs to be excluded from that comparison.
- No actual height/size measurement exists for these animals.
- Age is approximate (birth year only).
- A genomic test can take about a month to return, so a young untested-looking animal may just be awaiting results.
- `%R` in the data is "Relationship Percent" (genetic relationship to the breed population, used to monitor inbreeding) — not a reliability measure, despite the similar name.

## Future research

A natural next step would combine these genetic evaluations with herd-level production, health, longevity, and economic records to test whether the regional patterns found here translate into measurable biological or economic outcomes — ideally with complete national evaluation datasets rather than top-ranked subsets, and with longitudinal data to test whether higher information integration today precedes faster genetic progress over time.

## How to run this yourself

1. Get the provincial Excel files **and** the `diccionario_lactanet.xlsx` dictionary file from Lactanet, and put them all in a `data/raw/` folder next to the notebook.
2. Install the Python packages: `pip install -r requirements.txt`
3. Open `analisis_guiado.ipynb` in Jupyter or VS Code.
4. Run it top to bottom (Kernel → Restart & Run All).

**Python version note:** built and tested on Python 3.12. Very new Python/pandas releases (e.g., Python 3.14 with pandas 3.x) can hit compatibility issues — if you run into unexplained errors, an older, more established Python version is worth ruling out first.

## Data source and copyright

This project uses provincial genetic evaluation data published by [Lactanet](https://www.lactanet.ca). Per Lactanet's Website Terms of Use, users are authorized to "view, download and print portions of the Website solely for [...] personal and non-commercial use," while "reproduction... modifications... distributions... republication... transmission... re-transmissions; or... public showing" of Website materials, without Lactanet's prior written permission, is "strictly prohibited." Based on that clause, **the original Excel files are not included in this repository** — get them directly from Lactanet if you want to reproduce this analysis.

The Terms of Use don't specifically address independent statistical analysis or derivative works built from downloaded data. If you plan to publish something similar, check with Lactanet directly rather than assuming either way.

The statistical analysis, code, visualizations, and written conclusions in this repository are my own original work. I'm not claiming Lactanet reviewed, endorses, or authorized this project, and I'm not claiming any ownership over the underlying data itself.

Lactanet's Terms also state that Website information is provided "without warranty of any kind" — the same caution applies here: verify anything important directly with Lactanet before relying on it.

## License

The code, notebook, charts, and written analysis in this repository (not the underlying Lactanet data, which isn't included) are shared under the [MIT License](LICENSE) — reuse, adapt, or build on them, with attribution.
