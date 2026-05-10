from flask import Flask, render_template, request, redirect, session, abort, flash
import sqlite3

from flask import jsonify
import json
from werkzeug.security import generate_password_hash, check_password_hash
import random
import string

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # для сессий


###. АДМИНКА. ###
    # def is_admin():
    #     print("CHECK ADMIN:", session)
    #     return session.get('role') == 'admin'

    # # ===================== ADMIN: USERS =====================
    # @app.route('/admin/users')
    # def admin_users():
    #     if not is_admin(): abort(403)
    #     db = get_db()
    #     users = db.execute("SELECT * FROM users").fetchall()
    #     return render_template('admin/users.html', users=users)


    # @app.route('/admin/delete_user/<int:id>')
    # def delete_user(id):
    #     if not is_admin(): abort(403)
    #     db = get_db()
    #     db.execute("DELETE FROM users WHERE id=?", (id,))
    #     db.commit()
    #     flash('Пользователь удален')
    #     return redirect('/admin/users')

    # # ===================== ADMIN: TESTS =====================
    # @app.route('/admin/tests')
    # def admin_tests():
    #     if not is_admin(): abort(403)
    #     db = get_db()
    #     tests = db.execute("SELECT * FROM tests").fetchall()
    #     return render_template('admin/tests.html', tests=tests)


    # @app.route('/admin/tests/create', methods=['GET', 'POST'])
    # def create_test():
    #     if not is_admin(): abort(403)

    #     if request.method == 'POST':
    #         title = request.form['title']
    #         topic = request.form['topic']
    #         description = request.form['description']

    #         db = get_db()
    #         db.execute(
    #             "INSERT INTO tests (title, topic, description) VALUES (?, ?, ?)",
    #             (title, topic, description)
    #         )
    #         db.commit()
    #         flash('Тест создан')
    #         return redirect('/admin/tests')

    #     return render_template('admin/create_test.html')

    # @app.route('/admin/tests/edit/<int:id>', methods=['GET', 'POST'])
    # def edit_test(id):
    #     if not is_admin(): abort(403)
    #     db = get_db()

    #     if request.method == 'POST':
    #         title = request.form['title']
    #         topic = request.form['topic']
    #         description = request.form['description']

    #         db.execute(
    #             "UPDATE tests SET title=?, topic=?, description=? WHERE id=?",
    #             (title, topic, description, id)
    #         )
    #         db.commit()
    #         flash('Тест обновлен')
    #         return redirect('/admin/tests')

    #     test = db.execute("SELECT * FROM tests WHERE id=?", (id,)).fetchone()
    #     return render_template('admin/edit_test.html', test=test)

    # @app.route('/admin/tests/delete/<int:id>')
    # def delete_test(id):
    #     if not is_admin(): abort(403)
    #     db = get_db()
    #     db.execute("DELETE FROM tests WHERE id=?", (id,))
    #     db.commit()
    #     flash('Тест удален')
    #     return redirect('/admin/tests')


# ИНИЦИАЛИЗАЦИЯ БД 

def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    conn.commit()
    conn.close()

