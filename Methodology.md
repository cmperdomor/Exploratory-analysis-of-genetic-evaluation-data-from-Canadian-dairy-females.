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
| **PA only** | PA | not genotyped | Only the average of its sire and dam - no DNA test, no production/type records of its own | 37.9% | 35.1% |
| **G+PA** ("genomic potential") | PA | genotyped | A DNA-based prediction of genetic merit, but no confirmed milk recording or classification yet | 81.0% | 77.6% |
| **EBV, no G** | EBV | not genotyped | Confirmed own (or daughters') production and type records, but no DNA test | 56.2% | 48.0% |
| **EBV + G** ("proven + genomic") | EBV | genotyped | Both a DNA-based prediction *and* confirmed production/type records - the most complete information available | 84.1% | 81.3% |

**This is not an ordering by age or a data-quality problem - it's four legitimately different amounts of evidence**, and the dataset's own reliability columns (`REL_PROT`, `REL_CONF`) confirm the ordering makes sense: reliability climbs from PA-only (weakest) to EBV+G (strongest), with one notable detail - **G+PA animals average higher `REL` (81.0%) than EBV-without-G animals (56.2%)**. This means genomic predictions currently have higher reliability than phenotype-only animals in this dataset - a precise, checkable statement. It does not mean genomics "does more work" than phenotype records in some general causal sense; reliability is a property of the estimate's precision, not a measure of which information source is more important.

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

**The gap survives the age control.** Even comparing only same-age (2+ year old) animals, `PA only` remains far less reliable (42.5%) than `EBV+G` (84.1%), so this is not simply an artifact of younger animals dragging down the PA-only average. The sample size for mature PA-only animals is smaller than the all-ages figure (92 vs. 1,060), a genuine reduction worth keeping in mind, but still large enough to support the comparison.



### How the analysis handles this

Most provinces have relatively few animals in the highest-information group (genomic test + phenotype-based evaluation): as low as 2 in Manitoba, versus 361 in Quebec.

**Primary estimator: unweighted simple mean.** Provincial comparisons in this analysis use the simple, unweighted mean of each province's 400 listed animals. The top-400 list is a real, enumerated group, not a random sample used to infer a broader population - the simple mean directly answers "what is the average official value across the animals on this list," which is the question these comparisons ask. This also matches standard practice in dairy genetics reporting (herd averages and genetic trend graphs are conventionally unweighted means of published EBVs/PTAs).

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

**How the sensitivity analysis is used:** province means were computed using the unweighted mean of each province's 400 animals as the primary result. Because estimated breeding values differ in reliability, a secondary sensitivity analysis recalculated all provincial means using `REL_PROT`/`REL_CONF` as analytical weights. Results were highly consistent between the two approaches for most provinces (e.g., Ontario: 9.61 unweighted vs. 9.68 weighted; Quebec: 9.42 vs. 9.48) - provinces whose results changed substantially between approaches (Manitoba, Prince Edward Island) were interpreted with additional caution rather than having either number presented as the single answer. The EBV+G-only mean (strictest, but smallest sample) is reported as a third reference point where relevant, particularly to illustrate how unstable a very small subgroup mean can be (Manitoba's EBV+G group, n=2, produced a mean over twice as high as either the unweighted or weighted estimate for the same province).

## 2. Descriptive statistics

| Analysis | Method | Why | Code |
|---|---|---|---|
| National/provincial averages | Mean, median, std, min, max via `.agg()` | Standard way to summarize central tendency and spread for each genetic index | `df.groupby("Province Name")[cols].agg(["mean","median","std","min","max"])` |
| Homogeneity by province | Standard deviation + Coefficient of Variation (CV% = std/mean × 100) | Std alone doesn't account for scale differences between provinces with different means; CV normalizes spread as a % of the mean, making "how consistent is this group" comparable across provinces | `(std/mean*100)` |
| % genotyped by province/year | Proportion (`.mean()` on a boolean column) | The mean of a True/False column directly gives the proportion `True` | `df.groupby(...)["Is Genomic"].mean() * 100` |
| Duplicate detection | `.duplicated()` / `.drop_duplicates()` on `Identification` | Animals appear in more than one province's file (shared reference sires/dams); de-duplicating gives a true unique-animal count instead of inflating totals | `df.drop_duplicates("Identification")` |

