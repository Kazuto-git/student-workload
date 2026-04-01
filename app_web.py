import cherrypy
import urllib.parse
import sqlite3 as sq
import os
from database import database

# Корневая папка для файлового браузера
BROWSER_ROOT = os.path.expanduser("~")

class WebApp:
    def __init__(self):
        self.database_file = None

    @cherrypy.expose
    def index(self):
        """Главная: выбор базы"""
        browser_root_safe = BROWSER_ROOT.replace('\\', '/')
    
        return f"""<!DOCTYPE html>
    <html>
    <head>
        <title>Распределение нагрузки</title>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: Arial; background: #ececec; padding: 20px; }}
            .container {{ max-width: 600px; margin: 0 auto; background: white; padding: 25px; border-radius: 5px; }}
            h1 {{ color: #333; }}
            .form-row {{ margin: 15px 0; }}
            label {{ display: block; margin: 5px 0; font-weight: bold; }}
            input {{ width: 100%; padding: 8px; box-sizing: border-box; }}
            button {{ padding: 10px 20px; margin: 5px; background: #4CAF50; color: white; border: none; border-radius: 3px; cursor: pointer; }}
            button:hover {{ background: #45a049; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📚 Распределение нагрузки</h1>
        
            <div class="form-row">
                <form action="open_db" method="post">
                    <label>Путь к базе:</label>
                    <input type="text" name="db_path" placeholder="C:/Users/.../university.db" required>
                    <button type="submit">Открыть</button>
                </form>
            </div>
        
            <div class="form-row">
                <form action="create_db" method="post">
                    <label>Имя файла:</label>
                    <input type="text" name="filename" placeholder="university.db" required>
                    <label>Папка:</label>
                    <input type="text" name="save_path" value="{browser_root_safe}" readonly>
                    <button type="submit">Создать</button>
                </form>
            </div>
        </div>
    </body>
    </html>"""

    @cherrypy.expose
    def open_db(self, db_path):
        """Открывает существующую базу данных"""
        if db_path and os.path.exists(db_path):
            self.database_file = db_path
            # Кодируем путь для URL: \ → / + urlencode
            safe_path = urllib.parse.quote(db_path.replace('\\', '/'), safe=':/')
            raise cherrypy.HTTPRedirect(f"/main?db_path={safe_path}")
        else:
            return self.index()

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def api_files(self, path=None):
        """API: возвращает список файлов и папок"""
        if not path:
            path = BROWSER_ROOT
        
        try:
            path = os.path.normpath(path)
            if not (path.startswith(BROWSER_ROOT) or path.startswith(os.path.dirname(BROWSER_ROOT))):
                return {"error": "Доступ запрещён"}
            
            items = os.listdir(path)
        except Exception as e:
            return {"error": str(e)}
        
        folders = sorted([i for i in items if os.path.isdir(os.path.join(path, i))])
        files = sorted([i for i in items if i.endswith('.db') and os.path.isfile(os.path.join(path, i))])
        
        parent = os.path.dirname(path) if path != BROWSER_ROOT and path != os.path.dirname(path) else None
        
        return {
            "path": path.replace("\\", "/"),
            "parent": parent.replace("\\", "/") if parent else None,
            "folders": folders,
            "files": files
        }

    @cherrypy.expose
    def create_db(self, filename, save_path):
        """Создаёт новую базу данных"""
        if not filename.endswith('.db'):
            filename += '.db'
        
        db_path = os.path.join(save_path, filename).replace("\\", "/")
        
        try:
            database.create_database(db_path)
            self.database_file = db_path
            raise cherrypy.HTTPRedirect(f"/main?db_path={db_path}")
        except Exception as e:
            return self.index()

    @cherrypy.expose
    def main(self, db_path=None, table="workload", message=""):
        # Декодируем путь из URL
        if db_path:
            db_path = urllib.parse.unquote(db_path)
    
        if not db_path or not os.path.exists(db_path):
            raise cherrypy.HTTPRedirect("/")
    
        self.database_file = db_path

        if table == "teachers":
            data = database.get_all_teachers(db_path)
            columns = ["ID", "Фамилия", "Имя", "Отчество", "Степень", "Должность", "Стаж"]
            delete_action = "delete_teacher"
        elif table == "subjects":
            data = database.get_all_subjects(db_path)
            columns = ["ID", "Название", "Часы"]
            delete_action = "delete_subject"
        else:
            data = database.get_workload(db_path)
            columns = ["ID", "Преподаватель", "Предмет", "Группа", "Степень", "Должность", "Часы"]
            delete_action = "delete_workload"
        
        rows = ""
        for row in data:
            cells = "".join(f"<td>{cell if cell else ''}</td>" for cell in row[1:])
            actions = f'''
                <td>
                    <a href="/edit_form?table={table}&id={row[0]}" class="btn btn-edit">✏️</a>
                    <a href="/{delete_action}?id={row[0]}" class="btn btn-delete" onclick="return confirm('Удалить?')">🗑️</a>
                </td>
            '''
            rows += f"<tr><td>{row[0]}</td>{cells}{actions}</tr>"
        
        teachers = database.get_all_teachers(db_path)
        subjects = database.get_all_subjects(db_path)
        teacher_options = "".join(f'<option value="{t[0]}">{t[1]} {t[2]} {t[3]}</option>' for t in teachers)
        subject_options = "".join(f'<option value="{s[0]}">{s[1]}</option>' for s in subjects)
        
        show_teacher_form = 'block' if table == 'teachers' else 'none'
        show_subject_form = 'block' if table == 'subjects' else 'none'
        show_workload_form = 'block' if table == 'workload' else 'none'
        
        db_path_safe = db_path.replace('\\', '/')
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Распределение нагрузки</title>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; background: #ececec; padding: 20px; margin: 0; }}
                .container {{ max-width: 1400px; margin: 0 auto; background: white; padding: 20px; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
                h1 {{ color: #333; margin: 0 0 20px 0; }}
                .nav {{ margin: 0 0 20px 0; padding: 10px; background: #f5f5f5; border-radius: 3px; }}
                .nav a {{ margin-right: 10px; padding: 10px 15px; background: #2196F3; color: white; text-decoration: none; border-radius: 3px; display: inline-block; }}
                .nav a.active {{ background: #0b7dda; font-weight: bold; }}
                .nav a:hover {{ background: #0b7dda; }}
                .nav .back {{ background: #9e9e9e; }}
                table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                th, td {{ border: 1px solid #ddd; padding: 10px; text-align: left; }}
                th {{ background: #4CAF50; color: white; }}
                tr:nth-child(even) {{ background: #f9f9f9; }}
                tr:hover {{ background: #f1f1f1; }}
                .btn {{ padding: 5px 10px; margin: 2px; text-decoration: none; border-radius: 3px; display: inline-block; font-size: 14px; border: none; cursor: pointer; }}
                .btn-add {{ background: #4CAF50; color: white; }}
                .btn-edit {{ background: #2196F3; color: white; }}
                .btn-delete {{ background: #f44336; color: white; }}
                .form-popup {{ display: none; position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%); background: white; padding: 25px; border: 2px solid #333; border-radius: 5px; z-index: 100; min-width: 400px; }}
                .form-popup h3 {{ margin: 0 0 15px 0; }}
                .form-popup label {{ display: block; margin: 10px 0 5px; font-weight: bold; }}
                .form-popup input, .form-popup select {{ width: 100%; padding: 8px; margin-bottom: 10px; box-sizing: border-box; }}
                .form-popup button {{ margin: 5px; padding: 10px 20px; }}
                .overlay {{ display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); z-index: 50; }}
                .success {{ color: #155724; padding: 10px; background: #d4edda; border: 1px solid #c3e6cb; margin: 10px 0; border-radius: 3px; }}
                .db-path {{ font-size: 12px; color: #666; margin: 10px 0; }}
            </style>
            <script>
                function showForm(id) {{
                    document.getElementById(id).style.display = 'block';
                    document.getElementById('overlay').style.display = 'block';
                }}
                function hideForm(id) {{
                    document.getElementById(id).style.display = 'none';
                    document.getElementById('overlay').style.display = 'none';
                }}
            </script>
        </head>
        <body>
            <div class="container">
                <h1>📚 Распределение нагрузки преподавателей</h1>
                
                <div class="db-path">База: {db_path_safe}</div>
                
                <div class="nav">
                    <a href="/main?db_path={db_path_safe}&table=teachers" class="{'active' if table == 'teachers' else ''}">Преподаватели</a>
                    <a href="/main?db_path={db_path_safe}&table=subjects" class="{'active' if table == 'subjects' else ''}">Предметы</a>
                    <a href="/main?db_path={db_path_safe}&table=workload" class="{'active' if table == 'workload' else ''}">Нагрузка</a>
                    <a href="/" class="back">🏠 Выбрать другую базу</a>
                </div>
                
                {'<div class="success">' + message + '</div>' if message else ''}
                
                <h2>{'Преподаватели' if table == 'teachers' else 'Предметы' if table == 'subjects' else 'Нагрузка'}</h2>
                
                <button class="btn btn-add" onclick="showForm('addForm')">➕ Добавить</button>
                <a href="/main?db_path={db_path_safe}&table={table}" class="btn" style="background:#9e9e9e;color:white">🔄 Обновить</a>
                
                <table>
                    <tr>
                        {''.join(f'<th>{col}</th>' for col in columns)}
                        <th>Действия</th>
                    </tr>
                    {rows if rows else '<tr><td colspan="' + str(len(columns)+1) + '" style="text-align:center;color:#999">Нет данных</td></tr>'}
                </table>
                
                <div id="addForm" class="form-popup" style="display:{show_teacher_form}">
                    <h3>Добавить преподавателя</h3>
                    <form action="add_teacher" method="post">
                        <label>Фамилия *</label>
                        <input type="text" name="surname" required minlength="2" pattern="[A-Za-zА-Яа-яЁё]+">
                        <label>Имя *</label>
                        <input type="text" name="name" required minlength="2" pattern="[A-Za-zА-Яа-яЁё]+">
                        <label>Отчество</label>
                        <input type="text" name="patronymic" pattern="[A-Za-zА-Яа-яЁё]+">
                        <label>Ученая степень *</label>
                        <input type="text" name="degree" required minlength="2">
                        <label>Должность *</label>
                        <input type="text" name="position" required minlength="2">
                        <label>Стаж (лет) *</label>
                        <input type="number" name="experience" required min="0" max="100">
                        <button type="submit" class="btn btn-add">Сохранить</button>
                        <button type="button" class="btn" style="background:#9e9e9e;color:white" onclick="hideForm('addForm')">Отмена</button>
                    </form>
                </div>
                
                <div id="addFormSubject" class="form-popup" style="display:{show_subject_form}">
                    <h3>Добавить предмет</h3>
                    <form action="add_subject" method="post">
                        <label>Название предмета *</label>
                        <input type="text" name="title" required minlength="2" maxlength="70">
                        <label>Количество часов *</label>
                        <input type="number" name="hours" required min="1" max="1000">
                        <button type="submit" class="btn btn-add">Сохранить</button>
                        <button type="button" class="btn" style="background:#9e9e9e;color:white" onclick="hideForm('addFormSubject')">Отмена</button>
                    </form>
                </div>
                
                <div id="addFormWorkload" class="form-popup" style="display:{show_workload_form}">
                    <h3>Распределить нагрузку</h3>
                    <form action="add_workload" method="post">
                        <label>Преподаватель *</label>
                        <select name="teacher_id" required>
                            <option value="">Выберите...</option>
                            {teacher_options}
                        </select>
                        <label>Предмет *</label>
                        <select name="subject_id" required>
                            <option value="">Выберите...</option>
                            {subject_options}
                        </select>
                        <label>Номер группы *</label>
                        <input type="text" name="group_number" required>
                        <button type="submit" class="btn btn-add">Распределить</button>
                        <button type="button" class="btn" style="background:#9e9e9e;color:white" onclick="hideForm('addFormWorkload')">Отмена</button>
                    </form>
                </div>
                
                <div id="overlay" class="overlay" onclick="hideForm('addForm'); hideForm('addFormSubject'); hideForm('addFormWorkload');"></div>
            </div>
        </body>
        </html>
        """

    @cherrypy.expose
    def edit_form(self, table, id):
        if not self.database_file:
            raise cherrypy.HTTPRedirect("/")
        
        if table == "teachers":
            data = database.get_all_teachers(self.database_file)
            record = next((r for r in data if r[0] == int(id)), None)
            if not record:
                raise cherrypy.HTTPRedirect("/main?table=teachers")
            return self._edit_teacher_form(record)
        elif table == "subjects":
            data = database.get_all_subjects(self.database_file)
            record = next((r for r in data if r[0] == int(id)), None)
            if not record:
                raise cherrypy.HTTPRedirect("/main?table=subjects")
            return self._edit_subject_form(record)
        elif table == "workload":
            data = database.get_workload(self.database_file)
            record = next((r for r in data if r[0] == int(id)), None)
            if not record:
                raise cherrypy.HTTPRedirect("/main?table=workload")
            return self._edit_workload_form(record)
        raise cherrypy.HTTPRedirect("/")

    def _edit_teacher_form(self, record):
        return f"""
        <!DOCTYPE html><html><head><title>Изменить</title>
        <style>body{{font-family:Arial;background:#ececec;padding:20px}}.container{{max-width:500px;margin:0 auto;background:white;padding:25px;border-radius:5px}}label{{display:block;margin:10px 0 5px;font-weight:bold}}input{{width:100%;padding:8px;margin-bottom:10px;box-sizing:border-box}}button{{padding:10px 20px;margin:5px}}</style></head>
        <body><div class="container"><h3>✏️ Изменить преподавателя</h3>
        <form action="update_teacher" method="post"><input type="hidden" name="id" value="{record[0]}">
        <label>Фамилия *</label><input type="text" name="surname" value="{record[1]}" required minlength="2">
        <label>Имя *</label><input type="text" name="name" value="{record[2]}" required minlength="2">
        <label>Отчество</label><input type="text" name="patronymic" value="{record[3] or ''}">
        <label>Степень *</label><input type="text" name="degree" value="{record[4]}" required minlength="2">
        <label>Должность *</label><input type="text" name="position" value="{record[5]}" required minlength="2">
        <label>Стаж *</label><input type="number" name="experience" value="{record[6]}" required min="0" max="100">
        <button type="submit" style="background:#4CAF50;color:white">Сохранить</button>
        <a href="/main?table=teachers" style="padding:10px 20px;background:#9e9e9e;color:white;text-decoration:none">Отмена</a></form></div></body></html>
        """

    def _edit_subject_form(self, record):
        return f"""
        <!DOCTYPE html><html><head><title>Изменить</title>
        <style>body{{font-family:Arial;background:#ececec;padding:20px}}.container{{max-width:500px;margin:0 auto;background:white;padding:25px;border-radius:5px}}label{{display:block;margin:10px 0 5px;font-weight:bold}}input{{width:100%;padding:8px;margin-bottom:10px;box-sizing:border-box}}button{{padding:10px 20px;margin:5px}}</style></head>
        <body><div class="container"><h3>✏️ Изменить предмет</h3>
        <form action="update_subject" method="post"><input type="hidden" name="id" value="{record[0]}">
        <label>Название *</label><input type="text" name="title" value="{record[1]}" required minlength="2" maxlength="70">
        <label>Часы *</label><input type="number" name="hours" value="{record[2]}" required min="1" max="1000">
        <button type="submit" style="background:#4CAF50;color:white">Сохранить</button>
        <a href="/main?table=subjects" style="padding:10px 20px;background:#9e9e9e;color:white;text-decoration:none">Отмена</a></form></div></body></html>
        """

    def _edit_workload_form(self, record):
        teachers = database.get_all_teachers(self.database_file)
        subjects = database.get_all_subjects(self.database_file)
        teacher_options = "".join(f'<option value="{t[0]}"{" selected" if t[1]+" "+t[2]+" "+(t[3] or "")==record[1] else ""}>{t[1]} {t[2]} {t[3]}</option>' for t in teachers)
        subject_options = "".join(f'<option value="{s[0]}"{" selected" if s[1]==record[2] else ""}>{s[1]}</option>' for s in subjects)
        return f"""
        <!DOCTYPE html><html><head><title>Изменить</title>
        <style>body{{font-family:Arial;background:#ececec;padding:20px}}.container{{max-width:500px;margin:0 auto;background:white;padding:25px;border-radius:5px}}label{{display:block;margin:10px 0 5px;font-weight:bold}}input,select{{width:100%;padding:8px;margin-bottom:10px;box-sizing:border-box}}button{{padding:10px 20px;margin:5px}}</style></head>
        <body><div class="container"><h3>✏️ Изменить нагрузку</h3>
        <form action="update_workload" method="post"><input type="hidden" name="id" value="{record[0]}">
        <label>Преподаватель *</label><select name="teacher_id" required>{teacher_options}</select>
        <label>Предмет *</label><select name="subject_id" required>{subject_options}</select>
        <label>Группа *</label><input type="text" name="group_number" value="{record[3]}" required>
        <button type="submit" style="background:#4CAF50;color:white">Сохранить</button>
        <a href="/main?table=workload" style="padding:10px 20px;background:#9e9e9e;color:white;text-decoration:none">Отмена</a></form></div></body></html>
        """

    @cherrypy.expose
    def add_teacher(self, surname, name, patronymic="", degree="", position="", experience=0):
        try:
            database.add_teacher(self.database_file, surname, name, patronymic, degree, position, int(experience))
            raise cherrypy.HTTPRedirect(f"/main?db_path={self.database_file}&table=teachers&message=Преподаватель+добавлен!")
        except Exception as e:
            raise cherrypy.HTTPRedirect(f"/main?db_path={self.database_file}&table=teachers&message=Ошибка:+{str(e)}")

    @cherrypy.expose
    def add_subject(self, title, hours):
        try:
            database.add_subject(self.database_file, title, int(hours))
            raise cherrypy.HTTPRedirect(f"/main?db_path={self.database_file}&table=subjects&message=Предмет+добавлен!")
        except Exception as e:
            raise cherrypy.HTTPRedirect(f"/main?db_path={self.database_file}&table=subjects&message=Ошибка:+{str(e)}")

    @cherrypy.expose
    def add_workload(self, teacher_id, subject_id, group_number):
        try:
            database.add_workload(self.database_file, int(teacher_id), int(subject_id), group_number)
            raise cherrypy.HTTPRedirect(f"/main?db_path={self.database_file}&table=workload&message=Нагрузка+распределена!")
        except Exception as e:
            raise cherrypy.HTTPRedirect(f"/main?db_path={self.database_file}&table=workload&message=Ошибка:+{str(e)}")

    @cherrypy.expose
    def update_teacher(self, id, surname, name, patronymic="", degree="", position="", experience=0):
        try:
            database.update_teacher(self.database_file, int(id), surname, name, patronymic, degree, position, int(experience))
            raise cherrypy.HTTPRedirect(f"/main?db_path={self.database_file}&table=teachers&message=Преподаватель+изменен!")
        except Exception as e:
            raise cherrypy.HTTPRedirect(f"/main?db_path={self.database_file}&table=teachers&message=Ошибка:+{str(e)}")

    @cherrypy.expose
    def update_subject(self, id, title, hours):
        try:
            database.update_subject(self.database_file, int(id), title, int(hours))
            raise cherrypy.HTTPRedirect(f"/main?db_path={self.database_file}&table=subjects&message=Предмет+изменен!")
        except Exception as e:
            raise cherrypy.HTTPRedirect(f"/main?db_path={self.database_file}&table=subjects&message=Ошибка:+{str(e)}")

    @cherrypy.expose
    def update_workload(self, id, teacher_id, subject_id, group_number):
        try:
            database.update_workload(self.database_file, int(id), int(teacher_id), int(subject_id), group_number)
            raise cherrypy.HTTPRedirect(f"/main?db_path={self.database_file}&table=workload&message=Нагрузка+изменена!")
        except Exception as e:
            raise cherrypy.HTTPRedirect(f"/main?db_path={self.database_file}&table=workload&message=Ошибка:+{str(e)}")

    @cherrypy.expose
    def delete_teacher(self, id):
        try:
            success = database.delete_teacher(self.database_file, int(id))
            if success:
                raise cherrypy.HTTPRedirect(f"/main?db_path={self.database_file}&table=teachers&message=Преподаватель+удален!")
            else:
                raise cherrypy.HTTPRedirect(f"/main?db_path={self.database_file}&table=teachers&message=Нельзя+удалить!+Преподаватель+есть+в+нагрузке.")
        except Exception as e:
            raise cherrypy.HTTPRedirect(f"/main?db_path={self.database_file}&table=teachers&message=Ошибка:+{str(e)}")

    @cherrypy.expose
    def delete_subject(self, id):
        try:
            success = database.delete_subject(self.database_file, int(id))
            if success:
                raise cherrypy.HTTPRedirect(f"/main?db_path={self.database_file}&table=subjects&message=Предмет+удален!")
            else:
                raise cherrypy.HTTPRedirect(f"/main?db_path={self.database_file}&table=subjects&message=Нельзя+удалить!+Предмет+есть+в+нагрузке.")
        except Exception as e:
            raise cherrypy.HTTPRedirect(f"/main?db_path={self.database_file}&table=subjects&message=Ошибка:+{str(e)}")

    @cherrypy.expose
    def delete_workload(self, id):
        try:
            database.delete_workload(self.database_file, int(id))
            raise cherrypy.HTTPRedirect(f"/main?db_path={self.database_file}&table=workload&message=Нагрузка+удалена!")
        except Exception as e:
            raise cherrypy.HTTPRedirect(f"/main?db_path={self.database_file}&table=workload&message=Ошибка:+{str(e)}")

if __name__ == "__main__":
    cherrypy.config.update({
        'server.socket_host': '127.0.0.1',
        'server.socket_port': 8080,
    })
    cherrypy.quickstart(WebApp())