import streamlit as st
import pandas as pd



from database import (
    initialize_database,
    get_logs,
    insert_logs,
    update_anomaly,
    update_ai_result,
    add_activity,
    get_activities
)

from data_processor import validate_logs
from anomaly_detector import detect_anomalies
from groq_service import explain_anomaly
from realtime_generator import generate_log


# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="Smart Log Analyzer",
    page_icon="🔍",
    layout="wide"
)


# =====================================================
# DATABASE
# =====================================================

initialize_database()


# =====================================================
# SIDEBAR
# =====================================================

st.sidebar.title("🔍 Smart Log Analyzer")

st.sidebar.caption(
    "Intelligent Log Monitoring System"
)

page = st.sidebar.radio(
    "Navigation",
    [
        "🏠 Dashboard",
        "📋 Activity Logs",
        "🚨 Anomalies",
        "⚡ Real-Time Monitor",
        "📁 Import Logs",
        "📝 System Activity"
    ]
)


# =====================================================
# LOAD DATABASE LOGS
# =====================================================

df = get_logs()


# =====================================================
# DASHBOARD
# =====================================================

if page == "🏠 Dashboard":

    st.title("🏠 Admin Dashboard")

    st.caption(
        "Monitor application logs, detect anomalies and investigate incidents."
    )

    total_logs = len(df)

    anomaly_count = (
        int(df["is_anomaly"].sum())
        if not df.empty
        else 0
    )

    normal_count = total_logs - anomaly_count

    anomaly_rate = (
        anomaly_count / total_logs * 100
        if total_logs > 0
        else 0
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Total Logs",
        total_logs
    )

    col2.metric(
        "Anomalies",
        anomaly_count
    )

    col3.metric(
        "Normal Logs",
        normal_count
    )

    col4.metric(
        "Anomaly Rate",
        f"{anomaly_rate:.1f}%"
    )

    st.divider()

    # -------------------------------------------------
    # RUN DETECTION
    # -------------------------------------------------

    st.subheader("🔎 Anomaly Detection")

    if st.button(
        "Run Anomaly Detection",
        type="primary"
    ):

        if df.empty:

            st.warning(
                "No logs available for analysis."
            )

        else:

            results = detect_anomalies(df)

            detected_count = 0

            for _, result in results.iterrows():

                log_id = int(result["id"])

                update_anomaly(
                    log_id,
                    result["is_anomaly"],
                    result["score"],
                    result["reason"]
                )

                if result["is_anomaly"]:

                    detected_count += 1

                    add_activity(
                        "ANOMALY_DETECTED",
                        (
                            f"Anomaly detected with "
                            f"score {result['score']}."
                        ),
                        log_id
                    )

            add_activity(
                "DETECTION_COMPLETED",
                (
                    f"Analyzed {len(results)} logs "
                    f"and detected {detected_count} anomalies."
                )
            )

            st.success(
                f"Detection completed. "
                f"{detected_count} anomalies detected."
            )

            st.rerun()

    # -------------------------------------------------
    # RECENT LOGS
    # -------------------------------------------------

    df = get_logs()

    st.divider()

    st.subheader("📋 Recent Logs")

    if df.empty:

        st.info(
            "No logs available."
        )

    else:

        recent_df = df.head(10).copy()

        recent_df["Detection"] = (
            recent_df["is_anomaly"]
            .apply(
                lambda x:
                "🔴 Anomaly"
                if x == 1
                else "🟢 Normal"
            )
        )

        st.dataframe(
            recent_df[
                [
                    "timestamp",
                    "event_type",
                    "severity",
                    "source",
                    "status",
                    "anomaly_score",
                    "Detection"
                ]
            ],
            use_container_width=True,
            hide_index=True
        )

    # -------------------------------------------------
    # SOURCE CHART
    # -------------------------------------------------

    if not df.empty:

        st.divider()

        st.subheader("📊 Logs by Source")

        source_counts = (
            df["source"]
            .value_counts()
        )

        st.bar_chart(
            source_counts
        )


# =====================================================
# ACTIVITY LOGS
# =====================================================

