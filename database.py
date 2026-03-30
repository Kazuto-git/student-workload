import sqlite3 as sq

class database:

    # staticmethod используеться, т.к. функции могут работать и без объекта 
    def create_database(file_path):
        conn = sq.connect(file_path)
        cursor = conn.cursor()

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
            FOREIGN KEY (teacher_id) REFERENCES teachers(id) 
                ON DELETE SET NULL,
            FOREIGN KEY (subject_id) REFERENCES subjects(id)
                ON DELETE SET NULL
            )
        """)

        conn.commit()
        conn.close()

    def get_all_teachers(file_path):
        conn = sq.connect(file_path)
        cursor = conn.cursor()
        cursor.execute('SELECT id, surname, name, patronymic, degree, position, experience FROM teachers')
        data = cursor.fetchall()
        conn.close()
        return data

    def get_all_subjects(file_path):
        conn = sq.connect(file_path)
        cursor = conn.cursor()
        cursor.execute('SELECT id, title, hours FROM subjects')
        data = cursor.fetchall()
        conn.close()
        return data

    def get_workload(file_path):
        conn = sq.connect(file_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                w.id,
                t.surname || ' ' || t.name || ' ' || COALESCE(t.patronymic, ''),
                s.title,
                w.group_number,
                COALESCE(t.degree, ''),
                COALESCE(t.position, ''),
                s.hours
            FROM workload w
            LEFT JOIN teachers t ON w.teacher_id = t.id
            LEFT JOIN subjects s ON w.subject_id = s.id
        """)
        data = cursor.fetchall()
        conn.close()
        return data

    def add_teacher(file_path, surname, name, patronymic, degree, position, experience):
        conn = sq.connect(file_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO teachers (surname, name, patronymic, degree, position, experience)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (surname, name, patronymic, degree, position, experience))
        conn.commit()
        conn.close()

    def add_subject(file_path, title, hours):
        conn = sq.connect(file_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO subjects (title, hours) VALUES (?, ?)
        """, (title, hours))
        conn.commit()
        conn.close()

    def add_workload(file_path, teacher_id, subject_id, group_number):
        conn = sq.connect(file_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO workload (teacher_id, subject_id, group_number)
            VALUES (?, ?, ?)
        """, (teacher_id, subject_id, group_number))
        conn.commit()
        conn.close()

    def delete_teacher(file_path, teacher_id):
        conn = sq.connect(file_path)
        cursor = conn.cursor()
        
        # Проверяем, есть ли этот преподаватель в нагрузке
        cursor.execute('SELECT COUNT(*) FROM workload WHERE teacher_id = ?', (teacher_id,))
        count = cursor.fetchone()[0]
        
        if count > 0:
            conn.close()
            return False  # Нельзя удалить
        
        cursor.execute('DELETE FROM teachers WHERE id = ?', (teacher_id,))
        conn.commit()
        conn.close()
        return True

    def delete_subject(file_path, subject_id):
        conn = sq.connect(file_path)
        cursor = conn.cursor()
        
        # Проверяем, есть ли этот предмет в нагрузке
        cursor.execute('SELECT COUNT(*) FROM workload WHERE subject_id = ?', (subject_id,))
        count = cursor.fetchone()[0]
        
        if count > 0:
            conn.close()
            return False  # Нельзя удалить
        
        cursor.execute('DELETE FROM subjects WHERE id = ?', (subject_id,))
        conn.commit()
        conn.close()
        return True

    def delete_workload(file_path, workload_id):
        conn = sq.connect(file_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM workload WHERE id = ?', (workload_id,))
        conn.commit()
        conn.close()

    def update_teacher(file_path, teacher_id, surname, name, patronymic, degree, position, experience):
        conn = sq.connect(file_path)
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE teachers 
            SET surname=?, name=?, patronymic=?, degree=?, position=?, experience=?
            WHERE id=?
        """, (surname, name, patronymic, degree, position, experience, teacher_id))
        conn.commit()
        conn.close()

    def update_subject(file_path, subject_id, title, hours):
        conn = sq.connect(file_path)
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE subjects SET title=?, hours=? WHERE id=?
        """, (title, hours, subject_id))
        conn.commit()
        conn.close()

    def teacher_in_workload(file_path, teacher_id):
        conn = sq.connect(file_path)
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM workload WHERE teacher_id = ?', (teacher_id,))
        count = cursor.fetchone()[0]
        conn.close()
        return count > 0

    def subject_in_workload(file_path, subject_id):
        conn = sq.connect(file_path)
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM workload WHERE subject_id = ?', (subject_id,))
        count = cursor.fetchone()[0]
        conn.close()
        return count > 0