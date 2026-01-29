# BTC Fake - Training Completion Simulator

## High-Level Summary

BTC Fake is a training data simulator that generates realistic learning management system files by simulating:
- **Employee behavior**: Different engagement levels with training (Type A/B/F employees)
- **AI recommendations**: Integration with ML Training Recommender API for personalized suggestions
- **Manager assignments**: Realistic training assignment workflows with start/due dates
- **Vendor file formats**: Produces ContentUserCompletion and NonCompletedAssignments files in exact vendor format

This enables QA testing, development, and integration testing without production data or vendor dependencies. See [SUMMARY.md](SUMMARY.md) for complete details.

---

This project simulates real-world employees completing training courses and generates ContentUserCompletion files in the format that would normally be produced by BTC (a vendor that knows about our SFTP server and file specs).
## Project Purpose

The btc_fake project simulates employees who spend time taking training courses. The system:
- Downloads training content files from SFTP server (preprocessing)
- Reads employee population from CSV
- Manager assigns training content to all employees
- Generates NonCompletedAssignments CSV file with manager assignments
- Gets training recommendations from an external API
- Simulates training completion based on employee type
- Generates ContentUserCompletion CSV files with completion records
- Updates NonCompletedAssignments file to remove completed assignments

## Employee Types

Employees are classified by their engagement level with training. The system simulates employees completing both manager-assigned training and AI-recommended training based on their type:

- **Type A**: Completes all training (both manager-assigned and AI-recommended)
- **Type B**: Completes one training (from combined manager and AI list)
- **Type F**: Completes no training

**Note**: The `input/employees.csv` file supports comment rows. Any row where the employee_id starts with '#' will be ignored during processing. See `docs/actors/employees_file_format.md` for details.

## Project Structure

```
btc_fake/
├── input/
│   └── employees.csv          # Employee population with IDs and types
├── downloaded_files/          # Downloaded CourseCatalog files from SFTP
├── generated_files/           # Output directory for ContentUserCompletion files
├── docs/                      # Documentation and samples
├── btc_simulation.ipynb       # Main Jupyter notebook
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Jupyter Notebook support (VS Code, Cursor, or browser-based)

### Installation

1. Navigate to the project directory:
```bash
cd /Users/khansen/craft/stores/python/python-projects-rdi/btc_fake
```

2. Create a virtual environment (recommended):
```bash
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

### Environment Configuration

This project supports multiple environments (DEV, QA, PROD) with different configurations for each.

#### Quick Start

1. **Choose your environment** and copy the appropriate template:
   ```bash
   # For DEV/QA (default)
   cp .env.dev.example .env

   # For QA (alternate)
   cp .env.qa.example .env

   # For PROD
   cp .env.prod.example .env
   ```

2. **Fill in required credentials** in `.env`:
   - `DATABRICKS_TOKEN`: Personal access token from Databricks
   - `DATABRICKS_HOST`: Your Databricks workspace hostname
   - `DATABRICKS_HTTP_PATH`: SQL warehouse HTTP path
   - `SFTP_INBOUND_PASSWORD`: SFTP inbound server password

3. **Environment-specific values** (already configured in templates):
   - `API_BASE_URL`: ML Training Recommender API (**different in PROD**)
   - `DATABRICKS_CATALOG`: Catalog name (dev/qa/prod)
   - `SFTP_INBOUND_REMOTE_PATH`: Remote SFTP path (dev/qa/prod)

📖 **For detailed configuration guide**: See [docs/ENVIRONMENT_CONFIGURATION.md](docs/ENVIRONMENT_CONFIGURATION.md)

#### All Configurable Variables

**ML Training Recommender API:**
- `API_BASE_URL` - API base URL (⚠️ **PROD has `/public` in URL**)
- `API_ENDPOINT` - API endpoint path
- `API_TIMEOUT` - Request timeout in seconds

**File Paths:**
- `EMPLOYEES_FILE` - Input employees CSV file
- `OUTPUT_DIR` - Output directory for generated files
- `SFTP_LOCAL_DIR` - Local directory for downloaded files
- `USER_COMPLETION_TEMPLATE_FILE` - UserCompletion template file

