import pandas as pd

# Duplicated from the de-identification tool to keep this package independent.
IDENTIFIER_COLUMN_MAP = {
    'MRN': 'mrn',
    'UPN': 'upn',
    'Internal_ID': 'pmid',
    'PMID': 'pmid',
    'patient_id': 'pmid'
}

# Mappings for other messy sample metadata columns, harmonized with existing app
SAMPLE_COLUMN_MAP = {
    'Collection Date': 'collection_date',
    'collection_dt': 'collection_date',
    'sample_date': 'collection_date',
    'Sample Type': 'sample_source', # Harmonized name
    'source': 'sample_source',      # Harmonized name
    'sample_type': 'sample_source',
    'FASTQ': 'sequence_filename',
    'sequence_file': 'sequence_filename',
    'filename': 'sequence_filename',
    'Project': 'project_name',
    'PI': 'project_name'
}

# Controlled vocabulary for harmonizing sample sources, adopted from existing app
SAMPLE_SOURCE_VOCAB = {
    'stool': 'Stool',
    'skin': 'Skin',
    'oral': 'Oral',
    'nasal': 'Nasal',
    'blood': 'Blood',
    'tissue': 'Tissue',
    'other': 'Other',
}

def create_harmonized_sample_list(dataframes_dict, id_lookup_map):
    """
    Processes all dataframes, using the linkage key to replace legacy IDs
    with the new subject_id and harmonizing other data.
    """
    print("\n--- Phase 2: Creating De-identified Sample List ---")

    cleaned_dfs = []
    for source_key, df_raw in dataframes_dict.items():
        df = df_raw.copy()
        
        df.rename(columns={**IDENTIFIER_COLUMN_MAP, **SAMPLE_COLUMN_MAP}, inplace=True)

        if 'mrn' in df.columns:
            df['legacy_id'] = df['mrn'].astype(str)
        elif 'upn' in df.columns:
            df['legacy_id'] = df['upn'].astype(str)
        elif 'pmid' in df.columns:
            df['legacy_id'] = df['pmid'].astype(str)
        else:
            print(f"Skipping source '{source_key}' as no identifiable column was found.")
            continue

        df['subject_id'] = df['legacy_id'].map(id_lookup_map)

        df['collection_date'] = pd.to_datetime(df['collection_date'], errors='coerce')
        df['sample_source'] = df['sample_source'].str.lower().map(SAMPLE_SOURCE_VOCAB).fillna('Other')
        
        # Create unique barcode (harmonized name for sample_id)
        date_str = df['collection_date'].dt.strftime('%Y-%m-%d')
        df['barcode'] = df['subject_id'].astype(str) + '_' + date_str + '_' + df['sample_source'].astype(str)
        
        df['source_file'] = source_key

        final_columns = [
            'barcode', 'subject_id', 'collection_date', 'sample_source',
            'sequence_filename', 'project_name', 'source_file'
        ]
        
        cols_to_keep = [col for col in final_columns if col in df.columns]
        df_cleaned = df[cols_to_keep]

        cleaned_dfs.append(df_cleaned)

    if not cleaned_dfs:
        print("No data was harmonized. The process will stop.")
        return None

    master_df = pd.concat(cleaned_dfs, ignore_index=True)
    master_df.drop_duplicates(subset=['barcode'], keep='first', inplace=True)
    
    print("De-identified sample list created successfully.")
    return master_df