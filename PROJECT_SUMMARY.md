# Project Summary: Metagenome Sample Tracker

This document summarizes the work done to create a new, robust system for tracking metagenomic samples and their associated metadata.

## 1. Overview

The primary goal of this project is to replace an ad-hoc system of tracking samples in various Excel spreadsheets with a centralized, secure, and user-friendly web application. 

The architecture is designed around a two-phase process to ensure that sensitive patient data is handled securely and kept separate from the main application's de-identified data.

1.  **Phase 1: De-identification**: A standalone script, intended for a secure environment, processes raw Excel files to create a de-identified linkage key.
2.  **Phase 2: Harmonization & Import**: A second process uses the linkage key to create a clean, unified dataset, which is then imported into a new Django web application for management and analysis.

## 2. Data Processing Pipeline

### De-identification (`deidentification_tool/`)

This self-contained Python script is the only component that ever handles Protected Health Information (PHI).

-   **Input**: A collection of Excel files with inconsistent naming and overlapping data.
-   **Process**:
    1.  It reads all sheets from all provided Excel files.
    2.  It scans for columns containing patient identifiers (e.g., MRN, UPN, Internal ID).
    3.  It intelligently links these different identifiers to a single unique individual.
    4.  For each unique individual identified, it generates a new, random, and unique **Subject ID** (e.g., `SUBJ-407A9B19`).
-   **Output**: A sensitive file named `SECURE_linkage_key.csv` that maps the new `subject_id` to all of the original legacy identifiers. This file must be stored securely.

### Harmonization (`sample_importer/` and `run_harmonization.py`)

This process takes the de-identified linkage key and the raw data to produce the final clean dataset.

-   **Input**: The `SECURE_linkage_key.csv` and the original Excel files.
-   **Process**:
    1.  It uses the linkage key to replace all legacy patient identifiers with the new de-identified `subject_id`.
    2.  It standardizes column names (e.g., `Collection Date`, `collection_dt`, `sample_date` all become `collection_date`).
    3.  It generates a unique **Sample Barcode** for each sample record (e.g., `SUBJ-407A9B19_2024-10-05_Stool`), which serves as the unique primary key for a sample.
-   **Output**: A clean, de-identified, and unified dataset named `harmonized_deidentified_samples.tsv`.

## 3. The Django Web Application (`webapp/`)

A new Django application was built from the ground up to provide a web interface for the clean data.

-   **Database Models**: The database schema is designed for clarity and scalability:
    -   `Subject`: A table that stores the unique, de-identified `subject_id` for each person.
    -   `CrudeSample`: A table that stores all information for a specific sample, including its unique `barcode`, `collection_date`, `sample_source`, and a foreign key that links it to a `Subject`.
-   **Data Import**: A custom management command, `import_samples`, was created. This command reads the `harmonized_deidentified_samples.tsv` file and populates the `Subject` and `CrudeSample` tables in the database.
-   **User Interface**: The application provides a full suite of basic features for data management:
    -   A main page that lists all samples in the database.
    -   A form for creating new samples.
    -   Functionality to Edit and Delete existing samples.
    -   A secure login/logout system.
    -   A full-featured Admin Panel (`/admin`) for direct database management.

## 4. Relationship with `mgml_sampledb`

This is a key point of clarification: this new application is being built as a **modern, standalone replacement** for the existing `mgml_sampledb` application. It **does not** interface with or modify the old application directly.

Our strategy has been to **harmonize** the new application with the old one by incorporating its best features while building a better structure:

-   **Improved Database Design**: We have implemented a normalized database schema with separate `Subject` and `CrudeSample` tables. This is a more robust and scalable design than the original application's, and the intention is for this new structure to become the standard going forward.
-   **Consistent Naming**: Where it made sense, we have adopted the naming conventions from the old application. For example, our unique sample identifier is named `barcode` and the sample type is named `sample_source` to match the old system, which will make an eventual data migration much easier.
-   **Familiar Look and Feel**: We have copied the base HTML template and custom CSS from the old application. This ensures that when users begin using this new system, the interface will look and feel familiar, providing a seamless transition.

The eventual goal is for this new application to completely replace the old one. The small amount of data in the existing `mgml_sampledb` can be migrated into this new, superior system when it is ready for production deployment.

---

## Appendix: De-identification Workflow on a Secure Computer

This section outlines the steps to run the de-identification process on a separate, secure computer (e.g., a hospital-approved Windows desktop).

**Prerequisites:**
- Python must be installed on the computer. You can download it from the official Python website.

**Steps:**

1.  **Transfer the Tool**: Copy the entire `deidentification_tool` folder from this project to the secure computer.

2.  **Install Dependencies**:
    -   Open a command prompt or PowerShell on the secure computer.
    -   Navigate into the `deidentification_tool` folder.
    -   Run the following command to install the necessary Python libraries:
        ```
        pip install -r requirements.txt
        ```

3.  **Run the Script**:
    -   In the same command prompt, while inside the `deidentification_tool` folder, run the script:
        ```
        python deidentify.py
        ```

4.  **Select Files**:
    -   A file selection window will pop up.
    -   Navigate to the location of your Excel files, select all the files you want to process, and click "Open".

5.  **Retrieve the Output**:
    -   The script will run and create the `SECURE_linkage_key.csv` file in the main project directory (one level above `deidentification_tool`).
    -   This file contains the mapping between the original identifiers and the new, de-identified `subject_id`s.

6.  **Secure Transfer**: Securely transfer this `SECURE_linkage_key.csv` file to your main development machine and place it in the root of the `metagenome_sample_tracker` project directory. It is now ready to be used by the `run_harmonization.py` script.
