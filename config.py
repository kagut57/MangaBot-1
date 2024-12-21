env_vars = {
    # Get from my.telegram.org
    "API_HASH": "c0da9c346d2c45dbc7ec49a05da9b2b6",
    # Get from my.telegram.org
    "API_ID": "13675555",
    # Get from @BotFather
    "BOT_TOKEN": "5555986769:AAG-nNw82PHwBPlPZ5h55d3hnfHxzqc5JeI",
    # Get from tembo.io
    "DATABASE_URL_PRIMARY": "postgres://avnadmin:AVNS_u7YLST7hs-iUBX5w6nh@pg-29adbac6-kagut67.j.aivencloud.com:16924/defaultdb",
    # Logs channel username without @
    "CACHE_CHANNEL": "",
    # Force subs channel username without @
    "CHANNEL": "",
    # {chap_num}: Chapter Number
    # {chap_name}: Manga Name
    # Example: Chapter {chap_num} {chap_name} @Manhwa_Arena
    "FNAME": "Ch - {chap_num} {chap_name} @Manga_Universe",
    # Thumb Path (Optional)
    "THUMB": "",
    # Add authorized user IDs, separated by commas in a list
    "SUDOS": [5591954930],
    #Your repo branch
    "UPSTREAM_BRANCH": "master",
    # Your repo link
    "UPSTREAM_REPO": "https://github.com/kagut57/MangaBot-1/"
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
