import sqlite3

DB_NAME = "database.db"  # замени, если у тебя другое имя

def update_data():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # --- 1. Добавляем описания для первых 5 тестов ---
    descriptions = [
        (1, "Диагностика экстраверсии, интроверсии и уровня нейротизма личности."),
        (2, "Исследование свойств нервной системы: сила, подвижность и уравновешенность."),
        (3, "Определение акцентуаций характера и их выраженности."),
        (4, "Определение направленности личности: экстраверсия или интроверсия."),
        (5, "Диагностика выраженности характерологических особенностей личности.")
    ]

    for test_id, desc in descriptions:
        cursor.execute("""
            UPDATE tests
            SET description = ?
            WHERE id = ?
        """, (desc, test_id))

    # --- 2. Обновляем тип визуализации ---

    # Шкала мотивации одобрения → horizontal_bar
    cursor.execute("""
        UPDATE tests
        SET visualization_type = 'line'
        WHERE title = 'Шкала мотивации одобрения'
    """)

    # Методика ТиД → scatter (две оси: тревожность и депрессия)
    cursor.execute("""
        UPDATE tests
        SET visualization_type = 'custom'
        WHERE title = 'Методика ТиД'
    """)

    conn.commit()
    conn.close()
    print("Данные успешно обновлены!")

if __name__ == "__main__":
    update_data()