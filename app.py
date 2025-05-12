from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

# Function to initialize the database
def init_db():
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS candidates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                votes INTEGER DEFAULT 0
            );
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                has_voted INTEGER DEFAULT 0
            );
        ''')

# Home page to display voting options
@app.route('/')
def index():
    # Fetch all candidates from the database
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM candidates')
        candidates = cursor.fetchall()
    return render_template('index.html', candidates=candidates)

# Route to handle voting
@app.route('/vote/<int:candidate_id>', methods=['POST'])
def vote(candidate_id):
    # Check if the user has already voted
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE has_voted = 1 LIMIT 1')
        user = cursor.fetchone()
        
        if user:
            return redirect(url_for('results'))  # Redirect to results if user has voted
    
        # Increment vote count for the selected candidate
        cursor.execute('UPDATE candidates SET votes = votes + 1 WHERE id = ?', (candidate_id,))
        cursor.execute('INSERT INTO users (has_voted) VALUES (1)')  # Mark user as voted
        conn.commit()
    
    return redirect(url_for('results'))

# Results page to display vote counts
@app.route('/results')
def results():
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM candidates')
        candidates = cursor.fetchall()
    return render_template('results.html', candidates=candidates)

# Route to initialize candidates (for testing purposes)
@app.route('/init')
def init():
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.executemany('''
            INSERT INTO candidates (name) VALUES (?)
        ''', [('Alice',), ('Bob',), ('Charlie',)])
        conn.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()  # Initialize the database when the app starts
    app.run(debug=True)

