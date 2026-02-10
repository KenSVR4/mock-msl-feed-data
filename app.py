#!/usr/bin/env python3
"""
BTC Fake - Gradio Web Application
Training Completion Simulator with Interactive Web Interface
"""

import gradio as gr
import pandas as pd
import requests
from datetime import datetime, timedelta
import random
import string
import os
import io
import zipfile
from typing import List, Dict, Tuple
import urllib3
import pytz
from dotenv import load_dotenv
import paramiko
from databricks import sql

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Define timezones
PT = pytz.timezone('America/Los_Angeles')
UTC = pytz.UTC

# Load environment variables
load_dotenv()

# ==============================================================================
# Configuration
# ==============================================================================

def load_config():
    """Load configuration from environment variables"""
    config = {
        # API Configuration
        'api_base_url': os.getenv("API_BASE_URL", "https://dataiku-api-devqa.lower.internal.sephora.com"),
        'api_endpoint': os.getenv("API_ENDPOINT", "/public/api/v1/mltr/v3/run"),
        'api_timeout': int(os.getenv("API_TIMEOUT", "30")),

        # File Paths
        'employees_file': os.getenv("EMPLOYEES_FILE", "input/employees.csv"),
        'output_dir': os.getenv("OUTPUT_DIR", "generated_files"),
        'sftp_local_dir': os.getenv("SFTP_LOCAL_DIR", "generated_files"),
        'user_completion_template': os.getenv("USER_COMPLETION_TEMPLATE_FILE", "docs/sample_files/UserCompletion_v2_YYYY_m_d_1_000001.csv"),

        # Databricks
        'databricks_host': os.getenv("DATABRICKS_HOST", ""),
        'databricks_http_path': os.getenv("DATABRICKS_HTTP_PATH", ""),
        'databricks_token': os.getenv("DATABRICKS_TOKEN", ""),
        'databricks_catalog': os.getenv("DATABRICKS_CATALOG", "retail_systems_dev"),
        'databricks_schema': os.getenv("DATABRICKS_SCHEMA", "store_enablement"),

        # SFTP Inbound
        'sftp_inbound_host': os.getenv("SFTP_INBOUND_HOST", "sftp.sephora.com"),
        'sftp_inbound_user': os.getenv("SFTP_INBOUND_USER", "SephoraMSL"),
        'sftp_inbound_password': os.getenv("SFTP_INBOUND_PASSWORD", ""),
        'sftp_inbound_remote_path': os.getenv("SFTP_INBOUND_REMOTE_PATH", "/inbound/BTC/retailData/prod/vendor/mySephoraLearning-archive"),

        # SFTP Outbound
        'sftp_outbound_host': os.getenv("SFTP_OUTBOUND_HOST", "internal-sftp.sephoraus.com"),
        'sftp_outbound_user': os.getenv("SFTP_OUTBOUND_USER", "SephoraRDIInternal"),
        'sftp_outbound_password': os.getenv("SFTP_OUTBOUND_PASSWORD", ""),
        'sftp_outbound_remote_path': os.getenv("SFTP_OUTBOUND_REMOTE_PATH", "/inbound/BTC/retailData/prod/vendor/mySephoraLearningV2"),
        'sftp_publish_enabled': os.getenv("SFTP_PUBLISH_ENABLED", "true").lower() in ['true', '1', 'yes'],
    }
    return config

# ==============================================================================
# Core Simulation Functions
# ==============================================================================

def generate_random_suffix(length=6):
    """Generate random alphanumeric suffix"""
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

def format_content_id(content_id):
    """Format content ID with commas for readability"""
    id_str = str(content_id)
    if len(id_str) > 3:
        parts = []
        while id_str:
            if len(id_str) > 3:
                parts.insert(0, id_str[-3:])
                id_str = id_str[:-3]
            else:
                parts.insert(0, id_str)
                id_str = ""
        return ','.join(parts)
    return id_str

