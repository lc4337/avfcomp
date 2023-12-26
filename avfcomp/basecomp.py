"""Base compression library which deals with multiple compression formats."""

from bz2 import BZ2File
from enum import Enum
from gzip import GzipFile
from io import BufferedReader, BufferedWriter
from lzma import LZMAFile
from typing import Literal, Union


class CompType(Enum):
    """Compression type."""
    PLAIN = None
    GZIP = GzipFile
    BZIP2 = BZ2File
    LZMA = LZMAFile

T_CompFile = Union[BufferedReader, BufferedWriter, GzipFile, BZ2File, LZMAFile]


def copen(filename: str, mode: Literal["rb", "wb"], _type: CompType, **kwargs) -> T_CompFile:
    """Open a file with a compression format."""
    if _type == CompType.PLAIN:  # special case, just open the file
        return open(filename, mode, **kwargs)
    return _type.value(filename, mode, **kwargs)
