import sqlite3 as sq

DB_PATH = "university.db"  # ← Укажи свой файл базы данных

def fill_database():
    conn = sq.connect(DB_PATH)
    cursor = conn.cursor()

    # === 1. СОЗДАНИЕ ТАБЛИЦ (сначала это!) ===
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS teachers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            surname TEXT NOT NULL,
            name TEXT NOT NULL,
            patronymic TEXT,
            degree TEXT,
            position TEXT,
            experience INTEGER
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS subjects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            hours INTEGER NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS workload (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            teacher_id INTEGER,
            subject_id INTEGER,
            group_number TEXT,
            FOREIGN KEY (teacher_id) REFERENCES teachers(id) ON DELETE SET NULL,
            FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE SET NULL
        )
    """)

    # === 2. ПРЕПОДАВАТЕЛИ (10 штук) ===
    teachers = [
        (1, "Иванов", "Иван", "Иванович", "Доктор физико-математических наук", "Профессор", 25),
        (2, "Петров", "Пётр", "Сергеевич", "Кандидат технических наук", "Доцент", 15),
        (3, "Сидорова", "Анна", "Михайловна", "Кандидат педагогических наук", "Доцент", 12),
        (4, "Кузнецов", "Алексей", "Владимирович", "Ассистент", "Ассистент", 3),
        (5, "Смирнова", "Елена", "Дмитриевна", "Доктор экономических наук", "Профессор", 20),
        (6, "Васильев", "Дмитрий", "Александрович", "Кандидат исторических наук", "Доцент", 10),
        (7, "Морозова", "Ольга", "Николаевна", "Кандидат филологических наук", "Доцент", 8),
        (8, "Новиков", "Сергей", "Петрович", "Ассистент", "Ассистент", 2),
        (9, "Фёдорова", "Наталья", "Викторовна", "Доктор юридических наук", "Профессор", 18),
        (10, "Павлов", "Андрей", "Евгеньевич", "Кандидат биологических наук", "Доцент", 7),
    ]

    cursor.executemany("""
        INSERT OR REPLACE INTO teachers (id, surname, name, patronymic, degree, position, experience)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, teachers)

    # === 3. ПРЕДМЕТЫ (10 штук) ===
    subjects = [
        (1, "Высшая математика", 144),
        (2, "Программирование на Python", 108),
        (3, "Базы данных", 72),
        (4, "Философия", 54),
        (5, "Экономика предприятия", 90),
        (6, "История России", 72),
        (7, "Иностранный язык", 108),
        (8, "Физика", 126),
        (9, "Теория права", 90),
        (10, "Биология", 72),
    ]

    cursor.executemany("""
        INSERT OR REPLACE INTO subjects (id, title, hours)
        VALUES (?, ?, ?)
    """, subjects)

    # === 4. НАГРУЗКА (20 записей) ===
    workload = [
        (1, 1, 1, "ПИ-21-1"),
        (2, 1, 1, "ПИ-21-2"),
        (3, 2, 2, "ПИ-21-1"),
        (4, 2, 2, "ПИ-21-2"),
        (5, 3, 3, "ПИ-21-1"),
        (6, 4, 3, "ПИ-22-1"),
        (7, 5, 4, "ЭК-21-1"),
        (8, 5, 5, "ЭК-21-2"),
        (9, 6, 6, "ИФ-21-1"),
        (10, 7, 7, "ФИЛ-21-1"),
        (11, 7, 7, "ФИЛ-22-1"),
        (12, 8, 8, "ПИ-22-1"),
        (13, 1, 8, "ПИ-22-2"),
        (14, 9, 9, "ЮР-21-1"),
        (15, 9, 9, "ЮР-21-2"),
        (16, 10, 10, "БИО-21-1"),
        (17, 3, 2, "ПИ-22-1"),
        (18, 4, 1, "ПИ-23-1"),
        (19, 6, 6, "ИФ-22-1"),
        (20, 8, 3, "ПИ-23-1"),
    ]

    cursor.executemany("""
        INSERT OR REPLACE INTO workload (id, teacher_id, subject_id, group_number)
        VALUES (?, ?, ?, ?)
    """, workload)

    conn.commit()
    conn.close()

    print("✅ База данных заполнена!")
    print(f"   • Преподавателей: {len(teachers)}")
    print(f"   • Предметов: {len(subjects)}")
    print(f"   • Нагрузок: {len(workload)}")

if __name__ == "__main__":
    fill_database()