"""
db_setup.py

Helps in creating SQLite database and a `users` table that we use
to store user details with path of sign and photo files.

# python database/db_setup.py

use the above command to initialize the database.
"""

import sqlite3
import os

DB_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(DB_DIR, "app.db")


def get_connection():
    """Return a new SQLite connection to the app database."""
    conn = sqlite3.connect(DB_PATH)

    #config to return query result as dict instead of tuples
    conn.row_factory = sqlite3.Row

    return conn


def init_db():
    """Create `users` table if not already created."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL ,
            contact TEXT,
            location TEXT,
            sign_path TEXT NOT NULL,
            photo_path TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()
    print(f"Initialized database at {DB_PATH}")


if __name__ == "__main__":
    init_db()
