import sqlite3

def export_to_sql(db_file, sql_file):
    with open(db_file, 'r') as f:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        with open(sql_file, 'w') as f:
            for table in cursor.execute("SELECT name FROM sqlite_master WHERE type='table'"):
                cursor.execute(f"SELECT sql FROM sqlite_master WHERE name='{table[0]}'")
                f.write(cursor.fetchone()[0] + ';\n\n')
        
        conn.close()

# Использование
export_to_sql('university.db', 'schema.sql')