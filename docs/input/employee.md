# Employees
Employees work here and they sell merchandise. But they also take training courses that make them better at selling.

## Employee Types
Employees are classified as a certain type and the type determines their aggresiveness on taking training.
Type A - complete every assignment immediately
Type B - complete one assignment
Type F - complete no assignments

## How Employee completes training
When an employee completes a training they add a record to the completed_assignments file

## Employee Population
The population of employees who work here are in file input/employees.csv. It is a .csv file with a header row.

### File Format
The employees.csv file contains the following columns:
- **employee_id**: The unique identifier for the employee
- **employee_edu_type**: The employee type (a, b, or f)

### Comment Rows
Any row in the employees.csv file where the employee_id starts with '#' is treated as a comment and will be ignored during processing. This allows you to:
- Add descriptive comments within the file
- Temporarily disable specific employees without deleting their records
- Document test scenarios or notes

Example:
```csv
employee_id,employee_edu_type
# This is a comment row - ignored
63419,a
# 63492,a  <- This employee is commented out
75412,b
```
