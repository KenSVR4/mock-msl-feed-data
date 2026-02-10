# Databricks Migration - Quick Reference

Quick copy-paste code snippets for migrating the BTC simulation notebook to Databricks.

## 1. Replace Cell 1 (Configuration)

**Find and replace this entire section:**

```python
# OLD - Remove this
from dotenv import load_dotenv
load_dotenv()

EMPLOYEES_FILE = "input/employees.csv"
OUTPUT_DIR = "generated_files"
SFTP_LOCAL_DIR = "generated_files"

# SFTP Inbound Configuration
SFTP_INBOUND_HOST = os.getenv("SFTP_INBOUND_HOST", "sftp.sephora.com")
SFTP_INBOUND_USER = os.getenv("SFTP_INBOUND_USER", "SephoraMSL")
SFTP_INBOUND_PASSWORD = os.getenv("SFTP_INBOUND_PASSWORD", "")
SFTP_INBOUND_REMOTE_PATH = os.getenv("SFTP_INBOUND_REMOTE_PATH", "/inbound/BTC/retailData/prod/vendor/mySephoraLearning-archive")

# Databricks Configuration
DATABRICKS_HOST = os.getenv("DATABRICKS_HOST", "")
DATABRICKS_HTTP_PATH = os.getenv("DATABRICKS_HTTP_PATH", "")
DATABRICKS_TOKEN = os.getenv("DATABRICKS_TOKEN", "")
DATABRICKS_CATALOG = os.getenv("DATABRICKS_CATALOG", "retail_systems_dev")
DATABRICKS_SCHEMA = os.getenv("DATABRICKS_SCHEMA", "store_enablement")
```

**With this:**

```python
# NEW - Databricks version
import pandas as pd
import requests
from datetime import datetime, timedelta
import random
import string
from typing import List, Dict
import urllib3
import pytz
import os

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Pacific timezone
PT = pytz.timezone('America/Los_Angeles')

# Configuration
API_BASE_URL = "https://dataiku-api-devqa.lower.internal.sephora.com"
API_ENDPOINT = "/public/api/v1/mltr/v3/run"

# DBFS File Paths
EMPLOYEES_FILE = "/dbfs/FileStore/btc_simulation/input/employees.csv"
OUTPUT_DIR = "/dbfs/FileStore/btc_simulation/generated_files"
SFTP_LOCAL_DIR = "/dbfs/FileStore/btc_simulation/generated_files"

# SFTP Inbound Server Configuration
SFTP_INBOUND_HOST = "sftp.sephora.com"
SFTP_INBOUND_USER = "SephoraMSL"
SFTP_INBOUND_REMOTE_PATH = "/inbound/BTC/retailData/prod/vendor/mySephoraLearning-archive"

# SFTP Inbound Password (from Databricks Secrets)
try:
    SFTP_INBOUND_PASSWORD = dbutils.secrets.get(scope="btc-simulation", key="sftp-inbound-password")
    print("✓ SFTP inbound password retrieved from secrets")
except Exception as e:
    print(f"⚠ Warning: Could not retrieve SFTP inbound password from secrets: {e}")
    SFTP_INBOUND_PASSWORD = ""

# Databricks Configuration (for querying tables via Spark SQL)
DATABRICKS_CATALOG = "retail_systems_dev"
DATABRICKS_SCHEMA = "store_enablement"
```

---

## 2. Replace Cell: UserCompletion File Generation

Update the template file path:

```python
# OLD:
source_file = "docs/sample_files/UserCompletion_v2_YYYY_m_d_1_000001.csv"

# NEW:
source_file = "/dbfs/FileStore/btc_simulation/sample_files/UserCompletion_v2_YYYY_m_d_1_000001.csv"
```

---

## 3. Replace Cell: SFTP Configuration

Update SFTP variable:

```python
# OLD:
SFTP_INBOUND_PASSWORD = os.getenv("SFTP_INBOUND_PASSWORD", "your_SFTP_INBOUND_PASSWORD_placeholder")

# NEW:
# Already handled in Cell 1 configuration
# SFTP_INBOUND_PASSWORD is retrieved from dbutils.secrets
```

