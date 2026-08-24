import pandas as pd

from data_processor import validate_logs
from database import (
    initialize_database,
    insert_logs
)


CSV_FILE = "data/logs.csv"


df = pd.read_csv(CSV_FILE)

print("Original data:")
print(df.head())


df, errors = validate_logs(df)


if errors:

    print("\nValidation messages:")

    for error in errors:
        print("-", error)


if not df.empty:

    initialize_database()

    insert_logs(
        df,
        log_type="historical"
    )

    print(
        f"\nSuccessfully imported {len(df)} logs."
    )