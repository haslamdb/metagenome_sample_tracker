# Metagenome Sample Tracker

This project is designed to consolidate metagenomic sample metadata from various Excel spreadsheets into a unified, queryable database.

It consists of three main components:

1.  **De-identification Tool (`deidentification_tool/`)**: A standalone Python script for securely handling and de-identifying sensitive patient data (e.g., MRNs). This is designed to be run in a secure, firewalled environment.

2.  **Sample Importer (`sample_importer/`)**: A Python package responsible for reading different Excel formats, harmonizing the data into a consistent model, and preparing it for database insertion.

3.  **Web Application (`webapp/`)**: A Django-based web application that will house the final, de-identified database, providing an interface for querying and managing the sample data.

### Structure

-   `data/`: Raw data storage (e.g., Excel files). **This directory is in the .gitignore and will not be version controlled.**
-   `deidentification_tool/`: Script for de-identifying sensitive data.
-   `sample_importer/`: Python package for data extraction and transformation (ETL).
-   `webapp/`: Django project for the database and user interface.
