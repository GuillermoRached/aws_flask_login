from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

def get_db_connection():
    conn = sqlite3.connect('/home/ubuntu/flaskapp/users.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT UNIQUE NOT NULL,
                  password TEXT NOT NULL,
                  firstname TEXT NOT NULL,
                  lastname TEXT NOT NULL,
                  email TEXT NOT NULL)''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    return render_template('register.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        email = request.form['email']

        conn = get_db_connection()
        c = conn.cursor()
        try:
            c.execute("INSERT INTO users (username, password, firstname, lastname, email) VALUES (?, ?, ?, ?, ?)",
                      (username, password, firstname, lastname, email))
            conn.commit()
        except sqlite3.IntegrityError:
            conn.close()
            return "Username already exists. Please choose a different username."
        conn.close()

        return redirect(url_for('profile', username=username))
    return render_template('register.html')

@app.route('/profile/<username>')
def profile(username):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT firstname, lastname, email FROM users WHERE username=?", (username,))
    user = c.fetchone()
    conn.close()

    if user:
        return render_template('profile.html', user=user, username=username)
    return "User not found", 404

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=?", (username,))
        user = c.fetchone()
        conn.close()

        if user and user['password'] == password:
            session['username'] = username
            return redirect(url_for('profile', username=username))
        return "Invalid username or password"
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)