elif page == "📋 Activity Logs":

    st.title("📋 Activity Logs")

    st.caption(
        "Browse and filter stored application logs."
    )

    if df.empty:

        st.info(
            "No logs found in database."
        )

    else:

        col1, col2, col3 = st.columns(3)

        with col1:

            detection_filter = st.selectbox(
                "Detection",
                [
                    "All",
                    "Normal",
                    "Anomaly"
                ]
            )

        with col2:

            severity_options = [
                "All"
            ] + sorted(
                df["severity"]
                .dropna()
                .unique()
                .tolist()
            )

            severity_filter = st.selectbox(
                "Severity",
                severity_options
            )

        with col3:

            source_options = [
                "All"
            ] + sorted(
                df["source"]
                .dropna()
                .unique()
                .tolist()
            )

            source_filter = st.selectbox(
                "Source",
                source_options
            )

        filtered_df = df.copy()

        if detection_filter == "Normal":

            filtered_df = filtered_df[
                filtered_df["is_anomaly"] == 0
            ]

        elif detection_filter == "Anomaly":

            filtered_df = filtered_df[
                filtered_df["is_anomaly"] == 1
            ]

        if severity_filter != "All":

            filtered_df = filtered_df[
                filtered_df["severity"]
                == severity_filter
            ]

        if source_filter != "All":

            filtered_df = filtered_df[
                filtered_df["source"]
                == source_filter
            ]

        st.write(
            f"Showing {len(filtered_df)} logs"
        )

        display_df = filtered_df.copy()

        display_df["Detection"] = (
            display_df["is_anomaly"]
            .apply(
                lambda x:
                "🔴 Anomaly"
                if x == 1
                else "🟢 Normal"
            )
        )

        st.dataframe(
            display_df[
                [
                    "timestamp",
                    "event_type",
                    "severity",
                    "source",
                    "status",
                    "message",
                    "anomaly_score",
                    "Detection"
                ]
            ],
            use_container_width=True,
            hide_index=True
        )


# =====================================================
# ANOMALIES
# =====================================================

elif page == "🚨 Anomalies":

    st.title("🚨 Anomaly Investigation")

    st.caption(
        "Investigate anomalies detected by the Python detection engine."
    )

    anomaly_df = df[
        df["is_anomaly"] == 1
    ]

    if anomaly_df.empty:

        st.success(
            "No anomalies detected."
        )

    else:

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Total Anomalies",
            len(anomaly_df)
        )

        col2.metric(
            "Highest Score",
            int(
                anomaly_df["anomaly_score"].max()
            )
        )

        col3.metric(
            "Affected Sources",
            anomaly_df["source"].nunique()
        )

        st.divider()

        st.subheader(
            "Detected Anomalies"
        )

        st.dataframe(
            anomaly_df[
                [
                    "timestamp",
                    "event_type",
                    "severity",
                    "source",
                    "status",
                    "anomaly_score",
                    "anomaly_reason"
                ]
            ],
            use_container_width=True,
            hide_index=True
        )

        st.divider()

        selected_id = st.selectbox(
            "Select an anomaly to investigate",
            anomaly_df["id"].tolist()
        )

        selected = anomaly_df[
            anomaly_df["id"] == selected_id
        ].iloc[0]

        st.subheader(
            "🔎 Anomaly Details"
        )

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Status",
            selected["status"]
        )

        col2.metric(
            "Anomaly Score",
            selected["anomaly_score"]
        )

        col3.metric(
            "Severity",
            selected["severity"]
        )

        st.write(
            "**Timestamp:**",
            selected["timestamp"]
        )

        st.write(
            "**Event Type:**",
            selected["event_type"]
        )

        st.write(
            "**Source:**",
            selected["source"]
        )

        st.write(
            "**Message:**",
            selected["message"]
        )

        st.markdown(
            "### Why was this flagged?"
        )

        st.warning(
            selected["anomaly_reason"]
        )

        st.divider()

        st.subheader(
            "🤖 AI Analysis"
        )

        if not selected["ai_explanation"]:

            st.info(
                "This anomaly has not been analyzed by AI yet."
            )

            if st.button(
                "🤖 Analyze with Groq",
                type="primary"
            ):

                with st.spinner(
                    "Analyzing anomaly with Groq..."
                ):

                    try:

                        result = explain_anomaly(
                            selected.to_dict()
                        )

                        update_ai_result(
                            int(selected_id),
                            result["explanation"],
                            result["root_cause"],
                            result["next_step"]
                        )

                        add_activity(
                            "AI_ANALYSIS_COMPLETED",
                            (
                                "Groq generated an explanation, "
                                "root cause and recommended next step."
                            ),
                            int(selected_id)
                        )

                        st.success(
                            "AI analysis completed."
                        )

                        st.rerun()

                    except Exception as e:

                        st.error(
                            f"Groq analysis failed: {e}"
                        )

        else:

            st.markdown(
                "### What happened?"
            )

            st.write(
                selected["ai_explanation"]
            )

            st.markdown(
                "### Likely Root Cause"
            )

            st.write(
                selected["root_cause"]
            )

            st.markdown(
                "### Recommended Next Step"
            )

            st.write(
                selected["next_step"]
            )


# =====================================================
# REAL-TIME MONITOR
# =====================================================

