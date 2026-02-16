"""
BTC Fake - Training Completion Simulator Core Module

This module contains the shared business logic for simulating training completions.
It is used by both the Gradio web application (app.py) and the Jupyter notebook (btc_simulation.ipynb).
"""

import os
import pandas as pd
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import urllib3
import pytz
import paramiko
import re
import glob
import shutil
import random

# Disable SSL warnings when ignoring certificate verification
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Define timezones globally
PT = pytz.timezone('America/Los_Angeles')
UTC = pytz.UTC


# =============================================================================
# CONFIGURATION
# =============================================================================

def load_config() -> Dict:
    """
    Load configuration from environment variables.

    Returns:
        Dictionary containing all configuration values
    """
    return {
        # ML Training Recommender API
        'api_base_url': os.getenv("API_BASE_URL", "https://dataiku-api-devqa.lower.internal.sephora.com"),
        'api_endpoint': os.getenv("API_ENDPOINT", "/public/api/v1/mltr/v3/run"),
        'api_timeout': int(os.getenv("API_TIMEOUT", "30")),

        # File Paths
        'employees_file': os.getenv("EMPLOYEES_FILE", "input/employees.csv"),
        'output_dir': os.getenv("OUTPUT_DIR", "generated_files"),
        'sftp_local_dir': os.getenv("SFTP_LOCAL_DIR", "generated_files"),
        'user_completion_template_file': os.getenv("USER_COMPLETION_TEMPLATE_FILE",
                                                   "docs/sample_files/UserCompletion_v2_YYYY_m_d_1_000001.csv"),

        # Databricks
        'databricks_host': os.getenv("DATABRICKS_HOST", ""),
        'databricks_http_path': os.getenv("DATABRICKS_HTTP_PATH", ""),
        'databricks_token': os.getenv("DATABRICKS_TOKEN", ""),
        'databricks_catalog': os.getenv("DATABRICKS_CATALOG", "retail_systems_dev"),
        'databricks_schema': os.getenv("DATABRICKS_SCHEMA", "store_enablement"),

        # SFTP Inbound Server
        'sftp_inbound_host': os.getenv("SFTP_INBOUND_HOST", "sftp.sephora.com"),
        'sftp_inbound_user': os.getenv("SFTP_INBOUND_USER", "SephoraMSL"),
        'sftp_inbound_password': os.getenv("SFTP_INBOUND_PASSWORD", ""),
        'sftp_inbound_remote_path': os.getenv("SFTP_INBOUND_REMOTE_PATH",
                                             "/inbound/BTC/retailData/prod/vendor/mySephoraLearning-archive"),

        # SFTP Outbound Server (Publishing)
        'sftp_outbound_host': os.getenv("SFTP_OUTBOUND_HOST", "internal-sftp.sephoraus.com"),
        'sftp_outbound_user': os.getenv("SFTP_OUTBOUND_USER", "SephoraRDIInternal"),
        'sftp_outbound_password': os.getenv("SFTP_OUTBOUND_PASSWORD", ""),
        'sftp_outbound_remote_path': os.getenv("SFTP_OUTBOUND_REMOTE_PATH",
                                              "/inbound/BTC/retailData/prod/vendor/mySephoraLearningV2"),
        'sftp_publish_enabled': os.getenv("SFTP_PUBLISH_ENABLED", "true").lower() in ['true', '1', 'yes']
    }


# =============================================================================
# CONTENT DEFINITIONS
# =============================================================================

# Sample Daily Dose content IDs and names
DAILY_DOSE_CONTENT = [
    {'id': '2033875', 'name': "What's Hot For February"},
    {'id': '2030735', 'name': "January Training Product"}
]

# Sample non-Daily Dose content IDs and names for random assignment
NON_DAILY_DOSE_CONTENT = [
    {'id': '2021630', 'name': "What's Hot For January"},
    {'id': '1670279', 'name': "3CX - How to Use the Language Services Line"},
    {'id': '1670278', 'name': "3CX - How to Transfer to the Escalation Line"},
    {'id': '2020001', 'name': "Lead NCR IR Process"},
    {'id': '2033002', 'name': "Nécessaire: Rosemary Mask"},
    {'id': '1915085', 'name': "Beauty Insider Community Overview"},
    {'id': '892298', 'name': "Client Service Excellence Training"},
    {'id': '1561228', 'name': "Product Knowledge: Skincare Basics"}
]

