"""
Manager Functionality - Saved for Later Use

This module contains the manager functionality to query Databricks and check
the status of employee training assignments.

To use this later, add these cells to the notebook:
1. Cell with imports and configuration
2. Cell with get_employee_assignments function
3. Cell with print_manager_report function
4. Cell with execution code
"""

# CELL 1: Imports and Configuration
CELL_1_IMPORTS = """
# Import additional libraries for manager functionality
import os
from dotenv import load_dotenv
from databricks import sql
import config

# Load environment variables from .env file
load_dotenv()

# Get Databricks credentials
DATABRICKS_TOKEN = os.getenv("DATABRICKS_TOKEN", "your_databricks_token_placeholder")
DATABRICKS_SERVER = config.DATABRICKS_CONFIG["server_hostname"]
DATABRICKS_HTTP_PATH = config.DATABRICKS_CONFIG["http_path"]
"""

# CELL 2: Query Function
CELL_2_QUERY_FUNCTION = """
def get_employee_assignments(employee_ids: List[int] = None) -> pd.DataFrame:
    '''
    Query Databricks to get training assignments for employees.

    Args:
        employee_ids: Optional list of employee IDs to filter. If None, gets all employees.

    Returns:
        DataFrame with columns: UserId, ContentId, ContentName, UserCourseStatus
    '''
    try:
        # Build query
        table_name = f"{config.DATABRICKS_CONFIG['catalog']}.{config.DATABRICKS_CONFIG['schema']}.{config.DATABRICKS_CONFIG['table']}"

        if employee_ids:
            employee_list = ",".join(str(id) for id in employee_ids)
            query = f'''
                SELECT
                    UserId,
                    ContentId,
                    ContentName,
                    UserCourseStatus
                FROM {table_name}
                WHERE UserId IN ({employee_list})
                ORDER BY UserId, ContentId
            '''
        else:
            query = f'''
                SELECT
                    UserId,
                    ContentId,
                    ContentName,
                    UserCourseStatus
                FROM {table_name}
                ORDER BY UserId, ContentId
                LIMIT {config.QUERY_CONFIG['max_rows']}
            '''

        # Connect to Databricks
        with sql.connect(
            server_hostname=DATABRICKS_SERVER,
            http_path=DATABRICKS_HTTP_PATH,
            access_token=DATABRICKS_TOKEN
        ) as connection:
            with connection.cursor() as cursor:
                cursor.execute(query)

                # Fetch results
                columns = [desc[0] for desc in cursor.description]
                rows = cursor.fetchall()

                # Convert to DataFrame
                df = pd.DataFrame(rows, columns=columns)
                return df

    except Exception as e:
        print(f"Error querying Databricks: {e}")
        return pd.DataFrame()  # Return empty DataFrame on error
"""

# CELL 3: Report Function
CELL_3_REPORT_FUNCTION = """
def print_manager_report(assignments_df: pd.DataFrame):
    '''
    Print a formatted report of employee training assignments.

    Args:
        assignments_df: DataFrame with employee assignment data
    '''
    if assignments_df.empty:
        print("No assignment data available.")
        return

    print("=" * 80)
    print("MANAGER REPORT - Employee Training Assignments")
    print("=" * 80)
    print()

    # Group by employee
    grouped = assignments_df.groupby('UserId')

    for employee_id, employee_data in grouped:
        print(f"Employee {employee_id}:")

        for _, row in employee_data.iterrows():
            content_id = row['ContentId']
            content_name = row['ContentName']
            status = row['UserCourseStatus']

            # Format status with visual indicator
            status_indicator = "✓" if status.lower() == "completed" else "○"

            print(f"  {status_indicator} [{content_id}] {content_name} - Status: {status}")

        print()

    # Summary statistics
    total_assignments = len(assignments_df)
    completed = len(assignments_df[assignments_df['UserCourseStatus'].str.lower() == 'completed'])
    completion_rate = (completed / total_assignments * 100) if total_assignments > 0 else 0

    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total Assignments: {total_assignments}")
    print(f"Completed: {completed}")
    print(f"In Progress: {total_assignments - completed}")
    print(f"Completion Rate: {completion_rate:.1f}%")
    print("=" * 80)
"""

# CELL 4: Execution
CELL_4_EXECUTION = """
# Execute Manager Report
# This cell queries Databricks and prints the status of employee training assignments

print("\\n" + "=" * 80)
print("MANAGER - Checking Employee Training Assignments")
print("=" * 80)
print()

# Get employee IDs from the earlier simulation
employee_ids = employees_df['employee_id'].tolist()

print(f"Querying Databricks for {len(employee_ids)} employees...")
print(f"Table: {config.DATABRICKS_CONFIG['catalog']}.{config.DATABRICKS_CONFIG['schema']}.{config.DATABRICKS_CONFIG['table']}")
print()

# Query Databricks
assignments_df = get_employee_assignments(employee_ids)

if not assignments_df.empty:
    print(f"Retrieved {len(assignments_df)} assignment records\\n")
    # Print formatted report
    print_manager_report(assignments_df)
else:
    print("No assignment data found or error connecting to Databricks.")
    print("Please check:")
    print("  1. .env file contains valid DATABRICKS_TOKEN")
    print("  2. config.py has correct server_hostname and http_path")
    print("  3. Table exists and is accessible")
"""

# MARKDOWN CELL: Documentation
MARKDOWN_CELL = """
# Manager - Check Employee Training Assignments

This section implements the manager functionality to query Databricks and check the status of employee training assignments.

## Setup Required:
1. Copy `.env.example` to `.env` and add your Databricks Personal Access Token
2. Update `config.py` with your Databricks workspace URL and warehouse path
3. Ensure the table `retail_systems_qa.store_enablement.user_course_completion_staging` is accessible
"""
