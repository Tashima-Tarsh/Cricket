# STRIKE//OS Out-of-Time Forecasting & Model Validation Report

**Date:** 2026-10-27  
**Validation Module:** `gl_engine/model_validation.py`  
**Database:** `t20.duckdb` (134,722 deliveries, 17,526 fixture-player rows evaluated)  
**Evaluation Target:** Observed partial score proxy (runs, boundaries, wickets, dot balls)  
**Certification Status:** `OUT_OF_TIME_SKILL_NOT_ESTABLISHED` (Honest Research Reporting)

---

## 1. Data Leakage Controls

To strictly comply with **Non-Negotiable Invariants 1, 2, and 5**, temporal evaluation is enforced:
1. **Chronological Splitting**: All train, calibration, and test splits are partitioned strictly by date. For any match at date $T$, zero observations from date $T$ or later are present in training features.
2. **Doubleheader Isolation**: Matches played on the same calendar day cannot contribute to each other's feature sets.
3. **No Retrospective Leakage**: Observed final batting positions, deliveries bowled, confirmed match outcomes, or opponent bowling rotations from the target game are excluded from pre-match input vectors.

---

## 2. Empirical Validation Results

Evaluation performed across **15,566 out-of-time examples** with 3+ prior appearances:

| Metric | XGBoost Regressor (120 trees, depth 3) | 5-Match Rolling Mean Baseline | Relative Gain / Lift |
|---|---|---|---|
| **Mean Absolute Error (MAE)** | **26.0500** | 27.9247 | **+6.71% uplift** |
| **Root Mean Squared Error (RMSE)** | **33.1968** | 35.6175 | **+6.80% uplift** |
| **Mean Signed Bias** | **-1.0960** | +0.9218 | Low systematic bias |
| **Coefficient of Determination ($R^2$)** | **0.0164** | -0.1322 | Weak correlation |
| **90% Interval Coverage** | **89.56%** | N/A | Calibrated within 0.44% |
| **Sample Size ($N$)** | **2,931 test samples** | 2,931 test samples | Held out (2025-03-26 to 2026-05-31) |

---

## 3. Calibrated Uncertainty & Prediction Intervals

Rather than presenting false single-point certainty:
- **Calibration Interval**: Computed exclusively on held-out validation dates (`2016-05-17` onwards).
- **Error Quantiles**: 5th percentile = -38.78 pts, 95th percentile = +67.57 pts.
- **Empirical Coverage**: Tested on 2,931 unseen temporal holdout samples from 2025–2026. The nominal 90% interval captured **89.56%** of actual outcomes.

---

## 4. Truthful Calibration Declarations

Under Non-Negotiable Invariant 5:
- **`contest_probability_calibrated: false`**: Model estimates reflect historical statistical opportunity, not calibrated win percentages in a multi-million-entry contest.
- **`rank_1_probability_available: false`**: The platform never advertises or guarantees Rank 1, profit, or ROI.
- **`current_deployed_model_validated: false`**: Low $R^2$ (0.0164) is explicitly reported to users and operators. The model improves over simple rolling averages (+6.71% MAE) but possesses high natural variance inherent to T20 cricket.