def get_db():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    username = session.get('username')

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # получаем все тесты
    cursor.execute("""
        SELECT id, topic, title, description
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

    for test_id, topic, title, description in rows:
        if topic not in grouped_tests:
            grouped_tests[topic] = []

        grouped_tests[topic].append({
            'id': test_id,
            'title': title,
            'description': description,
            'completed': test_id in completed_tests
        })

    return render_template(
        'index.html',
        username=username,
        tests=grouped_tests,
        completed_tests=completed_tests
    )
  
# АВТОРИЗАЦИЯ И РЕГИСТРАЦИЯ

@app.route('/auth')
def auth_page():
    return render_template('auth.html')

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
        return jsonify({"success": False, "errors": {"username": "Логин уже занят"}})

    session['username'] = username
    return jsonify({"success": True,"redirect": "/"})

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

    cursor.execute("""
        SELECT id, password, role 
        FROM users 
        WHERE username=?
    """, (username,))

    user = cursor.fetchone()

    if user is None:
        conn.close()
        return jsonify({"success": False, "errors": {"username": "Пользователь не найден"}})

    user_id, hashed_password, role = user

    if not check_password_hash(hashed_password, password):
        conn.close()
        return jsonify({"success": False, "errors": {"password": "Неверный пароль"}})


    session.clear()
    session['username'] = username
    session['user_id'] = user_id
    session['role'] = role

    # print("LOGIN SESSION:", session)  # для проверки

    conn.close()
    if role == 'admin':
        return jsonify({"success": True, "redirect": "/admin/admin"})
    elif role == 'teacher':
        return jsonify({"success": True, "redirect": "/teacher/teach"})
    else:
        return jsonify({"success": True, "redirect": "/"})

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

# РАЗДЕЛ ПРЕПОДАВАТЕЛЯ

@app.route('/teacher/teach')
def teach():
    if 'user_id' not in session:
        return redirect('/auth')

    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    user_id = session['user_id']

    cursor.execute("""
        SELECT id, title, description, topic
        FROM tests
        WHERE author_id = ?
        AND is_active = 1
    """, (user_id,))
    
    teacher_tests = cursor.fetchall()

    cursor.execute("""
        SELECT id, title, description, topic
        FROM tests
        WHERE is_active = 1
    """)
        
    all_tests_raw = cursor.fetchall()

    conn.close()

    # ===== ГРУППИРОВКА ПО ТЕМАМ (как у тебя на index) =====
    all_tests = {}

    for test in all_tests_raw:
        topic = test['topic'] or "Без категории"
        
        if topic not in all_tests:
            all_tests[topic] = []
        
        all_tests[topic].append(test)

    return render_template(
        "teacher/teach.html",
        username=session['username'],
        teacher_tests=teacher_tests,
        tests=all_tests
    )

@app.route('/teacher/create_test_page')
def create_test_page():
    if session.get('role') != 'teacher':
        return redirect('/')
    return render_template('teacher/create_test.html')

# @app.route('/teacher/create_test', methods=['POST'])
# def create_test():
#     data = request.json

#     db = get_db()

#     cursor = db.cursor()

#     cursor.execute("""
#         INSERT INTO tests (title, description)
#         VALUES (?, ?)
#     """, (data['title'], data['description']))

#     test_id = cursor.lastrowid

#     scale_ids = []

#     for s in data['scales']:
#         cursor.execute("""
#             INSERT INTO scales (name, test_id)
#             VALUES (?, ?)
#         """, (s, test_id))

#         scale_ids.append(cursor.lastrowid)

#     for q in data['questions']:
#         cursor.execute("""
#             INSERT INTO questions (test_id, question, scale_id, q_type)
#             VALUES (?, ?, ?, 'single')
#         """, (test_id, q['text'], scale_ids[int(q['scale'])]))

#     db.commit()

#     return {"success": True}

@app.route('/teacher/create_test_full', methods=['POST'])
def create_test_full():
    

    data = request.get_json()
    db = get_db()
    cursor = db.cursor()

    try:
        # ===== TEST =====
        cursor.execute("""
            INSERT INTO tests (title, description, instruction, author_id, topic)
            VALUES (?, ?, ?, ?, ?)
        """, (
            data.get('title'),
            data.get('description'),
            data.get('instruction', ''),
            session.get('user_id'),
            data.get('topic')
        ))

        test_id = cursor.lastrowid

        # ===== SCALES =====
        scale_ids = []

        for s in data.get('scales', []):
            cursor.execute("""
                INSERT INTO scales (name, max_score, test_id)
                VALUES (?, ?, ?)
            """, (
                s.get('name'),
                s.get('max'),
                test_id
            ))
            scale_ids.append(cursor.lastrowid)

        # ===== QUESTIONS + ANSWERS =====
        for i, q in enumerate(data.get('questions', [])):

            scale_id = scale_ids[q.get('scale', 0)]

            cursor.execute("""
                INSERT INTO questions (test_id, question, order_num, scale_id)
                VALUES (?, ?, ?, ?)
            """, (
                test_id,
                q.get('text'),
                i,
                scale_id
            ))

            question_id = cursor.lastrowid

            for ans in q.get('answers', []):
                cursor.execute("""
                    INSERT INTO answer_options (question_id, answer_text, score)
                    VALUES (?, ?, ?)
                """, (
                    question_id,
                    ans.get('text'),     # ✅ FIX
                    ans.get('score', 0)  # ✅ FIX
                ))

        # ===== INTERPRETATIONS =====
        for block in data.get('interpretations', []):

            # scale_id = scale_ids[block.get('scale_index', 0)]
            # scale_id = block.get('scale_id')
            scale_index = block.get('scale_index', 0)
            scale_id = scale_ids[scale_index]

            for r in block.get('ranges', []):

                cursor.execute("""
                    INSERT INTO scale_interpretation
                    (scale_id, min_score, max_score, title, description)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    scale_id,
                    r.get('min'),
                    r.get('max'),
                    r.get('title'),
                    r.get('desc')
                ))

        db.commit()

        return {"success": True, "test_id": test_id}

    except Exception as e:
        db.rollback()
        print("ERROR:", e)
        return {"success": False, "error": str(e)}

# @app.route('/teacher/groups')
# def teacher_groups():
#     conn = sqlite3.connect('database.db')
#     conn.row_factory = sqlite3.Row
#     cursor = conn.cursor()

#     teacher_id = session.get('user_id')

#     # cursor.execute("""
#     #     SELECT 
#     #         g.id, 
#     #         g.name, 
#     #         COUNT(gs.user_id) AS students_count
#     #     FROM groups g
#     #     LEFT JOIN group_students gs ON g.id = gs.group_id
#     #     WHERE g.teacher_id = ?
#     #     GROUP BY g.id
#     # """, (teacher_id,))
#     cursor.execute("""
#         SELECT 
#             g.id, 
#             g.name,
#             g.invite_code,
#             COUNT(gs.user_id) AS students_count

#         FROM groups g

#         LEFT JOIN group_students gs
#             ON g.id = gs.group_id

#         WHERE g.teacher_id = ?

#         GROUP BY g.id
#     """, (teacher_id,))

#     groups = cursor.fetchall()

#     conn.close()

#     return render_template(
#         'teacher/groups.html',
#         username=session.get('username'),
#         groups=groups
#     )
@app.route('/teacher/groups')
def teacher_groups():

    if 'user_id' not in session:
        return redirect('/login')

    teacher_id = session['user_id']

    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    # -----------------------------
    # ГРУППЫ
    # -----------------------------
    cursor.execute("""
        SELECT 
            g.id,
            g.name,
            g.invite_code,
            COUNT(gs.user_id) AS students_count
        FROM groups g
        LEFT JOIN group_students gs 
            ON g.id = gs.group_id
        WHERE g.teacher_id = ?
        GROUP BY g.id
    """, (teacher_id,))

    groups = cursor.fetchall()

    groups = [dict(g) for g in groups]

    for group in groups:

        cursor.execute("""
            SELECT t.title
            FROM group_tests gt
            JOIN tests t ON gt.test_id = t.id
            WHERE gt.group_id = ?
        """, (group["id"],))

        group["assigned_tests"] = cursor.fetchall()

    cursor.execute("""
        SELECT
            id,
            title,
            topic
        FROM tests
        WHERE is_active = 1
        ORDER BY title
    """)

    tests = cursor.fetchall()

    conn.close()

    return render_template(
        'teacher/groups.html',
        username=session.get('username'),
        groups=groups,
        tests=tests
    )
    


def generate_invite_code(length=6):
    return ''.join(
        random.choices(
            string.ascii_uppercase + string.digits,
            k=length
        )
    )

@app.route('/teacher/create_group', methods=['POST'])
def create_group():

    # проверка авторизации
    if 'user_id' not in session:
        return redirect('/login')

    teacher_id = session['user_id']

    # получаем название
    group_name = request.form.get('group_name', '').strip()

    # проверка пустого названия
    if not group_name:
        return redirect('/teacher/groups')

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # генерируем уникальный код
    invite_code = generate_invite_code()

    # защита от совпадений
    while True:

        cursor.execute("""
            SELECT id FROM groups
            WHERE invite_code = ?
        """, (invite_code,))

        existing = cursor.fetchone()

        if not existing:
            break

        invite_code = generate_invite_code()

    # создаём группу
    cursor.execute("""
        INSERT INTO groups (
            name,
            teacher_id,
            invite_code
        )
        VALUES (?, ?, ?)
    """, (
        group_name,
        teacher_id,
        invite_code
    ))

    conn.commit()
    conn.close()

    return redirect('/teacher/groups')

@app.route('/teacher/assign_test', methods=['POST'])
def assign_test():

    group_id = request.form['group_id']
    test_title = request.form['test_title']

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # -----------------------------
    # ИЩЕМ ТЕСТ ПО НАЗВАНИЮ
    # -----------------------------

    cursor.execute("""
        SELECT id
        FROM tests
        WHERE title = ?
    """, (test_title,))

    test = cursor.fetchone()

    # если тест не найден
    if not test:
        conn.close()
        return redirect('/teacher/groups')

    test_id = test[0]

    # -----------------------------
    # ПРОВЕРКА НА ДУБЛИКАТ
    # -----------------------------

    cursor.execute("""
        SELECT id
        FROM group_tests
        WHERE group_id = ?
        AND test_id = ?
    """, (group_id, test_id))

    existing = cursor.fetchone()

    # -----------------------------
    # ДОБАВЛЯЕМ
    # -----------------------------

    if not existing:

        cursor.execute("""
            INSERT INTO group_tests (
                group_id,
                test_id
            )
            VALUES (?, ?)
        """, (
            group_id,
            test_id
        ))

        conn.commit()

    conn.close()

    return redirect('/teacher/groups')

@app.route('/teacher/delete_test/<int:test_id>')
def delete_test(test_id):
    import sqlite3

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE tests
        SET is_active = 0
        WHERE id = ?
    """, (test_id,))

    conn.commit()
    conn.close()

    return redirect('/teacher/teach')

@app.route('/teacher/edit_test/<int:test_id>')
def edit_test_page(test_id):

    if session.get('role') != 'teacher':
        return redirect('/')

    db = get_db()
    cursor = db.cursor()

    # ===== TEST =====
    cursor.execute("SELECT * FROM tests WHERE id=?", (test_id,))
    test = cursor.fetchone()

    # ===== SCALES =====
    cursor.execute("SELECT * FROM scales WHERE test_id=?", (test_id,))
    scales = cursor.fetchall()

    # ===== QUESTIONS =====
    cursor.execute("""
        SELECT * FROM questions
        WHERE test_id=?
        ORDER BY order_num
    """, (test_id,))
    questions = cursor.fetchall()

    # ===== ANSWERS =====
    cursor.execute("""
        SELECT * FROM answer_options
        WHERE question_id IN (
            SELECT id FROM questions WHERE test_id=?
        )
    """, (test_id,))
    answers = cursor.fetchall()

    # ===== INTERPRETATIONS (ВАЖНО ДОБАВИТЬ) =====
    cursor.execute("""
        SELECT si.*
        FROM scale_interpretation si
        JOIN scales s ON si.scale_id = s.id
        WHERE s.test_id = ?
    """, (test_id,))
    interpretations = cursor.fetchall()
    

    return render_template(
        "teacher/edit_test.html",
        mode="edit",
        test_id=test_id,

        test=dict(test),
        scales=[dict(s) for s in scales],
        questions=[dict(q) for q in questions],
        answers=[dict(a) for a in answers],
        interpretations=[dict(i) for i in interpretations]
    )

@app.route('/teacher/update_test/<int:test_id>', methods=['POST'])
def update_test(test_id):

    data = request.get_json()
    db = get_db()
    cursor = db.cursor()

    try:
        # ===== UPDATE TEST =====
        cursor.execute("""
            UPDATE tests
            SET title=?, description=?, instruction=?, topic=?
            WHERE id=?
        """, (
            data.get('title'),
            data.get('description'),
            data.get('instruction', ''),
            data.get('topic'),
            test_id
        ))

        # ===== DELETE OLD DATA (ВАЖНО ДЛЯ ТВОЕЙ СХЕМЫ) =====

        # answers
        cursor.execute("""
            DELETE FROM answer_options
            WHERE question_id IN (
                SELECT id FROM questions WHERE test_id=?
            )
        """, (test_id,))

        # questions
        cursor.execute("DELETE FROM questions WHERE test_id=?", (test_id,))

        # interpretations
        cursor.execute("""
            DELETE FROM scale_interpretation
            WHERE scale_id IN (
                SELECT id FROM scales WHERE test_id=?
            )
        """, (test_id,))

        # scales
        cursor.execute("DELETE FROM scales WHERE test_id=?", (test_id,))

        # ===== INSERT SCALES =====
        scale_ids = []

        for s in data.get('scales', []):
            cursor.execute("""
                INSERT INTO scales (name, max_score, test_id)
                VALUES (?, ?, ?)
            """, (
                s.get('name'),
                s.get('max'),
                test_id
            ))
            scale_ids.append(cursor.lastrowid)

        # ===== INSERT QUESTIONS + ANSWERS =====
        for i, q in enumerate(data.get('questions', [])):

            scale_id = scale_ids[q.get('scale', 0)]

            cursor.execute("""
                INSERT INTO questions (test_id, question, order_num, scale_id)
                VALUES (?, ?, ?, ?)
            """, (
                test_id,
                q.get('text'),
                i,
                scale_id
            ))

            question_id = cursor.lastrowid

            for a in q.get('answers', []):
                cursor.execute("""
                    INSERT INTO answer_options (question_id, answer_text, score)
                    VALUES (?, ?, ?)
                """, (
                    question_id,
                    a.get('text'),
                    a.get('score', 0)
                ))

        # ===== INTERPRETATIONS =====
        for block in data.get('interpretations', []):

            # scale_id = scale_ids[block.get('scale_index', 0)]
            # scale_id = block.get('scale_id')
            scale_index = block.get('scale_index', 0)
            scale_id = scale_ids[scale_index]

            for r in block.get('ranges', []):

                cursor.execute("""
                    INSERT INTO scale_interpretation
                    (scale_id, min_score, max_score, title, description)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    scale_id,
                    r.get('min'),
                    r.get('max'),
                    r.get('title'),
                    r.get('desc')
                ))

        db.commit()

        return {"success": True}

    except Exception as e:
        db.rollback()
        return {"success": False, "error": str(e)}

