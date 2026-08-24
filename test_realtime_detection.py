import pandas as pd

from database import (
    initialize_database,
    insert_logs,
    get_logs,
    update_anomaly,
    add_activity
)

from realtime_generator import generate_log

from anomaly_detector import detect_anomalies


# ============================================
# 1. Initialize database
# ============================================

initialize_database()


# ============================================
# 2. Generate one incoming log
# ============================================

new_log = generate_log()

print("\nIncoming real-time log:")
print(new_log)


# ============================================
# 3. Convert log to DataFrame
# ============================================

new_df = pd.DataFrame([new_log])


# ============================================
# 4. Store it as a real-time log
# ============================================

insert_logs(
    new_df,
    log_type="realtime"
)


# ============================================
# 5. Get the newly inserted log
# ============================================

logs = get_logs()

latest = logs.head(1)


# ============================================
# 6. Run anomaly detection
# ============================================

result = detect_anomalies(
    latest
)

detection = result.iloc[0]


# ============================================
# 7. Save detection result
# ============================================

log_id = int(
    latest.iloc[0]["id"]
)

update_anomaly(
    log_id,
    detection["is_anomaly"],
    detection["score"],
    detection["reason"]
)


# ============================================
# 8. Add activity
# ============================================

add_activity(
    "REALTIME_LOG_RECEIVED",
    f"Real-time {new_log['event_type']} log received.",
    log_id
)


# ============================================
# 9. Display result
# ============================================

print("\n================================")
print("REAL-TIME DETECTION RESULT")
print("================================")

print(
    "Event:",
    new_log["event_type"]
)

print(
    "Source:",
    new_log["source"]
)

print(
    "Status:",
    new_log["status"]
)

print(
    "Severity:",
    new_log["severity"]
)

print(
    "Anomaly Score:",
    detection["score"]
)

print(
    "Reason:",
    detection["reason"]
)


if detection["is_anomaly"]:

    print("\n🚨 ANOMALY DETECTED")

else:

    print("\n🟢 NORMAL LOG")