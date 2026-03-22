from flask import Flask, render_template, request, redirect, session
import sqlite3
import json

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # для сессий

# Инициализация БД
def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    conn.commit()
    conn.close()

# Главная страница
@app.route('/')
def index():
    username = session.get('username')
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, topic, title FROM tests WHERE is_active = 1 ORDER BY topic")
    rows = cursor.fetchall()
    conn.close()

    grouped_tests = {}

    for test_id, topic, title in rows:
        if topic not in grouped_tests:
            grouped_tests[topic] = []
        grouped_tests[topic].append({
            'id': test_id,
            'title': title
        })

    return render_template('index.html', username=username, tests=grouped_tests)

# Регистрация
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users(username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            session['username'] = username
            conn.close()
            return redirect('/')
        except sqlite3.IntegrityError:
            conn.close()
            return render_template('register_failed.html')
    return render_template('register.html')


# Вход
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            session['username'] = username
            return redirect('/')
        else:
            return render_template('login_failed.html')
    return render_template('login.html')


# Выход
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/')


# Tест
@app.route('/test/<int:test_id>')
def test_page(test_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    #Вопросы
    cursor.execute("""
        SELECT id, question, q_type, order_num 
        FROM questions
        WHERE test_id = ?
        ORDER BY order_num
    """, (test_id,))
    
    question_rows = cursor.fetchall()

    questions = []

    for q_id, question_text, q_type, order_num in question_rows:

        # Парсинг вопроса
        try:
            parsed_text = json.loads(question_text)
        except:
            parsed_text = [question_text]

        #Ответы
        cursor.execute("""
            SELECT id, answer_text, score 
            FROM answer_options
            WHERE question_id = ?
        """, (q_id,))
        
        options = cursor.fetchall()

        questions.append({
            'id': q_id,
            'text': parsed_text,
            'type': q_type,
            'order': order_num,
            'options': options
        })
        

    conn.close()

    return render_template('test.html', questions=questions, test_id=test_id)

@app.route('/submit_test', methods=['POST'])
def submit_test():
    if 'username' not in session:
        return redirect('/login')

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM users WHERE username = ?", (session['username'],))
    user_id = cursor.fetchone()[0]

    question_ids = [key.split('_')[1] for key in request.form if key.startswith('q_')]

    cursor.execute("""
        SELECT test_id FROM questions WHERE id = ?
    """, (question_ids[0],))
    test_id = cursor.fetchone()[0]


    cursor.execute("""
        INSERT INTO user_attempts (user_id, test_id)
        VALUES (?, ?)
    """, (user_id, test_id))

    attempt_id = cursor.lastrowid

    # сохранение ответов
    for key in request.form:
        if key.startswith('q_'):
            question_id = int(key.split('_')[1])
            answer_id = int(request.form[key])

            cursor.execute("""
                INSERT INTO user_answers (attempt_id, question_id, ans_opt_id)
                VALUES (?, ?, ?)
            """, (attempt_id, question_id, answer_id))

    cursor.execute("""
        SELECT id, name, max_score 
        FROM scales 
        WHERE test_id = ?
    """, (test_id,))

    scales = cursor.fetchall()

    results = []

    for scale_id, scale_name, max_score in scales:

        # сумма по шкале
        cursor.execute("""
            SELECT SUM(ao.score)
            FROM user_answers ua
            JOIN answer_options ao ON ua.ans_opt_id = ao.id
            WHERE ua.attempt_id = ? AND ao.scale_id = ?
        """, (attempt_id, scale_id))

        score = cursor.fetchone()[0]

        if score is None:
            score = 0

        # интерпретация
        cursor.execute("""
            SELECT title, description
            FROM scale_interpretation
            WHERE scale_id = ? AND ? BETWEEN min_score AND max_score
        """, (scale_id, score))

        interpretation = cursor.fetchone()

        title = interpretation[0] if interpretation else ""
        description = interpretation[1] if interpretation else ""

        # сохранение результатов
        cursor.execute("""
            INSERT INTO user_results (attempt_id, scale_id, score, user_id)
            VALUES (?, ?, ?, ?)
        """, (attempt_id, scale_id, score, user_id))

        results.append({
            'name': scale_name,
            'score': score,
            'max': max_score,
            'title': title,
            'desc': description
        })
    conn.commit()
    conn.close()

    return render_template('result.html', results=results)
if __name__ == '__main__':
    init_db()
    app.run(debug=True)