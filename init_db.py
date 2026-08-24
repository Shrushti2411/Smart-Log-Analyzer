def initialize_database():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            ...
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS activity_logs (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            action TEXT NOT NULL,

            description TEXT,

            log_id INTEGER,

            created_at TEXT DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (log_id)
                REFERENCES logs(id)
        )
    """)

    conn.commit()
    conn.close()