**Databricks:**
- `DATABRICKS_TOKEN` - Personal access token (**required**)
- `DATABRICKS_HOST` - Workspace hostname (**required**)
- `DATABRICKS_HTTP_PATH` - SQL warehouse path (**required**)
- `DATABRICKS_CATALOG` - Catalog name (retail_systems_dev/qa/prod)
- `DATABRICKS_SCHEMA` - Schema name

**SFTP Inbound Server:**
- `SFTP_INBOUND_HOST` - Server hostname
- `SFTP_INBOUND_USER` - Username
- `SFTP_INBOUND_PASSWORD` - Password (**required**)
- `SFTP_INBOUND_REMOTE_PATH` - Remote directory path

#### Running Locally (VS Code with Databricks Extension)

1. **VS Code Databricks Extension** (Recommended):
   - Install the Databricks extension in VS Code
   - Connect to your Databricks workspace
   - Run the notebook locally while querying remote Databricks tables

**Note**: If Databricks credentials are not configured, the system will skip the Databricks query and only use newly selected manager assignments.

#### Running in Databricks

To run this notebook directly in Databricks instead of VS Code:

📖 **See comprehensive migration guide:** [docs/DATABRICKS_MIGRATION.md](docs/DATABRICKS_MIGRATION.md)

🚀 **Quick reference with code snippets:** [docs/DATABRICKS_QUICK_REFERENCE.md](docs/DATABRICKS_QUICK_REFERENCE.md)

**Key changes required:**
- Replace `.env` file with Databricks secrets (`dbutils.secrets.get()`)
- Update file paths to DBFS (`/dbfs/FileStore/btc_simulation/...`)
- Replace `databricks-sql-connector` with Spark SQL (`spark.sql()`)
- Upload input files to DBFS
- Configure cluster libraries (paramiko)

The migration guides provide complete step-by-step instructions with copy-paste code examples.

## Preprocessing

Before running the main simulation, you can download files from the SFTP server using either the notebook or the command-line script.

### Files Downloaded:

1. **CourseCatalog** - Training curriculum elements like Courses and components
2. **StandAloneContent** - All training content (videos, PDFs, documents)

**SFTP Inbound Server Configuration:**

All SFTP inbound server settings are configurable via environment variables in `.env`:
- `SFTP_INBOUND_HOST`: Server hostname (default: `sftp.sephora.com`)
- `SFTP_INBOUND_USER`: Username (default: `SephoraMSL`)
- `SFTP_INBOUND_PASSWORD`: Password (required)
- `SFTP_INBOUND_REMOTE_PATH`: Remote directory path (default: `/inbound/BTC/retailData/prod/vendor/mySephoraLearning-archive`)

**Setup:**
1. Copy `.env.example` to `.env`
2. Configure SFTP settings in `.env`:
   ```bash
   SFTP_INBOUND_HOST=sftp.sephora.com
   SFTP_INBOUND_USER=SephoraMSL
   SFTP_INBOUND_PASSWORD=your_password_here
   SFTP_INBOUND_REMOTE_PATH=/inbound/BTC/retailData/prod/vendor/mySephoraLearning-archive
   ```
3. The defaults will work for most cases - you only need to set `SFTP_INBOUND_PASSWORD`

**File Formats:**
- CourseCatalog: `CourseCatalog_V2_YYYY_M_DD_1_random.csv`
- StandAloneContent: `StandAloneContent_v2_YYYY_M_DD_1_random.csv`
- The system identifies files based on the date in the filename

### Option 1: Using the download.sh Script

Download files for a date range using the command-line script:

```bash
# Download today's files only (default)
./download.sh

# Download files from today and yesterday (2 days total)
./download.sh 1

# Download files from the last 7 days (today through 7 days ago)
./download.sh 7

# Download files from the last 31 days (today through 31 days ago)
./download.sh 31
```

**Requirements:**
- `lftp` (recommended) or `sshpass` for automated downloads
- macOS: `brew install lftp`
- Linux: `sudo apt-get install lftp`

The script will:
- Connect to the SFTP server
- Download all files matching the target date patterns
- Save files to `temp_files/` directory
- Display a summary of downloaded files

### Option 2: Using the Jupyter Notebook

The notebook (cells 4-5) will automatically download the most recent files when executed

## Running the Simulation

### Option 1: Using VS Code or Cursor

1. Open the project in VS Code or Cursor
2. Open `btc_simulation.ipynb`
3. Select your Python kernel (the virtual environment you created)
4. Run all cells in the notebook

