"""
Collectors package for OSINT Independent Platform.
"""
from .base import BaseCollector, CollectorResult, CollectorRegistry, collector
from .web import WebCollector, CertificateCollector
from .api import VirusTotalCollector, CensysCollector, GitHubCollector

__all__ = [
    'BaseCollector',
    'CollectorResult',
    'CollectorRegistry',
    'collector',
    'WebCollector',
    'CertificateCollector',
    'VirusTotalCollector',
    'CensysCollector',
    'GitHubCollector',
]