#!/usr/bin/env python3
"""
BTC Fake - Gradio Web Application
Training Completion Simulator with Interactive Web Interface

This is the UI layer that uses simulation_core.py for all business logic.
"""

import gradio as gr
import pandas as pd
import os
import io
import zipfile
from dotenv import load_dotenv

# Import shared business logic
import simulation_core as core

# Load environment variables
load_dotenv()

# Load configuration
config = core.load_config()


# ==============================================================================
# Gradio UI Functions
# ==============================================================================

def run_simulation(employee_file, publish_enabled, progress=gr.Progress()):
    """
    Run the complete BTC training simulation.

    Args:
        employee_file: Uploaded CSV file with employee data
        publish_enabled: Whether to publish files to SFTP outbound
        progress: Gradio progress tracker

    Returns:
        Tuple of (summary_text, download_file_path)
    """
    summary_lines = []

    def add_progress(msg):
        """Add message to summary and update progress"""
        summary_lines.append(msg)
        progress(0.1, desc=msg[:100])  # Show first 100 chars in progress

    try:
        add_progress("=" * 80)
        add_progress("BTC FAKE - TRAINING COMPLETION SIMULATOR")
        add_progress("=" * 80)
        add_progress("")

        # Step 0: Cleanup - Remove old files from previous runs
        add_progress("STEP 0: Cleanup")
        add_progress("-" * 80)

        core.cleanup_output_directory(config, add_progress)
        add_progress("")

        # Step 1: Load employee file
        add_progress("STEP 1: Loading Employee Data")
        add_progress("-" * 80)

        if employee_file is None:
            return "Error: No employee file uploaded", None

        employees_df, filtered_count = core.load_and_filter_employees(
            employee_file.name, add_progress)
        add_progress("")

        # Step 2: Download files from SFTP
        add_progress("STEP 2: Downloading Files from SFTP")
        add_progress("-" * 80)

        course_catalog_path = core.download_most_recent_file_from_sftp(
            config, 'course_catalog', add_progress)
        standalone_content_path = core.download_most_recent_file_from_sftp(
            config, 'standalone_content', add_progress)

        if not course_catalog_path or not standalone_content_path:
            return "\n".join(summary_lines) + "\n\nError: Failed to download required files", None

        add_progress(f"Downloaded course catalog: {os.path.basename(course_catalog_path)}")
        add_progress(f"Downloaded standalone content: {os.path.basename(standalone_content_path)}")
        add_progress("")

        # Load standalone content for lookups
        standalone_df = pd.read_csv(standalone_content_path)

        # Step 3: Manager Assignments
        add_progress("STEP 3: Creating Manager Assignments")
        add_progress("-" * 80)

        employee_ids_list = employees_df['employee_id'].tolist()

        # Query Databricks for open assignments
        open_assignments_df = core.get_open_assignments_from_databricks(
            config, employee_ids_list, add_progress)

        # Convert Databricks assignments to output format
        databricks_assignments = core.convert_databricks_assignments_to_output_format(
            open_assignments_df)

        add_progress(f"Loaded {len(databricks_assignments)} open assignments from Databricks")

        # Create new manager assignments
        new_manager_assignments = core.create_manager_assignments(
            employees_df, add_progress)

        # Combine all assignments
        all_assignments = databricks_assignments + new_manager_assignments
        add_progress(f"Total assignments: {len(all_assignments)}")

        # Write NonCompletedAssignments file
        assignments_path = core.write_non_completed_assignments_file(
            all_assignments, config['output_dir'])
        add_progress(f"Generated: {os.path.basename(assignments_path)}")
        add_progress("")

        # Step 4: Employee Training Simulation
        add_progress("STEP 4: Simulating Employee Training Completions")
        add_progress("-" * 80)

        all_completions = []

        for employee in employees_df.itertuples():
            employee_id = employee.employee_id
            employee_type = employee.employee_edu_type

            add_progress(f"Processing employee {employee_id} (type {employee_type})...")

            # Get AI recommendations
            ai_recommendations = core.get_training_recommendations(config, employee_id, add_progress)

            # Get manager assignments
            manager_assignments = core.get_manager_assignments_for_employee(
                employee_id, assignments_path, standalone_df)

            # Process employee
            completions = core.process_employee(
                config, employee_id, employee_type,
                manager_assignments, ai_recommendations,
                standalone_df, add_progress)

            all_completions.extend(completions)

            if completions:
                add_progress(f"  Completed {len(completions)} training(s)")

        add_progress(f"Total completions: {len(all_completions)}")
        add_progress("")

        # Step 5: Generate Output Files
        add_progress("STEP 5: Generating Output Files")
        add_progress("-" * 80)

        if all_completions:
            output_path = core.write_content_user_completion_file(
                all_completions, config['output_dir'])
            add_progress(f"Generated: {os.path.basename(output_path)}")

            # Update NonCompletedAssignments file
            initial_count, removed_count = core.update_non_completed_assignments_file(
                assignments_path, all_completions)
            add_progress(f"Updated NonCompletedAssignments: removed {removed_count} completed assignments")
        else:
            add_progress("No completions to write")
            output_path = None

        # Generate UserCompletion file (dummy file)
        user_completion_path = core.generate_user_completion_file_from_template(
            config, add_progress)

        add_progress("")

        # Step 6: Publish to SFTP (if enabled)
        if publish_enabled:
            add_progress("STEP 6: Publishing Files to SFTP Outbound")
            add_progress("-" * 80)

            files_to_publish = []
            if output_path and os.path.exists(output_path):
                files_to_publish.append(output_path)
            if os.path.exists(assignments_path):
                files_to_publish.append(assignments_path)
            if os.path.exists(user_completion_path):
                files_to_publish.append(user_completion_path)
            if course_catalog_path:
                files_to_publish.append(course_catalog_path)
            if standalone_content_path:
                files_to_publish.append(standalone_content_path)

            # Override config for this run
            publish_config = config.copy()
            publish_config['sftp_publish_enabled'] = True

            success = core.publish_files_to_sftp_outbound(
                publish_config, files_to_publish, add_progress)

            if success:
                add_progress("✓ All files published successfully")
            else:
                add_progress("⚠ Some files failed to publish")

            add_progress("")

        # Step 7: Create downloadable ZIP file
        add_progress("Creating download package...")
        zip_buffer = io.BytesIO()

        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # Add generated files
            if output_path and os.path.exists(output_path):
                zip_file.write(output_path, os.path.basename(output_path))
            if os.path.exists(assignments_path):
                zip_file.write(assignments_path, os.path.basename(assignments_path))
            if os.path.exists(user_completion_path):
                zip_file.write(user_completion_path, os.path.basename(user_completion_path))

            # Add downloaded files
            if course_catalog_path and os.path.exists(course_catalog_path):
                zip_file.write(course_catalog_path, os.path.basename(course_catalog_path))
            if standalone_content_path and os.path.exists(standalone_content_path):
                zip_file.write(standalone_content_path, os.path.basename(standalone_content_path))

        zip_buffer.seek(0)

        # Save ZIP to temp file
        zip_path = os.path.join(config['output_dir'], "generated_files.zip")
        with open(zip_path, 'wb') as f:
            f.write(zip_buffer.read())

        add_progress("")
        add_progress("=" * 80)
        add_progress("SIMULATION COMPLETE")
        add_progress("=" * 80)

        summary = "\n".join(summary_lines)
        return summary, zip_path

    except Exception as e:
        error_msg = f"\n\nERROR: {str(e)}"
        summary_lines.append(error_msg)
        return "\n".join(summary_lines), None


