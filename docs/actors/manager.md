# manager is an actor that assigns training to employees
## manager knows about employees assignments
The manager will know the current training assignments for each employee by querying the databricks table retail_systems_qa.store_enablement.user_course_completion_staging. For each assignment the manager can use UserCourseStatus field to see if the employee has Completed the training.
The manager will print output for each employee so we can see the training name and the status of completion.

