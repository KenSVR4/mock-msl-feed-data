# UserCompletion file
A UserCompletion file is created by this process each time it is run.
The content of the file is not important.

## File Creation Logic
The process copies the file in sample_files called UserCompletion_v2_YYYY_m_d_1_000001.csv amd copies
it into the generated_files directory with a new file name. The new file name is decided by changing the sample files 'YYYY_m_d' pattern to current 4 digit year for 'YYYY', current 1 or 2 digit month for 'm', and currend 1 or 2 digit day for 'd'
