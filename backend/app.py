from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import PCA
import numpy as np

app = Flask(__name__)
CORS(app)

# Load the CSV file containing questions
df_100 = pd.read_csv("grade_one_questions_100.csv")

# Ensure there is an 'id' column to uniquely identify each question
if 'id' not in df_100.columns:
    df_100['id'] = df_100.index

# Assign weights based on cognitive levels (Remembering, Understanding, Applying)
def assign_weights(label):
    if label == "Remembering":
        return 1
    elif label == "Understanding":
        return 2
    elif label == "Applying":
        return 3

df_100['Weight'] = df_100['Label'].apply(assign_weights)

# Create or connect to the SQLite database for storing user data
conn = sqlite3.connect('user_responses.db', check_same_thread=False)
c = conn.cursor()

# Create users table if it doesn't exist
c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password TEXT,
        total_score REAL,
        remembering_score REAL,
        understanding_score REAL,
        applying_score REAL,
        num_sessions INTEGER
    )
''')

# Create responses table if it doesn't exist
c.execute('''
    CREATE TABLE IF NOT EXISTS responses (
        username TEXT,
        question_id INTEGER,
        user_response TEXT,
        response_similarity REAL,
        score REAL,
        time_taken REAL,
        FOREIGN KEY (username) REFERENCES users (username)
    )
