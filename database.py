import sqlite3
import pandas as pd


DB_NAME = "logs.db"


# =====================================================
# DATABASE CONNECTION
# =====================================================

def get_connection():

    return sqlite3.connect(DB_NAME)


# =====================================================
# INITIALIZE DATABASE
# =====================================================

def initialize_database():

    conn = get_connection()

    cursor = conn.cursor()


    # =================================================
    # LOGS TABLE
    # =================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS logs (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            timestamp TEXT NOT NULL,

            event_type TEXT NOT NULL,

            severity TEXT NOT NULL,

            source TEXT NOT NULL,

            status INTEGER NOT NULL,

            message TEXT NOT NULL,

            is_anomaly INTEGER DEFAULT 0,

            anomaly_score REAL DEFAULT 0,

            anomaly_reason TEXT,

            ai_explanation TEXT,

            root_cause TEXT,

            next_step TEXT,

            log_type TEXT DEFAULT 'historical',

            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)


    # =================================================
    # ACTIVITY LOGS TABLE
    # =================================================

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


# =====================================================
# INSERT LOGS
# =====================================================

def insert_logs(
    df,
    log_type="historical"
):

    conn = get_connection()

    records = []


    for _, row in df.iterrows():

        records.append((
            str(row["timestamp"]),
            str(row["event_type"]),
            str(row["severity"]),
            str(row["source"]),
            int(row["status"]),
            str(row["message"]),

            0,
            0,
            "",
            "",
            "",
            "",

            log_type
        ))


    conn.executemany("""
        INSERT INTO logs (

            timestamp,
            event_type,
            severity,
            source,
            status,
            message,

            is_anomaly,
            anomaly_score,
            anomaly_reason,

            ai_explanation,
            root_cause,
            next_step,

            log_type

        )

        VALUES (
            ?, ?, ?, ?, ?, ?,
            ?, ?, ?,
            ?, ?, ?,
            ?
        )
    """, records)


    conn.commit()

    conn.close()


# =====================================================
# GET ALL LOGS
# =====================================================

def get_logs():

    conn = get_connection()


    df = pd.read_sql_query(
        """
        SELECT *
        FROM logs
        ORDER BY timestamp DESC
        """,
        conn
    )


    conn.close()

    return df


# =====================================================
# UPDATE ANOMALY RESULT
# =====================================================

def update_anomaly(
    log_id,
    is_anomaly,
    score,
    reason
):

    conn = get_connection()


    conn.execute("""
        UPDATE logs

        SET
            is_anomaly = ?,
            anomaly_score = ?,
            anomaly_reason = ?

        WHERE id = ?
    """, (

        int(is_anomaly),
        float(score),
        reason,
        log_id

    ))


    conn.commit()

    conn.close()


# =====================================================
# UPDATE AI ANALYSIS
# =====================================================

def update_ai_result(
    log_id,
    explanation,
    root_cause,
    next_step
):

    conn = get_connection()


    conn.execute("""
        UPDATE logs

        SET
            ai_explanation = ?,
            root_cause = ?,
            next_step = ?

        WHERE id = ?
    """, (

        explanation,
        root_cause,
        next_step,
        log_id

    ))


    conn.commit()

    conn.close()


# =====================================================
# ADD SYSTEM ACTIVITY
# =====================================================

def add_activity(
    action,
    description,
    log_id=None
):

    conn = get_connection()


    conn.execute("""
        INSERT INTO activity_logs (

            action,
            description,
            log_id

        )

        VALUES (?, ?, ?)
    """, (

        action,
        description,
        log_id

    ))


    conn.commit()

    conn.close()


# =====================================================
# GET SYSTEM ACTIVITIES
# =====================================================

def get_activities():

    conn = get_connection()


    df = pd.read_sql_query(
        """
        SELECT

            id,
            action,
            description,
            log_id,
            created_at

        FROM activity_logs

        ORDER BY created_at DESC
        """,
        conn
    )


    conn.close()

    return df