@app.route('/teacher/group_results')
def teacher_results():

    if 'user_id' not in session:
        return redirect('/login')

    teacher_id = session['user_id']

    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    # -----------------------------
    # ГРУППЫ ПРЕПОДА
    # -----------------------------

    cursor.execute("""
        SELECT
            g.id,
            g.name,
            COUNT(gs.user_id) as students_count

        FROM groups g

        LEFT JOIN group_students gs
            ON g.id = gs.group_id

        WHERE g.teacher_id = ?

        GROUP BY g.id
    """, (teacher_id,))

    groups = [dict(g) for g in cursor.fetchall()]

    # -----------------------------
    # ДЛЯ КАЖДОЙ ГРУППЫ
    # -----------------------------

    for group in groups:

        group_id = group["id"]

        # -----------------------------
        # ТЕСТЫ ГРУППЫ
        # -----------------------------

        cursor.execute("""
            SELECT
                t.id,
                t.title,
                t.topic

            FROM group_tests gt

            JOIN tests t
                ON gt.test_id = t.id

            WHERE gt.group_id = ?
        """, (group_id,))

        tests = [dict(t) for t in cursor.fetchall()]

        # -----------------------------
        # ДЛЯ КАЖДОГО ТЕСТА
        # -----------------------------

        for test in tests:

            test_id = test["id"]

            # -----------------------------
            # РЕЗУЛЬТАТЫ СТУДЕНТОВ
            # -----------------------------

            cursor.execute("""
                SELECT
                    u.username,
                    ua.attempt_date,
                    SUM(ur.score) as score

                FROM user_attempts ua

                JOIN users u
                    ON ua.user_id = u.id

                JOIN user_results ur
                    ON ua.id = ur.attempt_id

                WHERE ua.test_id = ?
                AND ua.user_id IN (

                    SELECT user_id
                    FROM group_students
                    WHERE group_id = ?

                )

                GROUP BY ua.id

                ORDER BY ua.attempt_date DESC
            """, (test_id, group_id))

            test["results"] = cursor.fetchall()

            # -----------------------------
            # ПРОЦЕНТ ПРОШЕДШИХ
            # -----------------------------

            cursor.execute("""
                SELECT COUNT(DISTINCT user_id)
                FROM group_students
                WHERE group_id = ?
            """, (group_id,))

            total_students = cursor.fetchone()[0]

            cursor.execute("""
                SELECT COUNT(DISTINCT ua.user_id)

                FROM user_attempts ua

                WHERE ua.test_id = ?
                AND ua.user_id IN (

                    SELECT user_id
                    FROM group_students
                    WHERE group_id = ?

                )
            """, (test_id, group_id))

            completed_students = cursor.fetchone()[0]

            if total_students > 0:

                percent = round(
                    (completed_students / total_students) * 100
                )

            else:
                percent = 0

            test["completed_percent"] = percent

        group["tests"] = tests

    conn.close()

    return render_template(
        'teacher/group_results.html',
        username=session['username'],
        groups=groups
    )