# Create content name lookup dictionary (ID without commas -> name)
CONTENT_NAME_LOOKUP = {}
for content in DAILY_DOSE_CONTENT + NON_DAILY_DOSE_CONTENT:
    CONTENT_NAME_LOOKUP[content['id']] = content['name']


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def format_content_id(content_id: int) -> str:
    """
    Format content ID with commas for human readability.
    Example: 1915085 -> "1,915,085"

    Args:
        content_id: The numeric content ID

    Returns:
        Formatted string with commas
    """
    return f"{content_id:,}"


def get_sunday_of_current_week() -> datetime:
    """
    Get most recent Monday (current or past) at 01:15:00 UTC.

    NOTE: Function name says Sunday but returns Monday for assignment start dates.
    This matches the assignment date logic.

    Returns:
        datetime object for most recent Monday at 01:15:00 UTC
    """
    now = datetime.now(UTC)
    current_weekday = now.weekday()  # Monday is 0

    if current_weekday == 0:
        monday = now
    else:
        days_since_monday = current_weekday
        monday = now - timedelta(days=days_since_monday)

    monday = monday.replace(hour=1, minute=15, second=0, microsecond=0)
    return monday


def get_next_future_sunday() -> datetime:
    """
    Get next Monday (7 days after start Monday) at 01:03:00 UTC.

    NOTE: Function name says Sunday but returns next Monday for assignment due dates.
    This matches the assignment date logic.

    Returns:
        datetime object for next Monday at 01:03:00 UTC
    """
    start_monday = get_sunday_of_current_week()
    next_monday = start_monday + timedelta(days=7)
    next_monday = next_monday.replace(hour=1, minute=3, second=0, microsecond=0)
    return next_monday


def generate_request_id() -> str:
    """
    Generate RequestId in format: fake:DD
    Example: fake:14 (for the 14th day of the month)
    Uses PT timezone for date component.

    Returns:
        RequestId string
    """
    now = datetime.now(PT)
    day = now.strftime("%d")
    return f"fake:{day}"


def generate_non_completed_assignments_filename() -> str:
    """
    Generate NonCompletedAssignments filename with timestamp.
    Format: Non_Completed_Assignments_V2_YYYY_M_DD_1_HHMMSS.csv
    Uses PT timezone for date and time components.

    Returns:
        Generated filename
    """
    now = datetime.now(PT)
    year = now.strftime("%Y")
    month = now.strftime("%-m")
    day = now.strftime("%-d")
    time_suffix = now.strftime("%H%M%S")
    return f"Non_Completed_Assignments_V2_{year}_{month}_{day}_1_{time_suffix}.csv"


def generate_output_filename() -> str:
    """
    Generate ContentUserCompletion filename with timestamp.
    Format: ContentUserCompletion_V2_YYYY_MM_DD_1_HHMMSS.csv
    Uses PT timezone for date and time components.

    Returns:
        Generated filename
    """
    now = datetime.now(PT)
    year = now.strftime("%Y")
    month = now.strftime("%m")
    day = now.strftime("%d")
    time_suffix = now.strftime("%H%M%S")
    return f"ContentUserCompletion_V2_{year}_{month}_{day}_1_{time_suffix}.csv"


def generate_user_completion_filename() -> str:
    """
    Generate UserCompletion filename with timestamp.
    Format: UserCompletion_v2_YYYY_M_DD_1_HHMMSS.csv
    Uses PT timezone for date and time components.

    Returns:
        Generated filename
    """
    now = datetime.now(PT)
    year = now.strftime("%Y")
    month = now.strftime("%-m")
    day = now.strftime("%-d")
    time_suffix = now.strftime("%H%M%S")
    return f"UserCompletion_v2_{year}_{month}_{day}_1_{time_suffix}.csv"


