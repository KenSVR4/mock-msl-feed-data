# Migrating BTC Simulation Notebook to Databricks

This document outlines the changes required to run `btc_simulation.ipynb` in a Databricks environment.

## Overview of Required Changes

1. **Environment Variables & Secrets Management**
2. **File Paths (DBFS instead of local filesystem)**
3. **Databricks Query Approach**
4. **Library Installation**
5. **SFTP Access**
6. **Display & Output**

---

## 1. Environment Variables & Secrets Management

### Current Approach (VS Code)
```python
from dotenv import load_dotenv
import os

load_dotenv()
SFTP_INBOUND_HOST = os.getenv("SFTP_INBOUND_HOST", "sftp.sephora.com")
SFTP_INBOUND_USER = os.getenv("SFTP_INBOUND_USER", "SephoraMSL")
SFTP_INBOUND_PASSWORD = os.getenv("SFTP_INBOUND_PASSWORD", "")
SFTP_INBOUND_REMOTE_PATH = os.getenv("SFTP_INBOUND_REMOTE_PATH", "/inbound/BTC/retailData/prod/vendor/mySephoraLearning-archive")
DATABRICKS_HOST = os.getenv("DATABRICKS_HOST", "")
DATABRICKS_HTTP_PATH = os.getenv("DATABRICKS_HTTP_PATH", "")
DATABRICKS_TOKEN = os.getenv("DATABRICKS_TOKEN", "")
```

### Databricks Approach
Replace with Databricks secrets and configuration:

```python
# Remove dotenv import and load_dotenv()

# SFTP Inbound Configuration - use secrets and defaults
SFTP_INBOUND_HOST = "sftp.sephora.com"  # Or use dbutils.widgets for configurability
SFTP_INBOUND_USER = "SephoraMSL"
SFTP_INBOUND_PASSWORD = dbutils.secrets.get(scope="btc-simulation", key="sftp-inbound-password")
SFTP_INBOUND_REMOTE_PATH = "/inbound/BTC/retailData/prod/vendor/mySephoraLearning-archive"

# Databricks connection - not needed in Databricks environment
DATABRICKS_HOST = ""  # Not needed - you're already in Databricks
DATABRICKS_HTTP_PATH = ""  # Not needed
DATABRICKS_TOKEN = ""  # Not needed
```

### Setup Databricks Secrets
Run these commands in Databricks CLI or notebook:

```bash
# Create secret scope (one time)
databricks secrets create-scope --scope btc-simulation

# Add secrets
databricks secrets put --scope btc-simulation --key sftp-inbound-password
```

Or use the Databricks UI: Workspace → Settings → Secrets

---

## 2. File Paths - DBFS Migration

### Current Approach (VS Code)
```python
EMPLOYEES_FILE = "input/employees.csv"
OUTPUT_DIR = "generated_files"
SFTP_LOCAL_DIR = "generated_files"
```

### Databricks Approach
Use DBFS paths:

```python
# DBFS paths (accessible via /dbfs/ prefix)
EMPLOYEES_FILE = "/dbfs/FileStore/btc_simulation/input/employees.csv"
OUTPUT_DIR = "/dbfs/FileStore/btc_simulation/generated_files"
SFTP_LOCAL_DIR = "/dbfs/FileStore/btc_simulation/generated_files"

# Alternative: Use dbfs:// protocol (for dbutils operations)
# EMPLOYEES_FILE = "dbfs:/FileStore/btc_simulation/input/employees.csv"
```

### File Upload to DBFS

Upload your input files:

**Option 1: Databricks UI**
1. Go to Data → DBFS → FileStore
2. Create folder: `btc_simulation/input`
3. Upload `employees.csv`

**Option 2: Databricks CLI**
```bash
databricks fs cp input/employees.csv dbfs:/FileStore/btc_simulation/input/employees.csv
databricks fs cp docs/sample_files/UserCompletion_v2_YYYY_m_d_1_000001.csv dbfs:/FileStore/btc_simulation/sample_files/
```

**Option 3: Within Notebook**
```python
# Create directories
dbutils.fs.mkdirs("dbfs:/FileStore/btc_simulation/input")
dbutils.fs.mkdirs("dbfs:/FileStore/btc_simulation/generated_files")
```