def call_recommendation_api(employee_id: str, config: dict, progress_callback=None) -> List[str]:
    """Call ML Training Recommender API for employee recommendations"""
    url = f"{config['api_base_url']}{config['api_endpoint']}"
    payload = {"data": {"ba_id": int(employee_id)}}

    if progress_callback:
        progress_callback(f"Calling API for employee {employee_id}...")

    try:
        response = requests.post(url, json=payload, timeout=config['api_timeout'], verify=False)
        response.raise_for_status()
        recommendations = response.json()

        if 'data' in recommendations and 'results' in recommendations['data']:
            results = recommendations['data']['results']
            if 'training_element_id' in results:
                return [str(tid) for tid in results['training_element_id']]
        return []
    except Exception as e:
        if progress_callback:
            progress_callback(f"Warning: API call failed for employee {employee_id}: {str(e)}")
        return []

def simulate_employee_training(employee_id: str, employee_type: str, manager_assignments: List[str],
                               ai_recommendations: List[str], current_time: datetime) -> List[Dict]:
    """Simulate training completion for one employee"""
    completions = []
    all_training = manager_assignments + ai_recommendations

    if employee_type.lower() == 'a':
        # Type A: Complete all training
        selected_training = all_training
    elif employee_type.lower() == 'b':
        # Type B: Complete one training
        selected_training = random.sample(all_training, min(1, len(all_training)))
    else:
        # Type F: Complete no training
        selected_training = []

    for training_id in selected_training:
        start_time = current_time - timedelta(minutes=random.randint(5, 30))
        end_time = current_time

        completion = {
            'UserId': employee_id,
            'ContentId': format_content_id(training_id),
            'DateStarted': start_time.strftime('%Y-%m-%dT%H:%M:%SZ'),
            'DateCompleted': end_time.strftime('%Y-%m-%dT%H:%M:%SZ'),
            'source': 'manager' if training_id in manager_assignments else 'AI'
        }
        completions.append(completion)

    return completions

