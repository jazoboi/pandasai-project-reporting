# Automated Project Reporting with PandasAI

> Natural language analytics on Jira ticket data — ask questions, get auto-generated charts and exportable reports.

## Role
**Full-Stack Developer** — Built the Jira integration and PandasAI query interface.

## Overview
Automated project reporting tool that connects to Jira's REST API, ingests ticket data, and enables natural language queries via PandasAI. Ask "Show bug trends by sprint" and get auto-generated charts.

## Architecture
```
Jira REST API → Data Extractor → Pandas DataFrame
                                        ↓
              User NL Query → PandasAI Engine → Auto Visualization
                                                      ↓
                                        Export (JSON / PDF / PNG)
```

## Key Features
- **Jira Integration** — Full REST API connector with pagination and caching
- **Natural Language Queries** — PandasAI translates English to pandas operations
- **Auto Visualization** — Charts generated from query results automatically
- **Scheduled Reports** — Cron-based report generation and email delivery
- **Export Formats** — JSON, PDF, PNG chart exports

## Tech Stack
`Python` · `PandasAI` · `Jira REST API` · `Matplotlib` · `JSON/PDF Export`

## Impact
- Reduced weekly reporting from **4 hours to 5 minutes**
- Adopted by **3 project teams**
- Auto-generates sprint burndown, velocity, and backlog charts

## Project Structure
```
src/
├── jira_client.py         # Jira REST API connector
├── pandasai_analyzer.py   # NL query engine
├── report_exporter.py     # Multi-format export
├── scheduler.py           # Cron-based scheduling
└── config.py              # API & report settings
```

## License
MIT