#групповые тесты
@app.route('/group_tests')
def student_group_tests():

    # проверка авторизации
    if 'user_id' not in session:
        return redirect('/login')

    user_id = session['user_id']
    username = session['username']

    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    # -----------------------------
    # ГРУППЫ ПОЛЬЗОВАТЕЛЯ
    # -----------------------------

    cursor.execute("""
        SELECT 
            g.id,
            g.name,
            COUNT(gt.test_id) as tests_count

        FROM groups g

        LEFT JOIN group_students gs 
            ON g.id = gs.group_id

        LEFT JOIN group_tests gt
            ON g.id = gt.group_id

        WHERE gs.user_id = ?

        GROUP BY g.id
    """, (user_id,))

    groups = cursor.fetchall()

    # -----------------------------
    # ГРУППОВЫЕ ТЕСТЫ
    # -----------------------------

    cursor.execute("""
        SELECT
            t.id,
            t.title,
            t.topic,
            t.description,
            g.name as group_name

        FROM group_students gs

        JOIN group_tests gt
            ON gs.group_id = gt.group_id

        JOIN tests t
            ON gt.test_id = t.id

        JOIN groups g
            ON g.id = gs.group_id

        WHERE gs.user_id = ?
    """, (user_id,))

    tests = cursor.fetchall()

    conn.close()

    return render_template(
        'group_tests.html',
        username=username,
        groups=groups,
        tests=tests
    )

