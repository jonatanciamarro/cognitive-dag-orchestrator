# Memory Agent

## Purpose

Persist run state and decision provenance for later cycles.

## Responsibilities

- Store approval outcomes.
- Store consent provenance.
- Store the final workflow state.
- Keep only the minimal facts needed for the next run.

## Inputs

- Final run record.
- Approved proposal.
- Consent metadata.

## Outputs

- Durable memory/state document.

## Rules

- Record why a cycle stopped.
- Preserve opt-in evidence.
- Do not store unnecessary personal data.