---

## 3. Correlation analysis

| Analysis | Method | Why this method | Code |
|---|---|---|---|
| Production vs. conformation traits | **Pearson correlation coefficient (r)** | Measures linear association between two continuous numeric variables (e.g., Fat vs. Feet&Legs) | `df[cols].corr()` or `scipy.stats.pearsonr(x, y)` |
| LPI vs. Pro$ agreement | **Pearson r** *and* **Spearman rank correlation (ρ)** | Pearson checks linear relationship; Spearman checks whether the *ranking order* of animals agrees between the two indices, which matters more than raw linearity when the question is "do they identify the same top animals" | `scipy.stats.spearmanr(x, y)` |
| "Worth reporting" threshold | `abs(r) ≥ 0.5` (moderate-strong), flagged at `≥0.3` | Standard rule of thumb in applied statistics: correlations below ~0.3 are considered noise-level in most practical contexts, regardless of statistical significance | Manual threshold applied to `corr()` output |
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

**Why both p-value and Cohen's d were reported together:** relying on p-value alone with a dataset this large (up to ~4,000 rows) risks calling negligible differences "significant." Reporting effect size alongside it is what allowed catching that, e.g., the Pro$ difference between EBV and PA animals was statistically real (p=0.03) but practically tiny (d=0.17), while the REL_PROT difference between genomic and non-genomic animals was both significant and enormous (d=4.92).

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

### 4.2 What does good conformation actually correlate with? (health, longevity, milk traits)

Since Section 3 found essentially no relationship between conformation and *production* traits, the natural follow-up question is what conformation *does* relate to. This required checking the same assumptions as any other correlation (Section 3.1) on variables not previously tested (`MS`, `SCS`, `BMR`, `LTI`, `HWI`, `MI`), plus the stability check from Section 3.

**Assumption checks on the new variables:**

| Variable | Normality (skew / kurtosis) | Outliers (IQR method) |
|---|---|---|
| `MS` (Mammary System) | skew=-0.19, kurtosis=0.06 | 1.8% |
| `SCS` (Somatic Cell Score) | skew=0.07, kurtosis=0.05 | 0.3% |
| `BMR` (Mastitis Resistance) | skew=0.21, kurtosis=0.12 | 0.5% |
| `LTI` (Lifetime milking efficiency) | skew=-0.01, kurtosis=-0.21 | 0.3% |
| `HWI` (Health & Wellness) | skew=0.21, kurtosis=0.16 | 0.9% |
| `MI` (Milking Efficiency) | skew=-0.04, kurtosis=0.20 | 1.1% |

All skew/kurtosis values are small and outlier shares are low (<2%) - same conclusion as Section 3.1: formal normality tests reject normality (large-n sensitivity), but the actual distributions are close enough to normal for Pearson's r to be trustworthy here.

**Stability check (5 random 50% subsamples), `MS` against each target:**

| Pair | r (5 resamples) | Stable? |
|---|---|---|
| MS vs. LTI | 0.821, 0.816, 0.806, 0.810, 0.810 | Yes - tight range |
| MS vs. BMR | -0.322, -0.310, -0.292, -0.321, -0.307 | Yes - tight range |
| MS vs. MI | 0.227, 0.256, 0.263, 0.247, 0.257 | Yes - tight range |
| MS vs. SCS | 0.008, 0.027, 0.021, 0.015, 0.058 | Yes, but stably near zero |
| MS vs. HWI | -0.032, -0.013, -0.020, -0.033, 0.008 | Yes, but stably near zero |

**Findings, applying the same ≥0.3/≥0.5 reporting threshold used throughout:**

