from database import get_logs

df = get_logs()

print(df.to_string(index=False))