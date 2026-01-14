# ConentUserCompletion file
When an employee completes a training the transaction is recorded in a new ContentUseCompletion file. It is a .csv file with a header row. The header row is "UserId","ContentId","DateStarted","DateCompleted"
Each time the process runs it will create a new file and the filename will have the Year (YY) Month (MM) day (DD) and a randmon (RAND) six character alphanumeric value. Like ContentUserCompletion_V2_:YY_:MM_:DD_1_:RAND.csv
All of the employees completed transactions will be appended into the one new output file.

## File description
An example file is sample_files/ContentUserCompletion_V2_2025_10_28_1_10e4ec.csv
Fields:
UserId the employee_id
ContentId the training identifier like the content_id. The value has commas. It is not an integer. It has commas to help human readability. AZZ
DateStarted when the employee began the training in iso-8601 format 
DateCompleted when the employee finished the training in iso-8601 format 
