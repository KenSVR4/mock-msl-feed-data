# Gradio Web Application - Setup Guide

## Overview

The BTC Fake project now includes a **web-based interface** using Gradio. Instead of running Jupyter notebooks, you can use a browser-based UI to:

- Upload employee CSV files
- Configure simulation parameters
- Run simulations with real-time progress
- and then Download generated files
- As a bonus you can Test ML API connections
- And View current configuration

---

## Quick Start

### 1. Install Dependencies

First, ensure Gradio is installed:

```bash
pip install -r requirements.txt
```

This will install `gradio>=4.0.0` along with all other dependencies.

### 2. Configure Environment

Make sure your `.env` file is properly configured:

```bash
# Copy example if you don't have .env yet
cp .env.example .env

# Edit .env with your credentials
nano .env
```

**Required settings:**
Values for the following must be input into the .env file
- `DATABRICKS_TOKEN` - Personal access token
- `DATABRICKS_HOST` - Databricks workspace hostname
- `DATABRICKS_HTTP_PATH` - SQL warehouse path
- `SFTP_INBOUND_PASSWORD` - SFTP inbound password
- `SFTP_OUTBOUND_PASSWORD` - SFTP outbound password (if publishing)

### 3. Launch the Application

```bash
python app.py
```

You'll see output like:

```
Running on local URL:  http://0.0.0.0:7860

To create a public link, set `share=True` in `launch()`.
```

### 4. Open in Browser

Open your browser and navigate to that link:

```
http://localhost:7860
```

---

## Using the Web Interface

### Tab: Run Simulation

This is the main interface for running simulations.

**Steps:**

1. **Upload Employees CSV**
   - Click "Upload Employees CSV"
   - Select your employee file (example is in `input/employees.csv`)
   - File must have columns: `employee_id`, `employee_edu_type`

2. **Set Parameters**
   - **Enable SFTP Publishing**: Check to upload files to SFTP outbound

3. **Run Simulation**
   - Click "🚀 Run Simulation"
   - Watch progress updates in real-time
   - View summary when complete

4. **Download Results**
   - Click "Download Generated Files (ZIP)"
   - Contains all generated files plus downloaded SFTP files

**Example Summary Output:**

```
================================================================================
BTC FAKE - TRAINING COMPLETION SIMULATOR
================================================================================

STEP 0: Cleanup
--------------------------------------------------------------------------------
Cleaned generated_files/ - removed 5 file(s)

STEP 1: Loading Employee Data
--------------------------------------------------------------------------------
Filtered out 1 comment row(s)
Loaded 3 employee(s)

STEP 2: Downloading Files from SFTP
--------------------------------------------------------------------------------
Connecting to SFTP server: sftp.sephora.com
Connected. Listing files in: /inbound/BTC/retailData/prod/vendor/mySephoraLearning-archive
Downloading: CourseCatalog_V2_2026_2_14_1_f802de.csv (date: 2026-02-14)
Downloaded to: generated_files/CourseCatalog_V2_2026_2_14_1_f802de.csv
Connecting to SFTP server: sftp.sephora.com
Connected. Listing files in: /inbound/BTC/retailData/prod/vendor/mySephoraLearning-archive
Downloading: StandAloneContent_v2_2026_2_14_1_d3850f.csv (date: 2026-02-14)
Downloaded to: generated_files/StandAloneContent_v2_2026_2_14_1_d3850f.csv
Downloaded course catalog: CourseCatalog_V2_2026_2_14_1_f802de.csv
Downloaded standalone content: StandAloneContent_v2_2026_2_14_1_d3850f.csv

STEP 3: Creating Manager Assignments
--------------------------------------------------------------------------------
Connecting to Databricks: adb-8437939873721563.3.azuredatabricks.net
Querying 3 employee(s) for open assignments
Retrieved 146 open assignment(s) from Databricks
Loaded 146 open assignments from Databricks
Created 9 new manager assignments
Total assignments: 155
Generated: Non_Completed_Assignments_V2_2026_2_14_1_163128.csv

STEP 4: Simulating Employee Training Completions
--------------------------------------------------------------------------------
Processing employee 109828999 (type a)...
Calling ML Reco API for employee 109828999...
  no ML recommendations returned
  Completed 3 training(s)
Processing employee 319994 (type f)...
Calling ML Reco API for employee 319994...
  no ML recommendations returned
Processing employee 13 (type a)...
Calling ML Reco API for employee 13...
  no ML recommendations returned
  Completed 3 training(s)
Total completions: 6

STEP 5: Generating Output Files
--------------------------------------------------------------------------------
Generated: ContentUserCompletion_V2_2026_02_14_1_163138.csv
Updated NonCompletedAssignments: removed 6 completed assignments
Generated: UserCompletion_v2_2026_2_14_1_163138.csv

Creating download package...

================================================================================
SIMULATION COMPLETE
================================================================================
```

### Tab 2: Test ML Reco API

Test connectivity to ML Training Recommender API.

**Steps:**

1. Enter an employee ID (e.g., `88563`)
2. Click "🧪 Test API Connection"
3. View API response and recommendations

**Example Success:**

```
✓ API Success!

Recommendations for employee 88563:
  - 1915085
  - 892298
  - 1561228
```

**Example Error:**

```
✗ API Error: Connection timeout
```

### Tab 3: Configuration

View current configuration loaded from `.env` file.

Shows all settings:
- API configuration
- Databricks connection
- SFTP servers
- File paths

---

## Deployment Options

### Local Development

Best for: Personal use, development

```bash
python app.py
# Access at http://localhost:7860
```

---

## Troubleshooting

### Issue: Module Not Found

**Error**: `ModuleNotFoundError: No module named 'gradio'`

**Solution**:

```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: API Connection Timeout

**Error**: API calls fail in "Test ML Reco API" tab

**Solution**:

- Connect to VPN
- Verify `.env` has correct `API_BASE_URL`
- Check network connectivity
- Test API endpoint manually with curl:

```bash
curl -X POST https://dataiku-api-devqa.lower.internal.sephora.com/public/api/v1/mltr/v3/run \
  -H "Content-Type: application/json" \
  -d '{"data": {"ba_id": 88563}}'
```

---

## Summary

The Gradio web interface provides an easy-to-use alternative to Jupyter notebooks:

**To get started:**

```bash
pip install -r requirements.txt
python app.py
# Open http://localhost:7860
```

Enjoy the web interface!
