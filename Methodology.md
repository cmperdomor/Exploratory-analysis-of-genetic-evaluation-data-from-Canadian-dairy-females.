# Statistical Methodology - Lactanet Genetics Analysis

This document summarizes every statistical method used in this project, why
it was chosen, and which Python library/function implements it. Use this to
explain or defend the analysis (e.g., in a report or presentation).

---

## 1. Data preparation

| Step | Method | Why | Code |
|---|---|---|---|
| Load 10 provincial Excel files | `pandas.read_excel(header=1)` | Row 1 of each sheet is a title, not column headers, so headers start on row 2 (index 1) | `pd.read_excel(path, header=1)` |
| Extract province code from filename | Regex pattern matching | Two different file-naming conventions existed (`Lactanet_Genetics_MB.xlsx` and `Lactanet Genetics (MB).xlsx`); regex handles both without manual renaming | `re.compile(r"\(([A-Za-z]+)\)")` and `re.compile(r"Lactanet[_ ]Genetics[_ ]([A-Za-z]+)")` |
| Type coercion | `pandas.to_numeric(errors="coerce")` | Ensures index columns are true numbers, not text; unparseable values become `NaN` instead of silently breaking later `.mean()`/`.sum()` calls | `pd.to_numeric(col, errors="coerce")` |
| Recode letter-codes into booleans | Boolean comparison | `Act.` (`A`/blank) and `GS` (`G`/blank) are shorthand codes; converting to `Is Active`/`Is Genomic` booleans makes filtering and grouping explicit and less error-prone | `df["Act."].fillna("").eq("A")` |
| Remove whitespace inconsistencies | `.str.strip()` on all text columns | Prevents silent grouping errors (e.g., `"EBV"` vs `"EBV "` being treated as different groups) | `df[col].astype("string").str.strip()` |

---

## 1.1 Data composition: what information actually exists per animal, and per province

Before comparing regions on any trait, it matters what *kind* of information each animal's number is built from - not every animal in this dataset carries the same amount of evidence behind its estimate. Two fields determine this: `LPI Code` (does the animal have an official index built from real production/type records, or only from pedigree?) and `GS` (does the animal have a DNA/genomic test on file?). Crossing them gives four genuinely different information states:

| Group | `LPI Code` | `GS` | What's actually known about the animal | Avg. `REL_PROT` | Avg. `REL_CONF` |
|---|---|---|---|---|---|
| **PA** | PA | not genotyped | Pedigree-based evaluation: only the average of its sire and dam, no DNA test, no production/type records of its own | 38.0% | 35.3% |
| **GPA** | PA | genotyped | Pedigree + genomic information: a DNA-based prediction of genetic merit, but no confirmed milk recording or classification yet | 81.0% | 77.8% |
| **EBV** | EBV | not genotyped | Pedigree + phenotype-based information: confirmed own (or daughters') production and type records, but no DNA test | 55.6% | 48.1% |
| **GEBV** | EBV | genotyped | Pedigree + phenotype-based + genomic information: both a DNA-based prediction *and* confirmed production/type records, the most complete information available | 84.1% | 81.1% |

Genomic information does not replace pedigree in any of these categories, it integrates with it, so none of the four is "genomics alone" or "phenotype alone." "Proven" (as in "proven sire") has a specific technical meaning tied to progeny-tested bulls and is not used here for GEBV females.

**This is not an ordering by age or a data-quality problem - it's four legitimately different amounts of evidence**, and the dataset's own reliability columns (`REL_PROT`, `REL_CONF`) confirm the ordering makes sense: reliability climbs from PA (weakest) to GEBV (strongest), with one notable detail - **GPA animals average higher `REL` (81.0%) than EBV animals (55.6%)**. This means genomic information is associated with higher reliability than phenotype-based records without genomics in this dataset - a precise, checkable statement. It does not mean genomics "does more work" than phenotype records in some general causal sense; reliability is a property of the estimate's precision, not a measure of which information source is more important.

**How this breaks down by province** (out of 400 animals each):

| Province | PA only | G+PA | EBV, no G | EBV+G |
|---|---|---|---|---|
| Alberta | 107 | 248 | 21 | 24 |
| British Columbia | 35 | 301 | 6 | 58 |
| Manitoba | 34 | 361 | 3 | 2 |
| New Brunswick | 223 | 141 | 26 | 10 |
| Newfoundland & Labrador | 56 | 281 | 1 | 62 |
| Nova Scotia | 110 | 252 | 14 | 24 |
| Ontario | 22 | 310 | 1 | 67 |
| Prince Edward Island | 191 | 163 | 18 | 28 |
| Quebec | 36 | 334 | 7 | 23 |
| Saskatchewan | 246 | 81 | 35 | 38 |

All 10 provinces now show a believable mix across all four groups.

### 1.1.1 Robustness check: is this gap just an age effect?

The table above mixes animals of very different ages: `EBV` and `EBV+G` animals are always 2+ years old (confirmed directly, 0 animals with an official phenotype-based evaluation are under 2 years), but `PA only` and `G+PA` include large numbers of very young animals (59% and 31% respectively are age 0, i.e., born in the current year) simply because they haven't had time to accumulate phenotype records yet, not necessarily because they were passed over.

Restricting all four groups to animals 2+ years old only (an apples-to-apples age comparison) gives:

| Group | N (2+ years) | REL_PROT | REL_CONF |
|---|---|---|---|
| PA only | 92 | 42.5% | 35.3% |
| G+PA | 400 | 82.1% | 79.0% |
| EBV, no G | 132 | 55.6% | 48.1% |
| EBV+G | 336 | 84.1% | 81.1% |

**The gap survives the age control.** Comparing animals restricted to mature (2+ years old), not necessarily the same exact age, `PA` remains far less reliable (42.5%) than `GEBV` (84.1%), so this is not simply an artifact of younger animals dragging down the PA average. The sample size for mature PA animals is smaller than the all-ages figure (92 vs. 1,060), a genuine reduction worth keeping in mind, but still large enough to support the comparison.



### How the analysis handles this

Most provinces have relatively few animals in the highest-information group (genomic test + phenotype-based evaluation): ranging from as low as 2 in Manitoba to 67 in Ontario.

**Primary estimator: unweighted simple mean.** Provincial comparisons in this analysis use the simple, unweighted mean of each province's 400 listed animals. The top-400 list is a real, enumerated group, not a random sample used to infer a broader population - the simple mean directly answers "what is the average official value across the animals on this list," which is the question these comparisons ask. This also matches standard practice in dairy genetics reporting (herd averages and genetic trend graphs are conventionally unweighted means of published EBVs/PTAs).

**A tension worth naming directly: this analysis uses both a census framing and inferential statistics side by side.** The mean of a province's 400 listed animals is a fact about those exact 400 animals, no sampling uncertainty applies to it, since there is no sample, just a fully enumerated list. But this analysis also reports confidence intervals, ANOVA, and t-tests, which are inferential tools that assume some form of sampling from a broader population. These two framings answer different questions: the census framing answers "what is true of these 400 animals," while the inferential framing implicitly asks "would this difference likely hold if we saw a different top-400 list from the same province, at a different point in time, or a broader elite population." This analysis does not commit to one specific target population for the inferential statistics, and that population is genuinely ambiguous here (a future top-400 release, the province's broader elite tier, or something else), the top-400 is not a random sample of any of them, may include related animals or animals sharing a herd, and its membership is itself selected on the outcome variable (LPI). Confidence intervals and p-values in this analysis should be read as descriptive approximations of how distinguishable these groups are, not as formal proof about a specific, well-defined population beyond the 4,000 animals studied.