---

## 4. Replace Function: get_open_assignments_from_databricks()

**Replace the entire function with this Spark SQL version:**

```python
def get_open_assignments_from_databricks(employee_ids: list) -> pd.DataFrame:
    """
    Query Databricks content_assignments table using Spark SQL.

    Args:
        employee_ids: List of employee IDs (ba_id) to query assignments for

    Returns:
        Pandas DataFrame with assignment data
    """
    if not employee_ids:
        print("No employee IDs provided. Skipping assignments query.")
        return pd.DataFrame()

    try:
        # Build IN clause for employee IDs
        employee_ids_str = ", ".join([str(emp_id) for emp_id in employee_ids])

        # Query table name
        table_name = f"{DATABRICKS_CATALOG}.{DATABRICKS_SCHEMA}.content_assignments"
        print(f"Querying table: {table_name}")
        print(f"  For {len(employee_ids)} employee(s): {sorted(employee_ids)}")

        # Query using Spark SQL
        query = f"""
        SELECT
            ba_id,
            content_id,
            assignment_date,
            assignment_begin_date,
            assignment_due_date,
            content_type
        FROM {table_name}
        WHERE ba_id IN ({employee_ids_str})
        ORDER BY ba_id, assignment_due_date
        """

        # Execute query and convert to pandas
        spark_df = spark.sql(query)
        df = spark_df.toPandas()

        print(f"✓ Retrieved {len(df)} assignment(s) from Databricks")
        if len(df) > 0:
            unique_employees = df['ba_id'].nunique()
            print(f"  Assignments for {unique_employees} employee(s)")

        return df

    except Exception as e:
        print()
        print("=" * 80)
        print("ERROR: Failed to query Databricks")
        print("=" * 80)
        print()
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        print()
        print("Connection details:")
        print(f"  Catalog: {DATABRICKS_CATALOG}")
        print(f"  Schema: {DATABRICKS_SCHEMA}")
        print(f"  Table: {DATABRICKS_CATALOG}.{DATABRICKS_SCHEMA}.content_assignments")
        print()
        print("Common issues:")
        print("  1. Table does not exist")
        print("     → Verify catalog and schema names")
        print("  2. Insufficient permissions")
        print("     → Verify your account has SELECT permission on the table")
        print("  3. Unity Catalog not enabled")
        print("     → Check if Unity Catalog is configured")
        print()
        print("=" * 80)
        raise RuntimeError(f"Databricks query failed: {str(e)}") from e
```

---

## 5. Setup Commands (Run Once)

### Create DBFS Directories

Add this cell at the beginning (run once):

```python
# Create required DBFS directories
dbutils.fs.mkdirs("dbfs:/FileStore/btc_simulation/input")
dbutils.fs.mkdirs("dbfs:/FileStore/btc_simulation/generated_files")
dbutils.fs.mkdirs("dbfs:/FileStore/btc_simulation/sample_files")

print("✓ DBFS directories created")

# List directories to verify
print("\nDirectory structure:")
display(dbutils.fs.ls("dbfs:/FileStore/btc_simulation/"))
```

### Install Required Libraries

Add this cell at the very top of the notebook:

```python
%pip install paramiko
```

---

## 6. Upload Files to DBFS

### Option A: Using Databricks CLI (from your local machine)

```bash
# Upload employees file
databricks fs cp input/employees.csv dbfs:/FileStore/btc_simulation/input/employees.csv

# Upload UserCompletion template
databricks fs cp docs/sample_files/UserCompletion_v2_YYYY_m_d_1_000001.csv dbfs:/FileStore/btc_simulation/sample_files/UserCompletion_v2_YYYY_m_d_1_000001.csv
```

### Option B: Using Notebook (upload small files)

```python
# For small files, you can upload directly
import base64

# Read local file content (if accessible)
with open("input/employees.csv", "r") as f:
    content = f.read()

# Write to DBFS
dbutils.fs.put("dbfs:/FileStore/btc_simulation/input/employees.csv", content, overwrite=True)
print("✓ File uploaded to DBFS")
```

