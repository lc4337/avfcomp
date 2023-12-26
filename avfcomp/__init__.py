"""Initialization for avfcomp package."""

__all__ = ['AVFParser', 'AVFComp', 'AVFDecomp', 'CompType']

from .basecomp import CompType
from .base import AVFParser
from .comp import AVFComp
from .decomp import AVFDecomp