### Update File Template Path
```python
# OLD:
source_file = "docs/sample_files/UserCompletion_v2_YYYY_m_d_1_000001.csv"

# NEW:
source_file = "/dbfs/FileStore/btc_simulation/sample_files/UserCompletion_v2_YYYY_m_d_1_000001.csv"
```

---

## 3. Databricks Query Approach

### Current Approach (VS Code)
Uses `databricks-sql-connector` to query Databricks from external client.

### Databricks Approach
**Remove** the entire `get_open_assignments_from_databricks()` function and replace with Spark SQL:

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

    # Build IN clause for employee IDs
    employee_ids_str = ", ".join([str(emp_id) for emp_id in employee_ids])

    # Use catalog and schema from configuration
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
```

**Update Configuration:**
```python
# Keep catalog and schema configuration, remove connection details
DATABRICKS_CATALOG = "retail_systems_dev"  # Or use dbutils.widgets
DATABRICKS_SCHEMA = "store_enablement"     # Or use dbutils.widgets

# Remove these (not needed in Databricks):
# DATABRICKS_HOST = os.getenv("DATABRICKS_HOST", "")
# DATABRICKS_HTTP_PATH = os.getenv("DATABRICKS_HTTP_PATH", "")
# DATABRICKS_TOKEN = os.getenv("DATABRICKS_TOKEN", "")
```

---

## 4. Library Installation

### Current Approach (VS Code)
Uses `requirements.txt` with pip install.

### Databricks Approach

**Option 1: Cluster Libraries (Recommended for production)**
1. Go to Cluster → Libraries → Install New
2. Install PyPI packages:
   - `paramiko` (for SFTP)
   - `python-dotenv` (optional, only if keeping dotenv approach)
   - `requests` (usually pre-installed)
   - `pandas` (usually pre-installed)
   - `pytz` (usually pre-installed)

**Option 2: Notebook-scoped Install**
Add this cell at the top of your notebook:

```python
%pip install paramiko
```

**Remove this package (not needed in Databricks):**
- `databricks-sql-connector` - replaced by Spark SQL

---

## 5. SFTP Access Considerations

### Network Access
Databricks clusters may have network restrictions. Ensure:

1. **VPC/Network Configuration**: SFTP server (`sftp.sephora.com`) is accessible from Databricks VPC
2. **Firewall Rules**: Allow outbound connections on port 22
3. **Network Security Group**: Configure if using Azure Databricks

### Alternative Approach: Pre-download Files
If SFTP access is restricted, download files externally and upload to DBFS:

```python
# Instead of downloading from SFTP, read from DBFS
course_catalog_path = "/dbfs/FileStore/btc_simulation/generated_files/CourseCatalog_V2_2026_1_20_1_65ccb9.csv"
standalone_content_path = "/dbfs/FileStore/btc_simulation/generated_files/StandAloneContent_v2_2026_1_20_1_acbffc.csv"
```

---

## 6. Display & Output

### Enhanced Display
Replace pandas print statements with Databricks `display()`:

```python
# OLD:
print(f"Loaded {len(employees_df)} employees")

