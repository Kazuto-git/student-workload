import cherrypy
import urllib.parse
import os
from database import database

BROWSER_ROOT = os.path.expanduser("~")


class WebApp:
    def __init__(self):
        self.database_file = None

    @cherrypy.expose
    def index(self):
        browser_root_safe = BROWSER_ROOT.replace('\\', '/')
        return f"""
        <!DOCTYPE html><html><head><meta charset="UTF-8"><title>📚 Распределение нагрузки</title></head>
        <body style="font-family:Arial;padding:20px;background:#f5f5f5">
        <div style="max-width:600px;margin:0 auto;background:white;padding:30px;border-radius:8px">
            <h2>📚 Распределение нагрузки преподавателей</h2>
            <form method="post" action="/open_db">
                <label>Путь к базе:</label><br>
                <input type="text" name="db_path" size="60" placeholder="C:/path/to/university.db" value="{browser_root_safe}"><br><br>
                <button type="submit">Открыть</button>
            </form>
            <hr>
            <form method="post" action="/create_db">
                <label>Имя файла:</label><br>
                <input type="text" name="filename" placeholder="university.db" required><br><br>
                <label>Папка:</label><br>
                <input type="text" name="save_path" size="60" value="{browser_root_safe}" required><br><br>
                <button type="submit">Создать</button>
            </form>
        </div></body></html>
        """

    @cherrypy.expose
    def open_db(self, db_path):
        if db_path and os.path.exists(db_path):
            self.database_file = db_path
            safe_path = urllib.parse.quote(db_path.replace('\\', '/'), safe='')
            raise cherrypy.HTTPRedirect(f"/main?db_path={safe_path}")
        return self.index()

    @cherrypy.expose
    def create_db(self, filename, save_path):
        if not filename.endswith('.db'):
            filename += '.db'
        db_path = os.path.join(save_path, filename).replace("\\", "/")
        try:
            database.create_database(db_path)
            self.database_file = db_path
            safe_path = urllib.parse.quote(db_path, safe='')
        except Exception:
            pass
        raise cherrypy.HTTPRedirect(f"/main?db_path={safe_path}")

    @staticmethod
    def _encode_path(path: str) -> str:
        return urllib.parse.quote(path.replace('\\', '/'), safe='')

    def _safe_redirect(self, db_path_enc: str, table: str, message: str):
        query = urllib.parse.urlencode({
            'db_path': db_path_enc,
            'table': table,
            'message': message
        }, quote_via=urllib.parse.quote)
        raise cherrypy.HTTPRedirect(f"/main?{query}")

    @cherrypy.expose
    def main(self, db_path=None, table="workload", message=""):
        if db_path:
            db_path = urllib.parse.unquote(db_path)

        if not db_path or not os.path.exists(db_path):
            raise cherrypy.HTTPRedirect("/")

        self.database_file = db_path

        if table == "teachers":
            data = database.get_all_teachers(db_path)
            columns = ["№", "Фамилия", "Имя", "Отчество", "Степень", "Должность", "Стаж"]
            delete_action = "delete_teacher"
        elif table == "subjects":
            data = database.get_all_subjects(db_path)
            columns = ["№", "Название", "Часы"]
            delete_action = "delete_subject"
        else:
            data = database.get_workload(db_path)
            columns = ["№", "Преподаватель", "Предмет", "Группа", "Степень", "Должность", "Часы"]
            delete_action = "delete_workload"

        db_path_enc = self._encode_path(db_path)
        db_path_display = db_path.replace('\\', '/')

        rows = ""
        for i, row in enumerate(data, 1):
            cells = "".join(f"<td>{cell if cell is not None else ''}</td>" for cell in row[1:])
            actions = (
                f'<td>'
                f'<a href="/edit_form?table={table}&id={row[0]}&db_path={db_path_enc}">✏️</a> '
                f'<a href="/{delete_action}?id={row[0]}&db_path={db_path_enc}" onclick="return confirm(\'Удалить?\')">🗑️</a>'
                f'</td>'
            )
            rows += f"<tr><td>{i}</td>{cells}{actions}</tr>"

        teachers = database.get_all_teachers(db_path)
        subjects = database.get_all_subjects(db_path)
        teacher_options = "".join(
            f'<option value="{t[0]}">{t[1]} {t[2]} {t[3] or ""}</option>' for t in teachers
        )
        subject_options = "".join(
            f'<option value="{s[0]}">{s[1]}</option>' for s in subjects
        )

        table_title = {'teachers': 'Преподаватели', 'subjects': 'Предметы'}.get(table, 'Нагрузка')
        add_form = {
            'teachers': f'''
            <details><summary>➕ Добавить преподавателя</summary>
            <form method="post" action="/add_teacher">
                <input type="hidden" name="db_path" value="{db_path_enc}">
                <label>Фамилия *</label><input type="text" name="surname" required><br>
                <label>Имя *</label><input type="text" name="name" required><br>
                <label>Отчество</label><input type="text" name="patronymic"><br>
                <label>Степень *</label><input type="text" name="degree" required><br>
                <label>Должность *</label><input type="text" name="position" required><br>
                <label>Стаж (лет) *</label><input type="number" name="experience" required><br>
                <button type="submit">Сохранить</button>
                <a href="/main?db_path={db_path_enc}&table=teachers">Отмена</a>
            </form></details>''',
            'subjects': f'''
            <details><summary>➕ Добавить предмет</summary>
            <form method="post" action="/add_subject">
                <input type="hidden" name="db_path" value="{db_path_enc}">
                <label>Название предмета *</label><input type="text" name="title" required><br>
                <label>Количество часов *</label><input type="number" name="hours" required><br>
                <button type="submit">Сохранить</button>
                <a href="/main?db_path={db_path_enc}&table=subjects">Отмена</a>
            </form></details>''',
            'workload': f'''
            <details><summary>➕ Распределить нагрузку</summary>
            <form method="post" action="/add_workload">
                <input type="hidden" name="db_path" value="{db_path_enc}">
                <label>Преподаватель *</label>
                <select name="teacher_id" required>{teacher_options}</select><br>
                <label>Предмет *</label>
                <select name="subject_id" required>{subject_options}</select><br>
                <label>Номер группы *</label><input type="text" name="group_number" required><br>
                <button type="submit">Распределить</button>
                <a href="/main?db_path={db_path_enc}&table=workload">Отмена</a>
            </form></details>'''
        }.get(table, '')

        msg_class = "error" if message.startswith("Ошибка") else "success" if message else ""
        msg_html = f'<div class="msg {msg_class}">{urllib.parse.unquote(message)}</div>' if message else ''

        return f"""
        <!DOCTYPE html><html><head><meta charset="UTF-8"><title>📚 {table_title}</title>
        <style>
            body{{font-family:Arial;background:#f5f5f5;padding:20px}}
            .container{{max-width:1200px;margin:0 auto;background:white;padding:20px;border-radius:8px}}
            table{{width:100%;border-collapse:collapse;margin:15px 0}}
            th,td{{border:1px solid #ddd;padding:8px;text-align:left}}
            th{{background:#4a90e2;color:white}}
            tr:nth-child(even){{background:#f9f9f9}}
            a{{text-decoration:none;margin:0 5px}}
            details{{margin:10px 0;padding:10px;background:#f9f9f9;border-radius:4px}}
            label{{display:block;margin:8px 0 4px;font-weight:bold}}
            input,select{{width:100%;padding:6px;margin-bottom:10px;box-sizing:border-box}}
            button{{padding:8px 16px;margin:5px 5px 5px 0;cursor:pointer}}
            .msg{{padding:10px;border-radius:4px;margin:10px 0}}
            .success{{background:#d4edda;color:#155724}}
            .error{{background:#f8d7da;color:#721c24}}
        </style></head><body>
        <div class="container">
            <h2>📚 Распределение нагрузки преподавателей</h2>
            <p><strong>База:</strong> {db_path_display}</p>
            <nav>
                <a href="/main?db_path={db_path_enc}&table=teachers">Преподаватели</a> |
                <a href="/main?db_path={db_path_enc}&table=subjects">Предметы</a> |
                <a href="/main?db_path={db_path_enc}&table=workload">Нагрузка</a> |
                <a href="/">🏠 Выбрать другую базу</a>
            </nav>
            {msg_html}
            <h3>{table_title}</h3>
            {add_form}
            <a href="/main?db_path={db_path_enc}&table={table}">🔄 Обновить</a>
            <table><thead><tr>
                {''.join(f'<th>{col}</th>' for col in columns)}
                <th>Действия</th>
            </tr></thead><tbody>
                {rows if rows else '<tr><td colspan="100%">Нет данных</td></tr>'}
            </tbody></table>
        </div></body></html>
        """

    @cherrypy.expose
    def edit_form(self, table, id, db_path=None):
        if db_path:
            db_path = urllib.parse.unquote(db_path)
        else:
            db_path = self.database_file

        if not db_path or not os.path.exists(db_path):
            raise cherrypy.HTTPRedirect("/")

        self.database_file = db_path
        db_path_enc = self._encode_path(db_path)

        if table == "teachers":
            data = database.get_all_teachers(db_path)
            record = next((r for r in data if r[0] == int(id)), None)
            if not record:
                raise cherrypy.HTTPRedirect(f"/main?db_path={db_path_enc}&table=teachers")
            return self._edit_teacher_form(record, db_path_enc)
        elif table == "subjects":
            data = database.get_all_subjects(db_path)
            record = next((r for r in data if r[0] == int(id)), None)
            if not record:
                raise cherrypy.HTTPRedirect(f"/main?db_path={db_path_enc}&table=subjects")
            return self._edit_subject_form(record, db_path_enc)
        elif table == "workload":
            data = database.get_workload(db_path)
            record = next((r for r in data if r[0] == int(id)), None)
            if not record:
                raise cherrypy.HTTPRedirect(f"/main?db_path={db_path_enc}&table=workload")
            return self._edit_workload_form(record, db_path_enc, db_path)
        raise cherrypy.HTTPRedirect("/")

    _EDIT_STYLE = (
        "body{font-family:Arial;background:#ececec;padding:20px}"
        ".container{max-width:500px;margin:0 auto;background:white;padding:25px;border-radius:5px}"
        "label{{display:block;margin:10px 0 5px;font-weight:bold}}"
        "input,select{{width:100%;padding:8px;margin-bottom:10px;box-sizing:border-box}}"
        "button{{padding:10px 20px;margin:5px}}"
    )

    def _edit_teacher_form(self, record, db_path_enc):
        return f"""
        <!DOCTYPE html><html><head><meta charset="UTF-8"><title>✏️ Редактировать</title>
        <style>{self._EDIT_STYLE}</style></head><body>
        <div class="container">
            <h2>✏️ Изменить преподавателя</h2>
            <form action="/update_teacher" method="post">
                <input type="hidden" name="db_path" value="{db_path_enc}">
                <input type="hidden" name="id" value="{record[0]}">
                <label>Фамилия *</label><input type="text" name="surname" value="{record[1]}" required>
                <label>Имя *</label><input type="text" name="name" value="{record[2]}" required>
                <label>Отчество</label><input type="text" name="patronymic" value="{record[3] or ''}">
                <label>Степень *</label><input type="text" name="degree" value="{record[4]}" required>
                <label>Должность *</label><input type="text" name="position" value="{record[5]}" required>
                <label>Стаж *</label><input type="number" name="experience" value="{record[6]}" required>
                <button type="submit">Сохранить</button>
                <a href="/main?db_path={db_path_enc}&table=teachers">Отмена</a>
            </form>
        </div></body></html>
        """

    def _edit_subject_form(self, record, db_path_enc):
        return f"""
        <!DOCTYPE html><html><head><meta charset="UTF-8"><title>✏️ Редактировать</title>
        <style>{self._EDIT_STYLE}</style></head><body>
        <div class="container">
            <h2>✏️ Изменить предмет</h2>
            <form action="/update_subject" method="post">
                <input type="hidden" name="db_path" value="{db_path_enc}">
                <input type="hidden" name="id" value="{record[0]}">
                <label>Название *</label><input type="text" name="title" value="{record[1]}" required>
                <label>Часы *</label><input type="number" name="hours" value="{record[2]}" required>
                <button type="submit">Сохранить</button>
                <a href="/main?db_path={db_path_enc}&table=subjects">Отмена</a>
            </form>
        </div></body></html>
        """

    def _edit_workload_form(self, record, db_path_enc, db_path):
        teachers = database.get_all_teachers(db_path)
        subjects = database.get_all_subjects(db_path)
        teacher_opts = "".join(
            f'<option value="{t[0]}" {"selected" if t[0] == record[1] else ""}>{t[1]} {t[2]} {t[3] or ""}</option>' for t in teachers
        )
        subject_opts = "".join(
            f'<option value="{s[0]}" {"selected" if s[0] == record[2] else ""}>{s[1]}</option>' for s in subjects
        )
        return f"""
        <!DOCTYPE html><html><head><meta charset="UTF-8"><title>✏️ Редактировать</title>
        <style>{self._EDIT_STYLE}</style></head><body>
        <div class="container">
            <h2>✏️ Изменить нагрузку</h2>
            <form action="/update_workload" method="post">
                <input type="hidden" name="db_path" value="{db_path_enc}">
                <input type="hidden" name="id" value="{record[0]}">
                <label>Преподаватель *</label><select name="teacher_id" required>{teacher_opts}</select>
                <label>Предмет *</label><select name="subject_id" required>{subject_opts}</select>
                <label>Группа *</label><input type="text" name="group_number" value="{record[3]}" required>
                <button type="submit">Сохранить</button>
                <a href="/main?db_path={db_path_enc}&table=workload">Отмена</a>
            </form>
        </div></body></html>
        """

    @cherrypy.expose
    def add_teacher(self, db_path, surname, name, patronymic="", degree="", position="", experience=0):
        db_path = urllib.parse.unquote(db_path)
        db_path_enc = self._encode_path(db_path)
        try:
            database.add_teacher(db_path, surname, name, patronymic, degree, position, int(experience))
            msg = "Преподаватель добавлен!"
        except Exception as e:
            msg = f"Ошибка: {str(e)}"
        self._safe_redirect(db_path_enc, "teachers", msg)

    @cherrypy.expose
    def add_subject(self, db_path, title, hours):
        db_path = urllib.parse.unquote(db_path)
        db_path_enc = self._encode_path(db_path)
        try:
            database.add_subject(db_path, title, int(hours))
            msg = "Предмет добавлен!"
        except Exception as e:
            msg = f"Ошибка: {str(e)}"
        self._safe_redirect(db_path_enc, "subjects", msg)

    @cherrypy.expose
    def add_workload(self, db_path, teacher_id, subject_id, group_number):
        db_path = urllib.parse.unquote(db_path)
        db_path_enc = self._encode_path(db_path)
        try:
            database.add_workload(db_path, int(teacher_id), int(subject_id), group_number)
            msg = "Нагрузка распределена!"
        except Exception as e:
            msg = f"Ошибка: {str(e)}"
        self._safe_redirect(db_path_enc, "workload", msg)

    @cherrypy.expose
    def update_teacher(self, db_path, id, surname, name, patronymic="", degree="", position="", experience=0):
        db_path = urllib.parse.unquote(db_path)
        db_path_enc = self._encode_path(db_path)
        try:
            database.update_teacher(db_path, int(id), surname, name, patronymic, degree, position, int(experience))
            msg = "Преподаватель изменён!"
        except Exception as e:
            msg = f"Ошибка: {str(e)}"
        self._safe_redirect(db_path_enc, "teachers", msg)

    @cherrypy.expose
    def update_subject(self, db_path, id, title, hours):
        db_path = urllib.parse.unquote(db_path)
        db_path_enc = self._encode_path(db_path)
        try:
            database.update_subject(db_path, int(id), title, int(hours))
            msg = "Предмет изменён!"
        except Exception as e:
            msg = f"Ошибка: {str(e)}"
        self._safe_redirect(db_path_enc, "subjects", msg)

    @cherrypy.expose
    def update_workload(self, db_path, id, teacher_id, subject_id, group_number):
        db_path = urllib.parse.unquote(db_path)
        db_path_enc = self._encode_path(db_path)
        try:
            database.update_workload(db_path, int(id), int(teacher_id), int(subject_id), group_number)
            msg = "Нагрузка изменена!"
        except Exception as e:
            msg = f"Ошибка: {str(e)}"
        self._safe_redirect(db_path_enc, "workload", msg)

    @cherrypy.expose
    def delete_teacher(self, id, db_path=None):
        if db_path:
            db_path = urllib.parse.unquote(db_path)
        else:
            db_path = self.database_file
        db_path_enc = self._encode_path(db_path)
        try:
            success = database.delete_teacher(db_path, int(id))
            msg = "Преподаватель удалён!" if success else "Нельзя удалить! Есть записи в нагрузке."
        except Exception as e:
            msg = f"Ошибка: {str(e)}"
        self._safe_redirect(db_path_enc, "teachers", msg)

    @cherrypy.expose
    def delete_subject(self, id, db_path=None):
        if db_path:
            db_path = urllib.parse.unquote(db_path)
        else:
            db_path = self.database_file
        db_path_enc = self._encode_path(db_path)
        try:
            success = database.delete_subject(db_path, int(id))
            msg = "Предмет удалён!" if success else "Нельзя удалить! Есть записи в нагрузке."
        except Exception as e:
            msg = f"Ошибка: {str(e)}"
        self._safe_redirect(db_path_enc, "subjects", msg)

    @cherrypy.expose
    def delete_workload(self, id, db_path=None):
        if db_path:
            db_path = urllib.parse.unquote(db_path)
        else:
            db_path = self.database_file
        db_path_enc = self._encode_path(db_path)
        try:
            database.delete_workload(db_path, int(id))
            msg = "Нагрузка удалена!"
        except Exception as e:
            msg = f"Ошибка: {str(e)}"
        self._safe_redirect(db_path_enc, "workload", msg)


if __name__ == "__main__":
    cherrypy.config.update({
        'server.socket_host': '127.0.0.1',
        'server.socket_port': 8080,
    })
    cherrypy.quickstart(WebApp())