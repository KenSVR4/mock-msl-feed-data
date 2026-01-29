# Employees File Format

## File Location
`input/employees.csv`

## Purpose
Contains the population of employees used in the training completion simulation.

## File Structure

### Header Row
```csv
employee_id,employee_edu_type
```

### Data Columns

| Column | Type | Description | Valid Values |
|--------|------|-------------|--------------|
| employee_id | Integer | Unique identifier for the employee | Any positive integer |
| employee_edu_type | String | Employee training engagement type | a, b, or f |

### Employee Types

- **Type A**: Completes all training (both manager-assigned and AI-recommended)
- **Type B**: Completes one training from combined list (manager + AI)
- **Type F**: Completes no training

## Comment Rows

Rows where `employee_id` starts with `#` are treated as comments and ignored during processing.

### Use Cases for Comments

1. **Documentation**: Add descriptive notes within the file
   ```csv
   # Production employees
   63419,a
   63492,b
   ```

2. **Temporarily Disable**: Comment out employees without deleting their records
   ```csv
   # 75412,b  <- Temporarily disabled for testing
   ```

3. **Test Scenarios**: Document test configurations
   ```csv
   # Test scenario: High engagement group
   63419,a
   85038,a
   # Test scenario: Low engagement group
   86994,f
   ```

## Example File

```csv
employee_id,employee_edu_type
# Active employees - Type A (high engagement)
63419,a
63492,a
85038,a
# Active employees - Type B (moderate engagement)
75412,b
# Active employees - Type F (low engagement)
86994,f
88563,f
# Disabled for testing
# 104829,a
# 109828,a
```

## Processing Behavior

When the simulation loads the employees file:
1. Reads all rows from the CSV
2. Filters out any rows where `employee_id` starts with '#'
3. Logs the number of comment rows filtered
4. Processes remaining employees for training simulation

Example output:
```
Loading employees from input/employees.csv...
Filtered out 3 comment row(s)
Loaded 26 employees
```
