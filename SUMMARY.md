# BTC Fake - Project Summary

## Overview

BTC Fake is a training data simulator that generates realistic training completion and assignment files for Sephora's learning management system. It simulates the behavior of a third-party vendor (BTC) that would normally produce these files based on real employee training activity.

## Business Purpose

This project enables testing and development of learning management systems without requiring:
- Access to production data
- Dependency on external vendors
- Real employee training activity

It provides controlled, repeatable test data that matches the exact format and business logic of actual vendor-generated files.

## What It Simulates

### 1. Employee Training Behavior
The system models three types of employees based on their engagement with training. Employees receive training from two sources (manager assignments and AI recommendations) and complete them based on their type:
- **Type A (Engaged)**: Completes all training (both manager-assigned and AI-recommended)
- **Type B (Moderate)**: Completes one training (from combined manager and AI list)
- **Type F (Disengaged)**: Does not complete training

### 2. AI-Powered Recommendations
Integrates with Sephora's ML Training Recommender API to get personalized training recommendations for each employee, simulating a real recommendation engine.

### 3. Manager Assignment Workflow
Simulates managers assigning training content to their teams by:
- Selecting the most recent "Daily Dose" training content
- Assigning up to 3 training items to all employees
- Setting realistic assignment windows (Monday start, Saturday due date)

## Data Flow

```
1. PREPROCESSING
   └─> Download latest training content catalogs from SFTP server

2. MANAGER SIMULATION
   ├─> Filter training content (Daily_Dose_BA = TRUE)
   ├─> Select 3 most recent items
   ├─> Assign to all employees
   └─> Generate NonCompletedAssignments file

3. EMPLOYEE SIMULATION
   ├─> Read employee population from CSV
   ├─> For each employee:
   │   ├─> Load manager assignments from NonCompletedAssignments file
   │   ├─> Get AI recommendations from ML API
   │   ├─> Combine manager assignments + AI recommendations
   │   ├─> Simulate completions based on employee type
   │   └─> Record completed training with source (manager or AI)
   └─> Generate ContentUserCompletion file
```

## Output Files

### ContentUserCompletion
Records of employees who completed training courses:
- Employee ID
- Training content ID
- Start and completion timestamps
- Simulates successful training completion

### NonCompletedAssignments
Manager-assigned training that employees haven't completed yet:
- Employee ID
- Assigned training content
- Assignment dates (start and due)
- Simulates pending work

## Technical Approach

- **Language**: Python 3.8+
- **Interface**: Jupyter Notebook for interactive execution and visibility
- **Data Sources**:
  - SFTP server for production-like training catalogs
  - CSV file for employee population
  - REST API for ML recommendations
- **Output Format**: CSV files matching vendor specifications exactly

## Use Cases

1. **QA Testing**: Generate test data for learning management system testing
2. **Development**: Provide realistic data for feature development
3. **Load Testing**: Create large datasets to test system performance
4. **Integration Testing**: Validate SFTP file processing and database imports
5. **Demo/Training**: Create demonstration data for stakeholder presentations

## Key Features

- ✓ Realistic employee behavior modeling
- ✓ Integration with actual ML recommendation API
- ✓ Production-like SFTP file download
- ✓ Exact vendor file format compliance
- ✓ Configurable employee populations
- ✓ Date-range batch processing via shell script
- ✓ Reproducible test data generation

## Value Proposition

**Replaces**: Manual test data creation, dependency on vendor files, production data copying

**Provides**: On-demand, realistic, compliant test data that accelerates development and testing cycles while maintaining data privacy and security.
