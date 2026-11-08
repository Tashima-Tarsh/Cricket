# dream11-edge

Simulation-driven Dream11 grand league engine.

## Why

Most fantasy tools predict points and optimise expected score. Grand leagues pay the
tail, so the objective is a *rank percentile* against a *simulated field*. This
project simulates correlated match outcomes, simulates the opponent field, and emits
a portfolio optimised for `P(top 0.01%)`.

## Install

    pip install -e .
    edge init
    edge build --demo --entries 60 --open

## Commands

    edge init                                create db, load rules
    edge sync                                pull today's fixtures
    edge matches                             list matches
    edge build <match_id> --entries 200      full pipeline
    edge watch <match_id>                    live toss loop
    edge backtest <from> <to>                walk-forward evaluation
    edge serve                               open dashboard
    pytest                                   run invariant tests

## Architecture

    ingest -> features -> fit -> correlate -> simulate -> field -> solve -> portfolio

The two invariants that must hold every run:
  1. copula.verify: realised correlation within 0.06 of target
  2. constraints.is_legal: every emitted lineup is legal

If (1) fails, every downstream number is fiction.
