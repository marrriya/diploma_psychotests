from flask import Flask, render_template, request, redirect, session
from flask import jsonify
import sqlite3
import json
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
app.secret_key = 'supersecretkey'  # для сессий

# Инициализация БД
def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    conn.commit()
    conn.close()


@app.route('/')
def index():
    username = session.get('username')

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # получаем все тесты
    cursor.execute("""
        SELECT id, topic, title 
        FROM tests 
        WHERE is_active = 1 
        ORDER BY id
    """)
    rows = cursor.fetchall()

    # если пользователь авторизован — получаем его пройденные тесты
    completed_tests = set()

    if username:
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()

        if user:
            user_id = user[0]

            cursor.execute("""
                SELECT DISTINCT test_id 
                FROM user_attempts 
                WHERE user_id = ?
            """, (user_id,))

            completed_tests = {row[0] for row in cursor.fetchall()}

    conn.close()

    # группировка + добавление completed
    grouped_tests = {}

    for test_id, topic, title in rows:
        if topic not in grouped_tests:
            grouped_tests[topic] = []

        grouped_tests[topic].append({
            'id': test_id,
            'title': title,
            'completed': test_id in completed_tests
        })

    return render_template(
        'index.html',
        username=username,
        tests=grouped_tests,
        completed_tests=completed_tests
    )
  

@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    name = request.form['name']
    password = request.form['password']

    errors = {}

    if len(username) < 3:
        errors['username'] = "Минимум 3 символа"

    if len(password) < 5:
        errors['password'] = "Минимум 5 символов"

    if not name:
        errors['name'] = "Введите имя"

    if errors:
        # return {"success": False, "errors": errors}
        return jsonify({"success": False, "errors": errors})

    # hashed_password = generate_password_hash(password)
    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO users(username, name, password) VALUES (?, ?, ?)",
            (username, name, hashed_password)
        )
        conn.commit()
    except sqlite3.IntegrityError:
        # return {"success": False, "errors": {"username": "Логин уже занят"}}
        # return jsonify({"success": False, "errors": errors})
        return jsonify({"success": False, "errors": {"username": "Логин уже занят"}})

    session['username'] = username
    return jsonify({"success": True})

@app.route('/profile')
def profile():
    if 'username' not in session:
        return redirect('/')

    return render_template('profile.html', username=session['username'])

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute("SELECT password FROM users WHERE username=?", (username,))
    user = cursor.fetchone()
    if user is None:
        conn.close()
        return jsonify({"success": False, "errors": {"username": "Пользователь не найден"}})
    # if not user:
    #     # return {"success": False, "errors": {"username": "Пользователь не найден"}}
    #     return jsonify({"success": False, "errors": {"username": "Пользователь не найден"}})

    if not check_password_hash(user[0], password):
        # return {"success": False, "errors": {"password": "Неверный пароль"}}
        return jsonify({"success": False, "errors": {"password": "Неверный пароль"}})

    session['username'] = username
    conn.close()
    return jsonify({"success": True})

# Выход
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/')


# Tест

