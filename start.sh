echo "Started..."
gunicorn app:app & python3 main.py
