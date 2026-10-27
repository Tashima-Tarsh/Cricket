# STRIKE//OS Official Fantasy Scoring Engine & Rule Specifications

**Source:** [Dream11 Official Fantasy Cricket Point System](https://www.dream11.com/fantasy-cricket/point-system)  
**Verification Date:** 2026-10-27  
**Rule Version:** `dream11_published_2026_10_27`  
**Engines Covered:** `gl_engine/official_scoring.py`, `edgeforge/score/dream11.py`, `dream11-edge/edge/score.py`

---

## 1. Supported Formats & Milestone Profiles

| Category / Action | T20 / T20I | One Day International (ODI) | T10 |
|---|---|---|---|
| **Playing XI Appearance** | +4 pts | +4 pts | +4 pts |
| **Every Run Scored** | +1 pt | +1 pt | +1 pt |
| **Boundary Bonus (4s)** | +4 pts (published) / +1 pt (legacy) | +1 pt | +1 pt |
| **Six Bonus (6s)** | +6 pts (published) / +2 pts (legacy) | +2 pts | +2 pts |
| **Batting Milestones** | 25r: +4, 50r: +8, 75r: +12, 100r: +16 | 25r: +4, 50r: +8, 75r: +12, 100r: +16, 125r: +20, 150r: +24 | 25r: +8, 50r: +12, 75r: +16, 100r: +20 |
| **Duck Penalty (dismissed for 0)** | -2 pts (min 1 ball faced) | -3 pts (min 1 ball faced) | -2 pts (min 1 ball faced) |
| **Wicket (Excluding Run-Out)** | +30 pts (legacy: +25 pts) | +25 pts | +25 pts |
| **Bowled / LBW Bonus** | +8 pts | +8 pts | +8 pts |
| **Wicket Haul Bonus** | 3w: +4, 4w: +8, 5w: +12 | 4w: +4, 5w: +8, 6w: +12 | 2w: +4, 3w: +8, 4w: +12, 5w: +16 |
| **Maiden Over** | +12 pts | +4 pts | +16 pts |
| **Dot Balls** | +1 pt per dot | +1 pt per **3** dots | +1 pt per dot |
| **Catch** | +8 pts | +8 pts | +8 pts |
| **3 Catch Bonus** | +4 pts | +4 pts | +4 pts |
| **Stumping** | +12 pts | +12 pts | +12 pts |
| **Run Out (Direct / Indirect)** | +12 pts / +6 pts | +12 pts / +6 pts | +12 pts / +6 pts |

---

## 2. Strike-Rate Adjustments (Batting)

*Minimum balls faced: T20 (10 balls), ODI (20 balls), T10 (5 balls).*

| Format | S/R > 170 | S/R 150.1 – 170 | S/R 130 – 150 | S/R 60 – 70 | S/R 50 – 59.9 | S/R < 50 |
|---|---|---|---|---|---|---|
| **T20** | +6 pts | +4 pts | +2 pts | -2 pts | -4 pts | -6 pts |
| **ODI** *(S/R > 140 / 120 / 100)* | +6 pts (>140) | +4 pts (>120) | +2 pts (>=100) | -2 pts (40–50) | -4 pts (30–39.9) | -6 pts (<30) |
| **T10** *(S/R > 190 / 170 / 150)* | +6 pts (>190) | +4 pts (>170) | +2 pts (>=150) | -2 pts (70–80) | -4 pts (60–69.9) | -6 pts (<60) |

---

## 3. Economy-Rate Adjustments (Bowling)

*Minimum overs bowled: T20 (2.0 ov), ODI (5.0 ov), T10 (1.0 ov).*

| Format | Super Economy | Good Economy | Moderate Economy | Expensive | Very Expensive | Severe |
|---|---|---|---|---|---|---|
| **T20** | < 5.0 RPO (+6) | 5.0 – 5.99 (+4) | 6.0 – 7.0 (+2) | 10.0 – 11.0 (-2) | 11.01 – 12.0 (-4) | > 12.0 RPO (-6) |
| **ODI** | < 2.5 RPO (+6) | 2.5 – 3.49 (+4) | 3.5 – 4.5 (+2) | 7.0 – 8.0 (-2) | 8.01 – 9.0 (-4) | > 9.0 RPO (-6) |
| **T10** | < 7.0 RPO (+6) | 7.0 – 7.99 (+4) | 8.0 – 9.0 (+2) | 14.0 – 15.0 (-2) | 15.01 – 16.0 (-4) | > 16.0 RPO (-6) |

---

## 4. Multipliers & Reduced-Over Conditions

- **Captain**: Exactly `2.0x` total fantasy points.
- **Vice-Captain**: Exactly `1.5x` total fantasy points.
- **Captain & Vice-Captain Invariance**: The same player cannot be assigned both Captain and Vice-Captain; attempting this raises an explicit validation `ValueError`.
- **Rain Reduced Overs**: In shortened matches (DLS rain interruptions), strike-rate and economy-rate qualifying minimums scale proportionally with match length according to ICC Playing Conditions.

---

## 5. Versioning & Provenance Metadata

Every output from `score_official` or `POST /api/v1/score` carries:
- `rule_version`: e.g. `"dream11_published_2026_10_27"` or `"legacy_v3"`
- `provenance.source`: `"https://www.dream11.com/fantasy-cricket/point-system"`
- `provenance.verification_status`: `"VERIFIED"`
- `breakdown`: Detailed breakdown by batting, bowling, fielding, starting XI, dot balls, and milestone bonuses.
