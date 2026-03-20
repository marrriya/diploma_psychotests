from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # для сессий

# ======================
# Инициализация БД
# ======================
def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    ''')

        # Таблица тестов
    # cursor.execute('''
    #     CREATE TABLE IF NOT EXISTS tests(
    #         id INTEGER PRIMARY KEY AUTOINCREMENT,
    #         topic TEXT NOT NULL,
    #         title TEXT NOT NULL,
    #         is_active BOOLEAN DEFAULT 1
    #     )
    # ''')
    conn.commit()
    conn.close()

# ======================
# Главная страница
# ======================
@app.route('/')
def index():
    username = session.get('username')
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute("SELECT topic, title FROM tests WHERE is_active = 1 ORDER BY topic")
    rows = cursor.fetchall()
    conn.close()

    grouped_tests = {}

    for topic, title in rows:
        if topic not in grouped_tests:
            grouped_tests[topic] = []
        grouped_tests[topic].append(title)

    # return render_template('index.html', tests=grouped_tests)


    # # Преобразуем в список словарей
    # test_list = [{"id": t[0], "topic": t[1], "title": t[2]} for t in tests]
    return render_template('index.html', username=username, tests=grouped_tests)

# ======================
# Регистрация
# ======================
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

# ======================
# Вход
# ======================
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

# ======================
# Выход
# ======================
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/')




# def seed_tests():
#     conn = sqlite3.connect('database.db')
#     cursor = conn.cursor()
#     tests = [
#         ("Темперамент и характер", "Тест Айзенка"),
#         ("Темперамент и характер", "Большая пятёрка"),
#         ("Темперамент и характер", "Акцентуации характера"),
#         ("Темперамент и характер", "Тест Кеттелла"),
#         ("Темперамент и характер", "Тип личности (MBTI)")
#     ]
#     for topic, title in tests:
#         try:
#             cursor.execute("INSERT INTO tests(topic, title) VALUES (?, ?)", (topic, title))
#         except sqlite3.IntegrityError:
#             pass
#     conn.commit()
#     conn.close()

if __name__ == '__main__':
    init_db()
    # seed_tests()
    app.run(debug=True)