def generate_training_times(num_courses: int) -> List[Tuple[str, str]]:
    """
    Generate start and completion times for training courses.
    Calculates times in PT timezone (13:15 and 13:19), then converts to UTC for output.

    Args:
        num_courses: Number of courses to generate times for

    Returns:
        List of (start_time, end_time) tuples in ISO-8601 format with UTC timezone
    """
    times = []
    now = datetime.now(PT)

    start_time_pt = now.replace(hour=13, minute=15, second=0, microsecond=0)
    end_time_pt = now.replace(hour=13, minute=19, second=0, microsecond=0)

    start_time_utc = start_time_pt.astimezone(UTC)
    end_time_utc = end_time_pt.astimezone(UTC)

    for _ in range(num_courses):
        times.append((
            start_time_utc.isoformat(),
            end_time_utc.isoformat()
        ))

    return times


def cleanup_output_directory(config: Dict, progress_callback=None) -> int:
    """
    Remove old files from output directory before new simulation run.

    Args:
        config: Configuration dictionary
        progress_callback: Optional callback function for progress updates

    Returns:
        Number of files removed
    """
    output_dir = config['output_dir']
    files_removed = 0

    if not os.path.exists(output_dir):
        if progress_callback:
            progress_callback(f"Directory {output_dir}/ does not exist")
        return 0

    pattern = os.path.join(output_dir, "*")

    for file_path in glob.glob(pattern):
        # Skip .gitkeep files
        if os.path.basename(file_path) == ".gitkeep":
            continue

        # Only remove files, not subdirectories
        if os.path.isfile(file_path):
            try:
                os.remove(file_path)
                files_removed += 1
            except Exception as e:
                if progress_callback:
                    progress_callback(f"  Warning: Could not remove {file_path}: {e}")

    if progress_callback:
        progress_callback(f"Cleaned {output_dir}/ - removed {files_removed} file(s)")

    return files_removed


def load_and_filter_employees(file_path: str, progress_callback=None) -> Tuple[pd.DataFrame, int]:
    """
    Load employees CSV and filter out comment rows (starting with #).

    Args:
        file_path: Path to employees CSV file
        progress_callback: Optional callback function for progress updates

    Returns:
        Tuple of (filtered_dataframe, filtered_count)
    """
    employees_df = pd.read_csv(file_path)

    # Filter out comment rows
    initial_count = len(employees_df)
    employees_df['employee_id'] = employees_df['employee_id'].astype(str)
    employees_df = employees_df[~employees_df['employee_id'].str.startswith('#')].copy()
    employees_df['employee_id'] = employees_df['employee_id'].astype(int)

    filtered_count = initial_count - len(employees_df)

    if progress_callback:
        if filtered_count > 0:
            progress_callback(f"Filtered out {filtered_count} comment row(s)")
        progress_callback(f"Loaded {len(employees_df)} employee(s)")

    return employees_df, filtered_count


def convert_databricks_assignments_to_output_format(open_assignments_df: pd.DataFrame) -> List[Dict]:
    """
    Convert Databricks open assignments to NonCompletedAssignments output format.

    Args:
        open_assignments_df: DataFrame with columns: ba_id, content_id, assignment_date,
                            assignment_begin_date, assignment_due_date, content_type

    Returns:
        List of assignment dictionaries in output format
    """
    databricks_assignments = []

    if open_assignments_df.empty:
        return databricks_assignments

    for _, row in open_assignments_df.iterrows():
        databricks_assignments.append({
            "UserID": int(row['ba_id']),
            "CreateDate_text": row['assignment_date'].isoformat() if hasattr(row['assignment_date'], 'isoformat') else str(row['assignment_date']),
            "RequestId": generate_request_id(),
            "TrainingElementId": format_content_id(int(row['content_id'])),
            "Start_Date_text": row['assignment_begin_date'].isoformat() if hasattr(row['assignment_begin_date'], 'isoformat') else str(row['assignment_begin_date']),
            "DueDate_text": row['assignment_due_date'].isoformat() if hasattr(row['assignment_due_date'], 'isoformat') else str(row['assignment_due_date']),
            "ContentType": row['content_type'] if 'content_type' in row else "Media"
        })

    return databricks_assignments


