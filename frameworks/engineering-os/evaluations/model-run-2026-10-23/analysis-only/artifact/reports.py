CACHE = {}

def report(tenant, report_id):
    if report_id not in CACHE:
        CACHE[report_id] = {"tenant":tenant,"report_id":report_id}
    return dict(CACHE[report_id])
