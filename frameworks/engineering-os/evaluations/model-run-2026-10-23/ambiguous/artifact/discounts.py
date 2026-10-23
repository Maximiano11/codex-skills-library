DEFAULT_PERCENT = 5

def price(cents):
    return cents * (100 - DEFAULT_PERCENT) // 100
