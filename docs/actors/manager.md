# manager is an actor that assigns training to employees
## manager chooses training to assign to employees
The manager chooses Content to assign from the Content in the standalone_content file that was
most recently downloaded at the start of the project.
Manager will give up to 3 Contents to all the employees.
The manager tries to find 3 Contents to assign to employees.
A Content is chosen only if the field Daily_Dose_BA for that Content is TRUE.
Content with the most recent date in the field CreateDate are prioritized over older ones.

## manager saves the assignments into a new file
The Manager knows how to fashion a NonCompletedAssignments file and save it into the directory 'generated_files'

## manager considers employees current assignments
The manager knows employee state by using BOTH the content_assignments table AND the
content_completion table. The content_assignments table has all assignments in history,
and the completed_assignments table has those which employee has completed. 
The manager knows all of the open assignments by subtracing the completed assignments
from the content assignments from the tables for an employee.
Remember an employee is synonomous to a ba.
Every assignment that is open is to be written into the NonCompletedAssignments file product.
Tha manager puts the open trainings from the table query into the file before adding the 
new assignments they made into the file.
