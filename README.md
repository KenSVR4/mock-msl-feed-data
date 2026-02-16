# BTC Fake - MSL Training Completion Simulator


## High-Level Summary

### In a Nutshell
Run the code here to produce a set of files like the files that the BTC vendor
produces every day for our Production users. Then use the files as input to the
DEV or QA version of the MSL daily batch job.

There is an input file (employees.csv) with the IDs of the employees. 
- Each employee will be assigned three daily doses - unless databricks tables show that in the  current week they already have doses assigned. 
- Each employee will have course completion records if in the input file the employee is type a (completes all assignments) or type b (completes only one assignment).


### Overview

BTC Fake is a training data simulator that generates realistic but small BTC files by simulating:
- **Employee behavior**: Different engagement levels with training (Type A/B/F employees)
- **AI recommendations**: Integration with ML Training Recommender API 
- **Manager assignments**: Dose and other ssignment workflows with start/due dates
- **Vendor file formats**: Produces ContentUserCompletion and NonCompletedAssignments files in exact vendor format

This enables QA testing, development, and integration testing without production data or vendor dependencies. See [SUMMARY.md](SUMMARY.md) for complete details.

---

## 🌐 Two Ways to Run

**Option 1: Web Interface (Gradio)** - Browser-based UI for non-technical users
```bash
python app.py
# Open http://localhost:7860
```

**Option 2: Jupyter Notebook** - Code-based workflow for developers
```bash
# Open btc_simulation.ipynb in VS Code or Jupyter
```

📖 **Gradio Setup Guide**: See [GRADIO_SETUP.md](GRADIO_SETUP.md) for complete web interface documentation

---

## How is Works

The project:
- Downloads training content files from SFTP server (preprocessing)
- Reads employee population from input CSV
- Emulates a Manager who assigns training content to all employees
- Generates NonCompletedAssignments CSV file with manager assignments
- Gets training recommendations from ML Recommendation API
- Emulates training completion was done; based on employee type
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
├── generated_files/           # Output directory for generated and downloaded files
├── docs/                      # Documentation and samples
├── app.py                     # Gradio web application
├── btc_simulation.ipynb       # Jupyter notebook (alternative)
├── requirements.txt           # Python dependencies (includes Gradio)
├── GRADIO_SETUP.md            # Web interface documentation
└── README.md                  # This file
```

---

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- (If not using Gradio web option) Jupyter Notebook support (VS Code, Cursor, or browser-based)

### Installation

1. Navigate to the project directory

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

   ```

2. **Fill in required credentials** in `.env`:
   - `DATABRICKS_TOKEN`: Personal access token from Databricks
   - `DATABRICKS_HOST`: Your Databricks workspace hostname
   - `DATABRICKS_HTTP_PATH`: SQL warehouse HTTP path
   - `SFTP_INBOUND_PASSWORD`: SFTP inbound server password

3. **Environment-specific values** (already configured in templates):
   - `API_BASE_URL`: ML Training Recommender API (**different from PROD**)
   - `DATABRICKS_CATALOG`: Catalog name (dev/qa/prod)
   - `SFTP_INBOUND_REMOTE_PATH`: Remote SFTP path (dev/qa/prod)

📖 **For detailed configuration guide**: See [docs/ENVIRONMENT_CONFIGURATION.md](docs/ENVIRONMENT_CONFIGURATION.md)

#### All Configurable Variables

**ML Training Recommender API:**
- `API_BASE_URL` - API base URL
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

**SFTP Outbound Server (Publishing):**
- `SFTP_OUTBOUND_HOST` - Server hostname
- `SFTP_OUTBOUND_USER` - Username
- `SFTP_OUTBOUND_PASSWORD` - Password (**required**)
- `SFTP_OUTBOUND_REMOTE_PATH` - Remote directory path
- `SFTP_PUBLISH_ENABLED` - Enable/disable publishing (true/false)

#### Running Locally (VS Code with Databricks Extension)

1. **VS Code Databricks Extension** (Recommended):
   - Install the Databricks extension in VS Code
   - Connect to your Databricks workspace
   - Run the notebook locally while querying remote Databricks tables

**Note**: If Databricks credentials are not configured, the system will skip the Databricks query and only use newly selected manager assignments.

---

## Preprocessing

Code does some processing up front:

### Files Downloaded:

1. **CourseCatalog** - Training curriculum elements like Courses and components
2. **StandAloneContent** - Training content (videos, PDFs, documents)

**SFTP Inbound Server Configuration:**

All SFTP inbound server settings are configurable via environment variables in `.env`:
- `SFTP_INBOUND_HOST`: Server hostname (default: `sftp.sephora.com`)
- `SFTP_INBOUND_USER`: Username (default: `SephoraMSL`)
- `SFTP_INBOUND_PASSWORD`: Password (required)
- `SFTP_INBOUND_REMOTE_PATH`: Remote directory path (default: `/inbound/BTC/retailData/prod/vendor/mySephoraLearning-archive`)

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

---

## Output

The simulation will:

1. **Preprocessing**: Download the most recent CourseCatalog and StandAloneContent files from SFTP server to `generated_files/`

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

6. **Postprocessing - Publish Files** (Optional):
   - Uploads generated files AND downloaded files to SFTP outbound server
   - Only runs if `SFTP_PUBLISH_ENABLED=true` in `.env`
   - Can be bypassed by setting `SFTP_PUBLISH_ENABLED=false`
   - Files published:
     - Generated: ContentUserCompletion CSV, NonCompletedAssignments CSV, UserCompletion CSV
     - Downloaded: CourseCatalog CSV, StandAloneContent CSV
   - Server configured via environment variables (SFTP_OUTBOUND_*)

---

## Postprocessing - Publishing Files (optional)

After successfully generating output files, the process can optionally publish them to an SFTP outbound server. This step can be enabled or bypassed using a runtime flag.


### Files Published

When publishing is enabled, the following files are uploaded to the SFTP outbound server:

**Generated Files:**
1. **ContentUserCompletion CSV** - Completed training records
2. **NonCompletedAssignments CSV** - Open/incomplete assignments
3. **UserCompletion CSV** - Dummy file required by vendor format

**Downloaded Files (from preprocessing):**
4. **CourseCatalog CSV** - Training curriculum downloaded from SFTP inbound
5. **StandAloneContent CSV** - Training content catalog downloaded from SFTP inbound

The files are uploaded to the remote path specified in `SFTP_OUTBOUND_REMOTE_PATH`.

---

## API Configuration

The simulation uses the ML Training Recommender API for each input employee ID
---

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

---

## Features Roadmap

Future enhancements planned:

- [ ] Databricks query results preview
- [ ] Simulation history/logs
- [ ] CSV validation before simulation
- [ ] Moving the solution into Databricks and scheduling it regularly in QA, Dev
