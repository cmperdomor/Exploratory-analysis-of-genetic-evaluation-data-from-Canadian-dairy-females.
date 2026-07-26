# Regional Patterns in Canadian Dairy Genetic Evaluations

**Data source:** [Lactanet](https://www.lactanet.ca) - Canadian dairy cattle genetic evaluation service.

## Purpose

Provincial genetic reports are usually read on their own, each describing one region's elite dairy population independently. This project combined the top 400 animals from all 10 provinces into a single dataset to ask a broader question: do regional differences in genetic merit go along with regional differences in the *information* supporting those evaluations? Provinces are the unit of observation here, not the subject of the study - the subject is how that information is assembled.

**Throughout this project, "information integration" means the combination of pedigree, genomic testing, and official phenotype-based records (production and classification) behind an animal's genetic evaluation.** Genomic testing is one piece of that combination, not the focus on its own.

## Two concepts worth knowing before the numbers

An **Estimated Breeding Value (EBV)** is not a direct measurement - it's a statistical prediction of an animal's genetic merit, built from whatever information is available for it. **Reliability** reflects how much confidence to place in that prediction: how close it's likely to be to the animal's true genetic merit.

## The conceptual framework

```
Pedigree information
        |
        |-- without genomic or phenotype records -----> PA   (pedigree-based)
        |
        |-- plus genomic information ------------------> GPA  (pedigree + genomic)
        |
        |-- plus phenotype information (own/daughters') -> EBV  (pedigree + phenotype)
        |
        \-- plus phenotype AND genomic information -----> GEBV (pedigree + phenotype + genomic)
                        |
                        v
                  Reliability of that evaluation
                        |
                        v
                  Selection decisions
```

Genomic information does not replace pedigree, it integrates with it. Each of the four categories above reflects a different amount of evidence behind the same kind of number, which is why identical scores can carry different reliability.

Animals with similar LPI values may still differ substantially in the information supporting those evaluations. This project examines how much that varies across Canada, and what it's associated with.

## What's in this repo

- `genetic_analysis_Code.ipynb` - the full analysis, step by step, in a Jupyter notebook.
- `images/` - selected charts exported from the completed notebook (not generated automatically by a `savefig` call in the notebook itself, exported separately after running it).
- `Methodology.md` - every statistical method used and why.
- `conclusiones_generales.md` - the full findings, discussion, and a confidence rating for each conclusion.

## What this analysis found

**Information sources differ sharply in how much confidence they support.** Pedigree-based evaluations (PA) yield the lowest average reliability (38.0% on protein); pedigree plus genomic information (GPA) already exceeds pedigree plus phenotype-based records without genomics (EBV, 81.0% vs. 55.6%); pedigree plus phenotype plus genomic information (GEBV) yields the highest reliability of any combination (84.1%). Genomic information doesn't replace pedigree, it integrates with it, none of these four categories is "genomics alone" or "phenotype alone." Full breakdown in `conclusiones_generales.md`.

**A related regional pattern, with one clear exception.** Provinces with a higher share of genomically tested animals in their elite population tend to show higher average LPI, a measured association across all 10 provinces (r=0.73, p=0.016). Newfoundland & Labrador breaks the pattern: it has the 5th-highest genomic testing rate but an average LPI about 207 points below what that rate would predict, about 2.4 times the size of the next-largest gap of any province. Excluding it, the relationship among the other 9 provinces is much stronger (r=0.95). This dataset can't explain why Newfoundland & Labrador combines high testing with a lower-than-expected score, or why regions differ in genomic representation to begin with, nothing here speaks to producer cost, awareness, or access. It is not associated with greater consistency (SD, the primary dispersion measure: r=0.13, not significant; CV sensitivity check: r=0.01, not significant), genomic representation predicts a higher average, not a more uniform one.

**Production and conformation show weak linear association in this top-400 subset** - cows that produce more milk aren't meaningfully more or less likely to score well on conformation. Conformation's clearest real association in this data is an observed negative association between body capacity (Dairy Strength) and both health/welfare (r=-0.40) and reproduction (r=-0.46), not the udder-health link often assumed. This matches published research on the same Canadian conformation traits (Alcantara et al. 2022), which found a body-size component unfavorably linked to longevity, fertility, and non-return rates in Holstein cattle.

**Regional profiles differ in shape, not just rank.** Ontario has the highest average LPI; Quebec ranks a close 2nd but is the most internally consistent province in the dataset - a distinct strength from Ontario's. Newfoundland & Labrador and New Brunswick are statistically indistinguishable (confirmed by both classic Tukey HSD and, since province variances differ, the more robust Games-Howell test), and by far the widest spread between strongest and weakest animals belongs to Newfoundland & Labrador. Two other pairs are also statistically indistinguishable by both methods (Alberta/Nova Scotia, PEI/Saskatchewan) - a reminder that this is one data snapshot, not a fixed hierarchy. On a separate, exploratory contrast between type traits and health/reproduction traits, New Brunswick shows the strongest lean toward type (+1.44), with Nova Scotia and Ontario close behind, while Manitoba shows by far the strongest lean the other way (-2.93). Multivariate patterns are visible across provinces. A 2-cluster solution scores best on silhouette (0.305 vs. 0.257 for 3), and a 3-cluster exploratory solution, with adequate KMeans initialization (n_init=100), agrees perfectly with Ward hierarchical clustering (Adjusted Rand Index = 1.000). With only 10 provinces going into the clustering, neither solution should be treated as a definitive classification. Manitoba stands apart from every other province in both.

The same national LPI formula is used to rank the provincial lists analyzed here, although individual herds may apply different or customized selection priorities. A shared formula doesn't mean a shared profile: since LPI is a weighted sum (`PI` and `LTI` alone total 72% of the weight), two animals can reach an identical LPI through very different combinations of the 6 underlying subindexes. This is demonstrated directly in the notebook: among animals sharing essentially the same LPI, subindex values can differ by hundreds of points, including one real pair with the exact same LPI and markedly different profiles. A separate, exploratory diagnostic measuring how evenly each animal's 6 subindexes sit relative to each other (not an official LPI measure, and weighting all 6 domains equally, which the real LPI does not do) found a small but statistically real provincial difference (province is associated with approximately 4.6% of the observed variance; 26 of 45 province pairs differ significantly). Because every animal here was selected specifically for having a high LPI, itself built from these same subindexes, apparent trade-offs among components may partly reflect that selection process rather than a population-level pattern, this applies to the `DS`-`HWI`/`RI` associations elsewhere in this project too, which should be read as observed within this selected dataset but with uncertain generalizability beyond it. None of this determines whether a less even profile is harmful, beneficial, or intentional, that would require real herd outcomes this dataset doesn't have.

**Genomic status is strongly associated with confidence in the estimate, more so than with its magnitude.** The reliability gap between genomically tested (GPA/GEBV) and non-tested (PA/EBV) animals (Cohen's d up to 10.9) is far larger than the gap in the predicted values themselves (mature EBV vs. PA animals: d up to 0.22, and only Conformation reached statistical significance), and reliability is highest for GEBV, which combines genomic testing with phenotype-based records, rather than genomic information combined with pedigree but not yet phenotype records (GPA). This groups all genomically tested animals together regardless of age or evaluation status, so it's an association, not an isolated effect of genomic testing alone.

Full detail, regional breakdowns, and the "how confident should each of these be treated" table are in `conclusiones_generales.md`.

## A quick heads-up before you read the numbers

Each province's file is only its *top 400 animals by LPI* - the best-ranked tier, not an average farm. This is a selection-bias caveat that applies to every number below: statistics computed on a top-ranked subset (means, spreads, correlations) describe that elite tier, not each province's general cattle population, and provinces with larger underlying populations have a deeper pool to draw their top 400 from than provinces with smaller ones - something this dataset can't correct for. Full discussion in `Methodology.md`, Section 14.

## Things this analysis couldn't fully answer

- All 10 provinces now show a plausible pedigree-only vs. phenotype-based split - no province needs to be excluded from that comparison.
- No actual height/size measurement exists for these animals.
- Age is approximate (birth year only).
- A genomic test can take about a month to return, so a young untested-looking animal may just be awaiting results.
- `%R` in the data is "Relationship Percent" (genetic relationship to the breed population, used to monitor inbreeding) - not a reliability measure, despite the similar name.

## Future research

A natural next step would combine these genetic evaluations with herd-level production, health, longevity, and economic records to test whether the regional patterns found here translate into measurable biological or economic outcomes - ideally with complete national evaluation datasets rather than top-ranked subsets, and with longitudinal data to test whether higher information integration today precedes faster genetic progress over time.

## How to run this yourself

1. Get the provincial Excel files **and** the `DICTIONARY_lactanet.xlsx` dictionary file from Lactanet, and put them all in a `data/raw/` folder next to the notebook.
2. Install the Python packages: `pip install -r requirements.txt`
3. Open `genetic_analysis_Code.ipynb` in Jupyter or VS Code.
4. Run it top to bottom (Kernel → Restart & Run All).

**Python version note:** built and tested on Python 3.12. Very new Python/pandas releases (e.g., Python 3.14 with pandas 3.x) can hit compatibility issues - if you run into unexplained errors, an older, more established Python version is worth ruling out first.

## Data source and copyright

This project uses provincial genetic evaluation data published by [Lactanet](https://www.lactanet.ca). Per Lactanet's Website Terms of Use, users are authorized to "view, download and print portions of the Website solely for [...] personal and non-commercial use," while "reproduction... modifications... distributions... republication... transmission... re-transmissions; or... public showing" of Website materials, without Lactanet's prior written permission, is "strictly prohibited." Based on that clause, **the original Excel files are not included in this repository** - get them directly from Lactanet if you want to reproduce this analysis.

The Terms of Use don't specifically address independent statistical analysis or derivative works built from downloaded data. If you plan to publish something similar, check with Lactanet directly rather than assuming either way.

The statistical analysis, code, visualizations, and written conclusions in this repository are my own original work. I'm not claiming Lactanet reviewed, endorses, or authorized this project, and I'm not claiming any ownership over the underlying data itself.

Lactanet's Terms also state that Website information is provided "without warranty of any kind" - the same caution applies here: verify anything important directly with Lactanet before relying on it.

## License

The code, notebook, charts, and written analysis in this repository (not the underlying Lactanet data, which isn't included) are shared under the [MIT License](LICENSE) - reuse, adapt, or build on them, with attribution.
