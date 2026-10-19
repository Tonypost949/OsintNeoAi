# processing sub-package of OSINTNeoAI-Core
# Handles entity resolution, fuzzy mapping, and cleaning pipelines

from .correlation import AegisCorrelationEngine
from .npi_processor import NPIProcessor

__all__ = [
    'AegisCorrelationEngine',
    'NPIProcessor'
]