def create_manager_assignments(employees_df: pd.DataFrame, progress_callback=None) -> List[Dict]:
    """
    Create new manager assignments (Daily Dose + random non-DD) for all employees.

    Args:
        employees_df: DataFrame with employee_id column
        progress_callback: Optional callback function for progress updates

    Returns:
        List of assignment dictionaries
    """
    new_manager_assignments = []
    created_date = datetime.now(PT).astimezone(UTC).isoformat()
    start_date = get_sunday_of_current_week().isoformat()
    due_date = get_next_future_sunday().isoformat()

    for employee in employees_df.itertuples():
        employee_id = employee.employee_id

        # Assign Daily Dose
        for dd_content in DAILY_DOSE_CONTENT:
            new_manager_assignments.append({
                "UserID": employee_id,
                "CreateDate_text": created_date,
                "RequestId": generate_request_id(),
                "TrainingElementId": format_content_id(int(dd_content['id'])),
                "Start_Date_text": start_date,
                "DueDate_text": due_date,
                "ContentType": "Media"
            })

        # Assign random non-Daily Dose content
        random_content = random.choice(NON_DAILY_DOSE_CONTENT)
        new_manager_assignments.append({
            "UserID": employee_id,
            "CreateDate_text": created_date,
            "RequestId": generate_request_id(),
            "TrainingElementId": format_content_id(int(random_content['id'])),
            "Start_Date_text": start_date,
            "DueDate_text": due_date,
            "ContentType": "Media"
        })

    if progress_callback:
        progress_callback(f"Created {len(new_manager_assignments)} new manager assignments")

    return new_manager_assignments


def generate_user_completion_file_from_template(config: Dict, progress_callback=None) -> Optional[str]:
    """
    Generate UserCompletion file by copying template with timestamped filename.

    Args:
        config: Configuration dictionary
        progress_callback: Optional callback function for progress updates

    Returns:
        Path to generated file, or None if generation fails
    """
    user_completion_filename = generate_user_completion_filename()
    user_completion_path = os.path.join(config['output_dir'], user_completion_filename)

    if not os.path.exists(config['user_completion_template_file']):
        if progress_callback:
            progress_callback(f"  Template file not found: {config['user_completion_template_file']}")
        return None

    try:
        shutil.copy2(config['user_completion_template_file'], user_completion_path)
        if progress_callback:
            progress_callback(f"Generated: {os.path.basename(user_completion_path)}")
        return user_completion_path
    except Exception as e:
        if progress_callback:
            progress_callback(f"  Error generating UserCompletion file: {e}")
        return None


# =============================================================================
# SFTP OPERATIONS
# =============================================================================

def parse_course_catalog_filename(filename: str) -> Optional[Tuple]:
    """
    Parse course catalog filename to extract date components.
    Format: CourseCatalog_V2_YYYY_M_DD_1_random.csv

    Args:
        filename: The course catalog filename

    Returns:
        Tuple of (year, month, day, datetime_obj) or None if parsing fails
    """
    pattern = r'CourseCatalog_V2_(\d{4})_(\d{1,2})_(\d{1,2})_\d+_[a-z0-9]+\.csv'
    match = re.match(pattern, filename, re.IGNORECASE)

    if match:
        year = int(match.group(1))
        month = int(match.group(2))
        day = int(match.group(3))

        try:
            date_obj = datetime(year, month, day)
            return (year, month, day, date_obj)
        except ValueError:
            return None
    return None


def parse_standalone_content_filename(filename: str) -> Optional[Tuple]:
    """
    Parse standalone content filename to extract date components.
    Format: StandAloneContent_v2_YYYY_M_DD_1_random.csv

    Args:
        filename: The standalone content filename

    Returns:
        Tuple of (year, month, day, datetime_obj) or None if parsing fails
    """
    pattern = r'StandAloneContent_v2_(\d{4})_(\d{1,2})_(\d{1,2})_\d+_[a-z0-9]+\.csv'
    match = re.match(pattern, filename, re.IGNORECASE)

    if match:
        year = int(match.group(1))
        month = int(match.group(2))
        day = int(match.group(3))

        try:
            date_obj = datetime(year, month, day)
            return (year, month, day, date_obj)
        except ValueError:
            return None
    return None


