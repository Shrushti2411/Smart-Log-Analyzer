import pandas as pd


def detect_anomalies(df):

    df = df.copy()

    df["timestamp"] = pd.to_datetime(
        df["timestamp"],
        errors="coerce"
    )

    # Find failed requests
    failure_mask = df["status"] >= 400

    failure_counts = (
        df.loc[failure_mask]
        .groupby("source")
        .size()
    )

    results = []

    for _, row in df.iterrows():

        score = 0

        reasons = []

        status = int(row["status"])

        severity = str(
            row["severity"]
        ).upper()

        source = row["source"]

        # --------------------
        # STATUS
        # --------------------

        if status >= 500:

            score += 40

            reasons.append(
                f"Server error ({status})"
            )

        elif status in [401, 403]:

            score += 25

            reasons.append(
                f"Access/authentication failure ({status})"
            )

        # --------------------
        # SEVERITY
        # --------------------

        if severity == "ERROR":

            score += 30

            reasons.append(
                "ERROR severity"
            )

        elif severity == "CRITICAL":

            score += 40

            reasons.append(
                "CRITICAL severity"
            )

        elif severity == "WARNING":

            score += 10

            reasons.append(
                "WARNING severity"
            )

        # --------------------
        # BEHAVIOR
        # --------------------

        source_failures = failure_counts.get(
            source,
            0
        )

        if source_failures >= 3:

            score += 20

            reasons.append(
                f"Repeated failures from {source}"
            )

        # --------------------
        # FINAL DECISION
        # --------------------

        is_anomaly = score >= 50

        results.append({
            "id": row["id"],
            "is_anomaly": is_anomaly,
            "score": score,
            "reason": "; ".join(reasons)
        })

    return pd.DataFrame(results)