### Option C: Using Databricks UI

1. Go to **Data** → **DBFS** → **FileStore**
2. Navigate to or create `btc_simulation/input/`
3. Click **Upload** button
4. Select `employees.csv` and upload

---

## 7. Setup Databricks Secrets

### Using Databricks CLI

```bash
# Create secret scope (run once)
databricks secrets create-scope --scope btc-simulation

# Add SFTP password
databricks secrets put --scope btc-simulation --key sftp-inbound-password
# This will open an editor - paste your password, save, and exit
```

### Verify Secret Setup

In your notebook, test secret retrieval:

```python
# Test secret access
try:
    password = dbutils.secrets.get(scope="btc-simulation", key="sftp-inbound-password")
    print("✓ Secret retrieved successfully")
    print(f"  Password length: {len(password)} characters")
except Exception as e:
    print(f"✗ Failed to retrieve secret: {e}")
```

---

## 8. Optional: Add Widgets for Interactive Configuration

Add this cell near the top (after imports):

```python
# Create interactive widgets
dbutils.widgets.text("catalog", "retail_systems_dev", "Catalog")
dbutils.widgets.text("schema", "store_enablement", "Schema")
dbutils.widgets.dropdown("environment", "dev", ["dev", "qa", "prod"], "Environment")

# Get widget values
DATABRICKS_CATALOG = dbutils.widgets.get("catalog")
DATABRICKS_SCHEMA = dbutils.widgets.get("schema")
environment = dbutils.widgets.get("environment")

print(f"Configuration:")
print(f"  Catalog: {DATABRICKS_CATALOG}")
print(f"  Schema: {DATABRICKS_SCHEMA}")
print(f"  Environment: {environment}")
```

---

## 9. Testing Checklist

Run these test cells to verify setup:

### Test 1: DBFS Access

```python
# Test DBFS directory access
print("Testing DBFS access...")
try:
    files = dbutils.fs.ls("dbfs:/FileStore/btc_simulation/input/")
    print(f"✓ Found {len(files)} file(s) in input directory:")
    for file in files:
        print(f"  - {file.name}")
except Exception as e:
    print(f"✗ Failed to access DBFS: {e}")
```

### Test 2: Read Employees File

```python
# Test reading employees.csv
print("Testing employees file read...")
try:
    test_df = pd.read_csv(EMPLOYEES_FILE)
    print(f"✓ Successfully read {len(test_df)} rows")
    print(f"  Columns: {list(test_df.columns)}")
except Exception as e:
    print(f"✗ Failed to read employees file: {e}")
```

### Test 3: Database Query

```python
# Test Databricks table access
print("Testing database access...")
try:
    table_name = f"{DATABRICKS_CATALOG}.{DATABRICKS_SCHEMA}.content_assignments"
    test_query = f"SELECT COUNT(*) as count FROM {table_name}"
    result = spark.sql(test_query).toPandas()
    print(f"✓ Successfully queried table")
    print(f"  Total rows in content_assignments: {result['count'][0]:,}")
except Exception as e:
    print(f"✗ Failed to query table: {e}")
```

### Test 4: Secret Access

```python
# Test secret retrieval
print("Testing secret access...")
try:
    pwd = dbutils.secrets.get(scope="btc-simulation", key="sftp-inbound-password")
    print(f"✓ Secret retrieved successfully")
    print(f"  Length: {len(pwd)} characters")
except Exception as e:
    print(f"✗ Failed to retrieve secret: {e}")
```

---

## 10. Common Issues & Solutions

### Issue: "ModuleNotFoundError: No module named 'paramiko'"
**Solution:** Install library on cluster or use `%pip install paramiko`

### Issue: "Path does not exist: dbfs:/FileStore/btc_simulation/..."
**Solution:** Create directories using `dbutils.fs.mkdirs()` or upload files

### Issue: "KeyError: 'sftp-inbound-password'" or secret not found
**Solution:** Create secret scope and add secret using Databricks CLI or UI

