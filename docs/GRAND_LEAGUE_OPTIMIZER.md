# STRIKE//OS Grand League Lineup Optimization & Portfolio Intelligence

**Date:** 2026-10-27  
**Module:** `gl_engine/unique_engine.py` & `gl_engine/optimizer.py`  
**Solver Engine:** Google OR-Tools CP-SAT (Constraint Programming - Satisfiability)

---

## 1. Mathematical Formulation (CP-SAT MILP)

For a pool of $N$ eligible cricket players, let binary decision variable $x_i \in \{0, 1\}$ denote whether player $i$ is selected in the 11-player lineup.

### Decision Variables
- $x_i \in \{0, 1\}$: 1 if player $i$ is in the lineup, 0 otherwise.
- $c_i \in \{0, 1\}$: 1 if player $i$ is designated Captain ($2.0\times$ multiplier).
- $v_i \in \{0, 1\}$: 1 if player $i$ is designated Vice-Captain ($1.5\times$ multiplier).

### Core Contest Constraints
1. **Lineup Size**:
   $$\sum_{i=1}^N x_i = 11$$
2. **Configurable Credit Budget**:
   $$C_{\min} \le \sum_{i=1}^N \text{credits}_i \cdot x_i \le C_{\max}$$
   *Unused credits are a configurable strategic parameter ($C_{\max} \in [88.0, 100.0]$ depending on uniqueness tier), not an invariant constant.*
3. **Role Composition**:
   $$1 \le \sum_{i \in \text{WK}} x_i \le 4$$
   $$3 \le \sum_{i \in \text{BAT}} x_i \le 6$$
   $$1 \le \sum_{i \in \text{AR}} x_i \le 4$$
   $$3 \le \sum_{i \in \text{BOWL}} x_i \le 6$$
4. **Team Limits & Balanced Split**:
   $$\sum_{i \in \text{Team}_A} x_i \le 7, \quad \sum_{i \in \text{Team}_B} x_i \le 7$$
   $$4 \le \sum_{i \in \text{Team}_A} x_i \le 7 \quad (\text{enforces 6-5 or 7-4 split})$$
5. **Captain & Vice-Captain Exclusivity**:
   $$\sum_{i=1}^N c_i = 1, \quad \sum_{i=1}^N v_i = 1$$
   $$c_i \le x_i, \quad v_i \le x_i, \quad c_i + v_i \le 1 \quad \forall i$$

---

## 2. Grand League Unique Team Rules

1. **Differential Leverage Score**:
   $$\text{differential\_score}_i = \frac{\text{predicted\_points}_i}{\max(\text{predicted\_ownership}_i, 1.0)}$$
2. **Anti-Chalk Clumping**:
   Lineups must never contain all top-5 highest-owned players simultaneously:
   $$\sum_{i \in \text{Top5Chalk}} x_i \le \max(2, 5 - \lfloor \text{uniqueness} / 3 \rfloor)$$
3. **Differential Gem Requirement**:
   Contrarian lineups must include low-owned high-ceiling gems ($<35\%$ ownership):
   $$\sum_{i \in \text{Gems}} x_i \ge \max(1, \lfloor \text{uniqueness} / 2.5 \rfloor)$$
4. **Portfolio Diversity Cut**:
   For each previously generated lineup $K$ with indices $S_K$:
   $$\sum_{i \in S_K} x_i \le 9 \quad (\text{guarantees } \ge 2 \text{ player difference})$$
5. **Lock & Exclusion Strictness**:
   - $x_i = 1 \quad \forall i \in \text{Locked}$
   - $x_i = 0 \quad \forall i \in \text{Excluded}$
   - Excluded players are never reintroduced under any condition. If constraints cannot be satisfied, the solver returns an explicit infeasibility status.

---

## 3. Truthful Simulation vs Real-Field Probability

- **Monte Carlo Contest Simulation**: Simulates player scoring distributions via Gamma variance modeling and generates representative competitor fields.
- **Explicit Diagnostics**: Metrics are labelled as `uncalibrated_rank_1_pct` and `uncalibrated_top_10_pct`.
- **Zero Hallucinated Guarantees**: Calibrated probability fields (`rank_1_probability_pct`, `top_10_probability_pct`) are strictly output as `null` / `None` until validated against ground-truth multi-million contest field archives.

