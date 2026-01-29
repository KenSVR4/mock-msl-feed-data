# content_assignments table
## Purpose
The Entities in the table represent a training assignment that was given to a particular employee (aka 'ba').
The training that the employee is supposed to do is a Content in the training catlog.

## Table structure
The content_assignments table structure is as follows -
CREATE TABLE <catalog>.<schema>.content_assignments
 ( ba_id INT, 
 content_id INT, 
 assignment_date TIMESTAMP, 
 update_date DATE, 
 assignment_begin_date TIMESTAMP, 
 assignment_due_date TIMESTAMP, 
 content_type STRING) 
 USING delta TBLPROPERTIES ( 'delta.minReaderVersion' = '1', 'delta.minWriterVersion' = '2')

 ## Catalog and Schema details
 The schema for this table will be 'store_enablement'
 The catalog varies by environment: for DEV2 env it is retail_systems_dev, and for QA1 env it is retail_systems_qa

 ## Database
 The table is housed in databricks.