def test_api(employee_id_str):
    """Test ML Training Recommender API"""
    try:
        employee_id = int(employee_id_str)

        recommendations = core.get_training_recommendations(config, employee_id)

        if recommendations:
            result = f"✓ API Success!\n\nRecommendations for employee {employee_id}:\n"
            for rec in recommendations:
                content_id = rec.get("recommended_content_id", "N/A")
                content_name = rec.get("recommended_content", "N/A")
                result += f"  - {content_id}: {content_name}\n"
            return result
        else:
            return f"⚠ API returned no recommendations for employee {employee_id}"

    except Exception as e:
        return f"✗ API Error: {str(e)}"


def show_config():
    """Display current configuration"""
    config_text = "Current Configuration:\n"
    config_text += "=" * 80 + "\n\n"

    config_text += "API Configuration:\n"
    config_text += f"- Base URL: {config['api_base_url']}\n"
    config_text += f"- Endpoint: {config['api_endpoint']}\n"
    config_text += f"- Timeout: {config['api_timeout']}s\n\n"

    config_text += "Databricks:\n"
    config_text += f"- Host: {config['databricks_host']}\n"
    config_text += f"- Catalog: {config['databricks_catalog']}\n"
    config_text += f"- Schema: {config['databricks_schema']}\n\n"

    config_text += "SFTP Inbound:\n"
    config_text += f"- Host: {config['sftp_inbound_host']}\n"
    config_text += f"- User: {config['sftp_inbound_user']}\n"
    config_text += f"- Remote Path: {config['sftp_inbound_remote_path']}\n\n"

    config_text += "SFTP Outbound:\n"
    config_text += f"- Host: {config['sftp_outbound_host']}\n"
    config_text += f"- User: {config['sftp_outbound_user']}\n"
    config_text += f"- Remote Path: {config['sftp_outbound_remote_path']}\n"
    config_text += f"- Publishing Enabled: {config['sftp_publish_enabled']}\n\n"

    config_text += "File Paths:\n"
    config_text += f"- Employees File: {config['employees_file']}\n"
    config_text += f"- Output Dir: {config['output_dir']}\n"
    config_text += f"- SFTP Local Dir: {config['sftp_local_dir']}\n"

    return config_text


