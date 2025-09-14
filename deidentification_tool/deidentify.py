import pandas as pd
import uuid
import os
from pathlib import Path

# --- Configuration ---
# This map is crucial for standardizing identifiers from different files.
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

    Args:
        file_paths (list): A list of string paths to the Excel files.

    Returns:
        dict: A dictionary where keys are 'filename|sheetname' and values are DataFrames.
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
    # --- 1. Simulate Your Messy Excel Files ---
    # In a real scenario, you would use `load_all_sheets_from_files`
    # file_paths = ["/path/to/your/project_A.xlsx", "/path/to/your/project_B.xlsx"]
    # all_dfs_to_process = load_all_sheets_from_files(file_paths)
    
    # For this example, we use the simulated data:
    data_a = {'MRN': ['11223344', '11223344', '55667788'], 'Internal_ID': ['PMID-01', 'PMID-01', 'PMID-02'], 'Collection Date': ['10/05/2024', '11/15/2024', '10/08/2024'], 'Sample Type': ['Stool', 'Skin', 'stool'], 'FASTQ': ['p01_s1.fq.gz', 'p01_s2.fq.gz', 'p02_s1.fq.gz']}
    df_a = pd.DataFrame(data_a)
    data_b = {'UPN': ['UPN_A5', 'UPN_B9', 'UPN_B9'], 'PMID': ['PMID-03', 'PMID-04', 'PMID-04'], 'collection_dt': pd.to_datetime(['2023-11-01', '2023-11-02', '2023-12-01']), 'source': ['oral', 'stool', 'stool'], 'sequence_file': ['p03_s1.fq.gz', 'p04_s1.fq.gz', 'p04_s2.fq.gz'], 'Project': ['IBD_Cohort', 'IBD_Cohort', 'IBD_Cohort']}
    df_b = pd.DataFrame(data_b)
    data_c = {'patient_id': ['PMID-02', 'PMID-04', 'PMID-05'], 'sample_date': ['2024-01-20', '2024-02-15', '2024-03-10'], 'sample_type': ['stool', 'stool', 'skin'], 'filename': ['old_p02.fq.gz', 'old_p04.fq.gz', 'old_p05.fq.gz'], 'PI': ['Dr. Jones', 'Dr. Smith', 'Dr. Jones']}
    df_c = pd.DataFrame(data_c)
    all_dfs_raw = {
        'clinical_research_A.xlsx|Sheet1': df_a,
        'collab_lab_B.xlsx|2023_Samples': df_b,
        'collab_lab_B.xlsx|2024_Samples': df_c,
    }

    # Execute Phase 1
    linkage_key, _ = create_identifier_linkage_key(all_dfs_raw)
    
    if linkage_key is not None:
        # Save the linkage key to the project root.
        # In a real workflow, you might save this to a more secure, designated output folder.
        output_path = Path(__file__).parent.parent / 'SECURE_linkage_key.csv'
        linkage_key.to_csv(output_path, index=False)
        
        print(f"\n--- Linkage Key Output (`{output_path}`) ---")
        print("!! WARNING: THIS FILE CONTAINS PHI AND MUST BE STORED SECURELY !!")
        print(linkage_key)

if __name__ == "__main__":
    main()
