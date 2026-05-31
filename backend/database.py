"""
database.py - SQLite Database Setup
=====================================
Creates and manages the SQLite database.
We use a simple flat structure - one main table for colleges.
"""

import sqlite3
import os

# Database file location
DB_PATH = os.path.join(os.path.dirname(__file__), "../data/collegepath.db")


def init_db():
    """
    Initialize the database by creating tables if they don't exist.
    Called once when the server starts.
    """
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = get_db_connection()
    cursor = conn.cursor()

    # Main colleges table - stores cutoff data for all colleges
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS colleges (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            branch TEXT NOT NULL,
            category TEXT NOT NULL,           -- OPEN, OBC, SC, ST, EWS
            cutoff_percentile REAL,           -- e.g. 92.5
            cutoff_rank INTEGER,              -- e.g. 1200
            fees INTEGER,                     -- Annual fees in INR
            city TEXT,
            type TEXT,                        -- government or private
            placements_avg INTEGER,           -- Average placement package in LPA
            naac_grade TEXT,                  -- A++, A+, A, B++, etc.
            hostel_available INTEGER,         -- 1 = yes, 0 = no
            latitude REAL DEFAULT 18.5204,    -- for map display
            longitude REAL DEFAULT 73.8567,
            UNIQUE(name, branch, category)    -- avoid duplicates
        )
    """)

    # Students table - stores student profiles
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            percentage REAL,
            rank INTEGER,
            category TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()
    print("✅ Database initialized successfully")


def get_db_connection():
    """
    Returns a new database connection.
    row_factory=sqlite3.Row lets us access columns by name (like a dict).
    Always call conn.close() after you're done!
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row   # lets us do row["column_name"]
    return conn