"""Initialization for avfcomp package."""

__all__ = ['AVFParser', 'AVFComp', 'AVFDecomp', 'CompType']

from .base import AVFParser
from .basecomp import CompType
from .comp import AVFComp
from .decomp import AVFDecomp
