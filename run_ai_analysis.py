from database import get_logs, update_ai_result
from groq_service import explain_anomaly


# Get all logs from SQLite
df = get_logs()

# Only get logs already detected as anomalies
anomalies = df[df["is_anomaly"] == 1]

if anomalies.empty:
    print("No anomalies found.")
    exit()


for _, log in anomalies.iterrows():

    # Don't call Groq again if this anomaly
    # already has an AI explanation
    if log["ai_explanation"]:
        print(
            f"Log {log['id']} already analyzed. Skipping."
        )
        continue

    print(
        f"Analyzing anomaly ID: {log['id']}..."
    )

    # Send anomaly to Groq
    result = explain_anomaly(
        log.to_dict()
    )

    # Save AI response into SQLite
    update_ai_result(
        log["id"],
        result["explanation"],
        result["root_cause"],
        result["next_step"]
    )

    print(
        f"AI analysis saved for log {log['id']}"
    )


print("\nAI analysis completed successfully.")