from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY')  # From .env file

# DeepSeek API Config
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

users = {}  # Temporary user storage

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username in users and users[username]['password'] == password:
            session['username'] = username
            return redirect(url_for('ask'))
        return render_template('login.html', error="Invalid credentials")
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')
        if username in users:
            return render_template('signup.html', error="Username already exists")
        users[username] = {'password': password, 'email': email}
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/ask', methods=['GET', 'POST'])
def ask():
    if 'username' not in session:
        return jsonify({'error': 'Login required'}), 401

    if request.method == 'POST':
        question = request.json.get('question')
        headers = {
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": question}],
            "temperature": 0.7
        }
        try:
            response = requests.post(DEEPSEEK_API_URL, headers=headers, json=payload)
            response.raise_for_status()
            answer = response.json()['choices'][0]['message']['content']
            return jsonify({'answer': answer})
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    return render_template('ask.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)