- **Conformation (`Conf`, `MS`, `F&L`) is strongly and stably correlated with `LTI`** (r = 0.89, 0.81, 0.80 respectively) - but `LTI` barely correlates with actual milk production (r = -0.09 to -0.20 against Milk/Fat/Prot). Given the strength and stability of this relationship, and its near-absence with production, this is more consistent with `LTI` being partly *defined* using conformation inputs in Lactanet's own formula than with an independently discovered biological effect - this dataset cannot confirm or rule that out, since the exact formula isn't available here.
- **`DS` (Dairy Strength) vs. `BMR` (mastitis resistance): r = -0.59**, stable, and the strongest genuinely informative (non-definitional-looking) relationship found. This is read as a real, modest trade-off: animals bred for more body capacity show somewhat lower genetic mastitis resistance.
- **The intuitive hypothesis "better udder conformation (`MS`) → better udder health" is not supported.** `MS` vs. `SCS` (the direct mastitis/udder-health indicator) is r = 0.02 - stably near zero across every resample. `MS` vs. `HWI` (general health + fertility) is also stably near zero (r ≈ -0.02). `MS` vs. `BMR` is weak (r = -0.32, just past the 0.3 threshold) and in the opposite direction intuition would predict.
- **`MS` vs. `MI` (milking speed/ease): r = 0.26** - weak, below the 0.3 threshold, but directionally plausible (better-shaped udder, marginally easier to milk).

**Practical conclusion for the project:** don't claim a conformation-to-udder-health link - the data doesn't support it. The one strong, stable, health/longevity-adjacent finding worth featuring is the `DS`-`BMR` trade-off.

---

## 5. Multivariate / composite analysis

| Analysis | Method | Why | Code |
|---|---|---|---|
| "Standout trait" per province | **Z-scores** (standardization: `(x - mean) / std`) | Conformation traits (Conf, MS, F&L, DS, RP) are on different scales/ranges; z-scores put them on a common scale so they can be compared and ranked fairly against each other | `(series - series.mean()) / series.std()` |
| Conformation vs. health/fertility emphasis | Composite z-score (average of z-scores within each trait group) | Combines multiple related traits into one directional score per province, so provinces can be ranked on "leans toward conformation" vs. "leans toward health/fertility" without cherry-picking a single trait | `z_scores_df.mean(axis=1)` |
| Which trait best predicts LPI | **Multiple linear regression** (Ordinary Least Squares, standardized coefficients) | Quantifies how strongly each trait moves with LPI while holding the others constant (in a linear sense), unlike a simple pairwise correlation which ignores the other traits | `numpy.linalg.lstsq(X_standardized, y_standardized)` |
| Model fit | **R² (coefficient of determination)** | Reports what % of LPI's variation is explained by the traits included in the regression | `1 - SS_residual / SS_total` |

**Caveat documented alongside this analysis:** the regression traits are correlated with each other (multicollinearity), so individual coefficients should be read as "moves together with LPI," not as proven independent causal weights.

### 5.1 Regression diagnostics - how the model was validated

An interviewer's fair question is "how did you check the regression was valid?" - here's the answer, with results:

| Diagnostic | Method | Code | Result |
|---|---|---|---|
| **Residual plot** | Fitted values vs. residuals scatter | `ax.scatter(model.fittedvalues, model.resid)` | No strong funnel/curve pattern visually, but see Breusch-Pagan below for the formal test. |
| **QQ plot** | Residual quantiles vs. theoretical normal quantiles | `statsmodels.api.qqplot(model.resid, line="45")` | Residuals track the 45° line closely in the middle, with minor deviation in the tails - consistent with the normality test below. |
| **Homoscedasticity** | Breusch-Pagan test | `statsmodels.stats.diagnostic.het_breuschpagan()` | **p < 0.001 → heteroscedasticity present.** Residual variance is not fully constant across fitted values. Fix applied: refit with HC3 robust standard errors (`model.fit(cov_type="HC3")`). |
| **Normality of residuals** | D'Agostino-Pearson test + skew/kurtosis | `scipy.stats.normaltest(model.resid)` | Formally rejected (p=0.011) but skew=-0.12, kurtosis=0.02 - negligible in practice, same large-sample-sensitivity caveat as above. |
| **Multicollinearity** | **Variance Inflation Factor (VIF)**, not just a mention | `statsmodels.stats.outliers_influence.variance_inflation_factor()` | **`Conf` VIF = 125, `MS` VIF = 46** - severe. Both are expected: `Conf` (overall conformation) is itself built from `MS`, `F&L`, `DS`, `RP` by Lactanet's own scoring system, so it's mathematically redundant, not an independent predictor. Fix applied: dropped `Conf` from the model and refit using only its component sub-traits, which all have VIF < 12 individually. |

