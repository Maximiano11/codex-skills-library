def total(items):
    return sum(x["unit_cents"] * x["quantity"] for x in items)