elif page == "⚡ Real-Time Monitor":

    st.title("⚡ Real-Time Log Monitor")

    st.caption(
        "Continuously monitor incoming application logs "
        "and detect anomalies in real time."
    )

    # -------------------------------------------------
    # SESSION STATE
    # -------------------------------------------------

    if "monitoring" not in st.session_state:
        st.session_state.monitoring = False

    if "realtime_count" not in st.session_state:
        st.session_state.realtime_count = 0

    if "realtime_anomalies" not in st.session_state:
        st.session_state.realtime_anomalies = 0

    if "latest_realtime_log" not in st.session_state:
        st.session_state.latest_realtime_log = None

    if "latest_realtime_detection" not in st.session_state:
        st.session_state.latest_realtime_detection = None

    if "latest_realtime_id" not in st.session_state:
        st.session_state.latest_realtime_id = None

    # -------------------------------------------------
    # CONTROLS
    # -------------------------------------------------

    col1, col2 = st.columns(2)

    with col1:

        if st.button(
            "▶️ Start Monitoring",
            type="primary",
            use_container_width=True
        ):

            st.session_state.monitoring = True

            st.rerun()

    with col2:

        if st.button(
            "⏹️ Stop Monitoring",
            use_container_width=True
        ):

            st.session_state.monitoring = False

            st.rerun()

    # -------------------------------------------------
    # STATUS
    # -------------------------------------------------

    if st.session_state.monitoring:

        st.success(
            "🟢 Monitoring is ACTIVE"
        )

    else:

        st.info(
            "⏸️ Monitoring is stopped"
        )

    # -------------------------------------------------
    # AUTO REFRESH + NEW LOG
    # -------------------------------------------------

    if st.session_state.monitoring:

        st_autorefresh(
            interval=2000,
            key="realtime_monitor"
        )

        # Generate incoming log
        new_log = generate_log()

        # Convert to DataFrame
        new_df = pd.DataFrame([
            new_log
        ])

        # Store in SQLite
        insert_logs(
            new_df,
            log_type="realtime"
        )

        # Get latest record
        logs = get_logs()

        latest = logs.head(1)

        log_id = int(
            latest.iloc[0]["id"]
        )

        # Detect anomaly
        result = detect_anomalies(
            latest
        )

        detection = result.iloc[0]

        # Save detection result
        update_anomaly(
            log_id,
            detection["is_anomaly"],
            detection["score"],
            detection["reason"]
        )

        # Activity
        add_activity(
            "REALTIME_LOG_RECEIVED",
            (
                f"Real-time "
                f"{new_log['event_type']} log received."
            ),
            log_id
        )

        if detection["is_anomaly"]:

            add_activity(
                "REALTIME_ANOMALY_DETECTED",
                (
                    f"Real-time anomaly detected. "
                    f"Score: {detection['score']}. "
                    f"Reason: {detection['reason']}"
                ),
                log_id
            )

        # Session state
        st.session_state.realtime_count += 1

        if detection["is_anomaly"]:

            st.session_state.realtime_anomalies += 1

        st.session_state.latest_realtime_log = new_log

        st.session_state.latest_realtime_detection = (
            detection.to_dict()
        )

        st.session_state.latest_realtime_id = log_id

    # -------------------------------------------------
    # LIVE METRICS
    # -------------------------------------------------

    st.divider()

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Logs Received",
        st.session_state.realtime_count
    )

    col2.metric(
        "Anomalies",
        st.session_state.realtime_anomalies
    )

    if st.session_state.realtime_count > 0:

        anomaly_rate = (
            st.session_state.realtime_anomalies
            / st.session_state.realtime_count
        ) * 100

    else:

        anomaly_rate = 0

    col3.metric(
        "Anomaly Rate",
        f"{anomaly_rate:.1f}%"
    )

    # -------------------------------------------------
    # LATEST LOG
    # -------------------------------------------------

    if st.session_state.latest_realtime_log:

        new_log = (
            st.session_state.latest_realtime_log
        )

        detection = (
            st.session_state.latest_realtime_detection
        )

        log_id = (
            st.session_state.latest_realtime_id
        )

        st.divider()

        st.subheader(
            "📡 Latest Incoming Log"
        )

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "Event",
            new_log["event_type"]
        )

        col2.metric(
            "Source",
            new_log["source"]
        )

        col3.metric(
            "Status",
            new_log["status"]
        )

        col4.metric(
            "Score",
            detection["score"]
        )

        st.write(
            "**Timestamp:**",
            new_log["timestamp"]
        )

        st.write(
            "**Severity:**",
            new_log["severity"]
        )

        st.write(
            "**Message:**",
            new_log["message"]
        )

        st.divider()

        # -------------------------------------------------
        # ANOMALY RESULT
        # -------------------------------------------------

        if detection["is_anomaly"]:

            st.error(
                "🚨 ANOMALY DETECTED"
            )

            st.warning(
                detection["reason"]
            )

            st.write(
                f"**Anomaly Score:** "
                f"{detection['score']}"
            )

            # -------------------------------------------------
            # GROQ
            # -------------------------------------------------

            st.divider()

            st.subheader(
                "🤖 AI Investigation"
            )

            if st.button(
                "🤖 Analyze Latest Anomaly",
                key="live_groq"
            ):

                with st.spinner(
                    "Analyzing anomaly with Groq..."
                ):

                    try:

                        ai_result = explain_anomaly(
                            {
                                **new_log,

                                "id": log_id,

                                "anomaly_score":
                                    detection["score"],

                                "anomaly_reason":
                                    detection["reason"]
                            }
                        )

                        update_ai_result(
                            log_id,
                            ai_result["explanation"],
                            ai_result["root_cause"],
                            ai_result["next_step"]
                        )

                        add_activity(
                            "AI_ANALYSIS_COMPLETED",
                            "Groq analyzed a real-time anomaly.",
                            log_id
                        )

                        st.success(
                            "AI analysis completed."
                        )

                        st.markdown(
                            "### What Happened?"
                        )

                        st.write(
                            ai_result["explanation"]
                        )

                        st.markdown(
                            "### Likely Root Cause"
                        )

                        st.write(
                            ai_result["root_cause"]
                        )

                        st.markdown(
                            "### Recommended Next Step"
                        )

                        st.write(
                            ai_result["next_step"]
                        )

                    except Exception as e:

                        st.error(
                            f"Groq analysis failed: {e}"
                        )

        else:

            st.success(
                "🟢 NORMAL LOG"
            )

            st.write(
                "No anomaly was detected in this log."
            )

    # -------------------------------------------------
    # RECENT REAL-TIME LOGS
    # -------------------------------------------------

    st.divider()

    st.subheader(
        "📋 Recent Real-Time Logs"
    )

    realtime_logs = get_logs()

    if not realtime_logs.empty:

        realtime_logs = realtime_logs[
            realtime_logs["log_type"] == "realtime"
        ].head(15)

        if not realtime_logs.empty:

            display_df = realtime_logs.copy()

            display_df["Detection"] = (
                display_df["is_anomaly"]
                .apply(
                    lambda x:
                    "🔴 Anomaly"
                    if x == 1
                    else "🟢 Normal"
                )
            )

            st.dataframe(
                display_df[
                    [
                        "timestamp",
                        "event_type",
                        "severity",
                        "source",
                        "status",
                        "anomaly_score",
                        "Detection"
                    ]
                ],
                use_container_width=True,
                hide_index=True
            )

        else:

            st.info(
                "No real-time logs yet."
            )

    else:

        st.info(
            "No logs available."
        )


