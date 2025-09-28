"""
Data Adapters Package

Provides adapters for different dataset formats used in pronunciation translation.
"""

from .base import BaseDataAdapter
from .ipa_dict_adapter import IPADictAdapter

__all__ = ["BaseDataAdapter", "IPADictAdapter"]