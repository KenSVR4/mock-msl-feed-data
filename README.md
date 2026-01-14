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
- Gets training recommendations from an external API
- Simulates training completion based on employee type
- Generates ContentUserCompletion CSV files with completion records
- Manager assigns training content to all employees
- Generates NonCompletedAssignments CSV file with manager assignments

## Employee Types

Employees are classified by their engagement level with training. The system simulates employees completing both manager-assigned training and AI-recommended training based on their type:

- **Type A**: Completes all training (both manager-assigned and AI-recommended)
- **Type B**: Completes one training (from combined manager and AI list)
- **Type F**: Completes no training

**Note**: The `input/employees.csv` file supports comment rows. Any row where the employee_id starts with '#' will be ignored during processing. See `docs/input/employees_file_format.md` for details.

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

## Preprocessing

Before running the main simulation, you can download files from the SFTP server using either the notebook or the command-line script.

### Files Downloaded:

1. **CourseCatalog** - Training curriculum elements like Courses and components
2. **StandAloneContent** - All training content (videos, PDFs, documents)

**SFTP Configuration:**
- Host: `sftp.sephora.com`
- Remote Path: `/inbound/BTC/retailData/prod/vendor/mySephoraLearning-archive`
- User: `SephoraMSL`
- Password: Stored in `.env` file

**Setup:**
1. Copy `.env.example` to `.env`
2. Add your SFTP password: `SFTP_PASSWORD=your_password_here`

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
   - Manager selects up to 3 training contents (where Daily_Dose_BA = TRUE)
   - Assigns these contents to all employees
   - Generates NonCompletedAssignments CSV file

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
  - NonCompletedAssignments file: Records manager assignments
- The 6-character random suffix ensures unique filenames
- Manager assigns up to 3 training contents (with Daily_Dose_BA=TRUE) to all employees