def download_most_recent_file_from_sftp(config: Dict, file_type: str,
                                        progress_callback=None) -> Optional[str]:
    """
    Connect to SFTP inbound server and download the most recent file of specified type.

    Args:
        config: Configuration dictionary
        file_type: Either 'course_catalog' or 'standalone_content'
        progress_callback: Optional callback function for progress updates

    Returns:
        Path to the downloaded file, or None if download fails
    """
    try:
        if progress_callback:
            progress_callback(f"Connecting to SFTP server: {config['sftp_inbound_host']}")

        transport = paramiko.Transport((config['sftp_inbound_host'], 22))
        transport.connect(username=config['sftp_inbound_user'],
                         password=config['sftp_inbound_password'])
        sftp = paramiko.SFTPClient.from_transport(transport)

        sftp.chdir(config['sftp_inbound_remote_path'])

        if progress_callback:
            progress_callback(f"Connected. Listing files in: {config['sftp_inbound_remote_path']}")

        files = sftp.listdir()

        # Parse files based on type
        if file_type == 'course_catalog':
            parsed_files = [(f, parse_course_catalog_filename(f)) for f in files]
            parsed_files = [(f, p) for f, p in parsed_files if p is not None]
        else:  # standalone_content
            parsed_files = [(f, parse_standalone_content_filename(f)) for f in files]
            parsed_files = [(f, p) for f, p in parsed_files if p is not None]

        if not parsed_files:
            if progress_callback:
                progress_callback(f"No valid {file_type} files found")
            sftp.close()
            transport.close()
            return None

        # Sort by date (most recent first)
        parsed_files.sort(key=lambda x: x[1][3], reverse=True)
        most_recent_file = parsed_files[0][0]
        most_recent_date = parsed_files[0][1][3]

        if progress_callback:
            progress_callback(f"Downloading: {most_recent_file} (date: {most_recent_date.strftime('%Y-%m-%d')})")

        # Download the file
        local_path = os.path.join(config['sftp_local_dir'], most_recent_file)
        sftp.get(most_recent_file, local_path)

        sftp.close()
        transport.close()

        if progress_callback:
            progress_callback(f"Downloaded to: {local_path}")

        return local_path

    except Exception as e:
        if progress_callback:
            progress_callback(f"Error downloading {file_type}: {e}")
        return None


def publish_files_to_sftp_outbound(config: Dict, files_to_publish: List[str],
                                   progress_callback=None) -> bool:
    """
    Publish generated files to SFTP outbound server.

    Args:
        config: Configuration dictionary
        files_to_publish: List of local file paths to upload
        progress_callback: Optional callback function for progress updates

    Returns:
        True if all files published successfully, False otherwise
    """
    if not config['sftp_publish_enabled']:
        if progress_callback:
            progress_callback("SFTP publishing is disabled (SFTP_PUBLISH_ENABLED=false)")
        return False

    if not config['sftp_outbound_password']:
        if progress_callback:
            progress_callback("ERROR: SFTP outbound password not configured")
        return False

    if not files_to_publish:
        if progress_callback:
            progress_callback("No files to publish")
        return False

    try:
        if progress_callback:
            progress_callback(f"Connecting to SFTP outbound server: {config['sftp_outbound_host']}")

        transport = paramiko.Transport((config['sftp_outbound_host'], 22))
        transport.connect(username=config['sftp_outbound_user'],
                         password=config['sftp_outbound_password'])
        sftp = paramiko.SFTPClient.from_transport(transport)

        sftp.chdir(config['sftp_outbound_remote_path'])

        if progress_callback:
            progress_callback(f"Connected. Publishing to: {config['sftp_outbound_remote_path']}")

        published_count = 0
        failed_count = 0

        for local_file_path in files_to_publish:
            if not os.path.exists(local_file_path):
                if progress_callback:
                    progress_callback(f"File not found (skipping): {local_file_path}")
                failed_count += 1
                continue

            filename = os.path.basename(local_file_path)

            try:
                sftp.put(local_file_path, filename)
                if progress_callback:
                    progress_callback(f"Uploaded: {filename}")
                published_count += 1
            except Exception as e:
                if progress_callback:
                    progress_callback(f"Failed to upload {filename}: {e}")
                failed_count += 1

        sftp.close()
        transport.close()

        if progress_callback:
            progress_callback(f"Publishing complete: {published_count} succeeded, {failed_count} failed")

        return failed_count == 0

    except Exception as e:
        if progress_callback:
            progress_callback(f"ERROR: Failed to publish files: {e}")
        return False


# =============================================================================
# DATABRICKS OPERATIONS
# =============================================================================