@app.route('/test/<int:test_id>')
def test_page(test_id):
    # if 'username' not in session:
    #     return redirect('/')
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    username = session.get('username')
    user_id = None
    retake_mode = request.args.get('retake')

    if username:
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        if user:
            user_id = user[0]

    

    # user_id
    # cursor.execute("SELECT id FROM users WHERE username = ?", (session['username'],))
    # user_id = cursor.fetchone()[0]
    # username = session.get('username')
    # user_id = None

    # if username:
    #     cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
    #     user = cursor.fetchone()

    #     if user:
    #         user_id = user[0]

    # инфа о тесте
    cursor.execute("""
        SELECT title, description, visualization_type
        FROM tests
        WHERE id = ?
    """, (test_id,))
    test_data = cursor.fetchone()

    title, description, visualization_type = test_data

    # проверяем последнюю попытку
    cursor.execute("""
        SELECT id FROM user_attempts
        WHERE user_id = ? AND test_id = ?
        ORDER BY id DESC LIMIT 1
    """, (user_id, test_id))

    attempt = cursor.fetchone()

    # ЕСЛИ УЖЕ ПРОХОДИЛ → ПОКАЗЫВАЕМ РЕЗУЛЬТАТ
    if user_id and attempt and not retake_mode:
        attempt_id = attempt[0]

        # cursor.execute("""
        #     SELECT s.name, ur.score, s.max_score
        #     FROM user_results ur
        #     JOIN scales s ON ur.scale_id = s.id
        #     WHERE ur.attempt_id = ?
        # """, (attempt_id,))

        # rows = cursor.fetchall()

        # results = []
        # for name, score, max_score in rows:
        #     results.append({
        #         'name': name,
        #         'score': score,
        #         'max': max_score
        #     })
        cursor.execute("""
            SELECT s.name, ur.score, s.max_score, si.title, si.description
            FROM user_results ur
            JOIN scales s ON ur.scale_id = s.id
            LEFT JOIN scale_interpretation si
                ON si.scale_id = s.id
                AND ur.score BETWEEN si.min_score AND si.max_score
            WHERE ur.attempt_id = ?
        """, (attempt_id,))

        rows = cursor.fetchall()

        results = []
        for name, score, max_score, title, desc in rows:
            results.append({
                'name': name,
                'score': score,
                'max': max_score,
                'title': title or "",
                'desc': desc or ""
            })

        conn.close()

        return render_template(
            'result.html',
            results=results,
            chart_labels=json.dumps([r['name'] for r in results]),
            chart_values=json.dumps([r['score'] for r in results]),
            chart_type=visualization_type,
            test_id=test_id
        )

    # ЕСЛИ НЕ ПРОХОДИЛ → ПОКАЗЫВАЕМ ТЕСТ

    cursor.execute("""
        SELECT id, question, q_type, order_num
        FROM questions
        WHERE test_id = ?
        ORDER BY order_num
    """, (test_id,))
    
    question_rows = cursor.fetchall()

    questions = []

    for q_id, question_text, q_type, order_num in question_rows:

        try:
            parsed_text = json.loads(question_text)
        except:
            parsed_text = [question_text]

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

    return render_template(
        'test.html',
        questions=questions,
        test_id=test_id,
        title=title,
        description=description
    )

@app.route('/cancel_test')
def cancel_test():
    return redirect('/')

@app.route('/submit_test', methods=['POST'])
def submit_test():
    # if 'username' not in session:
    #     return redirect('/login')
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    username = session.get('username')
    user_id = None

    if username:
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        if user:
            user_id = user[0]

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # cursor.execute("SELECT id FROM users WHERE username = ?", (session['username'],))
    # user_id = cursor.fetchone()[0]

    question_ids = [key.split('_')[1] for key in request.form if key.startswith('q_')]

    cursor.execute("""
        SELECT test_id FROM questions WHERE id = ?
    """, (question_ids[0],))
    test_id = cursor.fetchone()[0]


    # cursor.execute("""
    #     INSERT INTO user_attempts (user_id, test_id)
    #     VALUES (?, ?)
    # """, (user_id, test_id))

    # attempt_id = cursor.lastrowid
    attempt_id = None

    if user_id:
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

            # cursor.execute("""
            #     INSERT INTO user_answers (attempt_id, question_id, ans_opt_id)
            #     VALUES (?, ?, ?)
            # """, (attempt_id, question_id, answer_id))
            if attempt_id:
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

        score = 0

        for key in request.form:
            if key.startswith('q_'):
                question_id = int(key.split('_')[1])
                answer_id = int(request.form[key])

                # получаем балл ответа + шкалу вопроса
                cursor.execute("""
                    SELECT ao.score, q.scale_id
                    FROM answer_options ao
                    JOIN questions q ON ao.question_id = q.id
                    WHERE ao.id = ?
                """, (answer_id,))

                row = cursor.fetchone()

                if row:
                    answer_score, question_scale_id = row

                    # добавляем только если это нужная шкала
                    if question_scale_id == scale_id:
                        score += answer_score

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
        if user_id:
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
    # получаем тип визуализации
    cursor.execute("SELECT visualization_type FROM tests WHERE id = ?", (test_id,))
    visualization_type = cursor.fetchone()[0]
    # conn.commit()
    if user_id:
        conn.commit()   
    conn.close()
    labels = [r['name'] for r in results]
    values = [r['score'] for r in results]  

    # return render_template('result.html', results=results)
    return render_template(
    'result.html',
    results=results,
    chart_labels=json.dumps(labels),
    chart_values=json.dumps(values),
    chart_type=visualization_type
    )