# ==============================================================================
# Gradio Interface
# ==============================================================================

with gr.Blocks(title="BTC Fake - Training Simulator") as app:
    gr.Markdown("# 🎓 BTC Fake - Training Completion Simulator")
    gr.Markdown("Generate realistic training completion data for testing and development")

    with gr.Tabs():
        # Tab 1: Run Simulation
        with gr.Tab("Run Simulation"):
            gr.Markdown("### Upload employee data and run the simulation")

            employee_file_input = gr.File(label="Upload Employees CSV", file_types=[".csv"])

            publish_checkbox = gr.Checkbox(
                label="Enable SFTP Publishing",
                value=False
            )

            run_button = gr.Button("🚀 Run Simulation", variant="primary")
            output_summary = gr.Textbox(
                label="Simulation Summary",
                lines=40,
                max_lines=60
            )
            download_button = gr.File(label="Download Generated Files (ZIP)")

            run_button.click(
                fn=run_simulation,
                inputs=[employee_file_input, publish_checkbox],
                outputs=[output_summary, download_button]
            )

        # Tab 2: Test ML Reco API
        with gr.Tab("Test ML Reco API"):
            gr.Markdown("### Test ML Training Recommender API connectivity")

            employee_id_input = gr.Textbox(
                label="Employee ID",
                placeholder="Enter employee ID (e.g., 88563)"
            )
            test_api_button = gr.Button("🧪 Test API Connection")
            api_output = gr.Textbox(label="API Response", lines=20)

            test_api_button.click(
                fn=test_api,
                inputs=[employee_id_input],
                outputs=[api_output]
            )

        # Tab 3: Configuration
        with gr.Tab("Configuration"):
            gr.Markdown("### View current configuration from .env file")

            config_button = gr.Button("📋 Show Configuration")
            config_output = gr.Textbox(label="Current Configuration", lines=30)

            config_button.click(
                fn=show_config,
                inputs=[],
                outputs=[config_output]
            )

    gr.Markdown("---")
    gr.Markdown("Built with [Gradio](https://gradio.app) | Powered by simulation_core.py")


if __name__ == "__main__":
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False
    )