def get_open_assignments_from_databricks(config: Dict, employee_ids: List[int],
                                        progress_callback=None) -> pd.DataFrame:
    """
    Query Databricks to get open (non-completed) assignments for specific employees.

    Open assignments = content_assignments - content_completion

    Args:
        config: Configuration dictionary
        employee_ids: List of employee IDs (ba_id) to query assignments for
        progress_callback: Optional callback function for progress updates

    Returns:
        DataFrame with columns: ba_id, content_id, assignment_date, assignment_begin_date,
                               assignment_due_date, content_type
        Returns empty DataFrame if Databricks is not configured.
    """
    # Check if Databricks is configured
    if not all([config['databricks_host'], config['databricks_http_path'], config['databricks_token']]):
        if progress_callback:
            progress_callback("Databricks not configured. Skipping assignments query.")
        return pd.DataFrame()

    if not employee_ids:
        if progress_callback:
            progress_callback("No employee IDs provided. Skipping assignments query.")
        return pd.DataFrame()

    try:
        from databricks import sql

        if progress_callback:
            progress_callback(f"Connecting to Databricks: {config['databricks_host']}")

        connection = sql.connect(
            server_hostname=config['databricks_host'],
            http_path=config['databricks_http_path'],
            access_token=config['databricks_token']
        )

        cursor = connection.cursor()

        assignments_table = f"{config['databricks_catalog']}.{config['databricks_schema']}.content_assignments"
        completion_table = f"{config['databricks_catalog']}.{config['databricks_schema']}.content_completion"

        if progress_callback:
            progress_callback(f"Querying {len(employee_ids)} employee(s) for open assignments")

        employee_ids_str = ", ".join([str(emp_id) for emp_id in employee_ids])

        query = f"""
        SELECT
            a.ba_id,
            a.content_id,
            a.assignment_date,
            a.assignment_begin_date,
            a.assignment_due_date,
            a.content_type
        FROM {assignments_table} a
        LEFT JOIN {completion_table} c
            ON a.ba_id = c.ba_id
            AND a.content_id = c.content_id
        WHERE a.ba_id IN ({employee_ids_str})
            AND c.ba_id IS NULL
        ORDER BY a.ba_id, a.assignment_due_date
        """

        cursor.execute(query)

        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()

        cursor.close()
        connection.close()

        df = pd.DataFrame(rows, columns=columns)

        if progress_callback:
            progress_callback(f"Retrieved {len(df)} open assignment(s) from Databricks")

        return df

    except Exception as e:
        if progress_callback:
            progress_callback(f"ERROR: Failed to query Databricks: {e}")
        raise RuntimeError(f"Databricks query failed: {str(e)}") from e


def get_employee_recent_completions(config: Dict, employee_id: int,
                                    lookback_days: int = 13) -> set:
    """
    Query content_completion table to get training completed by employee in the last N days.

    Args:
        config: Configuration dictionary
        employee_id: The employee's ID (ba_id)
        lookback_days: Number of days to look back (default: 13 = today + prior 12 days)

    Returns:
        Set of content IDs completed in the lookback period
    """
    if not all([config['databricks_host'], config['databricks_http_path'], config['databricks_token']]):
        return set()

    try:
        from databricks import sql

        connection = sql.connect(
            server_hostname=config['databricks_host'],
            http_path=config['databricks_http_path'],
            access_token=config['databricks_token']
        )

        cursor = connection.cursor()

        completion_table = f"{config['databricks_catalog']}.{config['databricks_schema']}.content_completion"

        now_pt = datetime.now(PT)
        start_date = (now_pt - timedelta(days=lookback_days - 1)).date()
        end_date = now_pt.date()

        query = f"""
        SELECT DISTINCT content_id
        FROM {completion_table}
        WHERE ba_id = {employee_id}
            AND completion_date >= '{start_date}'
            AND completion_date <= '{end_date}'
        """

        cursor.execute(query)
        rows = cursor.fetchall()

        cursor.close()
        connection.close()

        recent_content_ids = set()
        for row in rows:
            content_id = int(row[0])
            recent_content_ids.add(content_id)

        return recent_content_ids

    except Exception as e:
        return set()


# =============================================================================
# API CALLS
# =============================================================================

