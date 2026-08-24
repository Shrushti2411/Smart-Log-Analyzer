import random
from datetime import datetime


SOURCES = [
    "server-1",
    "server-2",
    "server-3"
]


EVENTS = [
    "LOGIN",
    "GET_USERS",
    "GET_PRODUCTS",
    "SEARCH",
    "PAYMENT",
    "GET_ORDERS",
    "LOGOUT"
]


NORMAL_MESSAGES = {
    "LOGIN": "Login successful",
    "GET_USERS": "Users fetched successfully",
    "GET_PRODUCTS": "Products fetched successfully",
    "SEARCH": "Search completed",
    "PAYMENT": "Payment successful",
    "GET_ORDERS": "Orders fetched successfully",
    "LOGOUT": "Logout successful"
}


def generate_log():

    suspicious = random.random() < 0.15

    source = random.choice(SOURCES)

    event_type = random.choice(EVENTS)

    if suspicious:

        if random.random() < 0.7:

            status = 500
            severity = "ERROR"
            message = "Internal server error"

        else:

            status = 403
            severity = "WARNING"
            message = "Access denied"

    else:

        status = 200
        severity = "INFO"

        message = NORMAL_MESSAGES[
            event_type
        ]

    return {
        "timestamp": datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
        "event_type": event_type,
        "severity": severity,
        "source": source,
        "status": status,
        "message": message
    }