@app.route('/student/join_group', methods=['POST'])
def join_group():

    # проверка авторизации
    if 'user_id' not in session:
        return redirect('/login')

    user_id = session['user_id']

    # получаем код
    code = request.form.get('code', '').strip().upper()

    # проверка пустого поля
    if not code:
        return redirect('/groups')

    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    # -----------------------------
    # ИЩЕМ ГРУППУ ПО КОДУ
    # -----------------------------

    cursor.execute("""
        SELECT id
        FROM groups
        WHERE invite_code = ?
    """, (code,))

    group = cursor.fetchone()

    # если группа не найдена
    if not group:
        conn.close()
        return redirect('/groups')

    group_id = group['id']

    # -----------------------------
    # ПРОВЕРЯЕМ:
    # УЖЕ СОСТОИТ В ГРУППЕ?
    # -----------------------------

    cursor.execute("""
        SELECT id
        FROM group_students
        WHERE group_id = ?
        AND user_id = ?
    """, (group_id, user_id))

    existing = cursor.fetchone()

    # если уже состоит
    if existing:
        conn.close()
        return redirect('/groups')

    # -----------------------------
    # ДОБАВЛЯЕМ В ГРУППУ
    # -----------------------------

    cursor.execute("""
        INSERT INTO group_students (
            group_id,
            user_id
        )
        VALUES (?, ?)
    """, (
        group_id,
        user_id
    ))

    conn.commit()
    conn.close()

    return redirect('/groups')