def run_full_simulation(employee_csv_content: str, num_employees: int, enable_publishing: bool,
                       config: dict, progress_callback=None) -> Tuple[str, List[str]]:
    """
    Run the complete simulation

    Returns:
        Tuple of (summary_text, list_of_output_file_paths)
    """
    output_files = []
    summary_lines = []

    # Header
    summary_lines.append("=" * 80)
    summary_lines.append("BTC FAKE - TRAINING COMPLETION SIMULATOR")
    summary_lines.append("=" * 80)
    summary_lines.append("")

    # Parse employee CSV
    if progress_callback:
        progress_callback("Parsing employee data...")

    summary_lines.append("Step 1: Loading Employee Data")
    summary_lines.append("-" * 80)

    df_employees = pd.read_csv(io.StringIO(employee_csv_content))
    original_count = len(df_employees)
    df_employees = df_employees[~df_employees['employee_id'].astype(str).str.startswith('#')]
    active_count = len(df_employees)

    summary_lines.append(f"Total rows in CSV: {original_count}")
    summary_lines.append(f"Active employees (excluding # comments): {active_count}")

    if num_employees > 0:
        df_employees = df_employees.head(num_employees)
        summary_lines.append(f"Limiting to first {num_employees} employees")

    summary_lines.append(f"Processing {len(df_employees)} employees")
    summary_lines.append("")

    # Employee type breakdown
    type_counts = df_employees['employee_edu_type'].value_counts()
    summary_lines.append("Employee Type Breakdown:")
    for emp_type, count in type_counts.items():
        summary_lines.append(f"  Type {emp_type.upper()}: {count} employees")
    summary_lines.append("")

    # Generate timestamps
    current_time = datetime.now(UTC)
    random_suffix = generate_random_suffix()
    date_str = current_time.strftime('%Y_%m_%d')

    summary_lines.append("Step 2: Configuration")
    summary_lines.append("-" * 80)
    summary_lines.append(f"Simulation Time: {current_time.strftime('%Y-%m-%d %H:%M:%S UTC')}")
    summary_lines.append(f"Random Suffix: {random_suffix}")
    summary_lines.append(f"Output Directory: {config['output_dir']}")
    summary_lines.append(f"API Base URL: {config['api_base_url']}")
    summary_lines.append("")

    # Create output directory
    os.makedirs(config['output_dir'], exist_ok=True)

    # Simulate completions
    summary_lines.append("Step 3: Processing Employees")
    summary_lines.append("-" * 80)
    summary_lines.append("")

    all_completions = []
    api_success_count = 0
    api_failure_count = 0

    # Track data for execution summary
    employee_ml_recommendations = []  # List of (employee_id, recommendations_list)
    employee_assigned_daily_dose = {}  # Dict of employee_id -> list of daily dose content
    employee_assigned_random = {}  # Dict of employee_id -> random content info
    employee_summaries = []  # List of (employee_id, course_details_list)

    # Sample Daily Dose content IDs and names
    daily_dose_content = [
        {'id': '2033875', 'name': "What's Hot For February"},
        {'id': '2030735', 'name': "January Training Product"}
    ]

    # Sample non-Daily Dose content IDs and names for random assignment
    non_daily_dose_content = [
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
    content_name_lookup = {}
    for content in daily_dose_content + non_daily_dose_content:
        content_name_lookup[content['id']] = content['name']

    for idx, row in df_employees.iterrows():
        employee_id = str(row['employee_id'])
        employee_type = str(row['employee_edu_type'])

        if progress_callback:
            progress_callback(f"Processing employee {idx + 1}/{len(df_employees)}: {employee_id}")

        summary_lines.append(f"Employee {idx + 1}/{len(df_employees)}: {employee_id} (Type {employee_type.upper()})")

        # Get AI recommendations
        summary_lines.append(f"  ├─ Calling ML Training Recommender API...")
        ai_recommendations = call_recommendation_api(employee_id, config, progress_callback)

        # Track ML recommendations for execution summary
        if ai_recommendations:
            api_success_count += 1
            summary_lines.append(f"  ├─ ✓ API Success: {len(ai_recommendations)} recommendations")

            # Store recommendations with dummy names for execution summary
            ml_recs_list = []
            for rec in ai_recommendations[:5]:  # Show first 5
                summary_lines.append(f"  │  └─ {format_content_id(rec)}")
                ml_recs_list.append({
                    "content_id": format_content_id(rec),
                    "content_name": f"Training Content {rec}"
                })
            if len(ai_recommendations) > 5:
                summary_lines.append(f"  │  └─ ... and {len(ai_recommendations) - 5} more")
                for rec in ai_recommendations[5:]:
                    ml_recs_list.append({
                        "content_id": format_content_id(rec),
                        "content_name": f"Training Content {rec}"
                    })

            employee_ml_recommendations.append((employee_id, ml_recs_list))
        else:
            api_failure_count += 1
            summary_lines.append(f"  ├─ ⚠ API returned no recommendations")

        # Simulate manager assignments
        # Daily Dose = first 2 (same for all employees)
        daily_dose_ids = [content['id'] for content in daily_dose_content]

        # Random = randomly chosen (different for each employee)
        random_content = random.choice(non_daily_dose_content)
        random_id = random_content['id']
        random_name = random_content['name']

        manager_assignments = daily_dose_ids + [random_id]

        summary_lines.append(f"  ├─ Manager Assignments: {len(manager_assignments)} training items")
        for ma in manager_assignments:
            summary_lines.append(f"  │  └─ {format_content_id(ma)}")

        # Track manager assignments for execution summary
        employee_assigned_daily_dose[employee_id] = [
            {"content_id": format_content_id(content['id']), "content_name": content['name']}
            for content in daily_dose_content
        ]
        employee_assigned_random[employee_id] = {
            "content_id": format_content_id(random_id),
            "content_name": random_name
        }

        # Combined training pool
        all_training = manager_assignments + ai_recommendations
        summary_lines.append(f"  ├─ Total Available Training: {len(all_training)} items")

        # Simulate training completion
        completions = simulate_employee_training(
            employee_id, employee_type, manager_assignments,
            ai_recommendations, current_time
        )

        all_completions.extend(completions)

        # Track completions for execution summary
        course_details = []
        for c in completions:
            # Look up content name from our content lookup dictionary
            content_id_formatted = c['ContentId']
            content_id_no_commas = c['ContentId'].replace(',', '')

            # Try to find the content name in our lookup dictionary
            content_name = content_name_lookup.get(content_id_no_commas,
                                                   f"Training Content {content_id_no_commas}")

            course_details.append((content_id_formatted, content_name, c['source']))

        employee_summaries.append((employee_id, course_details))

        # Summary for this employee
        if completions:
            summary_lines.append(f"  └─ ✓ Completed {len(completions)} training(s):")
            for c in completions:
                summary_lines.append(f"     └─ {c['ContentId']} (source: {c['source']})")
        else:
            summary_lines.append(f"  └─ ○ No completions (Type F behavior)")

        summary_lines.append("")

    # Statistics
    summary_lines.append("Step 4: Simulation Statistics")
    summary_lines.append("-" * 80)
    summary_lines.append(f"Total Employees Processed: {len(df_employees)}")
    summary_lines.append(f"Total Training Completions: {len(all_completions)}")
    summary_lines.append(f"API Calls Successful: {api_success_count}")
    summary_lines.append(f"API Calls Failed/No Data: {api_failure_count}")

    # Breakdown by source
    manager_completions = [c for c in all_completions if c['source'] == 'manager']
    ai_completions = [c for c in all_completions if c['source'] == 'AI']
    summary_lines.append(f"Manager-Assigned Completions: {len(manager_completions)}")
    summary_lines.append(f"AI-Recommended Completions: {len(ai_completions)}")

    # Breakdown by employee type
    summary_lines.append("")
    summary_lines.append("Completions by Employee Type:")
    for emp_type in ['a', 'b', 'f']:
        type_employees = df_employees[df_employees['employee_edu_type'] == emp_type]
        type_completions = [c for c in all_completions if c['UserId'] in type_employees['employee_id'].astype(str).values]
        summary_lines.append(f"  Type {emp_type.upper()}: {len(type_completions)} completions from {len(type_employees)} employees")

    summary_lines.append("")

    # Generate files
    summary_lines.append("Step 5: Generating Output Files")
    summary_lines.append("-" * 80)
    summary_lines.append("")

    # Generate ContentUserCompletion file
    if progress_callback:
        progress_callback("Generating ContentUserCompletion file...")

    completion_filename = f"ContentUserCompletion_V2_{date_str}_1_{random_suffix}.csv"
    completion_path = os.path.join(config['output_dir'], completion_filename)

    df_completions = pd.DataFrame([
        {
            'UserId': c['UserId'],
            'ContentId': c['ContentId'],
            'DateStarted': c['DateStarted'],
            'DateCompleted': c['DateCompleted']
        }
        for c in all_completions
    ])

    df_completions.to_csv(completion_path, index=False, quoting=1)
    output_files.append(completion_path)

    file_size = os.path.getsize(completion_path)
    summary_lines.append(f"1. ContentUserCompletion CSV")
    summary_lines.append(f"   ├─ Filename: {completion_filename}")
    summary_lines.append(f"   ├─ Path: {completion_path}")
    summary_lines.append(f"   ├─ Records: {len(df_completions)}")
    summary_lines.append(f"   ├─ Size: {file_size:,} bytes")
    summary_lines.append(f"   └─ Status: ✓ Generated")
    summary_lines.append("")

    # Generate NonCompletedAssignments file
    if progress_callback:
        progress_callback("Generating NonCompletedAssignments file...")

    assignments_filename = f"Non_Completed_Assignments_V2_{date_str}_1_{random_suffix}.csv"
    assignments_path = os.path.join(config['output_dir'], assignments_filename)

    # Create assignments (simplified version)
    most_recent_monday = current_time - timedelta(days=current_time.weekday())
    most_recent_monday = most_recent_monday.replace(hour=1, minute=15, second=0, microsecond=0)
    next_monday = most_recent_monday + timedelta(days=7)
    next_monday = next_monday.replace(hour=1, minute=3, second=0, microsecond=0)

    summary_lines.append(f"Assignment Date Range:")
    summary_lines.append(f"   ├─ Start Date: {most_recent_monday.strftime('%Y-%m-%d %H:%M:%S')}")
    summary_lines.append(f"   └─ Due Date: {next_monday.strftime('%Y-%m-%d %H:%M:%S')}")
    summary_lines.append("")

    assignments = []
    for idx, row in df_employees.iterrows():
        employee_id = str(row['employee_id'])
        # Add sample assignments
        assignments.append({
            'UserID': employee_id,
            'CreateDate_text': current_time.strftime('%Y-%m-%dT%H:%M:%SZ'),
            'RequestId': str(25000 + idx),
            'TrainingElementId': '2,033,875',
            'Start_Date_text': most_recent_monday.strftime('%Y-%m-%dT%H:%M:%SZ'),
            'DueDate_text': next_monday.strftime('%Y-%m-%dT%H:%M:%SZ'),
            'ContentType': 'Media'
        })

    df_assignments = pd.DataFrame(assignments)
    df_assignments.to_csv(assignments_path, index=False, quoting=1)
    output_files.append(assignments_path)

    file_size = os.path.getsize(assignments_path)
    summary_lines.append(f"2. NonCompletedAssignments CSV")
    summary_lines.append(f"   ├─ Filename: {assignments_filename}")
    summary_lines.append(f"   ├─ Path: {assignments_path}")
    summary_lines.append(f"   ├─ Records: {len(df_assignments)}")
    summary_lines.append(f"   ├─ Size: {file_size:,} bytes")
    summary_lines.append(f"   └─ Status: ✓ Generated")
    summary_lines.append("")

    # Generate UserCompletion file (dummy)
    if progress_callback:
        progress_callback("Generating UserCompletion file...")

    user_completion_filename = f"UserCompletion_v2_{date_str}_1_{random_suffix}.csv"
    user_completion_path = os.path.join(config['output_dir'], user_completion_filename)

    # Copy template or create minimal file
    pd.DataFrame(columns=['UserId', 'ContentId', 'DateCompleted']).to_csv(user_completion_path, index=False, quoting=1)
    output_files.append(user_completion_path)

    file_size = os.path.getsize(user_completion_path)
    summary_lines.append(f"3. UserCompletion CSV (Template)")
    summary_lines.append(f"   ├─ Filename: {user_completion_filename}")
    summary_lines.append(f"   ├─ Path: {user_completion_path}")
    summary_lines.append(f"   ├─ Records: 0 (template file)")
    summary_lines.append(f"   ├─ Size: {file_size:,} bytes")
    summary_lines.append(f"   └─ Status: ✓ Generated")
    summary_lines.append("")

    # ===========================================================================
    # EXECUTION SUMMARY (matching VS Code notebook format)
    # ===========================================================================
    summary_lines.append("-" * 80)
    summary_lines.append("EXECUTION SUMMARY")
    summary_lines.append("-" * 80)
    summary_lines.append("")

    # PART 1: MANAGER-ASSIGNMENTS GIVEN NEW
    summary_lines.append("=" * 80)
    summary_lines.append("MANAGER-ASSIGNMENTS GIVEN NEW")
    summary_lines.append("=" * 80)
    summary_lines.append("")

    # PART A: Daily Dose Assignments
    if employee_assigned_daily_dose:
        summary_lines.append("PART A: DAILY DOSE ASSIGNMENTS")
        summary_lines.append("-" * 80)
        summary_lines.append("")
        summary_lines.append(f"Daily Dose training assigned to {len(employee_assigned_daily_dose)} employee(s):")
        summary_lines.append("")

        # Get the contents from the first employee (they all have the same Daily Dose)
        first_employee_contents = list(employee_assigned_daily_dose.values())[0]

        summary_lines.append("Daily Dose Contents:")
        for content_info in first_employee_contents:
            content_id = content_info['content_id']
            content_name = content_info['content_name']
            summary_lines.append(f"  {content_id} - {content_name}")

        summary_lines.append("")

        # Print list of all employees who received these assignments
        employee_ids_str = ", ".join([str(emp_id) for emp_id in sorted(employee_assigned_daily_dose.keys())])
        summary_lines.append(f"Employees: {employee_ids_str}")
        summary_lines.append("")
    else:
        summary_lines.append("PART A: DAILY DOSE ASSIGNMENTS")
        summary_lines.append("-" * 80)
        summary_lines.append("")
        summary_lines.append("No Daily Dose assignments were created in this run.")
        summary_lines.append("")

    # PART B: Random Non-Daily Dose Assignments
    if employee_assigned_random:
        summary_lines.append("PART B: RANDOM NON-DAILY DOSE ASSIGNMENTS")
        summary_lines.append("-" * 80)
        summary_lines.append("")
        summary_lines.append(f"Random non-Daily Dose training assigned to {len(employee_assigned_random)} employee(s):")
        summary_lines.append("")

        # Print header
        summary_lines.append(f"{'Employee ID':<15} | {'Content ID':<15} | {'Course Name'}")
        summary_lines.append(f"{'-' * 15} | {'-' * 15} | {'-' * 50}")

        # Print each employee's random assignment
        for emp_id in sorted(employee_assigned_random.keys()):
            content_info = employee_assigned_random[emp_id]
            content_id = content_info['content_id']
            content_name = content_info['content_name']
            summary_lines.append(f"{emp_id:<15} | {content_id:<15} | {content_name}")

        summary_lines.append("")
    else:
        summary_lines.append("PART B: RANDOM NON-DAILY DOSE ASSIGNMENTS")
        summary_lines.append("-" * 80)
        summary_lines.append("")
        summary_lines.append("No random non-Daily Dose assignments were created in this run.")
        summary_lines.append("")

    # PART 2: RECOMMENDATIONS GIVEN BY ML API
    summary_lines.append("=" * 80)
    summary_lines.append("RECOMMENDATIONS GIVEN BY ML API")
    summary_lines.append("=" * 80)
    summary_lines.append("")

    if employee_ml_recommendations:
        # Collect all recommendation rows
        recommendation_rows = []

        for employee_id, ml_recs in employee_ml_recommendations:
            for rec in ml_recs:
                content_id = rec["content_id"]
                content_name = rec["content_name"]
                recommendation_rows.append((employee_id, content_id, content_name))

        # Sort by employee ID, then content ID
        recommendation_rows.sort(key=lambda x: (x[0], str(x[1])))

        # Print header
        summary_lines.append(f"{'Employee ID':<15} | {'Content ID':<15} | {'Content Name'}")
        summary_lines.append(f"{'-' * 15} | {'-' * 15} | {'-' * 50}")

        # Print each recommendation as a separate row
        for employee_id, content_id, content_name in recommendation_rows:
            summary_lines.append(f"{employee_id:<15} | {content_id:<15} | {content_name}")

        summary_lines.append("")
    else:
        summary_lines.append("No ML recommendations were given to any employee.")
        summary_lines.append("")

    # PART 3: EMPLOYEE TRAINING COMPLETIONS OF MANAGER-ASSIGNED
    summary_lines.append("=" * 80)
    summary_lines.append("EMPLOYEE TRAINING COMPLETIONS OF MANAGER-ASSIGNED")
    summary_lines.append("=" * 80)
    summary_lines.append("")

    # Track if any manager assignments were completed
    manager_completions_found = False
    manager_completion_rows = []

    for employee_id, course_details in employee_summaries:
        # Filter for manager-assigned training only
        manager_courses = [(content_id, course_name) for content_id, course_name, source in course_details if source == "manager"]

        if manager_courses:
            manager_completions_found = True
            for content_id, course_name in manager_courses:
                manager_completion_rows.append((employee_id, content_id, course_name))

    if manager_completions_found:
        # Sort by employee ID, then content ID
        manager_completion_rows.sort(key=lambda x: (x[0], str(x[1])))

        # Print header
        summary_lines.append(f"{'Employee ID':<15} | {'Content ID':<15} | {'Course Name'}")
        summary_lines.append(f"{'-' * 15} | {'-' * 15} | {'-' * 50}")

        # Print each completion on a separate row
        for employee_id, content_id, course_name in manager_completion_rows:
            summary_lines.append(f"{employee_id:<15} | {content_id:<15} | {course_name}")
    else:
        summary_lines.append("No manager-assigned training was completed by any employee.")

    summary_lines.append("")

    # PART 4: EMPLOYEE TRAINING COMPLETIONS OF ML-RECOMMENDED
    summary_lines.append("=" * 80)
    summary_lines.append(" EMPLOYEE TRAINING COMPLETIONS OF ML-RECOMMENDED")
    summary_lines.append("=" * 80)
    summary_lines.append("")

    # Track if any ML recommendations were completed
    ml_completions_found = False
    ml_completion_rows = []

    for employee_id, course_details in employee_summaries:
        # Filter for ML-recommended training only
        ml_courses = [(content_id, course_name) for content_id, course_name, source in course_details if source == "AI"]

        if ml_courses:
            ml_completions_found = True
            for content_id, course_name in ml_courses:
                ml_completion_rows.append((employee_id, content_id, course_name))

    if ml_completions_found:
        # Sort by employee ID, then content ID
        ml_completion_rows.sort(key=lambda x: (x[0], str(x[1])))

        # Print header
        summary_lines.append(f"{'Employee ID':<15} | {'Content ID':<15} | {'Course Name'}")
        summary_lines.append(f"{'-' * 15} | {'-' * 15} | {'-' * 50}")

        # Print each completion on a separate row
        for employee_id, content_id, course_name in ml_completion_rows:
            summary_lines.append(f"{employee_id:<15} | {content_id:<15} | {course_name}")
    else:
        summary_lines.append("No ML-recommended training was completed by any employee.")

    summary_lines.append("")
    summary_lines.append("=" * 80)
    summary_lines.append("execution complete")
    summary_lines.append("=" * 80)
    summary_lines.append("")

    # Final summary
    summary_lines.append("=" * 80)
    summary_lines.append("SIMULATION COMPLETE")
    summary_lines.append("=" * 80)
    summary_lines.append("")
    summary_lines.append("Summary:")
    summary_lines.append(f"  ├─ Employees Processed: {len(df_employees)}")
    summary_lines.append(f"  ├─ Training Completions: {len(all_completions)}")
    summary_lines.append(f"  ├─ Files Generated: {len(output_files)}")
    summary_lines.append(f"  ├─ Output Directory: {config['output_dir']}/")
    summary_lines.append(f"  └─ Random Suffix: {random_suffix}")
    summary_lines.append("")

    summary_lines.append("Generated Files:")
    for i, file_path in enumerate(output_files, 1):
        filename = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)
        summary_lines.append(f"  {i}. {filename} ({file_size:,} bytes)")
    summary_lines.append("")

    # Publishing
    if enable_publishing and config['sftp_publish_enabled']:
        if progress_callback:
            progress_callback("Publishing files to SFTP...")
        summary_lines.append("Step 6: Publishing to SFTP")
        summary_lines.append("-" * 80)
        summary_lines.append("⚠ Note: SFTP publishing is skipped in Gradio web interface")
        summary_lines.append("        Use the Jupyter notebook for SFTP upload functionality")
        summary_lines.append("")
        summary_lines.append(f"Files ready for manual upload in: {config['output_dir']}/")
        summary_lines.append("")

    summary_lines.append("=" * 80)
    summary_lines.append("All files have been packaged into a downloadable ZIP file.")
    summary_lines.append("Click 'Download Generated Files (ZIP)' below to get all outputs.")
    summary_lines.append("=" * 80)

    summary_text = '\n'.join(summary_lines)
    return summary_text, output_files

