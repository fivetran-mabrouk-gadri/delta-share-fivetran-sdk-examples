# Setup Guide

## Prerequisites

- Python 3.10–3.14
- pip
- A Fivetran account (for deployment)
- A `configuration.json` file with your Delta Sharing credentials (see below)

---

## 1. Environment Setup

### Linux

```bash
# Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install the Fivetran CLI
pip install fivetran-connector-sdk
```

### Windows

```powershell
# Create and activate a virtual environment
python -m venv .venv
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install the Fivetran CLI
pip install fivetran-connector-sdk
```

---

## 2. Configuration

Create a `configuration.json` file in the project root. All values must be strings:

```json
{
    "bearer_token": "<your_bearer_token>",
    "endpoint": "<your_delta_sharing_endpoint>",
    "share_name": "<your_share_name>",
    "schema_name": "<your_schema_name>"
}
```

Do not commit this file to source control.

---

## 3. Local Testing

The Fivetran SDK provides a `debug` mode that runs the connector locally and writes output to a local DuckDB file (`warehouse.db`).

### Run the connector

```bash
python connector.py
```

### Using the Fivetran CLI

```bash
# Run with the CLI (equivalent to the above)
fivetran debug --configuration configuration.json

# Reset state and warehouse between runs
fivetran reset
```

---

## 4. Inspecting the Output (DuckDB)

After a successful run, the SDK writes results to `warehouse.db` in the project root.

### Install DuckDB CLI

**Linux:**
```bash
curl -Lo duckdb.zip https://github.com/duckdb/duckdb/releases/latest/download/duckdb_cli-linux-amd64.zip
unzip duckdb.zip
chmod +x duckdb
sudo mv duckdb /usr/local/bin/
```

**Windows** (PowerShell):
```powershell
winget install DuckDB.cli
```

Or download the binary directly from [duckdb.org/docs/installation](https://duckdb.org/docs/installation).

### Open and query the database

```bash
duckdb warehouse.db
```

```sql
-- List all tables
SHOW TABLES;

-- Preview data
SELECT * FROM customer LIMIT 10;
SELECT * FROM district LIMIT 10;

-- Check row counts
SELECT COUNT(*) FROM customer;
SELECT COUNT(*) FROM district;
```

### Install DuckDB Python client (optional)

```bash
pip install duckdb
```

```python
import duckdb

con = duckdb.connect("warehouse.db")
print(con.execute("SHOW TABLES").fetchall())
print(con.execute("SELECT COUNT(*) FROM customer").fetchone())
```

---

## 5. Deployment to Fivetran

### 5.1 Log in to Fivetran

```bash
fivetran login
```

This opens a browser window to authenticate with your Fivetran account.

### 5.2 Deploy the connector

```bash
fivetran deploy --configuration configuration.json
```

The CLI will prompt you to select or create a destination and connector name. On success, it returns a connector ID.

### 5.3 Configure in the Fivetran dashboard

1. Go to **Fivetran Dashboard → Connectors**
2. Find your deployed connector
3. Enter the configuration values (bearer token, endpoint, share name, schema name) in the connector settings form
4. Trigger a manual sync or set a sync schedule

### 5.4 Monitor sync

Sync logs and run history are available in the Fivetran dashboard under the connector's **Logs** tab.

---

## Reference

- [Fivetran Connector SDK Docs](https://fivetran.com/docs/connector-sdk)
- [CLI Command Reference](https://fivetran.com/docs/connector-sdk/technical-reference/connector-sdk-commands)
- [Best Practices](https://fivetran.com/docs/connector-sdk/best-practices)
- [DuckDB Installation](https://duckdb.org/docs/installation)
