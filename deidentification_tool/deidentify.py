import pandas as pd
import uuid
import os
from pathlib import Path
import tkinter as tk
from tkinter import filedialog

# --- Configuration ---
IDENTIFIER_COLUMN_MAP = {
    'MRN': 'mrn',
    'UPN': 'upn',
    'Internal_ID': 'pmid',
    'PMID': 'pmid',
    'patient_id': 'pmid'
}

def load_all_sheets_from_files(file_paths):
    """
    Loads all sheets from a list of Excel files into a single dictionary.
    """
    all_dfs = {}
    for path in file_paths:
        try:
            sheets_dict = pd.read_excel(path, sheet_name=None)
            for sheet_name, df in sheets_dict.items():
                source_key = f"{os.path.basename(path)}|{sheet_name}"
                all_dfs[source_key] = df
        except Exception as e:
            print(f"Could not read or process file: {path}. Error: {e}")
    return all_dfs

def create_identifier_linkage_key(dataframes_dict):
    """
    Scans all dataframes to find unique individuals and creates a master
    linkage key mapping all known legacy IDs to a new, random subject_id.
    """
    print("--- Phase 1: Creating Identifier Linkage Key ---")
    
    all_identifiers_list = []
    for source_key, df in dataframes_dict.items():
        df_renamed = df.rename(columns=IDENTIFIER_COLUMN_MAP)
        id_cols = ['mrn', 'upn', 'pmid']
        present_id_cols = [col for col in id_cols if col in df_renamed.columns]
        if not present_id_cols:
            continue
            
        df_ids = df_renamed[present_id_cols].copy()
        df_ids.dropna(how='all', inplace=True)
        
        for col in present_id_cols:
            df_ids[col] = df_ids[col].astype(str)

        all_identifiers_list.append(df_ids)

    if not all_identifiers_list:
        print("No identifiers found. Exiting.")
        return None, None

    master_ids_df = pd.concat(all_identifiers_list, ignore_index=True)
    master_ids_df.drop_duplicates(inplace=True)

    id_to_person_map = {}
    person_data = []
    
    for _, row in master_ids_df.iterrows():
        ids_in_row = {col: val for col, val in row.items() if pd.notna(val)}
        found_person_idx = None
        
        for id_type, id_val in ids_in_row.items():
            if id_val in id_to_person_map:
                found_person_idx = id_to_person_map[id_val]
                break
        
        if found_person_idx is not None:
            for id_type, id_val in ids_in_row.items():
                person_data[found_person_idx][id_type].add(id_val)
                id_to_person_map[id_val] = found_person_idx
        else:
            new_person_idx = len(person_data)
            new_person = {'mrn': set(), 'upn': set(), 'pmid': set()}
            for id_type, id_val in ids_in_row.items():
                new_person[id_type].add(id_val)
                id_to_person_map[id_val] = new_person_idx
            person_data.append(new_person)

    linkage_key_records = []
    for person in person_data:
        new_subject_id = f"SUBJ-{str(uuid.uuid4())[:8].upper()}"
        record = {
            'subject_id': new_subject_id,
            'mrn': ';'.join(sorted(list(person['mrn']))),
            'upn': ';'.join(sorted(list(person['upn']))),
            'pmid': ';'.join(sorted(list(person['pmid'])))
        }
        linkage_key_records.append(record)
        
    linkage_key_df = pd.DataFrame(linkage_key_records)

    legacy_to_new_id_map = {}
    for _, row in linkage_key_df.iterrows():
        new_id = row['subject_id']
        for id_type in ['mrn', 'upn', 'pmid']:
            for legacy_id in row[id_type].split(';'):
                if legacy_id:
                    legacy_to_new_id_map[legacy_id] = new_id

    print("Linkage key created successfully.")
    return linkage_key_df, legacy_to_new_id_map

def main():
    """
    Main function to execute the de-identification process.
    """
    # --- 1. Open a GUI file dialog to select Excel files ---
    root = tk.Tk()
    root.withdraw() # Hide the small root window

    print("Opening file dialog to select Excel files...")
    file_paths = filedialog.askopenfilenames(
        title="Select Excel Files for De-identification",
        filetypes=(("Excel Files", "*.xlsx *.xls"), ("All files", "*.*"))
    )

    if not file_paths:
        print("No files were selected. Exiting.")
        return

    # --- 2. Load and process the selected files ---
    print(f"Processing {len(file_paths)} selected file(s)...")
    all_dfs_to_process = load_all_sheets_from_files(file_paths)

    # --- 3. Execute Phase 1 ---
    linkage_key, _ = create_identifier_linkage_key(all_dfs_to_process)
    
    if linkage_key is not None:
        # --- 4. Save the output file ---
        output_path = Path(__file__).parent.parent / 'SECURE_linkage_key.csv'
        linkage_key.to_csv(output_path, index=False)
        
        print(f"\n--- Linkage Key Output (`{output_path}`) ---")
        print("!! WARNING: THIS FILE CONTAINS PHI AND MUST BE STORED SECURELY !!")
        print(linkage_key)
        print("\nProcess complete. You can now securely transfer the SECURE_linkage_key.csv file.")

if __name__ == "__main__":
    main()