**Net effect of the fixes:** the corrected model (Conf dropped, HC3 robust SE) is the version that should be cited/defended - it addresses both the multicollinearity and the heteroscedasticity found in the initial diagnostics, rather than reporting the original R²/coefficients uncritically.

---

## 6. Comparing more than 2 groups: ANOVA + Tukey HSD

The EBV-vs-PA and genomic-vs-not comparisons (Section 4) only involve 2 groups, where a t-test is appropriate. Comparing **10 provinces** at once calls for a different test:

| Element | Method | Why | Code |
|---|---|---|---|
| Omnibus test | **One-way ANOVA** | Tests whether *at least one* province's mean differs from the others, across all 10 groups at once - using 45 separate t-tests instead would inflate the false-positive rate (multiple comparisons problem) | `scipy.stats.f_oneway(*groups)` |
| Post-hoc comparison | **Tukey HSD** | ANOVA only tells you *that* a difference exists somewhere; Tukey HSD tests *every pair* of provinces while controlling the family-wise error rate, so you can say specifically which pairs differ | `statsmodels.stats.multicomp.pairwise_tukeyhsd()` |

**Results:** ANOVA was significant (p<0.001) for LPI, Milk, Fat, Protein, and Conformation - province is a real source of variation. Of the 45 province pairs tested with Tukey HSD on LPI, **3** were *not* significantly different: **Alberta vs. Nova Scotia**, **New Brunswick vs. Newfoundland & Labrador**, and **Prince Edward Island vs. Saskatchewan**. Which specific pairs land in this "statistically indistinguishable" set has changed each time a source file was corrected during this project - a reminder that with several provinces sitting within a few dozen LPI points of each other, this is expected and shouldn't be read as a permanently fixed set of pairs.

---

## 7. Confidence intervals

Point estimates (means) were reported alongside 95% confidence intervals to communicate estimation uncertainty, not just a single number:

| Method | Code |
|---|---|
| 95% CI using the t-distribution (appropriate for finite-sample means, more conservative than using the normal distribution) | `margin = (std/sqrt(n)) * scipy.stats.t.ppf(0.975, n-1)` |

With n=400 per province, the resulting intervals are narrow (roughly ±6 to ±14 LPI points), which is itself evidence that the between-province differences found by ANOVA are unlikely to be sampling noise.

---

## 8. Reducing many traits to a comparable picture: PCA

| Element | Method | Why | Code |
|---|---|---|---|
| Dimensionality reduction | **Principal Component Analysis (PCA)** on province-level trait averages (10 provinces × 17 traits, standardized first) | Directly answers "how do provinces group together based on their overall genetic profile," compressing 17 correlated traits into 2 interpretable axes | `sklearn.decomposition.PCA(n_components=2)` on `sklearn.preprocessing.StandardScaler()`-scaled data |
| Interpreting the axes | Component loadings | Shows which original traits drive each principal component | `pca.components_` |

