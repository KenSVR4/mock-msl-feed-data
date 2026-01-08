# The course_catalog file
This type of file is a .csv file that represents training curriculum elements
like Courses and components of Courses. 

## Sample file name and naming standard
CourseCatalog_V2_2025_5_20_1_ec83a5.csv is a sample file name.
Inside the filename to the right of 'V2_' there is a year,
month, and day value separated by underscore. And then there is a sequence number and a random.

## Processing
The system will connect to SFTP server, and pick the course_catalog file that is most recent
and download it into the local folder downloaded_files.
Recency is determined by the date components inside the file name. 

Refer to SFTP.md for connectity details.