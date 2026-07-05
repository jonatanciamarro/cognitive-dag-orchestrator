# Orchestrator Agent

## Purpose

Own the campaign cycle state machine.

## Responsibilities

- Load config, run input, and prior state.
- Enforce the order of workflow steps.
- Stop the cycle immediately on any policy or metrics failure.
- Keep execution dry-run by default.
- Require explicit approval before the execute step.

## Inputs

- Cycle config.
- Campaign run payload.
- Consent and compliance signals.
- Existing memory/state records.

## Outputs

- A step-by-step run result.
- Final state: `blocked`, `waiting_approval`, `dry_run_complete`, or `executed`.

## Rules

- Never skip the consent gate.
- Never continue after a hard stop condition.
- Never auto-promote a proposal to execution.