**Results (re-run after correcting Alberta, Ontario, PEI, and Saskatchewan's source files):** PC1 explains 60.5% of variance and PC2 explains 26.7% (87.2% combined - a 2D plot still captures most of the real structure, slightly less cleanly than before the PEI/Saskatchewan correction). **PC1 ≈ overall strength**: nearly every trait (Pro$, Prot, LPI, Fat, %P, %F, HWI, F&L, RI, SCS, MS, MI, Conf, Milk - loadings 0.16 to 0.31) moves together on this axis, while `DS` loads near zero (-0.08) and `EI` loads weakly (+0.09) - this axis is not driven by any single trait, it's a genuine "most things above/below average together" signal. **PC2 ≈ a feed-efficiency-vs-conformation trade-off**, confirmed by loadings (`EI` +0.43; `DS` -0.43, `RP` -0.40, `Conf` -0.38, `MS` -0.34) and independently confirmed in the raw group averages: Manitoba has the highest `EI` of any province (525.6) and is the only province with negative average `DS` (-1.4), while Ontario/Quebec have the lowest `EI` paired with the highest `Conf`. This interpretation held up unchanged across both the Alberta-only correction and the later PEI/Saskatchewan correction - only the province-level scores and cluster memberships shifted, not the meaning of the axes themselves.

---

## 9. Do provinces form natural clusters? KMeans + hierarchical clustering

| Element | Method | Why | Code |
|---|---|---|---|
| Partition-based clustering | **KMeans (k=3)** on the same standardized province profiles used for PCA | Directly answers "do provinces have similar genetic profiles" by grouping them algorithmically instead of eyeballing the PCA plot | `sklearn.cluster.KMeans(n_clusters=3, random_state=42)` |
| Hierarchical clustering | **Agglomerative clustering, Ward's method** + dendrogram | Cross-checks the KMeans result with a different clustering algorithm that doesn't require pre-choosing k, and visualizes *how* provinces merge together | `scipy.cluster.hierarchy.linkage(X, method="ward")` |

**Result (current, final dataset - all 10 source files verified, 0 cross-province overlap, all 10 with a plausible `LPI Code` split):** both methods agree on 3 groups - (1) Quebec, Ontario: above dataset average on PC1 ("overall strength") and leaning most heavily toward conformation on PC2; (2) Manitoba, British Columbia, Prince Edward Island, Alberta: a more mixed group on PC2 (Manitoba is the most extreme province on that axis); (3) New Brunswick, Newfoundland & Labrador, Nova Scotia, Saskatchewan: below dataset average on PC1. Agreement between two independent clustering methods is evidence the grouping reflects real structure given the current data. **This groups provinces by similarity of multivariate profile, not by rank or genetic superiority** - group (1)/(2) score higher on most individual traits than group (3), which is a factual difference, but "different profile" and "better/worse" are separate claims, and clustering only supports the former. All groupings describe each province's top-400-by-LPI subset, not its general cattle population.

This 3-cluster grouping reflects the current data and should be treated as one reasonable read of it, not a permanently fixed classification - with only 10 provinces (data points) going into the clustering, membership near the boundary between groups is inherently less stable than membership clearly in the middle of one.

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
| **Pinned/documented library versions** | `requirements.txt` lists minimum versions; run `pip freeze > requirements.txt` in the project's environment to capture exact versions used, for full reproducibility on another machine. |
| **README** | Documents setup steps, folder structure, and how to run the project end-to-end (see the project's `README.md`). |
| **Deterministic data pipeline** | Loading and cleaning steps involve no randomness - the same input files always produce the same cleaned dataset, independent of the analyses run afterward. |

---

## 13. Choices made deliberately for interpretability

- **No heatmaps.** All comparisons across provinces/traits use sorted, colored (green=positive/red=negative) horizontal or vertical bar charts instead, so a reader can identify "which province, which direction" without needing to interpret a color-intensity matrix.
- **EBV-only subsets for "best animal" rankings.** Comparing PA (pedigree-only) and EBV (official phenotype-based) animals directly would be unfair, since they're evaluated on different amounts of information; EBV-only animals were used for "best animal by province" rankings, and PA-vs-EBV was only ever compared as its own separate, explicit analysis.
- **Excluded 2 provinces from PA vs. EBV comparisons.** Newfoundland & Labrador and Nova Scotia show 100% `EBV` / 0% `PA`, which is not a realistic split for a real population - including these 2 provinces would have silently biased the comparison.

---

## 14. Selection bias - the single most important methodological caveat

Every animal in this dataset comes from a province's **top 400 by LPI**, not a random or complete sample of that province's cattle population. This has a specific, predictable consequence: any statistic computed on this data (means, standard deviations, correlations) describes the *selected elite tier*, not the underlying population those animals were drawn from. Two concrete ways this matters:

- **Range restriction.** Selecting the top 400 by LPI truncates the distribution of LPI itself (and, more weakly, of traits correlated with LPI) within each province. Correlations and variances computed on a range-restricted sample are generally attenuated relative to the full population - so relationships that appear weak in this dataset (e.g., production vs. conformation) could in principle be somewhat stronger in the unrestricted population, though the very low values found here (mostly r<0.1) make it unlikely that restriction alone explains the near-zero result.
- **Province-to-province comparability depends on population size.** A province with a larger underlying cattle population has a deeper pool to draw its top 400 from; a province with a smaller population's "top 400" reaches further down its actual distribution. This dataset cannot correct for that, because provincial population sizes aren't included - it's a limitation to flag explicitly, not one this analysis can resolve.

This caveat applies to every provincial comparison in this report and is the primary reason regional patterns here are described as observed associations within elite populations, not as claims about each province's general dairy herd.

---

## 15. Context: the Canadian genetic evaluation system

Canada's national genetic evaluation system has been in continuous development since the Canadian Dairy Network (one of Lactanet's predecessor organizations) introduced LPI in 1991, initially combining production, durability, and health/fertility traits (Lactanet extension publications, B. Van Doormaal, Chief Services Officer). Canada implemented genomic evaluations in August 2009, early relative to most other dairy genetic evaluation systems internationally. Two general points from the broader quantitative genetics literature are relevant background for interpreting this analysis, without this project claiming to test either directly:

- **Genomic and pedigree-based information are commonly combined into a single evaluation (single-step methods)** rather than treated as fully separate pipelines (Misztal et al., 2009). This is broader methodological context for why this dataset's four information states (pedigree-only, genomic-only, phenotype-only, combined) behave as they do, not a claim about which specific method Lactanet uses internally.
- **International comparisons of genetic evaluations across countries are coordinated through Interbull**, which is a separate function from within-country provincial reporting; this analysis is entirely within-Canada and does not involve Interbull data or methods.

**On the `DS`-`BMR` trade-off (Section 4.2, r=-0.59):** one established biological framework for why selection toward a production/capacity-related trait might coincide with reduced disease resistance is resource-allocation trade-off theory in livestock - the idea that selecting hard for one trait can leave fewer physiological resources available for others, including immune function (Rauw et al., 1998). This is offered as a plausible mechanism worth considering, not a claim this dataset tests directly; confirming it would require physiological or immunological data this project doesn't have.

---

## References

- Hayes, B.J., Bowman, P.J., Chamberlain, A.J., Goddard, M.E. (2009). Invited review: Genomic selection in dairy cattle: Progress and challenges. *Journal of Dairy Science*, 92(2), 433-443.
- Misztal, I., Legarra, A., Aguilar, I. (2009). Computing procedures for genetic evaluation including phenotypic, full pedigree, and genomic information. *Journal of Dairy Science*, 92(9), 4648-4655.
- Rauw, W.M., Kanis, E., Noordhuizen-Stassen, E.N., Grommers, F.J. (1998). Undesirable side effects of selection for high production efficiency in farm animals: a review. *Livestock Production Science*, 56(1), 15-33.
- VanRaden, P.M. (2008). Efficient methods to compute genomic predictions. *Journal of Dairy Science*, 91(11), 4414-4423.
- Van Doormaal, B. Lactanet extension publications on LPI history and genomic evaluation implementation in Canada (lactanet.ca).

These are cited for general methodological and biological context. None of them were used to derive or validate the specific statistical results in this project - those come entirely from the analysis described in Sections 1-12.