def get_training_recommendations(config: Dict, employee_id: int,
                                progress_callback=None) -> List[Dict]:
    """
    Call the ML Training Recommender API for a given employee.

    Args:
        config: Configuration dictionary
        employee_id: The employee's ID (ba_id)
        progress_callback: Optional callback function for progress updates

    Returns:
        List of recommended training courses with 'recommended_content_id',
        'recommended_content', and 'source' fields
    """
    url = f"{config['api_base_url']}{config['api_endpoint']}"
    payload = {"data": {"ba_id": employee_id}}

    if progress_callback:
        progress_callback(f"Calling ML Reco API for employee {employee_id}...")

    try:
        response = requests.post(url, json=payload, timeout=config['api_timeout'], verify=False)
        response.raise_for_status()
        data = response.json()

        # Parse response structure
        if isinstance(data, dict):
            response_data = data.get("response", {})
            if isinstance(response_data, dict):
                recommendations = response_data.get("ml_recommendations", [])
            else:
                recommendations = response_data if isinstance(response_data, list) else []
        else:
            recommendations = []

        # Tag recommendations with source
        for rec in recommendations:
            rec["source"] = "ai"

        # Output recommendations summary
        if progress_callback:
            if not recommendations:
                progress_callback("  no ML recommendations returned")
            else:
                course_ids = [str(rec.get("recommended_content_id", "N/A")) for rec in recommendations]
                course_ids_str = ", ".join(course_ids)
                progress_callback(f"  {len(recommendations)} ML recommendation(s): {course_ids_str}")

        return recommendations if isinstance(recommendations, list) else []

    except Exception as e:
        if progress_callback:
            progress_callback(f"Error fetching recommendations for employee {employee_id}: {e}")
        return []


# =============================================================================
# EMPLOYEE PROCESSING
# =============================================================================

def process_employee(config: Dict, employee_id: int, employee_type: str,
                    manager_assignments: List[Dict], ai_recommendations: List[Dict],
                    standalone_df: pd.DataFrame, progress_callback=None) -> List[Dict]:
    """
    Process a single employee: combine manager assignments and AI recommendations,
    filter recent completions, then simulate completions based on employee type.

    Args:
        config: Configuration dictionary
        employee_id: The employee's ID
        employee_type: The employee's type (a, b, or f)
        manager_assignments: List of manager-assigned training
        ai_recommendations: List of AI-recommended training
        standalone_df: DataFrame containing standalone content for lookups
        progress_callback: Optional callback function for progress updates

    Returns:
        List of completed training records with UTC timestamps
    """
    employee_type = employee_type.lower().strip()

    # Check for recently completed training (last 13 days)
    # This ONLY applies to AI recommendations, NOT to manager assignments
    recent_completions = get_employee_recent_completions(config, employee_id, lookback_days=13)

    filtered_ai_recommendations = []

    if ai_recommendations:
        if recent_completions:
            for rec in ai_recommendations:
                content_id = rec["recommended_content_id"]

                if content_id not in recent_completions:
                    filtered_ai_recommendations.append(rec)
        else:
            filtered_ai_recommendations = ai_recommendations

    # Combine manager assignments (unfiltered) with filtered AI recommendations
    all_training = manager_assignments + filtered_ai_recommendations

    if not all_training:
        return []

    # Determine how many courses to complete based on employee type
    if employee_type == 'a':
        courses_to_complete = all_training
    elif employee_type == 'b':
        courses_to_complete = all_training[:1]
    else:  # Type F
        courses_to_complete = []

    # Generate completion records
    completions = []
    times = generate_training_times(len(courses_to_complete))

    for i, course in enumerate(courses_to_complete):
        try:
            if not isinstance(course, dict):
                if progress_callback:
                    progress_callback(f"  Warning: Skipping non-dict course at index {i}")
                continue

            start_time, end_time = times[i]
            source = course.get("source", "unknown")

            # Validate required fields
            if "recommended_content_id" not in course:
                if progress_callback:
                    progress_callback(f"  Warning: Course missing 'recommended_content_id': {course}")
                continue

            completions.append({
                "UserId": employee_id,
                "ContentId": format_content_id(course["recommended_content_id"]),
                "DateStarted": start_time,
                "DateCompleted": end_time,
                "CourseName": course.get("recommended_content", "Unknown"),
                "Source": source
            })
        except (KeyError, Exception) as e:
            if progress_callback:
                progress_callback(f"  Warning: Error processing course {i}: {e}")
            continue

    return completions