@app.route('/retake/<int:test_id>')
def retake(test_id):
    if 'username' not in session:
        return redirect('/')

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM users WHERE username = ?", (session['username'],))
    user_id = cursor.fetchone()[0]

    # удаляем старые попытки
    cursor.execute("""
        DELETE FROM user_attempts
        WHERE user_id = ? AND test_id = ?
    """, (user_id, test_id))

    conn.commit()
    conn.close()

    # return redirect(f'/test/{test_id}')
    return redirect(f'/test/{test_id}?retake=1')


@app.route('/completed')
def completed_tests_page():
    if 'username' not in session:
        return redirect('/')

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM users WHERE username = ?", (session['username'],))
    user_id = cursor.fetchone()[0]

    # последние попытки по каждому тесту
    cursor.execute("""
        SELECT t.id, t.title, MAX(ua.id)
        FROM user_attempts ua
        JOIN tests t ON ua.test_id = t.id
        WHERE ua.user_id = ?
        GROUP BY t.id
    """, (user_id,))

    tests = cursor.fetchall()

    conn.close()

    return render_template('completed.html', tests=tests)


# @app.route('/portrait')
# def portrait():
#     if 'username' not in session:
#         return redirect('/')

#     conn = sqlite3.connect('database.db')
#     cursor = conn.cursor()

#     cursor.execute("SELECT id FROM users WHERE username = ?", (session['username'],))
#     user_id = cursor.fetchone()[0]

#     # берем последние результаты пользователя
#     cursor.execute("""
#         SELECT t.title, s.name, ur.score
#         FROM user_results ur
#         JOIN scales s ON ur.scale_id = s.id
#         JOIN user_attempts ua ON ur.attempt_id = ua.id
#         JOIN tests t ON ua.test_id = t.id
#         WHERE ur.user_id = ?
#         ORDER BY ua.id DESC
#     """, (user_id,))

#     results = cursor.fetchall()

#     conn.close()

#     return render_template('portrait.html', results=results)
@app.route('/portrait')
def portrait():
    import sqlite3
    from flask import session, render_template

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    user_id = session.get("user_id")  # ⚠️ важно: пользователь должен быть залогинен

    # берём ВСЕ результаты пользователя
    cursor.execute("""
        SELECT 
            t.id,
            t.title,
            t.visualization_type,
            s.name,
            ur.score
        FROM user_results ur
        JOIN scales s ON ur.scale_id = s.id
        JOIN tests t ON s.test_id = t.id
        WHERE ur.user_id = ?
        ORDER BY t.id
    """, (user_id,))

    rows = cursor.fetchall()

    # --- собираем графики ---
    charts_dict = {}

    for test_id, test_title, chart_type, scale_name, score in rows:

        if test_id not in charts_dict:
            charts_dict[test_id] = {
                "type": chart_type,
                "labels": [],
                "values": []
            }

        charts_dict[test_id]["labels"].append(scale_name)
        charts_dict[test_id]["values"].append(score)

    # --- преобразуем в список ---
    charts = list(charts_dict.values())

    conn.close()

    return render_template("portrait.html", charts=charts)
if __name__ == '__main__':
    init_db()
    app.run(debug=True)
    # app.run(debug=True, port=5050)