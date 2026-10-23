def migrate(conn):
    columns = conn.execute("PRAGMA table_info(users)").fetchall()
    if not any(column[1].casefold() == "timezone" for column in columns):
        conn.execute("ALTER TABLE users ADD COLUMN timezone TEXT")
