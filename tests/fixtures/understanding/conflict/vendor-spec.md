# Vendor spec — sync interval (fixture)

## Commitment

The connector synchronizes every 60 seconds. Sync is atomic per batch; a failed batch
is retried on the next cycle.

## Version

Spec revision 3, effective 2026-06-01.
