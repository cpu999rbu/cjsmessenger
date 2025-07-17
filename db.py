import sqlite3
from contextlib import closing

DB = 'messenger.db'

def init_db():
    with closing(sqlite3.connect(DB)) as db:
        with open('schema.sql') as f:
            db.executescript(f.read())
        db.commit()

def get_db():
    conn = sqlite3.connect(DB, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn