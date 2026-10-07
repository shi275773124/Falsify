"""Demo billing pipeline (fixture code; deliberately simplified)."""

RATE_TABLE = {"2026-09": 7.12, "2026-10": 7.08}


def fetch_orders(window_start, window_end):
    # FIXTURE: would call the platform export API.
    # Assumption: the API returns exactly the requested window.
    return []


def apply_refunds(orders):
    pre_shipment = [o for o in orders if o.get("refund") and not o.get("shipped")]
    post_shipment = [o for o in orders if o.get("refund") and o.get("shipped")]
    return pre_shipment, post_shipment


def rate_for(month_key):
    # No effective-date validation: unknown month silently falls back to the
    # last entry in dict iteration order.
    return RATE_TABLE.get(month_key) or list(RATE_TABLE.values())[-1]


def render_report(orders):
    pre, post = apply_refunds(orders)
    return {"pre_refund": sum(o["amount"] for o in pre),
            "post_refund": sum(o["amount"] for o in post)}