### Issue: "Table or view not found: retail_systems_dev.store_enablement.content_assignments"
**Solution:** Verify catalog/schema names, check Unity Catalog is enabled, verify permissions

### Issue: SFTP connection fails
**Solution:** Check network configuration, verify firewall rules allow outbound port 22

### Issue: "NameError: name 'dbutils' is not defined"
**Solution:** You're running in VS Code, not Databricks. This code only works in Databricks environment.

---

## 11. Migration Diff Summary

| What Changes | From | To |
|-------------|------|-----|
| **Secrets** | `.env` file | `dbutils.secrets.get()` |
| **Paths** | `input/employees.csv` | `/dbfs/FileStore/btc_simulation/input/employees.csv` |
| **DB Query** | `databricks.sql.connect()` | `spark.sql()` |
| **Libraries** | Manual pip install | Cluster libraries or `%pip install` |
| **DB Connection** | External (needs HOST, TOKEN) | Internal (Spark context) |

---

## 12. Full Modified Cell 1 (Complete)

Here's the complete replacement for your first configuration cell:

```python
# ==============================================================================
# BTC FAKE - Training Completion Simulator
# Databricks Version
# ==============================================================================

# Imports
import pandas as pd
import requests
from datetime import datetime, timedelta
import random
import string
from typing import List, Dict
import urllib3
import pytz
import os

# Disable SSL warnings when ignoring certificate verification
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Define Pacific timezone globally for all timestamp operations
PT = pytz.timezone('America/Los_Angeles')

# ==============================================================================
# Configuration
# ==============================================================================

# API Configuration
API_BASE_URL = "https://dataiku-api-devqa.lower.internal.sephora.com"
API_ENDPOINT = "/public/api/v1/mltr/v3/run"

# DBFS File Paths
EMPLOYEES_FILE = "/dbfs/FileStore/btc_simulation/input/employees.csv"
OUTPUT_DIR = "/dbfs/FileStore/btc_simulation/generated_files"
SFTP_LOCAL_DIR = "/dbfs/FileStore/btc_simulation/generated_files"

# SFTP Inbound Server Configuration
SFTP_INBOUND_HOST = "sftp.sephora.com"
SFTP_INBOUND_USER = "SephoraMSL"
SFTP_INBOUND_REMOTE_PATH = "/inbound/BTC/retailData/prod/vendor/mySephoraLearning-archive"

# Databricks Configuration (for querying tables via Spark SQL)
DATABRICKS_CATALOG = "retail_systems_dev"
DATABRICKS_SCHEMA = "store_enablement"

# Retrieve SFTP Inbound Password from Databricks Secrets
try:
    SFTP_INBOUND_PASSWORD = dbutils.secrets.get(scope="btc-simulation", key="sftp-inbound-password")
    print("✓ SFTP inbound password retrieved from secrets")
except Exception as e:
    print(f"⚠ Warning: Could not retrieve SFTP inbound password: {e}")
    print("  To set up secrets, run: databricks secrets create-scope --scope btc-simulation")
    print("  Then: databricks secrets put --scope btc-simulation --key sftp-inbound-password")
    SFTP_INBOUND_PASSWORD = ""

print("\n" + "=" * 80)
print("CONFIGURATION LOADED")
print("=" * 80)
print(f"Catalog: {DATABRICKS_CATALOG}")
print(f"Schema: {DATABRICKS_SCHEMA}")
print(f"Employees File: {EMPLOYEES_FILE}")
print(f"Output Directory: {OUTPUT_DIR}")
print(f"SFTP Local Directory: {SFTP_LOCAL_DIR}")
print(f"SFTP Inbound Host: {SFTP_INBOUND_HOST}")
print(f"SFTP Inbound User: {SFTP_INBOUND_USER}")
print(f"SFTP Inbound Remote Path: {SFTP_INBOUND_REMOTE_PATH}")
print("=" * 80 + "\n")
```

This quick reference gives you everything you need to migrate the notebook to Databricks!
