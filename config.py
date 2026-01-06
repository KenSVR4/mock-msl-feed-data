"""
Configuration file for BTC Fake project.
Contains Databricks and other service configurations.
"""

# Databricks Configuration
DATABRICKS_CONFIG = {
    # Databricks workspace URL
    # Example: "https://your-workspace.cloud.databricks.com"
#    "server_hostname": "https://adb-8248746818676744.4.azuredatabricks.net",
    "server_hostname": "https://adb-6751461761521240.0.azuredatabricks.net",

    # HTTP path to the SQL warehouse or cluster
    # Example: "/sql/1.0/warehouses/abc123def456"
    "http_path": "/sql/1.0/warehouses/adacb2febee2226e",

    # Database and table configuration
    "catalog": "retail_systems_qa",
    "schema": "store_enablement",
    "table": "user_course_completion_staging",
}

# Query configuration
QUERY_CONFIG = {
    # Maximum number of rows to fetch
    "max_rows": 1000,

    # Query timeout in seconds
    "timeout": 60,
}