# ПРОХОЖДЕНИЕ ТЕСТА И РЕЗУЛЬТАТ

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



    # инфа о тесте
    cursor.execute("""
        SELECT title, description, instruction, visualization_type
        FROM tests
        WHERE id = ?
    """, (test_id,))
    test_data = cursor.fetchone()

    # title, description, visualization_type = test_data
    title, description, instruction, visualization_type = test_data

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

    # return render_template(
    #     'test.html',
    #     questions=questions,
    #     test_id=test_id,
    #     title=title,
    #     description=description
    # )
    return render_template(
        'test.html',
        questions=questions,
        test_id=test_id,
        title=title,
        description=description,
        instruction=instruction
    )

@app.route('/cancel_test')
def cancel_test():
    return redirect('/')

@app.route('/submit_test', methods=['POST'])
def submit_test():
    
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


    question_ids = [key.split('_')[1] for key in request.form if key.startswith('q_')]

    cursor.execute("""
        SELECT test_id FROM questions WHERE id = ?
    """, (question_ids[0],))
    test_id = cursor.fetchone()[0]

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

    # return render_template('completed.html', tests=tests)
    return render_template('completed.html', username=session.get('username'), tests=tests)

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



# def is_admin():
#     return True

# @app.route('/admin')
# # @login_required
# def admin_panel():
#     if current_user.role != 'admin' and current_user.role != 'superadmin':
#         abort(403)

#     users = db.execute("SELECT * FROM users").fetchall()
#     tests = db.execute("SELECT * FROM tests").fetchall()

#     results = db.execute("""
#         SELECT u.username, t.title as test_title, s.name as scale_name, ur.score
#         FROM user_results ur
#         JOIN users u ON ur.user_id = u.id
#         JOIN scales s ON ur.scale_id = s.id
#         JOIN tests t ON s.test_id = t.id
#     """).fetchall()

#     return render_template('admin.html', users=users, tests=tests, results=results)



if __name__ == '__main__':
    init_db()
    app.run(debug=True)
    # app.run(debug=True, port=5050)