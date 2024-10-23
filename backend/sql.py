import sqlite3

# Create or connect to the SQLite database
conn = sqlite3.connect('user_responses.db', check_same_thread=False)
c = conn.cursor()

# Update the users table if necessary (adding any new columns if needed)
c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password TEXT,
        total_score REAL DEFAULT 0,
        remembering_score REAL DEFAULT 0,
        understanding_score REAL DEFAULT 0,
        applying_score REAL DEFAULT 0,
        num_sessions INTEGER DEFAULT 0
    )
''')

# Update the responses table
# We drop and recreate the table to include the new schema adjustments
c.execute('DROP TABLE IF EXISTS responses')

# Create the responses table with the correct schema
c.execute('''
    CREATE TABLE IF NOT EXISTS responses (
        username TEXT,
        session_id INTEGER,
        question_id INTEGER,
        user_response TEXT,
        response_similarity REAL,
        correct INTEGER,
        score REAL,
        time_taken REAL,
        FOREIGN KEY (username) REFERENCES users (username)
    )
''')

# Commit the changes
conn.commit()
