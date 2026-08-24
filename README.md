# 🔍 Smart Log Analyzer

A Python-based log monitoring and anomaly detection system that analyzes both historical and real-time application logs, detects suspicious activity using a custom anomaly scoring engine, and uses Groq LLMs to explain detected anomalies.

## 🚀 Features

- 📁 Upload and analyze historical CSV logs
- ⚡ Real-time log monitoring and detection
- 🔎 Rule-based anomaly detection
- 📊 Anomaly scoring and detection reasons
- 🤖 Groq-powered anomaly explanation
- 🧠 AI-generated probable root cause
- 🛠️ Recommended next steps for detected anomalies
- 🗄️ SQLite database for persistent log storage
- 📋 Log filtering and investigation
- 📝 System activity / audit logs
- 📊 Streamlit admin dashboard
- 🔐 Environment-based API key configuration

---

## 🏗️ Architecture

```text
                 ┌──────────────────┐
                 │  Historical CSV  │
                 └────────┬─────────┘
                          │
                          │
                 ┌────────▼─────────┐
                 │ Data Validation  │
                 └────────┬─────────┘
                          │
                          │
┌─────────────────┐       │
│ Real-Time Logs  │───────┤
└─────────────────┘       │
                          ▼
                   ┌──────────────┐
                   │    SQLite    │
                   └──────┬───────┘
                          │
                          ▼
                ┌────────────────────┐
                │ Anomaly Detector   │
                │                    │
                │ Score + Reason     │
                └─────────┬──────────┘
                          │
                    Anomaly detected
                          │
                          ▼
                    ┌───────────┐
                    │   Groq    │
                    │    LLM    │
                    └─────┬─────┘
                          │
              ┌───────────┼───────────┐
              ▼           ▼           ▼
         Explanation  Root Cause  Next Step
              │           │           │
              └───────────┼───────────┘
                          ▼
                       SQLite
                          │
                          ▼
                  ┌──────────────┐
                  │  Streamlit   │
                  │  Dashboard   │
                  └──────────────┘