**Reliability as a sensitivity analysis, not a weighting scheme for the mean.** `REL_PROT`/`REL_CONF` express the precision of an individual animal's own estimated breeding value (formally, `REL = 1 - PEV/σ²_A`, or equivalently the squared correlation between true and estimated breeding value) - a well-established use, per Interbull/BLUP theory, for combining multiple sources of information *about the same animal* (its own record, its relatives, genomics) into one combined EBV. Scaling *one animal's contribution to a group mean* by its own reliability is a different question - the literature reviewed for this project (Journal of Dairy Science, Genetics Selection Evolution, Interbull documentation) supports the former use extensively; none of it recommends the latter as a standard way to compute a population or provincial mean. Using `REL` as sampling weights for a group average changes the estimand - from "the mean of the animals on this list" to "a precision-adjusted mean."

For that reason, the reliability-weighted mean is presented here only as a sensitivity analysis: it recalculates each provincial mean using `REL_PROT`/`REL_CONF` as weights, to check whether accounting for uncertainty in individual EBVs would materially change the conclusion drawn from the unweighted mean.

```python
import numpy as np

def weighted_mean(group, value_col, weight_col):
    weights = group[weight_col].fillna(0)
    values = group[value_col]
    mask = values.notna() & (weights > 0)
    return np.average(values[mask], weights=weights[mask]) if mask.sum() > 0 else np.nan

def weighted_standard_error(group, value_col, weight_col):
    weights = group[weight_col].fillna(0)
    values = group[value_col]
    mask = values.notna() & (weights > 0)
    v, w = values[mask], weights[mask]
    wmean = np.average(v, weights=w)
    variance = np.average((v - wmean) ** 2, weights=w)
    effective_n = (w.sum() ** 2) / (w ** 2).sum() # accounts for unequal weighting
    return np.sqrt(variance / effective_n), effective_n
```

**How the sensitivity analysis is used:** province means were computed using the unweighted mean of each province's 400 animals as the primary result. As a sensitivity check, provincial mean Conformation was recalculated using `REL_CONF` as an analytical weight, this weighting was applied to Conformation specifically, not to every trait or index in this report (LPI, Milk, Fat, and other traits are reported using only the unweighted mean throughout). **The reliability-weighted sensitivity analysis did not materially change provincial mean Conformation: every weighted-versus-unweighted difference was smaller than 0.4 points** (Saskatchewan +0.37, the largest change; Nova Scotia +0.26; Manitoba -0.02, essentially unchanged, the smallest change of any province; British Columbia 0.00). The GEBV-only reference mean remains unstable in provinces with very small subgroups, particularly Manitoba (n=2, producing a mean over twice as high as either the unweighted or weighted estimate for the same province), but that is a separate issue from the weighted-mean sensitivity analysis itself, which is stable for every province including Manitoba.

## 2. Descriptive statistics

| Analysis | Method | Why | Code |
|---|---|---|---|
| Study-dataset/provincial averages | Mean, median, std, min, max via `.agg()` | Standard way to summarize central tendency and spread for each genetic index | `df.groupby("Province Name")[cols].agg(["mean","median","std","min","max"])` |
| Homogeneity by province | Standard deviation + Coefficient of Variation (CV% = std/mean × 100) | Std alone doesn't account for scale differences between provinces with different means; CV normalizes spread as a % of the mean, making "how consistent is this group" comparable across provinces | `(std/mean*100)` |
| % genotyped by province/year | Proportion (`.mean()` on a boolean column) | The mean of a True/False column directly gives the proportion `True` | `df.groupby(...)["Is Genomic"].mean() * 100` |
| Duplicate detection | `.duplicated()` on `Identification`, within and across provinces | Confirms directly whether any animal appears more than once, rather than assuming; in this snapshot, no within-province duplicates or cross-province ID overlaps were found | `df.duplicated(["Province Name","Identification"], keep=False)` and `df.groupby("Identification")["Province Name"].nunique()` |

---

## 3. Correlation analysis

| Analysis | Method | Why this method | Code |
|---|---|---|---|
| Production vs. conformation traits | **Pearson correlation coefficient (r)** | Measures linear association between two continuous numeric variables (e.g., Fat vs. Feet&Legs) | `df[cols].corr()` or `scipy.stats.pearsonr(x, y)` |
| LPI vs. Pro$ agreement | **Pearson r** *and* **Spearman rank correlation (ρ)** | Pearson checks linear relationship; Spearman checks whether the *ranking order* of animals agrees between the two indices, which matters more than raw linearity when the question is "do they identify the same top animals" | `scipy.stats.spearmanr(x, y)` |
| "Worth reporting" threshold | `abs(r) ≥ 0.5` (moderate-strong), flagged at `≥0.3` | For this exploratory project, `|r| ≥ 0.30` was used as a predefined threshold for emphasizing associations in the narrative. This is an interpretive convention adopted for readability, not a universal boundary between meaningful signal and noise, small associations can be biologically relevant in quantitative genetics. Many correlations were checked across this project without a formal multiple-comparisons adjustment (e.g., Benjamini-Hochberg/FDR); p-values for individual correlations should be read as exploratory rather than confirmatory | Manual threshold applied to `corr()` output |
| Stability check | Repeated correlation on random 50% subsamples | A real relationship should hold up (similar sign/magnitude) across different random halves of the data; a correlation that flips sign or magnitude between subsamples is likely noise, not signal | `df.sample(frac=0.5, random_state=i)` in a loop |

