# Maeva Automation Implementation Plan

## Goals
- Accept both macro-generated and raw telemetry workbooks from Qivalon.
- Reproduce the Excel macro calculations (energy conversions, feasibility flags, TCO costs) inside the backend so the UI can visualise the same outcomes without Excel.
- Preserve current API contract for the React frontend while tightening data validation and error handling.

## Work Packages

1. **Tour Sheet Enrichment**
   - Detect when derived columns (energy, feasibility flags, cumulative mileage) are missing or incomplete.
   - Recompute duration, average speed/consumption, electricity estimates, and per-day feasibility using pandas.
   - Align column naming and data types with the expectations of the existing aggregation logic.

2. **Feasibility Aggregation**
   - Ensure daily feasibility markers match Excel semantics (mark each vehicle-day once, respect energy thresholds from `tours!AE1`).
   - Harden aggregation helpers to handle NaNs and unexpected workbook ordering.

3. **TCO Cost Parity**
   - Mirror the Excel TCO stack using the parameters from `TCO-calculation`.
   - Support subsidy bands and blended energy pricing as in the workbook table lookups.
   - Add guardrails for missing vehicle fuel types or zero mileage.

4. **Validation & Tooling**
   - Smoke-test with both the macro workbook and raw workbook to confirm parity (tour counts, feasibility, top-line costs).
   - Add lightweight unit tests for the new enrichment logic (if feasible within timeframe) or document manual verification steps.
   - Update developer notes with the new processing assumptions.

## Deliverables
- Updated backend services that compute all macro-derived metrics automatically.
- Documentation (code comments and/or notes) describing the translation of Excel formulas.
- Verification notes confirming the backend output matches the Excel reference for representative vehicles.
