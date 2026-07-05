# Opt-In Only Cycle

This example shows the expected flow for a campaign cycle that cannot proceed without explicit opt-in.

## Inputs

- `configs/opt_in_cycle.json`
- `examples/opt_in_cycle_run.json`

## Expected behavior

1. Load the run inputs and consent evidence.
2. Check that opt-in is present.
3. Validate the latest metrics against thresholds.
4. Run the compliance gate.
5. Generate a constrained proposal.
6. Wait for explicit approval.
7. Execute only when approval is `approved` and the run is not forced into dry-run mode.
8. Record the outcome in memory/state.

## Example command shape

```bash
campaign-bot run --config configs/opt_in_cycle.json --input examples/opt_in_cycle_run.json
```

## Important rule

If opt-in or consent is missing, the cycle stops before optimization and no execution step runs.
