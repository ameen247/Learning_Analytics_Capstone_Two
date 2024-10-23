from flask import Flask, render_template, request, redirect, url_for, session, g
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'supersecretkey'

DATABASE = 'learners.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# Initialize the database and create tables
def init_db():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()

        # Create User table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS User (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            sessions_completed INTEGER DEFAULT 0,
            total_time_taken REAL DEFAULT 0.0
        )
        ''')

        # Create Session table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Session (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            session_number INTEGER NOT NULL,
            start_time TEXT DEFAULT CURRENT_TIMESTAMP,
            end_time TEXT,
            total_time REAL,
            FOREIGN KEY(user_id) REFERENCES User(id)
        )
        ''')

        # Create Response table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Response (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER NOT NULL,
            question TEXT NOT NULL,
            correct_answer TEXT NOT NULL,
            user_answer TEXT NOT NULL,
            is_correct INTEGER NOT NULL,
            label TEXT NOT NULL,
            FOREIGN KEY(session_id) REFERENCES Session(id)
        )
        ''')

        db.commit()

# Initialize the database
init_db()

# Sample questions data
questions = [
    {"question": "What color is the happy child's house?", "answer": "Red", "label": "Remembering"},
    {"question": "Why is the happy child happy?", "answer": "Because the child laughs and plays all day", "label": "Understanding"},
    {"question": "What does the wolf say before blowing down the house?", "answer": "I will huff and puff and blow your house down", "label": "Applying"}
]

@app.route('/')
def landing_page():
    return render_template('landing.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT * FROM User WHERE username = ? AND password = ?', (username, password))
        user = cursor.fetchone()
        if user:
            session['user_id'] = user[0]
            return redirect(url_for('questionnaire'))
        else:
            return "Invalid credentials!"
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT * FROM User WHERE username = ?', (username,))
        if cursor.fetchone():
            return "Username already exists!"
        cursor.execute('INSERT INTO User (username, password) VALUES (?, ?)', (username, password))
        db.commit()
        session['user_id'] = cursor.lastrowid
        return redirect(url_for('questionnaire'))
    return render_template('signup.html')

@app.route('/questionnaire', methods=['GET', 'POST'])
def questionnaire():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        user_id = session['user_id']
        db = get_db()
        cursor = db.cursor()

        # Start a new session
        cursor.execute('SELECT sessions_completed FROM User WHERE id = ?', (user_id,))
        sessions_completed = cursor.fetchone()[0] + 1
        cursor.execute('INSERT INTO Session (user_id, session_number) VALUES (?, ?)', (user_id, sessions_completed))
        db.commit()
        session_id = cursor.lastrowid

        # Record responses
        for q in questions:
            user_answer = request.form.get(q['question'])
            is_correct = 1 if user_answer.strip().lower() == q['answer'].strip().lower() else 0
            cursor.execute('''
            INSERT INTO Response (session_id, question, correct_answer, user_answer, is_correct, label)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (session_id, q['question'], q['answer'], user_answer, is_correct, q['label']))

        # End the session and update user info
        end_time = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute('''
        UPDATE Session
        SET end_time = ?, total_time = (julianday(?) - julianday(start_time)) * 86400.0
        WHERE id = ?
        ''', (end_time, end_time, session_id))

        cursor.execute('UPDATE User SET sessions_completed = ?, total_time_taken = total_time_taken + (SELECT total_time FROM Session WHERE id = ?) WHERE id = ?', (sessions_completed, session_id, user_id))
        db.commit()

        return redirect(url_for('result'))

    return render_template('questionnaire.html', questions=questions)

@app.route('/result')
def result():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    db = get_db()
    cursor = db.cursor()

    # Retrieve the last session and responses
    cursor.execute('SELECT * FROM Session WHERE user_id = ? ORDER BY id DESC LIMIT 1', (user_id,))
    last_session = cursor.fetchone()
    cursor.execute('SELECT * FROM Response WHERE session_id = ?', (last_session[0],))
    responses = cursor.fetchall()

    total_correct = sum([r[5] for r in responses])
    total_questions = len(responses)
    total_score = (total_correct / total_questions) * 100 if total_questions > 0 else 0

    level_scores = {
        "Remembering": 0,
        "Understanding": 0,
        "Applying": 0
    }
    level_counts = {
        "Remembering": 0,
        "Understanding": 0,
        "Applying": 0
    }

    for r in responses:
        level_scores[r[7]] += r[5]
        level_counts[r[7]] += 1

    for level in level_scores:
        if level_counts[level] > 0:
            level_scores[level] = (level_scores[level] / level_counts[level]) * 100

    feedback = []
    for level, score in level_scores.items():
        if score >= 70:
            feedback.append(f"Great job in {level}! You're doing really well.")
        elif 40 <= score < 70:
            feedback.append(f"Good work in {level}, but there's room for improvement.")
        else:
            feedback.append(f"You might need more practice in {level}.")

    cursor.execute('SELECT sessions_completed FROM User WHERE id = ?', (user_id,))
    sessions_completed = cursor.fetchone()[0]

    return render_template('result.html', total_score=total_score, level_scores=level_scores,
                           sessions_completed=sessions_completed, feedback=feedback)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('landing_page'))

if __name__ == '__main__':
    app.run(debug=True)
