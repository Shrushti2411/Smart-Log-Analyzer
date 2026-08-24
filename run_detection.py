from database import get_logs, update_anomaly
from anomaly_detector import detect_anomalies


df = get_logs()

print(f"Found {len(df)} logs in database.")


if df.empty:
    print("No logs found in database.")
    exit()


results = detect_anomalies(df)


for _, result in results.iterrows():

    update_anomaly(
        result["id"],
        result["is_anomaly"],
        result["score"],
        result["reason"]
    )


print("\nAnomaly Detection Results:")
print("-" * 80)


for _, result in results.iterrows():

    status = (
        "ANOMALY"
        if result["is_anomaly"]
        else "NORMAL"
    )

    print(
        f"ID: {result['id']} | "
        f"{status} | "
        f"Score: {result['score']}"
    )

    if result["is_anomaly"]:

        print(
            f"Reason: {result['reason']}"
        )

    print("-" * 80)