def get_manager_assignments_for_employee(employee_id: int, assignments_path: str,
                                        standalone_df: pd.DataFrame) -> List[Dict]:
    """
    Get manager assignments for a specific employee from NonCompletedAssignments file.

    Args:
        employee_id: The employee's ID
        assignments_path: Path to the NonCompletedAssignments CSV file
        standalone_df: DataFrame containing standalone content for content name lookups

    Returns:
        List of manager-assigned training with 'recommended_content_id',
        'recommended_content', and 'source' fields
    """
    manager_assignments = []

    if not os.path.exists(assignments_path):
        return manager_assignments

    assignments_df = pd.read_csv(assignments_path)
    assignments_df['UserID'] = assignments_df['UserID'].astype(int)
    employee_assignments = assignments_df[assignments_df['UserID'] == employee_id]

    for _, assignment in employee_assignments.iterrows():
        content_id = assignment['TrainingElementId']

        if isinstance(content_id, str):
            content_id_numeric = int(content_id.replace(',', ''))
        else:
            content_id_numeric = int(content_id)

        # Look up content name
        content_id_no_commas = str(content_id_numeric)
        content_name = CONTENT_NAME_LOOKUP.get(content_id_no_commas,
                                               f"Training Content {content_id_no_commas}")

        manager_assignments.append({
            "recommended_content_id": content_id_numeric,
            "recommended_content": content_name,
            "source": "manager"
        })

    return manager_assignments


# =============================================================================
# FILE GENERATION
# =============================================================================

def write_content_user_completion_file(completions: List[Dict], output_dir: str) -> str:
    """
    Write ContentUserCompletion CSV file.

    Args:
        completions: List of completion records
        output_dir: Output directory path

    Returns:
        Path to the generated file
    """
    output_filename = generate_output_filename()
    output_path = os.path.join(output_dir, output_filename)

    output_df = pd.DataFrame(completions)
    output_df = output_df[['UserId', 'ContentId', 'DateStarted', 'DateCompleted']]
    output_df.to_csv(output_path, index=False, quoting=1)

    return output_path


def write_non_completed_assignments_file(assignments: List[Dict], output_dir: str) -> str:
    """
    Write NonCompletedAssignments CSV file.

    Args:
        assignments: List of assignment records
        output_dir: Output directory path

    Returns:
        Path to the generated file
    """
    assignments_filename = generate_non_completed_assignments_filename()
    assignments_path = os.path.join(output_dir, assignments_filename)

    assignments_df = pd.DataFrame(assignments)
    assignments_df.to_csv(assignments_path, index=False, quoting=1)

    return assignments_path


def update_non_completed_assignments_file(assignments_path: str,
                                         completions: List[Dict]) -> Tuple[int, int]:
    """
    Update NonCompletedAssignments file to remove completed training.

    Args:
        assignments_path: Path to the NonCompletedAssignments CSV file
        completions: List of completion records

    Returns:
        Tuple of (initial_count, removed_count)
    """
    if not os.path.exists(assignments_path):
        return (0, 0)

    assignments_df = pd.read_csv(assignments_path)
    initial_count = len(assignments_df)

    # Build set of completed (UserID, ContentID) pairs
    completed_set = set()
    for completion in completions:
        user_id = completion['UserId']
        content_id = completion['ContentId']
        if isinstance(content_id, str):
            content_id_numeric = int(content_id.replace(',', ''))
        else:
            content_id_numeric = int(content_id)
        completed_set.add((user_id, content_id_numeric))

    # Filter out completed assignments
    def is_not_completed(row):
        user_id = int(row['UserID'])
        training_id = row['TrainingElementId']

        if isinstance(training_id, str):
            training_id_numeric = int(training_id.replace(',', ''))
        else:
            training_id_numeric = int(training_id)

        is_completed = (user_id, training_id_numeric) in completed_set
        return not is_completed

    remaining_assignments_df = assignments_df[assignments_df.apply(is_not_completed, axis=1)].copy()
    removed_count = initial_count - len(remaining_assignments_df)

    # Overwrite the file
    remaining_assignments_df.to_csv(assignments_path, index=False, quoting=1)

    return (initial_count, removed_count)
