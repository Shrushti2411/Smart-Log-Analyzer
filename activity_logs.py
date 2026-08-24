from database import (
    initialize_database,
    add_activity,
    get_activities
)


# Make sure all database tables exist
initialize_database()


# Add test activity
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