### 3.1 Pearson correlation assumptions - checked, not assumed

Pearson's r is sensitive to non-normality, non-linearity, and outliers. Each was checked before trusting the correlation results:

| Assumption | How checked | Method | Result on this data |
|---|---|---|---|
| **Normality** | D'Agostino-Pearson normality test + skewness/kurtosis | `scipy.stats.normaltest()`, `scipy.stats.skew()`, `scipy.stats.kurtosis()` | Formal tests reject normality (p<0.001) for LPI, Milk, Fat, Prot, Conf - expected with n≈4,000, where even trivial deviations become "significant." Actual skew (-0.27 to 0.04) and kurtosis (-0.80 to 0.22) are all small, meaning the distributions are close enough to normal in practice for Pearson to be reliable. |
| **Linearity** | Visual inspection via scatter plots before trusting any r value | `ax.scatter(x, y)` | Relationships inspected appeared linear (or flat/no relationship) rather than curved - no evidence of a hidden non-linear pattern being missed by Pearson. |
| **Outliers** | IQR method (values beyond 1.5×IQR from Q1/Q3) | `Q1, Q3 = series.quantile([0.25, 0.75])` | Outlier share is low across key traits (Milk 1.0%, Fat 0.9%, Prot 0.6%, LPI 0.0%) - not enough to be driving the correlation results. |

**Why this matters for defending the analysis:** Pearson's r can be distorted by skewed data, curved (non-linear) relationships, or a handful of extreme values. Checking all three before reporting r values (rather than assuming they hold) is what justifies using Pearson here instead of a non-parametric alternative like Spearman for every analysis.

---

## 4. Hypothesis testing (group comparisons)

Used to compare two groups (e.g., EBV vs. PA animals; genomic vs. non-genomic).

| Element | Method | Why | Code |
|---|---|---|---|
| Test statistic | **Welch's t-test** (unequal-variance t-test) | Standard t-test assumes both groups have equal variance; Welch's version doesn't require that assumption, which matters here since group sizes and variances differ substantially between EBV/PA and genomic/non-genomic groups | `scipy.stats.ttest_ind(a, b, equal_var=False)` |
| Statistical significance | p-value, threshold α = 0.05 | Standard convention for "is this difference unlikely to be due to random chance" | Output of `ttest_ind` |
| Practical significance | **Cohen's d** (effect size) | With large samples (hundreds to thousands of animals), even trivial differences become "statistically significant." Cohen's d measures the *size* of the difference in standard-deviation units, independent of sample size, so it tells you whether a significant difference is actually meaningful (0.2=small, 0.5=medium, 0.8=large) | `(mean_a - mean_b) / pooled_std` |

**Why both p-value and Cohen's d were reported together:** relying on p-value alone with a dataset this large (up to ~4,000 rows) risks calling negligible differences "significant," or missing that a non-significant difference is still worth noting. Reporting effect size alongside it is what allowed catching that, e.g., the Pro$ difference between EBV and PA animals (2+ years) was neither statistically significant (p=0.17) nor practically meaningful (d=-0.09), while the REL_PROT difference between genomic and non-genomic animals was both significant and enormous (d=9.59).

### 4.1 The phenotype-based-vs-pedigree comparison now includes all 10 provinces

Earlier drafts of this analysis excluded provinces whose `LPI Code` field showed a 100%-EBV / 0%-PA split - a pattern found, at different points, in Alberta, Ontario, PEI, Saskatchewan, Nova Scotia, and Newfoundland & Labrador's original source files. Each was resolved by obtaining a corrected file directly from Lactanet. The current counts, confirmed directly from the final source files:

| Province | EBV animals | PA animals | Total |
|---|---|---|---|
| Alberta | 45 | 355 | 400 |
| British Columbia | 64 | 336 | 400 |
| Manitoba | 5 | 395 | 400 |
| New Brunswick | 36 | 364 | 400 |
| Newfoundland & Labrador | 63 | 337 | 400 |
| Nova Scotia | 38 | 362 | 400 |
| Ontario | 68 | 332 | 400 |
| Prince Edward Island | 46 | 354 | 400 |
| Quebec | 30 | 370 | 400 |
| Saskatchewan | 73 | 327 | 400 |

All 10 provinces now have a non-empty PA group and a non-empty EBV group, so no province needs to be excluded on the "empty group" grounds that applied to earlier drafts (a t-test requires both groups non-empty; a mean of an empty group is undefined).

**Important distinction:** comparisons that don't require splitting by `LPI Code` - such as the ANOVA and Tukey HSD in Section 6 - never depended on this field and included all 10 provinces throughout.

