from database import get_logs
from groq_service import explain_anomaly


df = get_logs()

anomalies = df[df["is_anomaly"] == 1]

if anomalies.empty:
    print("No anomalies found.")
else:
    log = anomalies.iloc[0].to_dict()

    print("Testing Groq with log:")
    print(log)

    result = explain_anomaly(log)

    print("\n========== AI ANALYSIS ==========")
    print("\nExplanation:")
    print(result["explanation"])

    print("\nRoot Cause:")
    print(result["root_cause"])

    print("\nNext Step:")
    print(result["next_step"])