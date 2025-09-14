import pandas as pd
from pathlib import Path
from django.core.management.base import BaseCommand
from django.core.exceptions import ValidationError
from samples.models import Subject, CrudeSample

class Command(BaseCommand):
    help = 'Imports sample data from the harmonized TSV file into the database.'

    def handle(self, *args, **options):
        """The main logic for the management command."""
        tsv_path = Path(__file__).resolve().parent.parent.parent.parent.parent / 'harmonized_deidentified_samples.tsv'

        if not tsv_path.exists():
            self.stdout.write(self.style.ERROR(f'Error: Harmonized data file not found at {tsv_path}'))
            self.stdout.write(self.style.WARNING('Please run the harmonization script first to generate it.'))
            return

        self.stdout.write(f"Starting import from {tsv_path}...")
        
        try:
            df = pd.read_csv(tsv_path, sep='\t')
            df['collection_date'] = pd.to_datetime(df['collection_date'], errors='coerce')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Failed to read or parse TSV file: {e}"))
            return

        created_subjects = 0
        created_samples = 0
        updated_samples = 0

        for _, row in df.iterrows():
            try:
                if pd.isna(row['subject_id']) or pd.isna(row['barcode']) or pd.isna(row['collection_date']):
                    self.stdout.write(self.style.WARNING(f"Skipping row with missing essential data: {row['barcode']}"))
                    continue

                subject, created = Subject.objects.get_or_create(
                    subject_id=row['subject_id']
                )
                if created:
                    created_subjects += 1

                _, created_sample = CrudeSample.objects.update_or_create(
                    barcode=row['barcode'],
                    defaults={
                        'subject': subject,
                        'collection_date': row['collection_date'].date(),
                        'sample_source': row.get('sample_source', 'unknown'),
                        'sequence_filename': row.get('sequence_filename'),
                        'project_name': row.get('project_name'),
                        'source_file': row.get('source_file')
                    }
                )
                
                if created_sample:
                    created_samples += 1
                else:
                    updated_samples += 1

            except ValidationError as e:
                self.stdout.write(self.style.ERROR(f"Validation error on sample {row['barcode']}: {e}"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"An unexpected error occurred on sample {row['barcode']}: {e}"))

        self.stdout.write(self.style.SUCCESS("\nImport complete!"))
        self.stdout.write(f"- Subjects created: {created_subjects}")
        self.stdout.write(f"- Crude Samples created: {created_samples}")
        self.stdout.write(f"- Crude Samples updated: {updated_samples}")