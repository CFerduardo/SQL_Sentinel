# SQL-Sentinel 🛰️
**SQL-Sentinel** 
It's a proactive monitoring tool for database administrators (DBAs).
It's designed to centrally monitor the physical health of multiple **SQL Server** instances.


## 🚀 Main Features
* **Disk Monitoring:** Constant monitoring of available space on the volumes where the databases reside, alerts if available space falls below 15% (configurable).
* **Log Control:** Monitoring the growth of transaction files (`.ldf`) to prevent blockages due to lack of space.
* **Real-Time Alerts:** Instant notifications via **Telegram** with reports formatted in Markdown.
* **Local Persistence:** Historical record of events in a **SQLite** database for auditing and crash analysis.
* **Resilience:** Automatic retry system and offline server management.


## 🛠️ Technology Stack
* **Language:** Python 3.x
* **Local DB:** SQLite (History)
* **Connectivity:** `pyodbc` (SQL Server)
* **Alerts:** `python-telegram-bot` / `requests`
* **Logging:** `loguru`


## Project structure
```text
SQL-Sentinel/
├── config/
│   ├── servers.json      # List of server connections
│   └── settings.py       # Global configuration (thresholds, tokens)
├── database/
│   └── sentinel.db       # Local database for history
├── logs/
│   └── monitor.log       # Execution logs
├── src/
│   ├── database.py       # Connection logic and queries
│   ├── checks.py         # Specific queries for disks and logs
│   └── alerts.py         # Sending alerts (Telegram)
├── main.py               # Main script
├── requirements.txt      # Dependencies
└── README.md


## Requirements
- Python 3.8+
- Access to SQL Server instances (with permissions to run queries on  `sys.master_files` and `sys.dm_os_volume_stats`).
- Telegram token and chat ID for alerts.


## Installation
1. Clone the repository:
   ```bash
   git clone <url>
   cd SQL-Sentinel


## Install Dependencies
pip install -r requirements.txt


## ⚙️ Configuration

1. **Environmental Variables:** Create a `.env` file in the project root:
   ```env
   TELEGRAM_TOKEN=your_token_here
   TELEGRAM_CHAT_ID=your_chat_id_here
   
   # Credentials for the alias "SQL" in servers.json
   SQL_USER=my_user
   SQL_PASS=my_password
   
   # Credentials for the alias "SQL2"
   SQL2_USER=another_user
   SQL2_PASS=another_password


USAGE
## Run the main script
python main.py

Monitoring will start automatically and run every 5 minutes. Press Ctrl+C to stop.

Disk Monitoring
Healthy (>20%): Sufficient space for normal operations.
Warning (10%-15%): Purge logs or move files; Windows may slow down.
Critical (<5%): Risk of databases in "Suspect" or "Offline" status.
Log Monitoring
Monitored fields:

Database Name: Name of the database.

Log Size (MB): Size of the .ldf file.

Log Space Used (%): Percentage occupied by active/non-truncated transactions.

Status: Internal state (normally 0).

Almost Full (>85%): Possible long open transaction or lack of log backups.

Failing (99%-100%): Error 9002; database locked for writes. Check file size limits.