''')

# Save (commit) the changes to the database
conn.commit()

# Function to calculate the cosine similarity between the correct answer and user's response
def calculate_similarity(answer, user_response):
    vectorizer = TfidfVectorizer().fit_transform([answer, user_response])
    vectors = vectorizer.toarray()
    cosine_sim = cosine_similarity(vectors)
    return cosine_sim[0][1]

# User login endpoint
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data['username']
    password = data['password']
    
    # Check if user exists and password matches
    c.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    user = c.fetchone()
    
    if user:
        return jsonify({"message": "Login successful", "username": username}), 200
    else:
        return jsonify({"message": "Invalid username or password"}), 400
    

# User signup endpoint
@app.route('/signup', methods=['POST'])
def signup():
    data = request.json
    username = data['username']
    password = data['password']
    
    # Check if the username already exists
    c.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = c.fetchone()
    
    if user:
        return jsonify({"message": "Username already exists"}), 400
    
    # Insert new user into the database with initial scores set to 0
    c.execute("INSERT INTO users (username, password, total_score, remembering_score, understanding_score, applying_score, num_sessions) VALUES (?, ?, 0, 0, 0, 0, 0)", (username, password))
    conn.commit()
    
    return jsonify({"message": "Signup successful"}), 200

# Endpoint to get questions for a session
@app.route('/questions', methods=['POST'])
def get_questions():
    data = request.json
    username = data.get('username')
    if not username:
        return jsonify({"error": "No username provided"}), 400
    
    # Retrieve the user from the database
    c.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = c.fetchone()
    
    if not user:
        return jsonify({"message": "User not found"}), 400
    
    # Adjust the question levels based on the user's past performance
    question_set = adjust_question_levels(user)
    
    questions = question_set.to_dict(orient='records')
    return jsonify({"questions": questions})

# Function to dynamically adjust question levels based on performance
def adjust_question_levels(user):
    total_score = user[2]
    remembering_score = user[3]
    understanding_score = user[4]
    applying_score = user[5]
    num_sessions = user[6]
    
    # Initial session: equal weights across all cognitive levels
    if num_sessions == 0:
        weights = [1/3 if label == "Remembering" else 1/3 if label == "Understanding" else 1/3 for label in df_100['Label']]
    else:
        # Calculate average scores for each cognitive level
        avg_remembering_score = remembering_score / num_sessions
        avg_understanding_score = understanding_score / num_sessions
        avg_applying_score = applying_score / num_sessions

        # Calculate the total average score
        total_avg_score = avg_remembering_score + avg_understanding_score + avg_applying_score

        # Adjust weights based on performance
        remember_weight = (total_avg_score - avg_remembering_score) / total_avg_score
        understand_weight = (total_avg_score - avg_understanding_score) / total_avg_score
        apply_weight = (total_avg_score - avg_applying_score) / total_avg_score

        # Normalize weights so they sum to 1
        total_weight = remember_weight + understand_weight + apply_weight
        remember_weight /= total_weight
        understand_weight /= total_weight
        apply_weight /= total_weight

        weights = [remember_weight if label == "Remembering" else understand_weight if label == "Understanding" else apply_weight for label in df_100['Label']]
    
    # Select 5 questions based on the calculated weights
    return df_100.sample(5, weights=weights)

# Endpoint to submit answers and calculate scores
@app.route('/submit_answers', methods=['POST'])
def submit_answers():
    data = request.json
    username = data['username']
    answers = data['answers']
    
    # Retrieve the user from the database
    c.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = c.fetchone()
    
    if not user:
        return jsonify({"message": "User not found"}), 400
    
    try:
        # Attempt to convert total_score to float
        current_total_score = float(user[2])
    except ValueError:
        # Handle case where the value is corrupted or not a valid float
        current_total_score = 0.0
        c.execute("UPDATE users SET total_score = ? WHERE username = ?", (current_total_score, username))
        conn.commit()

    session_scores = []
    response_matrix = []
    
    for answer in answers:
        question_id = answer['question_id']
        user_response = answer['user_response']
        correct_answer = df_100[df_100['id'] == question_id]['Answer'].values[0]
        weight = df_100[df_100['id'] == question_id]['Weight'].values[0]
        label = df_100[df_100['id'] == question_id]['Label'].values[0]
        
        start_time = answer['start_time']
        end_time = answer['end_time']
        time_taken = end_time - start_time
        
        # Calculate similarity score
        similarity = calculate_similarity(correct_answer, user_response)
        binary_score = 1 if similarity >= 0.7 else 0
        
        # Collect data for PCA
        response_matrix.append([binary_score, weight])
        
        session_scores.append({
            "similarity": similarity,
            "weight": weight,
            "label": label,
            "binary_score": binary_score,
            "time_taken": time_taken
        })
    
    # Perform PCA on the response matrix
    pca = PCA(n_components=1)
    pca_scores = pca.fit_transform(np.array(response_matrix))
    
    # Convert PCA scores to a 1D list (flattening the list of lists, since pca_scores is a 2D array)
    pca_scores_list = [score[0] for score in pca_scores.tolist()]  # Extract the first component from the PCA result

    # Debugging print statement to check PCA scores
    print(f"PCA Scores: {pca_scores_list}")

    # Normalize the PCA scores
    pca_scores_min = min(pca_scores_list)  # Get the minimum value
    pca_scores_max = max(pca_scores_list)  # Get the maximum value

    if pca_scores_max != pca_scores_min:
        normalized_scores = 100 * (np.array(pca_scores_list) - pca_scores_min) / (pca_scores_max - pca_scores_min)
    else:
        normalized_scores = np.zeros_like(pca_scores_list)  # Avoid division by zero

    normalized_scores_list = normalized_scores.tolist()  # Convert normalized scores to list

    # Debugging print statement to check normalized scores
    print(f"Normalized Scores: {normalized_scores_list}")

    
    new_total_score = current_total_score + sum(normalized_scores_list)
    
    # Ensure the total score does not exceed 100
    new_total_score = min(100, new_total_score)
    
    # Debugging print statement to check the final total score
    print(f"New Total Score (capped at 100): {new_total_score}")
    
    # Calculate level-specific scores
    session_remembering_score = sum(s['binary_score'] * s['weight'] for s in session_scores if s['label'] == "Remembering")
    session_understanding_score = sum(s['binary_score'] * s['weight'] for s in session_scores if s['label'] == "Understanding")
    session_applying_score = sum(s['binary_score'] * s['weight'] for s in session_scores if s['label'] == "Applying")

    # Update user data with new scores
    new_remembering_score = user[3] + session_remembering_score
    new_understanding_score = user[4] + session_understanding_score
    new_applying_score = user[5] + session_applying_score
    new_num_sessions = user[6] + 1
    
    c.execute("UPDATE users SET total_score = ?, remembering_score = ?, understanding_score = ?, applying_score = ?, num_sessions = ? WHERE username = ?", 
              (new_total_score, new_remembering_score, new_understanding_score, new_applying_score, new_num_sessions, username))
    conn.commit()
    
    return jsonify({
        "total_score": float(new_total_score),  # Ensure it's a float
        "correct_answers": int(sum(s['binary_score'] for s in session_scores)),
        "incorrect_answers": int(len(session_scores) - sum(s['binary_score'] for s in session_scores)),
        "remembering_score": float(new_remembering_score),
        "understanding_score": float(new_understanding_score),
        "applying_score": float(new_applying_score),
        "feedback": provide_feedback(new_total_score),
        "average_time_taken": float(sum(s['time_taken'] for s in session_scores) / len(session_scores))
    })




# Provide feedback based on the total score
def provide_feedback(total_score):
    if total_score >= 80:
        return "Excellent performance! Keep up the good work!"
    elif total_score >= 50:
        return "Good job! There is room for improvement in higher-order thinking skills."
    else:
        return "Needs improvement. Focus on understanding and applying concepts."

if __name__ == '__main__':
    app.run(debug=True)
