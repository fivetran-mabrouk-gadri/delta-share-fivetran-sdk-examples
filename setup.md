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

## 3. Exploring the Share

Before running the connector, use `explore.py` to browse the share and verify your credentials and table structure.

### The `config.share` file

`explore.py` authenticates using a `.share` profile file — a JSON file provided by the Delta Sharing provider. It must be present locally and is **not** the same as `configuration.json`.

Format:

```json
{
    "shareCredentialsVersion": 1,
    "endpoint": "<your_delta_sharing_endpoint>",
    "bearerToken": "<your_bearer_token>",
    "expirationTime": "9999-12-31T00:00:00.000Z"
}
```

Save it as `config.share` in the project root. Do not commit it to source control.

### List all available tables

```bash
python explore.py config.share
```

Output:

```
3 table(s) available:

  my_share.my_schema.customer
  my_share.my_schema.district
```

### Inspect a table (schema + sample rows)

```bash
python explore.py config.share my_share.my_schema.district
```

### Inspect with a custom row limit

```bash
python explore.py config.share my_share.my_schema.customer --limit 25
```

This prints the column names, data types, and a sample of rows — useful for verifying the table structure before configuring `configuration.json`.

---

## 4. Local Testing

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

## 5. Inspecting the Output (DuckDB)

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

## 6. Deployment to Fivetran

### 6.1 Get your API key

In the Fivetran dashboard go to **Settings → API Config** and copy your API key and API secret. The deploy command expects them Base64-encoded in the format `{API-key}:{API-secret}`.

Encode on Linux/macOS:

```bash
echo -n "your_api_key:your_api_secret" | base64
```

Encode on Windows (PowerShell):

```powershell
[Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes("your_api_key:your_api_secret"))
```

Set it as an environment variable to avoid retyping:

```bash
export FIVETRAN_API_KEY="<base64_encoded_key>"   # Linux/macOS
```

```powershell
$env:FIVETRAN_API_KEY="<base64_encoded_key>"     # Windows
```

### 6.2 Deploy the connector

```bash
fivetran deploy --api-key <BASE64_API_KEY> --destination <DESTINATION_NAME> --connection <CONNECTION_NAME> --configuration configuration.json
```

- `--destination`: name of the destination as shown in your Fivetran dashboard
- `--connection`: name for this connection (must start with `_` or a lowercase letter, only lowercase letters, digits, and `_` allowed — no uppercase)

Example:

```bash
fivetran deploy --api-key dlkh34o8== --destination MyWarehouse --connection delta_share_connector --configuration configuration.json
```

To redeploy after code changes, run the same command again with the same connection and destination names.

### 6.3 Start syncing

New connections are **paused by default**. Unpause using one of:

- **Dashboard**: go to **Connections**, select your connector, then click **Start Initial Sync** or toggle to Enabled
- **Terminal link**: click the URL printed in the deploy output
- **REST API**: use the connection ID printed in the deploy log to call the "Update a Connection" endpoint

### 6.4 Monitor sync

Sync logs and run history are available in the Fivetran dashboard under the connector's **Logs** tab.

---

## Reference

- [Fivetran Connector SDK Docs](https://fivetran.com/docs/connector-sdk)
- [CLI Command Reference](https://fivetran.com/docs/connector-sdk/technical-reference/connector-sdk-commands)
- [Best Practices](https://fivetran.com/docs/connector-sdk/best-practices)
- [DuckDB Installation](https://duckdb.org/docs/installation)
