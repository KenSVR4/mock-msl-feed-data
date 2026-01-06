# btf fake project
This project produces fake files that would normally be produced by btc. btc is a vendor and they know about our SFTP server and file specs.

## project purpose
The project is btc_fake. The purpose is to simulate real world employees who spend some of their time taking training courses. Described in employee.md.

## structure
The coding standards come from the BAPH project which is in a folder on level up from this one.

## architecture
The project is a python notebook. An engineer should be able to run the project on macOS. The instructions for settting up dependencies  will be contained in README.md.

## execution
The process knows about the employee popluation. For each employee the recommendation_api will provide training recommendations. An employee has a type and based on that type the employee will complete some or all training. When employee completes training the process will write a line into the generated_files folder in a new ContentUserCompletion file in .csv format. 
At the end the process will summarize for each user the training they completed. One one line it prints the employee_id, and then the training courses completed. It prints the name of the new generated file. 

## User interface
The process can be run as a jupyter notebook using a tool like Curstor or VS Code. It can also be run using a browser that encapsulates the notebook. 
