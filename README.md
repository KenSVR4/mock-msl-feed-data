# BTC Fake - Training Completion Simulator

This project simulates real-world employees completing training courses and generates ContentUserCompletion files in the format that would normally be produced by BTC (a vendor that knows about our SFTP server and file specs).

## Project Purpose

The btc_fake project simulates employees who spend time taking training courses. The system:
- Reads employee population from CSV
- Gets training recommendations from an external API
- Simulates training completion based on employee type
- Generates ContentUserCompletion CSV files with completion records

## Employee Types

Employees are classified by their engagement level with training:

- **Type A**: Completes every assignment immediately
- **Type B**: Completes one assignment
- **Type F**: Completes no assignments

## Project Structure

```
btc_fake/
├── actors/
│   └── employees.csv          # Employee population with IDs and types
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

1. Read all employees from `actors/employees.csv`
2. For each employee:
   - Call the training recommendation API
   - Based on employee type, complete the appropriate number of trainings
   - Record completions with start and end timestamps

3. Generate a new ContentUserCompletion CSV file in `generated_files/` with format:
   - Filename: `ContentUserCompletion_V2_YY_MM_DD_1_RAND.csv`
   - Headers: `"UserId","ContentId","DateStarted","DateCompleted"`

4. Print summary:
   - Each employee's ID and completed training courses
   - Name of the generated file

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

## Example Output File

```csv
"UserId","ContentId","DateStarted","DateCompleted"
"104829","1,915,085","2025-12-22T10:43:05Z","2025-12-22T10:47:23Z"
"151557","892,298","2025-12-22T11:15:30Z","2025-12-22T11:28:45Z"
```

## Coding Standards

This project follows coding standards from the BAPH project located one folder level up.

## Notes

- ContentId values include commas for human readability
- Dates are in ISO-8601 format
- A new output file is generated each time the simulation runs
- The 6-character random suffix ensures unique filenames
