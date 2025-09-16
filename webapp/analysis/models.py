from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

class AnalysisID(models.Model):
    """
    Stores the final, opaque, prefixed sample ID used for bioinformatics analysis.
    This ID links to the analysis-ready sample, which can be either an
    Extract or a SequenceLibrary from the sampletracking app.
    """
    analysis_id = models.CharField(
        max_length=255,
        unique=True,
        help_text="The unique, prefixed ID for bioinformatics analysis (e.g., WGS_ABC123)."
    )

    # The GenericForeignKey to link to either an Extract or a SequenceLibrary
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.analysis_id

    class Meta:
        verbose_name = "Analysis ID"
        verbose_name_plural = "Analysis IDs"
        ordering = ['-created_at']