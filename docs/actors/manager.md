# manager is an actor that assigns training to employees
## manager chooses training to assign
The manager chooses Content to assign from the Content in the standalone_content file that was
most recently downloaded at the start of the project.
Manager will give up to 3 Contents to all the employees.
The manager tries to find 3 Contents to assign to employees.
A Content is chosen only if the field Daily_Dose_BA for that Content is TRUE.
Content with the most recent date in the field CreateDate are prioritized over older ones.

## manager saves the assignments into a new file
The Manager knows how to fashion a NonCompletedAssignments file and save it into the directory 'generated_files'


## manager considers employees current assignments
This feature will be implemented later. Ignore it for now.
<!-- The manager will know the current training assignments for each employee by querying the databricks table retail_systems_qa.store_enablement.user_course_completion_staging. For each assignment the manager can use UserCourseStatus field to see if the employee has Completed the training.
The manager will print output for each employee so we can see the training name and the status of completion. -->

