from django.db import models

class Subject(models.Model):
    """
    Represents a unique individual study subject.
    The subject_id is the de-identified, randomly generated ID.
    """
    subject_id = models.CharField(max_length=255, primary_key=True, unique=True, help_text="De-identified subject ID (e.g., SUBJ-ABC12345)")

    def __str__(self):
        return self.subject_id

class CrudeSample(models.Model):
    """
    Represents the initial crude sample, with field names and choices
    harmonized with the existing mgml_sampledb application.
    """
    SAMPLE_SOURCE_CHOICES = [
        ('Stool', 'Stool'),
        ('Oral', 'Oral Swab'),
        ('Nasal', 'Nasal Swab'),
        ('Skin', 'Skin Swab'),
        ('Blood', 'Blood'),
        ('Tissue', 'Tissue'),
        ('Other', 'Other'),
        ('unknown', 'Unknown'),
    ]
    
    STATUS_CHOICES = [
        ('AWAITING_RECEIPT', 'Awaiting Receipt'),
        ('AVAILABLE', 'Available'),
        ('IN_PROCESS', 'In Process'),
        ('EXHAUSTED', 'Exhausted'),
        ('CONTAMINATED', 'Contaminated'),
        ('ARCHIVED', 'Archived'),
    ]

    barcode = models.CharField(max_length=255, primary_key=True, unique=True, help_text="Unique identifier for the sample (e.g., SUBJ-ABC123_2024-10-05_stool)")
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="samples")
    collection_date = models.DateField(help_text="Date when the sample was collected")
    sample_source = models.CharField(max_length=100, choices=SAMPLE_SOURCE_CHOICES, default='unknown')
    notes = models.TextField(blank=True, null=True, help_text="Additional notes about this sample")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='AVAILABLE', help_text="The current status of the sample")
    sequence_filename = models.CharField(max_length=255, blank=True, null=True, help_text="Filename of the associated sequence data")
    project_name = models.CharField(max_length=255, blank=True, null=True, help_text="Name of the project or cohort")
    source_file = models.CharField(max_length=255, blank=True, null=True, help_text="Source file and sheet where this data originated from")

    def __str__(self):
        return self.barcode

    class Meta:
        ordering = ['subject', 'collection_date']
        verbose_name = "Crude Sample"
        verbose_name_plural = "Crude Samples"
