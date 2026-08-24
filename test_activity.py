from database import add_activity, get_activities


# Add one test activity
add_activity(
    "SYSTEM_TEST",
    "Activity logging system is working."
)


# Read activities
activities = get_activities()

print("\nSystem Activities:")
print(
    activities.to_string(
        index=False
    )
)