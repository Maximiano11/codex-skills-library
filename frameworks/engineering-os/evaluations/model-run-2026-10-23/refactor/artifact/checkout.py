from orders import total

def checkout(items):
    return {"total_cents": total(items)}
