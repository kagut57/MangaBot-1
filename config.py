env_vars = {
    # Get from my.telegram.org
    "API_HASH": "c0da9c346d2c45dbc7ec49a05da9b2b6",
    # Get from my.telegram.org
    "API_ID": "13675555",
    # Get from @BotFather
    "BOT_TOKEN": "5555986769:AAG-nNw82PHwBPlPZ5h55d3hnfHxzqc5JeI",
    # Get from tembo.io
    "DATABASE_URL_PRIMARY": "postgresql://db_muuwb1cxrk3p:xVHzjUlRyOdDhOCh1OPghz0y@up-de-fra1-postgresql-1.db.run-on-seenode.com:11550/db_muuwb1cxrk3p",
    # Logs channel username without @
    "CACHE_CHANNEL": "",
    # Force subs channel username without @
    "CHANNEL": "",
    # {chap_num}: Chapter Number
    # {chap_name}: Manga Name
    # Example: Chapter {chap_num} {chap_name} @Manhwa_Arena
    "FNAME": "",
    # Thumb link (Optional)
    "THUMB": "",
    # Add authorized user IDs, separated by commas in a list
    "SUDOS": [5591954930]
}

# Determine the database URL (default to SQLite if not provided)
dbname = (
    env_vars.get("DATABASE_URL_PRIMARY") 
    or env_vars.get("DATABASE_URL") 
    or "sqlite:///test.db"
)

# Ensure compatibility with SQLAlchemy if using older Postgres URL formats
if dbname.startswith("postgres://"):
    dbname = dbname.replace("postgres://", "postgresql://", 1)