# ==============================================================================
# Gradio Interface Functions
# ==============================================================================

def run_simulation_ui(employee_file, num_employees, enable_publishing, progress=gr.Progress()):
    """Gradio wrapper for simulation"""
    config = load_config()

    if employee_file is None:
        return "Error: Please upload an employee CSV file", None

    # Read uploaded file
    with open(employee_file.name, 'r') as f:
        employee_csv_content = f.read()

    # Progress callback
    def progress_callback(msg):
        progress(0.5, desc=msg)

    # Run simulation
    summary, output_files = run_full_simulation(
        employee_csv_content,
        num_employees,
        enable_publishing,
        config,
        progress_callback
    )

    # Create zip file of outputs
    if output_files:
        zip_path = os.path.join(config['output_dir'], f"simulation_output_{generate_random_suffix()}.zip")
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for file_path in output_files:
                zipf.write(file_path, os.path.basename(file_path))

        return summary, zip_path

    return summary, None

def preview_employees_ui(employee_file):
    """Preview uploaded employee file"""
    if employee_file is None:
        return "No file uploaded"

    df = pd.read_csv(employee_file.name)
    df = df[~df['employee_id'].astype(str).str.startswith('#')]

    summary = f"Total employees: {len(df)}\n\n"
    summary += f"Employee types:\n"
    summary += df['employee_edu_type'].value_counts().to_string()
    summary += f"\n\nFirst 20 rows:\n"

    return summary + "\n" + df.head(20).to_string()

