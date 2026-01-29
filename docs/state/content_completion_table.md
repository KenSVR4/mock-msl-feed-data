# content_completion table
## Purpose
The Entities in the table represent a training content that a particular employee (aka 'ba') completed.
For example a training Content that is a
movie file explaining a Work Procedure was watched in its entirety by employee.

## Table structure
The content_completion table structure is as follows -
CREATE TABLE content_completion (
  ba_id INT,
  content_id INT,
  completion_date DATE)
USING delta
TBLPROPERTIES (
  'delta.minReaderVersion' = '1',
  'delta.minWriterVersion' = '2')

 ## Catalog and Schema details
 The schema for this table will be 'store_enablement'
 The catalog varies by environment: for DEV2 env it is retail_systems_dev, and for QA1 env it is retail_systems_qa

 ## Database
 The table is housed in databricks.

