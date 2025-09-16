# Project Summary: Unified Sample and Analysis Tracker

This document summarizes the architecture of the unified system for end-to-end sample tracking, from wet-lab processing to bioinformatics analysis.

## 1. Overview

The primary goal of this project is to create a single, centralized, and secure web application that tracks the entire lifecycle of a sample. This system merges the physical sample tracking capabilities of the existing `mgml_sampledb` with a new, robust system for tracking downstream analysis and data.

The architecture is composed of two main Django apps:

1.  **`sampletracking`**: The core wet-lab tracking system, adapted from the original `mgml_sampledb` project. It manages the physical sample hierarchy: `CrudeSample` -> `Aliquot` -> `Extract` -> `SequenceLibrary`.
2.  **`analysis`**: A new application responsible for generating, storing, and managing the final, opaque `sample_id` used for bioinformatics analysis.

## 2. The Django Web Application (`webapp/`)

The application provides a comprehensive web interface for managing the entire sample lifecycle.

### Data Models

The database schema is designed to provide a complete audit trail for every sample:

-   **`sampletracking` app**:
    -   **`CrudeSample`**: The initial physical sample, identified by a scannable barcode.
    -   **`Aliquot`**: An aliquot derived from a `CrudeSample`.
    -   **`Extract`**: An extract (e.g., DNA, RNA, Protein) derived from an `Aliquot`.
    -   **`SequenceLibrary`**: A sequencing library prepared from an `Extract`.
    -   Each of these models has its own unique `barcode` to identify the physical item.

-   **`analysis` app**:
    -   **`AnalysisID`**: Stores the final, analysis-ready `sample_id`. It uses a GenericForeignKey to link to the final sample object, which can be either an `Extract` (for terminal analyses like metabolomics) or a `SequenceLibrary`.

### ID Generation

The system uses two distinct types of identifiers:

1.  **Physical Barcode**: A user-provided, scannable barcode that uniquely identifies each physical item (`CrudeSample`, `Aliquot`, etc.) in the wet lab.
2.  **Analysis Sample ID**: A system-generated, opaque ID created at the end of the wet-lab process. This ID is used for all downstream bioinformatics and data tracking. It is randomly generated and includes a prefix based on the intended analysis type (e.g., `WGS_`, `MSS_`, `MET_`).

### User Interface

The application provides a full-featured admin interface (`/admin`) for all data management, including:

-   Registering and tracking samples through the wet-lab pipeline.
-   A custom action to **Generate Analysis ID(s)** for selected `Extracts` or `SequenceLibraries` that are ready for analysis.

## 3. Legacy Data Import Workflow

A custom workflow has been developed to import thousands of existing legacy samples into the new system.

### Step 1: Prepare Your Data File

1.  Following the original project's de-identification workflow, run the `deidentification_tool` on your raw Excel files to produce the `SECURE_linkage_key.csv`.
2.  Then, run the `run_harmonization.py` script. This will use the linkage key and your raw data to produce the `harmonized_deidentified_samples.tsv` file.
3.  **Crucially:** Open the `harmonized_deidentified_samples.tsv` file in a spreadsheet program and manually add the two new required columns:
    -   `Extract Type` (e.g., DNA, RNA, Protein)
    -   `Analysis Type` (e.g., WGS, MSS, PTM)
    Fill these in for all your legacy samples and save the file.

### Step 2: Run the Import

Once your `.tsv` file is prepared and saved, open your terminal, navigate to the project root (`/home/david/projects/metagenome_sample_tracker/`), and run the following command:

```bash
python3.12 webapp/manage.py import_legacy_data /path/to/your/harmonized_deidentified_samples.tsv
```

**Remember to replace `/path/to/your/harmonized_deidentified_samples.tsv` with the actual path to your file.**

The script will then process the entire file, create all the necessary placeholder records for your legacy samples, and generate a new, correctly-prefixed analysis `sample_id` for each one.

---

## 4. TODO / Next Steps

This section outlines important tasks to complete when resuming work on the project.

-   **Run the Legacy Data Import**: The immediate next step is to prepare the `harmonized_deidentified_samples.tsv` file with the required extra columns and run the import command to populate the database with legacy data.

-   **Configure User Groups & Permissions**: The application views currently require specific permissions to access. For the application to be usable by non-superusers, we need to use the Django admin interface to create user groups (e.g., "Lab Staff", "Bioinformatician", "Sample Collectors") and assign the correct model permissions (e.g., `sampletracking | extract | Can add extract`) to each group.

-   **Write Automated Tests**: The project currently lacks automated tests. We should create a suite of unit and integration tests to verify all functionality, especially the sample lifecycle logic and the legacy data import, to ensure the application is robust.

-   **Review and Refine Frontend**: After data has been imported, the web interface should be thoroughly tested to find and fix any broken links, styling issues, or pages that need to be adapted to the new integrated logic.

-   **Plan for Production Deployment**: The current setup uses a development server and an SQLite database. Before the application is used by the full team, a production deployment plan is needed. This includes configuring a production-grade web server (like Gunicorn with Nginx) and migrating the database to the production MySQL server.
