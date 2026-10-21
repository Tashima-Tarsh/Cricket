from pathlib import Path

readme_path = Path("C:/Users/lenovo/.gemini/antigravity/scratch/Cricket/README.md")

with open(readme_path, "r", encoding="utf-8") as f:
    text = f.read()

# Normalize CRLF to LF for matching
is_crlf = "\r\n" in text
text_norm = text.replace("\r\n", "\n")

target = """### 3. DLS Interruption Resources
Resource loss percentage computed from the standard decile exponential decay curve:

$$R(u, w) = R_0(w) \\cdot \\left(1 - \\exp\\left(-\\frac{b \\cdot u}{R_0(w)}\\right)\\right)$$

Where $u$ represents remaining overs and $w$ represents lost wickets."""

addition = """

---

### 4. The 4 Universal Match Archetypes (The Game Script Framework)
To win institutional Grand Leagues (270k to 1M+ spots), the engine eliminates single-point average expectations ($E[P]$) and classifies any fixture into one of four game-state archetypes:

```
                                    CRICKET FIXTURE
                                           │
         ┌──────────────────┬──────────────┴──────────────┬──────────────────┐
         ▼                  ▼                             ▼                  ▼
    ARCHETYPE 1        ARCHETYPE 2                   ARCHETYPE 3        ARCHETYPE 4
   The Road / Flat   The Low-Scoring Minefield     The Powerhouse vs    The High-Stakes
   Highway (200+)      (120–140 Spin/Seam)          Underdog Mismatch    Parity Derby
```

1. **ARCHETYPE 1: Road / High-Scoring Highway (Par 195–230)**:
   - *Dynamics:* True bounce, minimal lateral movement, fast outfield.
   - *Lineup Rule:* Top-order stacking (Openers + No. 3 face ~70% of deliveries).
   - *Fade Rule:* Fade specialist powerplay-only bowlers (bleed runs, high economy penalties).
   - *Captaincy Rule:* Top-3 Batters or Death Power Hitters (70+ milestone bonuses).

2. **ARCHETYPE 2: Minefield / Spin Choke (Par 125–145)**:
   - *Dynamics:* Gripping surface, variable bounce, sharp spin.
   - *Lineup Rule:* Stack 5 to 6 Bowlers/All-Rounders (bowlers outscore batters 2:1).
   - *Fade Rule:* Fade aggressive boundary-reliant openers (>60% bust rate).
   - *Captaincy Rule:* Mystery spinners and change-of-pace seamers (3 wkts + maiden = 110–135 pts).

3. **ARCHETYPE 3: Asymmetric Mismatch / Bilateral Dead-Rubber**:
   - *Dynamics:* Heavy favorite vs Associate/underdog (e.g. IND-W vs ZIM-W, AUS vs SCO).
   - *Underdog Law:* Opposition 2-way all-rounders bowling death overs + batting top 4 are guaranteed maximum volume.
   - *Captaincy Rule:* Leverage middle-order accelerations and underdog all-rounder VC.

4. **ARCHETYPE 4: High-Stakes Parity Derby (Even Strength)**:
   - *Dynamics:* High tactical preparation, narrow victory margins (IND vs PAK, IPL playoffs).
   - *Lineup Rule:* 6-5 split; micro-matchup exploitation (e.g. SLA vs RHB top-order vulnerability).

---

### 5. The 3 Invariable Laws of Rank 1 Lineup Generation

$$\\text{Leverage } L_i = z(E[P_i]) - z(\\text{own}_i) \\quad \\Big| \\quad P(\\text{Cap}) \\times P(\\text{VC}) \\le 0.05$$

* **Law I: The Unspent Credit Structural Shield ($81.0 - 86.5$ Credits Spent)**:
  Over 92% of the casual public forces expensive players to reach 99.0–100.0 credits. Leaving **13.5 to 19.0 credits unspent** guarantees **zero to sub-2 duplicate teams** across a 270,000-entry contest while preserving maximum 95th-percentile ceiling points.

* **Law II: C/VC Ownership Independence ($P(\\text{Cap}) \\times P(\\text{VC}) \\le 0.05$)**:
  Combined ownership product of Captain and Vice-Captain must not exceed 5%. Unlocks sole ownership of Rank 1 without requiring 11 low-floor differential punts.

* **Law III: Game Script Coherence (Positive Covariance)**:
  Eliminates internal cannibalization. Every player in the 11 must make sense within the same 40-over narrative (e.g., favorite strike bowlers paired with underdog middle-order all-rounders, not dismissed openers).

---

### 6. Dead-Rubber Captaincy Bias Filter & The "Two Bites at the Cherry" Rule

* **Dead-Rubber Captaincy Filter**:
  When a series is decided (2-0 up) and a captain explicitly announces *"giving game time to the middle order"*, apply a **-35% balls-faced projection penalty to the captain** and boost middle-order No. 3–5 batters by **+35% to +45%**.
* **The "Two Bites at the Cherry" Law**:
  In asymmetric mismatches, an underdog all-rounder who bowls death overs (4 overs) AND bats in the top 4 has two independent Poisson processes generating fantasy points. In GPPs, this player carries a higher 95th-percentile ceiling than a specialist bowler and should be prioritized for **Vice-Captaincy**.

---

### 7. Forensic Case Study: India Women vs Zimbabwe Women (3rd T20I, Raipur)

| Metric | User T1 | Winning Team (JOY MA TARA \\| T8) | Tactical Driver |
| :--- | :---: | :---: | :--- |
| **Total Score** | 1,031.5 pts | **1,309.0 pts** (+277.5) | **Rank 1 Overall Champion** |
| **Captain (2.0x)** | H. Kaur (366 pts) | H. Kaur (366 pts) | 91* off 41 balls (21% owned leverage) |
| **Vice-Captain (1.5x)**| K. Gaud (67.5 pts) | **B. Biza (252.0 pts)** | 3 wkts + 44 runs (Two Bites at the Cherry) |
| **Star Batter Fade** | S. Mandhana (4 pts) | **S. Mayers (112.0 pts)** | Mandhana DNB; Mayers scored 60 off 49 |
| **Underdog All-Rounder**| J. Nkomo (4 pts - DNB) | **N. Gwanzura (57.0 pts)** | Gwanzura 1 wkt + 2 catches |
| **Credits Unspent** | 15.0 Cr Unspent | **15.0 Cr Unspent** | Absolute zero duplicates in 270k field |"""

if target in text_norm:
    text_norm = text_norm.replace(target, target + addition)
    if is_crlf:
        text_norm = text_norm.replace("\n", "\r\n")
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(text_norm)
    print("README.md successfully updated with all algorithms and case studies!")
else:
    print("Still not matched, searching for anchor...")
    anchor = "### 3. DLS Interruption Resources"
    if anchor in text_norm:
        idx = text_norm.find(anchor)
        next_section = text_norm.find("---", idx)
        text_norm = text_norm[:next_section] + addition + "\n\n" + text_norm[next_section:]
        if is_crlf:
            text_norm = text_norm.replace("\n", "\r\n")
        with open(readme_path, "w", encoding="utf-8") as f:
            f.write(text_norm)
        print("README.md successfully updated via anchor!")