# ENHANCED:
print(f"Loaded {len(employees_df)} employees")
display(employees_df)  # Shows interactive table in Databricks
```

### Download Output Files
To download generated CSV files from DBFS to local machine:

**Option 1: Databricks UI**
1. Navigate to Data → DBFS → FileStore → btc_simulation → generated_files
2. Click on file → Download

**Option 2: Databricks CLI**
```bash
databricks fs cp dbfs:/FileStore/btc_simulation/generated_files/ContentUserCompletion_V2_2026_01_20_1_171420.csv ./local_path/
```

---

## 7. Complete Migration Checklist

### Cell 1: Imports and Configuration
- [ ] Remove `from dotenv import load_dotenv` and `load_dotenv()`
- [ ] Update file paths to DBFS paths
- [ ] Remove Databricks connection config (HOST, HTTP_PATH, TOKEN)
- [ ] Add secrets retrieval using `dbutils.secrets.get()`

### Cell 2: File Cleanup
- [ ] Update `OUTPUT_DIR` and `SFTP_LOCAL_DIR` to DBFS paths
- [ ] Test directory cleanup works with DBFS

### Cell 3: UserCompletion Generation
- [ ] Update template file path to DBFS location
- [ ] Update destination path to DBFS

### Cell 4: SFTP Download
- [ ] Verify network access to SFTP server
- [ ] OR skip this cell and pre-upload files to DBFS

### Cell 5: Databricks Query
- [ ] Replace `get_open_assignments_from_databricks()` with Spark SQL version
- [ ] Remove `databricks-sql-connector` import
- [ ] Test query execution

### Cell 6: Manager Assignment Cell
- [ ] Verify file paths work correctly
- [ ] Check CSV writing to DBFS

### Cell 7: Employee Processing Cell
- [ ] Update assignments_path usage
- [ ] Verify API calls work (network egress allowed)

### Cell 8: Output Generation
- [ ] Verify CSV output to DBFS
- [ ] Test file accessibility

---

## 8. Testing Migration

### Test in Stages

**Stage 1: Basic Setup**
```python
# Test DBFS access
dbutils.fs.ls("dbfs:/FileStore/btc_simulation/")

# Test secrets
print("SFTP password retrieved:", "✓" if SFTP_INBOUND_PASSWORD else "✗")
```

**Stage 2: File Operations**
```python
# Test reading employees file
test_df = pd.read_csv(EMPLOYEES_FILE)
print(f"Read {len(test_df)} rows from employees file")
```

**Stage 3: Database Query**
```python
# Test Spark SQL query
test_query = f"SELECT COUNT(*) as count FROM {DATABRICKS_CATALOG}.{DATABRICKS_SCHEMA}.content_assignments"
result = spark.sql(test_query).toPandas()
print(f"Total assignments in table: {result['count'][0]}")
```

---

## 9. Recommended Databricks Cluster Configuration

### Cluster Settings
- **Runtime**: 13.3 LTS or higher (includes Python 3.10+)
- **Node Type**: Standard_DS3_v2 or similar (for development)
- **Workers**: 2-4 workers (can scale based on data volume)
- **Libraries**:
  - `paramiko` (PyPI)

### Cluster Policies
Ensure cluster has:
- Outbound internet access (for API calls)
- Access to SFTP server network
- Access to required catalogs/schemas

---

## 10. Optional: Use Databricks Widgets for Configuration

Add interactive widgets for parameters:

```python
# Create widgets
dbutils.widgets.text("catalog", "retail_systems_dev", "Databricks Catalog")
dbutils.widgets.text("schema", "store_enablement", "Databricks Schema")
dbutils.widgets.dropdown("employee_file", "test", ["test", "production"], "Employee Dataset")

# Get widget values
DATABRICKS_CATALOG = dbutils.widgets.get("catalog")
DATABRICKS_SCHEMA = dbutils.widgets.get("schema")
employee_dataset = dbutils.widgets.get("employee_file")

if employee_dataset == "production":
    EMPLOYEES_FILE = "/dbfs/FileStore/btc_simulation/input/employees_prod.csv"
else:
    EMPLOYEES_FILE = "/dbfs/FileStore/btc_simulation/input/employees_test.csv"
```

---

## Summary of Key Changes

| Component | VS Code (Local) | Databricks |
|-----------|----------------|------------|
| **Secrets** | `.env` file with `python-dotenv` | `dbutils.secrets.get()` |
| **File Paths** | Relative paths (`input/`, `generated_files/`) | DBFS paths (`/dbfs/FileStore/btc_simulation/...`) |
| **DB Queries** | `databricks-sql-connector` | Spark SQL (`spark.sql()`) |
| **Libraries** | `pip install -r requirements.txt` | Cluster libraries or `%pip install` |
| **SFTP** | Direct access | May need network config or pre-upload |
| **Display** | `print()` statements | `display()` for DataFrames |

---

## Next Steps

1. Set up Databricks secrets for SFTP password
2. Upload input files to DBFS
3. Create DBFS directories for outputs
4. Install required libraries on cluster
5. Update notebook cells according to this guide
6. Test each section incrementally
7. Validate output files in DBFS