# =====================================================
# IMPORT HISTORICAL LOGS
# =====================================================

elif page == "📁 Import Logs":

    st.title("📁 Import Historical Logs")

    st.caption(
        "Upload a CSV file containing application logs."
    )

    uploaded_file = st.file_uploader(
        "Choose CSV file",
        type=["csv"]
    )

    if uploaded_file:

        try:

            uploaded_df = pd.read_csv(
                uploaded_file
            )

            st.subheader(
                "Preview"
            )

            st.dataframe(
                uploaded_df.head(20),
                use_container_width=True,
                hide_index=True
            )

            st.write(
                f"Records found: {len(uploaded_df)}"
            )

            # -------------------------------------------------
            # VALIDATION
            # -------------------------------------------------

            validated_df, errors = validate_logs(
                uploaded_df
            )

            if errors:

                st.warning(
                    "Validation messages:"
                )

                for error in errors:

                    st.write(
                        f"⚠️ {error}"
                    )

            if not validated_df.empty:

                st.success(
                    "CSV validation completed."
                )

                if st.button(
                    "💾 Import into SQLite",
                    type="primary"
                ):

                    insert_logs(
                        validated_df,
                        log_type="historical"
                    )

                    add_activity(
                        "CSV_IMPORTED",
                        (
                            f"{len(validated_df)} "
                            f"historical logs imported."
                        )
                    )

                    st.success(
                        f"{len(validated_df)} logs imported successfully."
                    )

                    st.rerun()

        except Exception as e:

            st.error(
                f"Unable to read CSV: {e}"
            )


# =====================================================
# SYSTEM ACTIVITY
# =====================================================

elif page == "📝 System Activity":

    st.title("📝 System Activity")

    st.caption(
        "Audit trail of important system events."
    )

    activities = get_activities()

    if activities.empty:

        st.info(
            "No system activity recorded yet."
        )

    else:

        st.metric(
            "Total Activities",
            len(activities)
        )

        st.divider()

        st.dataframe(
            activities[
                [
                    "created_at",
                    "action",
                    "description",
                    "log_id"
                ]
            ],
            use_container_width=True,
            hide_index=True
        )
