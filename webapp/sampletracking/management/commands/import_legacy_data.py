import pandas as pd
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from sampletracking.models import Subject, CrudeSample, Aliquot, Extract, SequenceLibrary
from analysis.id_generator import create_analysis_id

class Command(BaseCommand):
    help = 'Imports legacy sample data from a harmonized TSV file and generates analysis IDs.'

    def add_arguments(self, parser):
        parser.add_argument('tsv_file', type=str, help='The path to the harmonized_deidentified_samples.tsv file.')

    @transaction.atomic
    def handle(self, *args, **options):
        tsv_file_path = options['tsv_file']
        self.stdout.write(self.style.SUCCESS(f'Starting import from "{tsv_file_path}"...'))

        try:
            df = pd.read_csv(tsv_file_path, sep='\t')
        except FileNotFoundError:
            raise CommandError(f'File not found at "{tsv_file_path}".')

        # --- Verify required columns ---
        required_cols = [
            'subject_id', 'collection_date', 'sample_source', 
            'sequence_filename', 'Extract Type', 'Analysis Type'
        ]
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise CommandError(f'The TSV file is missing the following required columns: {", ".join(missing_cols)}')

        # --- Define which analysis types require a SequenceLibrary ---
        library_required_types = ['WGS', 'WGL', 'MSS', 'MTS', 'CFS']

        # --- Process each row ---
        for index, row in df.iterrows():
            self.stdout.write(f"Processing sample {row['sequence_filename']}...")

            # 1. Get or create the Subject
            subject, created = Subject.objects.get_or_create(subject_id=row['subject_id'])
            if created:
                self.stdout.write(f"  Created new Subject: {subject.subject_id}")

            # 2. Create placeholder CrudeSample
            # We use the unique legacy sequence_filename as the barcode for the placeholder crude sample
            crude, crude_created = CrudeSample.objects.get_or_create(
                barcode=row['sequence_filename'],
                defaults={
                    'subject': subject,
                    'collection_date': pd.to_datetime(row['collection_date']).date(),
                    'sample_source': row['sample_source'],
                    'date_created': pd.to_datetime(row['collection_date']).date(),
                }
            )

            # 3. Create placeholder Aliquot
            aliquot, aliquot_created = Aliquot.objects.get_or_create(
                barcode=f"{crude.barcode}-ALIQ01",
                defaults={
                    'parent_barcode': crude,
                    'date_created': crude.date_created,
                }
            )

            # 4. Create placeholder Extract
            extract, extract_created = Extract.objects.get_or_create(
                barcode=f"{aliquot.barcode}-EXT01",
                defaults={
                    'parent': aliquot,
                    'extract_type': row['Extract Type'],
                    'date_created': crude.date_created,
                }
            )

            # 5. Determine the final analysis-ready object
            analysis_type = row['Analysis Type']
            final_object = None

            if analysis_type in library_required_types:
                # This analysis type requires a SequenceLibrary
                library, lib_created = SequenceLibrary.objects.get_or_create(
                    barcode=f"{extract.barcode}-LIB01",
                    defaults={
                        'parent': extract,
                        'analysis_type': analysis_type,
                        'date_created': crude.date_created,
                    }
                )
                final_object = library
            else:
                # This is a terminal extract
                final_object = extract

            # 6. Generate the final Analysis ID
            if final_object:
                new_analysis_id = create_analysis_id(final_object)
                if new_analysis_id:
                    self.stdout.write(self.style.SUCCESS(f"  Successfully generated Analysis ID: {new_analysis_id.analysis_id}"))
                else:
                    self.stdout.write(self.style.WARNING(f"  Could not generate Analysis ID for {final_object.barcode}. Check prefix mapping."))
            else:
                self.stdout.write(self.style.ERROR(f"  Could not determine final object for analysis type '{analysis_type}'."))

        self.stdout.write(self.style.SUCCESS(f'\nImport complete. Processed {len(df)} samples.'))