**Official definition, confirmed directly by the data owner:** `EBV` means the animal has an official published index for *both* production and conformation (from its own or its daughters' records); `PA` means it lacks an official index in at least one of those two areas. This is not limited to young heifers - a mature animal can be `PA` for other reasons, so the "2+ years old" filter used elsewhere in this analysis is a reasonable proxy for "old enough to likely have EBV," not a guarantee. A genotyped animal (`GS = G`) can still be `PA` if it hasn't met the phenotype/production requirement - that combination is expected, not a data anomaly.

### 4.2 What does good conformation actually correlate with? (health, longevity, reproduction)

Since Section 3 found essentially no relationship between conformation and *production* traits, the natural follow-up question is what conformation *does* relate to. This required checking the same assumptions as any other correlation (Section 3.1) on variables not previously tested (`MS`, `SCS`, `BMR`, `LTI`, `HWI`, `RI`, `MI`), plus the stability check from Section 3.

**Assumption checks on the new variables:**

| Variable | Normality (skew / kurtosis) | Outliers (IQR method) |
|---|---|---|
| `MS` (Mammary System) | skew=-0.19, kurtosis=0.06 | 1.8% |
| `SCS` (Somatic Cell Score) | skew=0.07, kurtosis=0.05 | 0.3% |
| `BMR` (Body Maintenance Requirements) | skew=0.21, kurtosis=0.12 | 0.5% |
| `LTI` (Longevity & Type Index) | skew=-0.01, kurtosis=-0.21 | 0.3% |
| `HWI` (Health & Welfare Index) | skew=0.21, kurtosis=0.16 | 0.9% |
| `RI` (Reproduction Index) | skew=0.11, kurtosis=0.09 | 0.7% |
| `MI` (Milkability Index) | skew=-0.04, kurtosis=0.20 | 1.1% |

All skew/kurtosis values are small and outlier shares are low (<2%), same conclusion as Section 3.1: formal normality tests reject normality (large-n sensitivity), but the actual distributions are close enough to normal for Pearson's r to be trustworthy here.

**Stability check (5 random 50% subsamples):**

| Pair | r (5 resamples) | Stable? |
|---|---|---|
| MS vs. LTI | 0.821, 0.816, 0.806, 0.810, 0.810 | Yes, tight range |
| DS vs. BMR | -0.614, -0.623, -0.611, -0.606, -0.599 | Yes, tight range |
| MS vs. MI | 0.205, 0.195, 0.242, 0.230, 0.215 | Yes, tight range |
| MS vs. SCS | -0.032, -0.001, -0.023, -0.032, -0.012 | Yes, but stably near zero |
| MS vs. HWI | -0.147, -0.116, -0.127, -0.131, -0.095 | Yes, weak but consistently negative |
| DS vs. HWI | -0.404, -0.369, -0.384, -0.391, -0.395 | Yes, tight range |
| DS vs. RI | -0.471, -0.442, -0.445, -0.454, -0.443 | Yes, tight range |
| Conf vs. HWI | -0.266, -0.236, -0.243, -0.251, -0.228 | Yes, tight range |
| Conf vs. RI | -0.313, -0.324, -0.322, -0.319, -0.326 | Yes, tight range |
| RP vs. RI | -0.273, -0.259, -0.296, -0.281, -0.283 | Yes, tight range |
| F&L vs. RI | -0.109, -0.152, -0.137, -0.140, -0.133 | Yes, weak but consistent |

**Findings, applying the same 0.3/0.5 reporting threshold used throughout:**

- **Conformation (`Conf`, `MS`, `F&L`) is strongly and stably correlated with `LTI`** (r = 0.88, 0.80, 0.79 respectively). This is expected by construction, not an independent discovery: per Lactanet's own published description, `LTI` (Longevity & Type Index) is explicitly built to "enhance herd longevity favouring functional conformation," with Herd Life, Mammary System, Feet & Legs, Dairy Strength, and Rump as its named components. Conformation traits are literal ingredients of `LTI`, so their high correlation with it confirms the known formula structure rather than revealing something new. This dataset has no separate Herd Life column, so it cannot independently test whether conformation actually predicts real herd longevity outside of this formula.
- **`DS` (Dairy Strength) shows an observed, non-definitional negative association within this selected dataset with two subindexes that do not share any ingredients with it: `HWI` (Health & Welfare Index, r = -0.40) and `RI` (Reproduction Index, r = -0.46).** `DS` is not a component of either `HWI` or `RI`, so this is not a definitional relationship, but as Section 14 notes, this dataset selects only high-LPI animals (itself built partly from these same subindexes), so part of the association may be induced by that selection rather than reflecting an unrestricted-population effect. `Conf` (overall conformation) shows a similar but weaker pattern (`HWI` r = -0.25, `RI` r = -0.33). The direction is biologically consistent with published evidence on Canadian Holstein conformation traits, though that research does not independently reproduce these exact correlations: Alcantara et al. (2022) found that Body Depth, a Dairy Strength component, was associated with lower Pro$ and cited multiple studies showing Body Depth has unfavorable genetic correlations with productive life and number of lactations (Zavadilová and Stipkova 2012: -0.22 to -0.26), with fertility measures such as days open and first-service-to-conception (Zink et al. 2014: 0.14 to 0.43, unfavorable direction), and with non-return rates (Jagusiak et al. 2014: -0.41). The same paper also reports that Dairy Capacity, another Dairy Strength component, correlates *positively* with longevity, meaning `DS` as a single aggregated trait in this dataset may combine sub-components that pull in different directions; this dataset does not have Body Depth and Dairy Capacity as separate columns, so this specific internal split cannot be tested directly here.
- **`DS` (Dairy Strength) vs. `BMR` (Body Maintenance Requirements, a feed-cost trait based on metabolic body weight, not a disease-resistance measure): r = -0.61**, stable. Because higher `BMR` values indicate *lower* maintenance feed requirements, this direction is expected: animals with more body capacity (`DS`) have greater metabolic body weight and therefore genuinely require more feed for maintenance, consistent with how Lactanet itself describes this trait. This is best read as an internal consistency check the data passes, not a novel biological trade-off, unlike the `DS`-`HWI`/`RI` findings above.
- **The intuitive hypothesis "better udder conformation (`MS`) improves udder health" is not clearly supported.** `MS` vs. `SCS` (the direct mastitis/udder-health indicator) is r = -0.03, stably near zero across every resample. `MS` vs. `HWI` (general health and welfare) is weak but consistently negative (r = -0.13), smaller than the `DS` relationships above and below the 0.3 reporting threshold used elsewhere in this document.
- **`MS` vs. `MI` (milking speed/ease): r = 0.21**, weak, below the 0.3 threshold, but directionally plausible (better-shaped udder, marginally easier to milk).

**Practical conclusion for the project:** a specific conformation-to-udder-health link (`MS` vs. `SCS`/`HWI`) is not supported by this data. But `DS` and, more weakly, overall `Conf` do show an observed, non-definitional negative association with both `HWI` and `RI` within this selected dataset, the direction biologically consistent with published evidence on Canadian Holstein conformation traits (Alcantara et al. 2022), though that research does not independently reproduce these exact correlations. This is the project's clearest evidence of an observed negative association involving conformation, distinct from the `DS`-`BMR` relationship, which is a mechanical consequence of body size and feed requirements rather than a health or reproduction finding.

---

## 5. Multivariate / composite analysis

| Analysis | Method | Why | Code |
|---|---|---|---|
| "Standout trait" per province | **Z-scores** (standardization: `(x - mean) / std`) | Conformation traits (Conf, MS, F&L, DS, RP) are on different scales/ranges; z-scores put them on a common scale so they can be compared and ranked fairly against each other | `(series - series.mean()) / series.std()` |
| Conformation vs. health/fertility emphasis | Composite z-score (average of z-scores within each trait group) | Combines multiple related traits into one directional score per province, so provinces can be ranked on "leans toward conformation" vs. "leans toward health/fertility" without cherry-picking a single trait | `z_scores_df.mean(axis=1)` |
| Which trait best predicts LPI | **Multiple linear regression** (Ordinary Least Squares, standardized coefficients) | Quantifies how strongly each trait moves with LPI while holding the others constant (in a linear sense), unlike a simple pairwise correlation which ignores the other traits | `numpy.linalg.lstsq(X_standardized, y_standardized)` |
| Model fit | **R² (coefficient of determination)** | Reports what % of LPI's variation is explained by the traits included in the regression | `1 - SS_residual / SS_total` |

**Caveat documented alongside this analysis:** the regression traits are correlated with each other (multicollinearity), so individual coefficients should be read as "moves together with LPI," not as proven independent causal weights.

**Important context confirmed against Lactanet's own published LPI structure (source: "Which Index is Right for My Herd?", Lactanet, March 2025):** LPI is officially calculated as a weighted sum of six subindexes: Production Index (PI, 40%), Longevity and Type Index (LTI, 32%), Health and Welfare Index (HWI, 8%), Reproduction Index (RI, 10%), Milkability Index (MI, 5%), and Environmental Impact Index (EI, 5%). `PI` is directly composed of Fat Yield (60%) and Protein Yield (40%); Milk Yield is a closely correlated trait, not a direct `PI` ingredient. `LTI`'s five direct components are Herd Life, Mammary System, Feet & Legs, Dairy Strength, and Rump; overall Conformation (`Conf`) is a trait correlated with `LTI`, not one of its five direct components.

Most of the traits used in this regression are either direct components of the official LPI subindexes or closely related published traits, not independent variables being tested against LPI. To be precise: `PI` is directly composed of Fat Yield (60%) and Protein Yield (40%); `Milk` is a closely correlated trait, not a direct `PI` ingredient. `LTI`'s five direct components are Herd Life, Mammary System, Feet & Legs, Dairy Strength, and Rump; the overall `Conf` score is a trait correlated with `LTI`, not one of its five direct components. The high R² found for this model (0.961 initial, 0.957 in the corrected model below) should be read mainly as confirming that the model is structurally linked to how LPI is constructed, not as an independent empirical discovery of what determines LPI. This is a broader version of the multicollinearity issue described below for `Conf` specifically: here the issue isn't just correlation between predictors, it's that most of the predictors are either direct ingredients of LPI's subindexes or closely related to them.

**A specific number worth correcting:** an earlier draft of this analysis reported Milk Yield's contribution to LPI as "near zero" based on this regression's standardized coefficient (0.02). Lactanet's own published correlation between Milk Yield and LPI is a real, moderate 0.43, not close to zero. The near-zero regression coefficient is a partial estimate that holds Fat and Protein yield constant, and Milk is highly correlated with both of them since all three come from the same PI subindex. That multicollinearity shrinks Milk's unique statistical contribution once Fat and Protein are already in the model, even though Milk's raw relationship with LPI is real. This regression cannot support a claim that milk volume doesn't matter to LPI. It can only say that, once Fat and Protein are already known, Milk adds comparatively little additional information beyond them in this specific model.

### 5.1 Regression diagnostics - how the model was validated

An interviewer's fair question is "how did you check the regression was valid?" - here's the answer, with results:

| Diagnostic | Method | Code | Result |
|---|---|---|---|
| **Residual plot** | Fitted values vs. residuals scatter | `ax.scatter(model.fittedvalues, model.resid)` | No strong funnel/curve pattern visually, but see Breusch-Pagan below for the formal test. |
| **QQ plot** | Residual quantiles vs. theoretical normal quantiles | `statsmodels.api.qqplot(model.resid, line="45")` | Residuals track the 45° line closely in the middle, with minor deviation in the tails - consistent with the normality test below. |
| **Homoscedasticity** | Breusch-Pagan test | `statsmodels.stats.diagnostic.het_breuschpagan()` | **p < 0.001 → heteroscedasticity present.** Residual variance is not fully constant across fitted values. Fix applied: refit with HC3 robust standard errors (`model.fit(cov_type="HC3")`). |
| **Normality of residuals** | D'Agostino-Pearson test + skew/kurtosis | `scipy.stats.normaltest(model.resid)` | Formally rejected (p=0.011) but skew=-0.12, kurtosis=0.02 - negligible in practice, same large-sample-sensitivity caveat as above. |
| **Multicollinearity** | **Variance Inflation Factor (VIF)**, not just a mention | `statsmodels.stats.outliers_influence.variance_inflation_factor()` | **`Conf` VIF = 95.22, `MS` VIF = 34.04** - severe. Both are expected: `Conf` (overall conformation) is itself built from `MS`, `F&L`, `DS`, `RP` by Lactanet's own scoring system, so it's mathematically redundant, not an independent predictor. Fix applied: dropped `Conf` from the model and refit (R²=0.961 initial, R²=0.957 corrected), with all remaining traits' VIF below 4 (maximum 3.51). |

**Net effect of the fixes:** the corrected model (Conf dropped, HC3 robust SE) addresses the multicollinearity and heteroscedasticity found in the initial diagnostics. Combined with the subindex-structure context above, the most defensible summary of this whole analysis is that it demonstrates how LPI's published formula weights show up in the data, and gives a relative sense of which components carry the most weight once others are held constant. It should not be presented as an independent discovery of "what drives LPI" separate from how LPI is defined.

---

## 6. Comparing more than 2 groups: Welch ANOVA + Games-Howell (primary), classic ANOVA + Tukey HSD (secondary sensitivity check)

The EBV-vs-PA and genomic-vs-not comparisons (Section 4) only involve 2 groups, where a t-test is appropriate. Comparing **10 provinces** at once calls for a different test. Levene's test (below) found that provincial variances are not homogeneous, so the primary method here is Welch ANOVA and Games-Howell, which do not assume equal variances; classic ANOVA and Tukey HSD are reported alongside as a secondary sensitivity check, since they produced the same conclusion despite the less appropriate assumption.

| Element | Method | Why | Code |
|---|---|---|---|
| Variance check | **Levene's test** | Tests whether provincial variances are homogeneous, the assumption Tukey HSD depends on | `scipy.stats.levene(*groups)` |
| Omnibus test (primary) | **Welch ANOVA** | Tests whether *at least one* province's mean differs from the others, without assuming equal variances | `statsmodels.stats.oneway.anova_oneway(..., use_var="unequal")` |
| Post-hoc comparison (primary) | **Games-Howell** | Tests every pair of provinces without assuming equal variances, the appropriate post-hoc test given Levene's result | `pingouin.pairwise_gameshowell()` |
| Omnibus test (secondary) | **Classic one-way ANOVA** | Assumes equal variances; reported as a sensitivity check against the primary Welch result | `scipy.stats.f_oneway(*groups)` |
| Post-hoc comparison (secondary) | **Tukey HSD** | Assumes equal variances; reported as a sensitivity check against the primary Games-Howell result | `statsmodels.stats.multicomp.pairwise_tukeyhsd()` |

**Results:** Levene's test is significant (p=3.07x10^-34), confirming provincial variances are not homogeneous. Welch ANOVA on LPI is significant (F≈1373.19, p<0.0001). Games-Howell identifies 42 of 45 province pairs as significantly different; the same 3 pairs are not significant as with the secondary classic-ANOVA/Tukey HSD check: **Alberta vs. Nova Scotia**, **New Brunswick vs. Newfoundland & Labrador**, and **Prince Edward Island vs. Saskatchewan**. This Welch/Games-Howell analysis was run for LPI specifically; Milk, Fat, Protein, and Conformation were only checked with the secondary classic ANOVA (all significant, p<0.001), so claims about those 4 traits rest on the less-preferred method given the variance-homogeneity violation. Which specific pairs land in the "statistically indistinguishable" set has changed each time a source file was corrected during this project - a reminder that with several provinces sitting within a few dozen LPI points of each other, this is expected and shouldn't be read as a permanently fixed set of pairs.

---

## 7. Confidence intervals

Point estimates (means) were reported alongside 95% confidence intervals to communicate estimation uncertainty, not just a single number:

| Method | Code |
|---|---|
| 95% CI using the t-distribution (appropriate for finite-sample means, more conservative than using the normal distribution) | `margin = (std/sqrt(n)) * scipy.stats.t.ppf(0.975, n-1)` |

With n=400 per province, the resulting intervals are narrow (roughly ±6 to ±14 LPI points). These intervals summarize the precision of the observed means under an independence-based approximation. Because the records form selected top-400 lists rather than random samples, and may include related animals or animals sharing a herd, they should not be interpreted as formal population-level confidence intervals, they describe how precisely each province's own top-400 mean is estimated under that approximation, not sampling uncertainty about a defined broader population.

---

## 8. Reducing many traits to a comparable picture: PCA

| Element | Method | Why | Code |
|---|---|---|---|
| Dimensionality reduction | **Principal Component Analysis (PCA)** on province-level trait averages (10 provinces, standardized first) | Directly answers "how do provinces group together based on their overall genetic profile," compressing several correlated traits into 2 interpretable axes | `sklearn.decomposition.PCA(n_components=2)` on `sklearn.preprocessing.StandardScaler()`-scaled data |
| Interpreting the axes | Component loadings | Shows which original traits drive each principal component | `pca.components_` |

An earlier version of this PCA used roughly 17 variables, including `LPI` and `Pro$` (themselves weighted sums of the six subindexes), the six subindexes, and several of the individual traits that build those same subindexes. Including a result alongside its own ingredients creates circular redundancy. The current PCA uses only the six official, non-overlapping LPI subindexes (`PI`, `LTI`, `HWI`, `RI`, `MI`, `EI`) as the province profile. Results are reported together with clustering in Section 9.

---

## 9. Do provinces form natural clusters? KMeans + hierarchical clustering

| Element | Method | Why | Code |
|---|---|---|---|
| Partition-based clustering | **KMeans (k=3)** on the same standardized province profiles used for PCA | Directly answers "do provinces have similar genetic profiles" by grouping them algorithmically instead of eyeballing the PCA plot | `sklearn.cluster.KMeans(n_clusters=3, random_state=42, n_init=100)` |
| Hierarchical clustering | **Agglomerative clustering, Ward's method** + dendrogram | Cross-checks the KMeans result with a different clustering algorithm that doesn't require pre-choosing k, and visualizes *how* provinces merge together | `scipy.cluster.hierarchy.linkage(X, method="ward")` |
| Cluster quality | **Silhouette score** across k=2 to 5, and **Adjusted Rand Index** between KMeans and hierarchical clustering at k=3 | Checks whether 3 is actually the best number of clusters, and how much the two methods actually agree, rather than assuming both | `sklearn.metrics.silhouette_score`, `sklearn.metrics.adjusted_rand_score` |

**Result (current, final dataset, PCA on the 6 official LPI subindexes):** PC1 (62%) reflects overall strength across all six subindexes. PC2 (23%) is dominated by `LTI` and `EI` pulling in opposite directions, not "feed efficiency vs. conformation," `EI` includes Methane Efficiency and Body Maintenance Requirements in addition to Feed Efficiency. **Two clusters receive the strongest silhouette support (0.305 vs. 0.257 for three). A three-cluster exploratory solution is also interpretable and, with adequate KMeans initialization (`n_init=100`), agrees perfectly with Ward hierarchical clustering (Adjusted Rand Index = 1.000).** Because the analysis contains only 10 provincial observations, neither solution should be treated as a definitive classification. Manitoba stands apart from every other province in both the 2-cluster and 3-cluster solutions, the most defensible specific claim from this analysis. All groupings describe each province's top-400-by-LPI subset, not its general cattle population.

---
---

## 10. Advanced visualization

| Chart | Library / function | Used for |
|---|---|---|
| **PCA scatter** | `matplotlib` (`ax.scatter`) on PCA-transformed data | Visualizing the province clusters from Section 9 in 2D |
| **Dendrogram** | `scipy.cluster.hierarchy.dendrogram` | Showing the hierarchical merge structure between provinces |
| **Bubble chart** | `matplotlib` (`ax.scatter` with `s=` mapped to a third variable) | LPI vs. Pro$ by province, with bubble size = animal count |
| **Radar chart** | `matplotlib` with `subplot_kw=dict(polar=True)` | Comparing the *shape* of a province's conformation profile across 5 traits at once (not just single-trait bar charts) |
| **Parallel coordinates** | `pandas.plotting.parallel_coordinates` | Comparing all 10 provinces across several standardized traits simultaneously, one line per province |

All of the above deliberately avoid heatmaps, per the project's earlier decision to prioritize charts that are readable without needing to interpret a color-intensity matrix.

---

## 11. Libraries used and what each was for

| Library | Used for |
|---|---|
| `pandas` | Loading Excel files, all data cleaning, grouping, and aggregation |
| `numpy` | Regression matrix algebra (`np.linalg.lstsq`), standardization |
| `scipy.stats` | `pearsonr`, `spearmanr` (correlation + p-values), `ttest_ind` (Welch's t-test), `f_oneway` (ANOVA), `normaltest`, `skew`, `kurtosis`, `t.ppf` (confidence intervals) |
| `statsmodels` | `sm.OLS` (regression with full diagnostics), `variance_inflation_factor` (VIF), `het_breuschpagan` (homoscedasticity test), `pairwise_tukeyhsd` (Tukey HSD), `qqplot` |
| `scikit-learn` | `PCA`, `StandardScaler`, `KMeans` |
| `scipy.cluster.hierarchy` | `linkage`, `dendrogram`, `fcluster` (hierarchical clustering) |
| `matplotlib.pyplot` | All chart rendering - bar charts, scatter plots, line plots, radar charts (polar projection), residual/QQ plots |
| `pandas.plotting` | `parallel_coordinates` |
| `seaborn` | Used only for `sns.set_style("whitegrid")` (visual styling) - no seaborn-specific statistical plots (e.g., heatmaps) were used in the final version, by request, in favor of plain matplotlib bar/scatter charts that are easier to read without prior heatmap-reading experience |

---

## 12. Reproducibility

| Practice | Implementation |
|---|---|
| **Fixed random seed** | `RANDOM_SEED = 42` used everywhere randomness appears: `KMeans(random_state=42)`, `PCA(random_state=42)`, and the correlation-stability subsampling (`df.sample(frac=0.5, random_state=i)`) - anyone re-running the code gets identical results. |
| **Pinned library versions** | `requirements.txt` lists the exact versions (`==`) used to build and execute this notebook, captured via `pip freeze`, not just minimum compatible versions. |
| **README** | Documents setup steps, folder structure, and how to run the project end-to-end (see the project's `README.md`). |
| **Deterministic data pipeline** | Loading and cleaning steps involve no randomness - the same input files always produce the same cleaned dataset, independent of the analyses run afterward. |

---

## 13. Choices made deliberately for interpretability

- **No heatmaps.** All comparisons across provinces/traits use sorted, colored (green=positive/red=negative) horizontal or vertical bar charts instead, so a reader can identify "which province, which direction" without needing to interpret a color-intensity matrix.
- **EBV-only subsets for "best animal" rankings.** Comparing PA (pedigree-only) and EBV (official phenotype-based) animals directly would be unfair, since they're evaluated on different amounts of information; EBV-only animals were used for "best animal by province" rankings, and PA-vs-EBV was only ever compared as its own separate, explicit analysis.
- **All 10 provinces are included in the PA vs. EBV comparison.** Earlier versions of this analysis excluded provinces whose source files had corrupted `LPI Code` fields (100% `EBV` / 0% `PA`, an unrealistic split). After obtaining corrected source files directly from Lactanet, all 10 provinces show a plausible split and are included in the final comparison (see Section 4.1).

---

## 14. Selection bias - the single most important methodological caveat

Every animal in this dataset comes from a province's **top 400 by LPI**, not a random or complete sample of that province's cattle population. This has a specific, predictable consequence: any statistic computed on this data (means, standard deviations, correlations) describes the *selected elite tier*, not the underlying population those animals were drawn from. Two concrete ways this matters:

- **Range restriction.** Selecting the top 400 by LPI truncates the distribution of LPI itself (and, more weakly, of traits correlated with LPI) within each province. Correlations and variances computed on a range-restricted sample are generally attenuated relative to the full population - so relationships that appear weak in this dataset (e.g., production vs. conformation) could in principle be somewhat stronger in the unrestricted population, though the very low values found here (mostly r<0.1) make it unlikely that restriction alone explains the near-zero result.
- **Province-to-province comparability depends on population size.** A province with a larger underlying cattle population has a deeper pool to draw its top 400 from; a province with a smaller population's "top 400" reaches further down its actual distribution. This dataset cannot correct for that, because provincial population sizes aren't included - it's a limitation to flag explicitly, not one this analysis can resolve.
- **Selection-induced correlation.** Because inclusion in every provincial file depends on a high LPI, a weighted composite of the subindexes analyzed throughout this project, conditioning on this selected group can induce apparent trade-offs among components. An animal with a relatively weak value in one domain may require stronger values elsewhere to remain in the top 400. Consequently, negative associations observed within this dataset (notably `DS` vs. `HWI`/`RI` in Section 4.2, and the cross-subindex dispersion measure in Section 16) may partly reflect the selection mechanism rather than a population-level effect, and should be validated in an unrestricted population before being treated as fully generalizable.

This caveat applies to every provincial comparison in this report and is the primary reason regional patterns here are described as observed associations within elite populations, not as claims about each province's general dairy herd.

---

## 15. Context: the Canadian genetic evaluation system

Canada's national genetic evaluation system has been in continuous development since the Canadian Dairy Network (one of Lactanet's predecessor organizations) introduced LPI in 1991, initially combining production, durability, and health/fertility traits (Lactanet extension publications, B. Van Doormaal, Chief Services Officer). Canada implemented genomic evaluations in August 2009, early relative to most other dairy genetic evaluation systems internationally. Two general points from the broader quantitative genetics literature are relevant background for interpreting this analysis, without this project claiming to test either directly:

- **Genomic and pedigree-based information are commonly combined into a single evaluation (single-step methods)** rather than treated as fully separate pipelines (Misztal et al., 2009). This is broader methodological context for why this dataset's four information states (PA, GPA, EBV, GEBV) behave as they do, not a claim about which specific method Lactanet uses internally.
- **International comparisons of genetic evaluations across countries are coordinated through Interbull**, which is a separate function from within-country provincial reporting; this analysis is entirely within-Canada and does not involve Interbull data or methods.

**On the `DS`-`BMR` relationship (Section 4.2, r=-0.61):** `BMR` is Body Maintenance Requirements, a feed-cost trait unrelated to disease resistance. Per Lactanet's own description of this trait, maintenance energy is proportional to an animal's metabolic body weight, so animals with more body capacity (`DS`) mechanically require more maintenance feed (equivalent to a lower `BMR` value, since higher `BMR` means lower requirements). The negative correlation is an expected consequence of how the two traits are defined, not an independent biological discovery.

**On the `DS`-`HWI` and `DS`-`RI` relationships (Section 4.2, r=-0.40 and r=-0.46):** unlike the `BMR` relationship above, these are not definitional, `HWI` and `RI` do not include `DS` as an ingredient. Alcantara et al. (2022), studying the same Canadian conformation traits and RBV system used in this dataset, found that Body Depth (a Dairy Strength component) was associated with lower Pro$ and cited genetic correlations from multiple studies showing Body Depth unfavorably associated with productive life, number of lactations, fertility measures, and non-return rates. This is biologically consistent with treating the `DS`-`HWI`/`RI` pattern as an observed negative association rather than a data artifact, though it does not directly reproduce these specific correlations, while noting that the same review also found a different Dairy Strength component (Dairy Capacity) associated positively with longevity, meaning the aggregated `DS` trait in this dataset may combine sub-components pulling in different directions that cannot be separated with the columns available here.

---

## 16. Does the same LPI mean the same cow? Cross-subindex profile analysis

This section documents the notebook's Steps 20.1-20.2, added specifically to test whether provinces differ not just in genetic merit, but in how evenly their elite animals perform across the 6 official LPI subindexes.

| Element | Method | Why | Code |
|---|---|---|---|
| Direct demonstration | Bin animals into narrow (10-point) LPI bands; report the max-min spread per subindex within the largest band, and a concrete pair with near-identical LPI and maximally different profiles | Since LPI is a weighted sum (`PI` 40% + `LTI` 32% = 72% of the weight), two animals can reach the same LPI through very different subindex combinations; showing this directly avoids reducing the question to a single summary statistic | `groupby` on rounded LPI bands, `itertools.combinations` for the pairwise search |
| Cross-subindex dispersion | Standardize all 6 subindexes (z-scores across the full dataset), then take the standard deviation of each animal's 6 z-scores | A lower value means an animal's 6 subindexes are numerically similar to each other. **This says nothing about whether those values are favorable** - an animal scoring far below average on all 6 subindexes would also show low dispersion. This measure must always be read alongside a level measure (e.g., LPI, or mean subindex z-score), never in isolation | `(z_subindex).std(axis=1)` |
| Weakest link | The single lowest of an animal's 6 standardized subindexes | A non-compensatory check: unlike a mean or dispersion, this cannot be improved by strength elsewhere, it answers "how weak is this animal's weakest domain" directly | `z_subindex.min(axis=1)` |
| Relatively low subindex count | Number of an animal's 6 subindexes more than 1 dataset standard deviation below the dataset mean | A relative marker **within this elite, LPI-selected group** - not a biological, economic, or Lactanet-defined threshold. An animal 1 SD below this elite group's average may still be well above the general breed average | `(z_subindex < -1).sum(axis=1)` |
| Group comparison | Welch ANOVA + Games-Howell across provinces, on the dispersion measure | Same rationale as Section 6: provincial variances are not assumed equal | `pingouin.welch_anova()`, `pingouin.pairwise_gameshowell()` |

**Terminology deliberately avoided:** this analysis is not called "whole-animal functional balance" or "severe weakness" in the notebook. "Balance" implies a favorable, validated state that a purely dispersion-based statistic cannot establish on its own (see the worked example below); "severe" implies a functional or economic threshold this dataset has no basis to set. The terms used instead are "cross-subindex dispersion," "weakest standardized subindex," and "relatively low subindex" (relative to this specific elite dataset).

**Why dispersion alone is not "balance":** consider two hypothetical animals: Animal A scores 2 standard deviations below the dataset mean on all 6 subindexes; Animal B scores 1 standard deviation above the mean on all 6. Both would show dispersion at or near zero, identical "evenness", despite Animal B being unambiguously the stronger animal. Dispersion measures internal consistency, not merit; it must be paired with a level measure (LPI, or mean subindex z-score) to be interpreted at all.

**Equal weighting is a deliberate departure from LPI, not an oversight.** LPI weights `PI` (40%) and `LTI` (32%) far more heavily than `HWI` (8%), `RI` (10%), `MI` (5%), or `EI` (5%). This dispersion measure treats all 6 equally. That makes it useful as an independent, non-compensatory critique of what LPI's own weighting can obscure (an animal can be exceptional on LPI while being comparatively weak on the lightly-weighted domains), but it is explicitly **not** a reproduction of the official LPI breeding objective, and does not establish that any provincial pattern violates that objective, since the objective itself does not require equal performance across all 6 domains.

**Selection-induced correlation applies directly here** (see Section 14's third point): because every animal analyzed was selected for a high LPI, itself built from these same 6 subindexes, some of the apparent trade-offs among components - and some of the provincial dispersion differences - may be induced by the selection mechanism rather than reflecting a pattern that would hold in an unrestricted population.

**What this analysis supports, precisely:** "Provinces differ modestly in the dispersion of their elite animals' six standardized LPI subindexes. Low dispersion does not necessarily indicate high functional merit or the absence of important weaknesses. The measure is an exploratory, equal-domain diagnostic constructed for this project, not an official balance index. Because the dataset is selected on high LPI, part of the apparent compensation among subindexes may be induced by the selection process." It does **not** support "Province X produces the most functionally balanced cow" - depending on whether dispersion, weakest-subindex, or share-with-no-relatively-low-subindex is used, the province ranking changes.

---

## References

- Hayes, B.J., Bowman, P.J., Chamberlain, A.J., Goddard, M.E. (2009). Invited review: Genomic selection in dairy cattle: Progress and challenges. *Journal of Dairy Science*, 92(2), 433-443.
- Misztal, I., Legarra, A., Aguilar, I. (2009). Computing procedures for genetic evaluation including phenotypic, full pedigree, and genomic information. *Journal of Dairy Science*, 92(9), 4648-4655.
- VanRaden, P.M. (2008). Efficient methods to compute genomic predictions. *Journal of Dairy Science*, 91(11), 4414-4423.
- Van Doormaal, B. Lactanet extension publications on LPI history and genomic evaluation implementation in Canada (lactanet.ca).
- Sweett, H. (2025). Which Index is Right for My Herd? Lactanet, March 27, 2025. Source for the official LPI subindex structure, weights, and trait correlations used in Sections 5 and 5.1 to reframe and correct the regression findings.
- Alcantara, L.M., Baes, C.F., de Oliveira Junior, G.A., Schenkel, F.S. (2022). Conformation traits of Holstein cows and their association with a Canadian economic selection index. *Canadian Journal of Animal Science*, 102, 490-500.

These are cited for general methodological and biological context. The Sweett (2025) and Alcantara et al. (2022) references were used to verify and correct specific project findings, not just for background: see Sections 5, 5.1, and 4.2.
