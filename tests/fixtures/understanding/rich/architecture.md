# Demo billing pipeline — architecture (fixture)

The pipeline ingests order events, applies refund logic, and writes a weekly billing report.

## Data flow

1. `fetch_orders()` pulls raw order events from the platform export (lines land in `orders_raw`).
2. `apply_refunds()` splits refunds into pre-shipment and post-shipment buckets.
3. `render_report()` emits the weekly table used by finance.

## Stated assumptions

- The platform export is assumed complete for the requested window (no silent truncation).
- Refund status is assumed final once the export marks it settled.
- Currency conversion uses a fixed rate table updated monthly.

## Known weak points

- The weekly window is passed as a request parameter; no independent verification that the
  returned rows actually fall inside that window.
- The rate table has no effective-date check; a stale table silently reuses last month's rate.
