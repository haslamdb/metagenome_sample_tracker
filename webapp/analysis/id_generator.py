import random
import string

from django.contrib.contenttypes.models import ContentType

from .models import AnalysisID
from sampletracking.models import Extract, SequenceLibrary


# This map defines the prefix based on the analysis type or extract type.
ID_PREFIX_MAP = {
    # From SequenceLibrary.analysis_type
    'WGS': 'WGS_',  # Whole Genome Sequencing (Short-Read)
    'WGL': 'WGL_',  # Whole Genome Sequencing (Long-Read)
    'MSS': 'MSS_',  # Metagenomic Shotgun Sequencing
    'MTS': 'MTS_',  # Metatranscriptomic Sequencing
    'CFS': 'CFS_',  # Cell-Free DNA Sequencing

    # From Extract.extract_type (for terminal extracts)
    'Protein': 'PTM_',
    'Metabolomics': 'MET_',
    'Antimicrobials': 'TDM_',
}

def generate_random_string(length=8):
    """Generates a random alphanumeric string of a given length."""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def create_analysis_id(source_object):
    """
    Generates a new, unique AnalysisID for a given source object (Extract or SequenceLibrary).

    Args:
        source_object: An instance of an Extract or SequenceLibrary.

    Returns:
        The newly created AnalysisID object, or None if a prefix is not defined.
    """
    if isinstance(source_object, SequenceLibrary):
        prefix_key = source_object.analysis_type
    elif isinstance(source_object, Extract):
        prefix_key = source_object.extract_type
    else:
        return None # Or raise an error

    prefix = ID_PREFIX_MAP.get(prefix_key)
    if not prefix:
        return None # Or raise an error

    # Generate a new unique ID
    while True:
        random_part = generate_random_string()
        new_id = f"{prefix}{random_part}"
        if not AnalysisID.objects.filter(analysis_id=new_id).exists():
            break

    # Create the new AnalysisID object
    analysis_id_obj = AnalysisID.objects.create(
        analysis_id=new_id,
        content_object=source_object
    )

    return analysis_id_obj
