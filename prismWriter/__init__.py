"""
prismWriter - Python library for creating GraphPad Prism files

This library allows you to programmatically create and manipulate
GraphPad Prism (.pzfx) files from pandas DataFrames.
"""

__version__ = "1.0.0"
__author__ = "smestern"

from .prism_writer import PrismFile

__all__ = ["PrismFile", "__version__"]