# NonCompletedAssignments file
Training content that a Manager assigns to an Employee appear
in the NonCompletedAssignments file until the Employee completes the training.
It is a .csv file with a header row. The header row is
"UserID","CreateDate_text","RequestId","TrainingElementId","Start_Date_text","DueDate_text","ContentType"

The Manager actor knows how to create a NonCompletedAssignments file each time the process is run. The Manager places the assignments that they have chosen for the employees into the file. 

Each time the process runs it will create a new file and the filename will have the Year (YY) Month (MM) day (DD) and a randmon (RAND) six character alphanumeric value. For example Non_Completed_Assignments_V2_2026_1_7_1_533f6b.csv

## File description
An example file is samples/ContentUserCompletion_V2_2025_10_28_1_10e4ec.csv
Fields:
UserId is the employee_id
CreatedDate_text will be the current time minus 5 minutes.
RequestId will be current date time and random 3 numbers like MMDDYY:Random
TrainingElementId is the id of the Content that the manager chose to assign to the employee.
Start_Date_text is always the most recent past Monday at 00:01
DueDate_text is always the next upcoming Saturday at 13:13:59
ContentType is always 'Media'
