# The standalone_content file
This type of file is a .csv file that represents all training Content.
A content can be a video file, or a .pdf or document.

## Sample file name and naming standard
StandAloneContent_v2_2026_1_6_1_77434e.csv is a sample file name.
Inside the filename to the right of 'V2_' there is a year,
month, and day value separated by underscore. And then there is a sequence number and a random.

## Processing
The system will connect to SFTP server, and pick the standalone_content file that is most recent
and download it into the local folder downloaded_files.
Recency is determined by the date components inside the file name. 

Refer to SFTP.md for connectity details.
