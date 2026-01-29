# btf fake project
This project produces fake files that would normally be produced by btc. btc is a vendor and they know about our SFTP server and file specs.

## project purpose
The project is btc_fake. The purpose is to simulate real world employees who spend some of their time taking training courses. Described in employee.md.

## structure
The coding standards come from the BAPH project which is in a folder on level up from this one.

## architecture
The project is a python notebook. An engineer should be able to run the project on macOS. The instructions for settting up dependencies  will be contained in README.md.

## preprocessing
The process will download most recent course_catalog file from SFTP location into a local directory. 

## execution
The process knows about the employee popluation. For each employee the recommendation_api will provide training recommendations. An employee has a type and based on that type the employee will complete some or all training. When employee completes training the process will write a line into the generated_files folder in a new ContentUserCompletion file in .csv format. 
At the end the process will summarize for each user the training they completed. One one line it prints the employee_id, and then the training courses completed. It prints the name of the new generated file. 

## User interface
The process can be run as a jupyter notebook using a tool like Curstor or VS Code. It can also be run using a browser that encapsulates the notebook. 

## Runtime

### Local Development with VS Code
Developers will run this project locally using VS Code with the Databricks extension installed:

1. **Setup**:
   - Install the Databricks extension in VS Code
   - Configure `.env` file with Databricks connection details (token, host, http_path)
   - Connect to Databricks workspace through VS Code extension

2. **Development Workflow**:
   - Run the Jupyter notebook locally in VS Code
   - The notebook connects to Databricks to query the `content_assignments` table
   - Downloads files from SFTP server
   - Calls the ML Training Recommender API
   - Generates output files in `generated_files/` directory

3. **Testing**:
   - Use DEV2 environment (`retail_systems_dev` catalog)
   - Validate queries against `content_assignments` table
   - Test full workflow end-to-end locally

### Databricks Native Execution
Eventually, the project will be packaged and deployed to run natively inside Databricks:

1. **Packaging**:
   - Convert Jupyter notebook to Databricks notebook format
   - Package dependencies
   - Configure environment-specific settings (catalog, schema)

2. **Deployment**:
   - Upload to Databricks workspace
   - Configure as Databricks job/workflow
   - Set up schedule for automated execution

3. **Execution**:
   - Runs directly in Databricks compute cluster
   - Accesses tables natively without SQL connector
   - Can be scheduled or triggered manually
   - Output files written to Databricks File System (DBFS) or mounted storage
