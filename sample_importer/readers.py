import pandas as pd
import os

def load_all_sheets_from_files(file_paths):
    """
    Loads all sheets from a list of Excel files into a single dictionary.

    Args:
        file_paths (list): A list of string paths to the Excel files.

    Returns:
        dict: A dictionary where keys are 'filename|sheetname' and values are DataFrames.
    """
    all_dfs = {}
    for path in file_paths:
        try:
            # sheet_name=None tells pandas to read all sheets
            sheets_dict = pd.read_excel(path, sheet_name=None)
            for sheet_name, df in sheets_dict.items():
                # Create a unique key for traceability
                source_key = f"{os.path.basename(path)}|{sheet_name}"
                all_dfs[source_key] = df
        except Exception as e:
            print(f"Could not read or process file: {path}. Error: {e}")
    return all_dfs