### Option 2: Using Jupyter in Browser

1. Start Jupyter:
```bash
jupyter notebook
```

2. Navigate to `btc_simulation.ipynb` in the browser
3. Run all cells

## Output

The simulation will:

1. **Preprocessing**: Download the most recent CourseCatalog and StandAloneContent files from SFTP server to `downloaded_files/`

2. **Manager Assignments**:
   - Queries Databricks `content_assignments` AND `content_completion` tables
   - Calculates open assignments (assignments - completions) for each employee
   - Manager selects up to 3 new Daily Dose training contents (where Daily_Dose_BA = TRUE)
   - Checks for Daily Dose conflicts:
     - Skips employees who completed ANY Daily Dose this week (queries content_completion)
     - Skips employees who have open Daily Dose assignments for this week
   - Assigns Daily Dose to eligible employees only
   - Assigns 1 random non-Daily Dose content to ALL employees
   - Combines Databricks open assignments with new manager assignments
   - Generates NonCompletedAssignments CSV file (Databricks open assignments first, then new assignments)

3. **Employee Training Simulation**:
   - Read all employees from `input/employees.csv`
   - For each employee:
     - Get manager-assigned training from NonCompletedAssignments file
     - Call the training recommendation API for AI recommendations
     - Combine manager assignments with AI recommendations
     - Based on employee type, complete the appropriate number of trainings
     - Record completions with start and end timestamps

4. Generate output files in `generated_files/`:
   - **ContentUserCompletion CSV**: Records of completed training
     - Filename: `ContentUserCompletion_V2_YY_MM_DD_1_RAND.csv`
     - Headers: `"UserId","ContentId","DateStarted","DateCompleted"`
   - **NonCompletedAssignments CSV**: Manager-assigned training (created in step 2)
     - Filename: `Non_Completed_Assignments_V2_YY_MM_DD_1_RAND.csv`
     - Headers: `"UserID","CreateDate_text","RequestId","TrainingElementId","Start_Date_text","DueDate_text","ContentType"`
     - Start_Date_text: Most recent past Monday at 00:01
     - DueDate_text: Next upcoming Saturday at 13:13:59

5. Print summary:
   - Each employee's ID and completed training courses (with source: manager or AI)
   - Manager assignment details
   - Names of generated files

## API Configuration

The simulation uses the Training Recommender API:

- **Endpoint**: `/public/api/v1/mltr/v3/run`
- **Method**: POST
- **Default Environment**: https://dataiku-api-devqa.lower.internal.sephora.com
- **Production**: https://dataiku-api-prod.prod.internal.sephora.com/public

Request payload format:
```json
{"data": {"ba_id": 88563}}
```

## Example Output Files

### ContentUserCompletion File

```csv
"UserId","ContentId","DateStarted","DateCompleted"
"104829","1,915,085","2025-12-22T10:43:05Z","2025-12-22T10:47:23Z"
"151557","892,298","2025-12-22T11:15:30Z","2025-12-22T11:28:45Z"
```

### NonCompletedAssignments File

```csv
"UserID","CreateDate_text","RequestId","TrainingElementId","Start_Date_text","DueDate_text","ContentType"
"100049","2025-12-26T10:52:34Z","25661","1,561,228","2024-12-30T02:15:00Z","2025-01-06T02:00:00Z","Media"
"100049","2025-01-02T11:52:58Z","25764","39,248","2025-01-06T02:15:00Z","2025-01-13T02:00:00Z","Media"
```

## Coding Standards

This project follows coding standards from the BAPH project located one folder level up.

## Notes

- ContentId/TrainingElementId values include commas for human readability
- Dates are in ISO-8601 format
- New output files are generated each time the simulation runs:
  - ContentUserCompletion file: Records completed trainings
  - NonCompletedAssignments file: Records manager assignments (updated to remove completed assignments)
- The 6-character random suffix ensures unique filenames
- Manager assigns up to 3 training contents (with Daily_Dose_BA=TRUE) to all employees
- **NonCompletedAssignments File Behavior**:
  - Initially contains all manager assignments (from Databricks + newly created)
  - After employees complete training, the file is automatically updated
  - Completed assignments are removed from the file
  - Only truly "non-completed" assignments remain
  - If all assignments are completed, the file will contain only headers
