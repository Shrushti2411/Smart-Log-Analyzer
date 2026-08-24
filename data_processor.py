import pandas as pd


REQUIRED_COLUMNS = [
    "timestamp",
    "event_type",
    "severity",
    "source",
    "status",
    "message"
]


def load_csv(file):
    return pd.read_csv(file)


def validate_logs(df):

    errors = []

    # Empty dataset
    if df.empty:
        errors.append("Dataset is empty.")
        return df, errors

    # Required columns
    missing_columns = [
        column
        for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing_columns:
        errors.append(
            f"Missing required columns: {missing_columns}"
        )

        return df, errors

    # Timestamp validation
    df["timestamp"] = pd.to_datetime(
        df["timestamp"],
        errors="coerce"
    )

    invalid_timestamps = df["timestamp"].isna().sum()

    if invalid_timestamps > 0:
        errors.append(
            f"{invalid_timestamps} invalid timestamp(s) found."
        )

    # Status validation
    df["status"] = pd.to_numeric(
        df["status"],
        errors="coerce"
    )

    invalid_status = df["status"].isna().sum()

    if invalid_status > 0:
        errors.append(
            f"{invalid_status} invalid status value(s) found."
        )

    return df, errors