def test_api_ui(employee_id):
    """Test API connection with sample employee"""
    config = load_config()

    if not employee_id:
        return "Please enter an employee ID"

    try:
        recommendations = call_recommendation_api(employee_id, config)
        if recommendations:
            return f"✓ API Success!\n\nRecommendations for employee {employee_id}:\n" + "\n".join(f"  - {r}" for r in recommendations)
        else:
            return f"⚠ API returned no recommendations for employee {employee_id}"
    except Exception as e:
        return f"✗ API Error: {str(e)}"

# ==============================================================================
# Gradio Application
# ==============================================================================

def create_app():
    """Create Gradio application"""

    with gr.Blocks(title="BTC Fake - Training Simulator") as app:

        gr.Markdown("# 🎓 BTC Fake - Training Completion Simulator")
        gr.Markdown("Generate realistic training completion data for testing and development")

        with gr.Tabs():

            # Tab 1: Run Simulation
            with gr.Tab("Run Simulation"):
                gr.Markdown("## Simulation Settings")

                with gr.Row():
                    with gr.Column():
                        employee_file_input = gr.File(
                            label="Upload Employees CSV",
                            file_types=[".csv"],
                            type="filepath"
                        )
                        num_employees_input = gr.Slider(
                            minimum=0,
                            maximum=2000,
                            value=0,
                            step=1,
                            label="Number of Employees (0 = all)",
                            info="Limit the number of employees to process"
                        )
                        enable_publishing_input = gr.Checkbox(
                            label="Enable SFTP Publishing",
                            value=False,
                            info="Upload generated files to SFTP outbound server"
                        )

                        run_button = gr.Button("🚀 Run Simulation", variant="primary", size="lg")

                    with gr.Column():
                        gr.Markdown("### Quick Info")
                        gr.Markdown("""
                        **Employee Types:**
                        - **Type A**: Completes all training (manager + AI)
                        - **Type B**: Completes one training
                        - **Type F**: Completes no training

                        **Generated Files:**
                        - ContentUserCompletion CSV
                        - NonCompletedAssignments CSV
                        - UserCompletion CSV
                        """)

                gr.Markdown("## Results")
                output_summary = gr.Textbox(
                    label="Simulation Summary",
                    lines=40,
                    max_lines=60
                )
                output_files = gr.File(
                    label="Download Generated Files (ZIP)",
                    type="filepath"
                )

                run_button.click(
                    fn=run_simulation_ui,
                    inputs=[employee_file_input, num_employees_input, enable_publishing_input],
                    outputs=[output_summary, output_files]
                )

            # Tab 2: Preview Data
            with gr.Tab("Preview Employees"):
                gr.Markdown("## Preview Employee Data")

                preview_file_input = gr.File(
                    label="Upload Employees CSV",
                    file_types=[".csv"],
                    type="filepath"
                )
                preview_button = gr.Button("👁️ Preview File")
                preview_output = gr.Textbox(
                    label="Employee Data Preview",
                    lines=25
                )

                preview_button.click(
                    fn=preview_employees_ui,
                    inputs=[preview_file_input],
                    outputs=[preview_output]
                )

            # Tab 3: Test API
            with gr.Tab("Test API"):
                gr.Markdown("## Test ML Training Recommender API")

                with gr.Row():
                    test_employee_id = gr.Textbox(
                        label="Employee ID",
                        placeholder="88563",
                        value="88563"
                    )
                    test_api_button = gr.Button("🧪 Test API Connection")

                api_test_output = gr.Textbox(
                    label="API Response",
                    lines=15
                )

                test_api_button.click(
                    fn=test_api_ui,
                    inputs=[test_employee_id],
                    outputs=[api_test_output]
                )

            # Tab 4: Configuration
            with gr.Tab("Configuration"):
                gr.Markdown("## Current Configuration")

                config = load_config()

                config_text = f"""
**API Configuration:**
- Base URL: {config['api_base_url']}
- Endpoint: {config['api_endpoint']}
- Timeout: {config['api_timeout']}s

**Databricks:**
- Host: {config['databricks_host'] or 'Not configured'}
- Catalog: {config['databricks_catalog']}
- Schema: {config['databricks_schema']}

**SFTP Inbound:**
- Host: {config['sftp_inbound_host']}
- User: {config['sftp_inbound_user']}
- Remote Path: {config['sftp_inbound_remote_path']}

**SFTP Outbound:**
- Host: {config['sftp_outbound_host']}
- User: {config['sftp_outbound_user']}
- Remote Path: {config['sftp_outbound_remote_path']}
- Publishing Enabled: {config['sftp_publish_enabled']}

**File Paths:**
- Output Directory: {config['output_dir']}
- SFTP Local Directory: {config['sftp_local_dir']}

💡 **Note**: Configuration is loaded from `.env` file
                """

                gr.Markdown(config_text)

        gr.Markdown("---")
        gr.Markdown("Built with Gradio • BTC Fake Training Simulator")

    return app

# ==============================================================================
# Main Entry Point
# ==============================================================================

if __name__ == "__main__":
    app = create_app()
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True
    )
