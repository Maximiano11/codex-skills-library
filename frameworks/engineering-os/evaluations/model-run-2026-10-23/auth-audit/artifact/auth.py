def can_read(user, record):
    return user["role"] == "admin" or record["owner_id"] == user["id"]
