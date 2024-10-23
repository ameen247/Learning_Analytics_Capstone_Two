import sqlite3
import pandas as pd

def get_db_connection():
    """Get a connection to the SQLite database."""
    conn = sqlite3.connect('user_responses.db')
    conn.row_factory = sqlite3.Row
    return conn

def view_table(table_name):
    """View the contents of a specific table."""
    conn = get_db_connection()
    c = conn.cursor()
    
    # Query to select all data from the specified table
    c.execute(f"SELECT * FROM {table_name}")
    
    # Fetch all rows from the table
    rows = c.fetchall()
    
    # Convert to a Pandas DataFrame for better visualization
    df = pd.DataFrame(rows, columns=[column[0] for column in c.description])
    
    conn.close()
    
    return df

# View the contents of the 'users' table
print("Users Table:")
print(view_table('users'))

# View the contents of the 'questions' table
print("\nQuestions Table:")
print(view_table('questions'))

# View the contents of the 'responses' table
print("\nResponses Table:")
print(view_table('responses'))

# View the contents of the 'session_results' table
print("\nSession Results Table:")
print(view_table('session_results'))
