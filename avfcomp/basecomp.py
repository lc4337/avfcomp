"""Base compression library which deals with multiple compression formats."""

from enum import IntEnum
from io import BufferedReader, BufferedWriter
from gzip import GzipFile
from bz2 import BZ2File
from lzma import LZMAFile

from typing import Literal, Union

class CompType(IntEnum):
    """Compression type."""
    PLAIN = 0
    GZIP = 1
    BZIP2 = 2
    LZMA = 3

T_CompFile = Union[BufferedReader, BufferedWriter, GzipFile, BZ2File, LZMAFile]
T_CompType = Literal[CompType.PLAIN, CompType.GZIP, CompType.BZIP2, CompType.LZMA]


def copen(filename: str, mode: Literal["rb", "wb"], _type: T_CompType, **kwargs) -> T_CompFile:
    """Open a file with a compression format."""
    if _type == CompType.PLAIN:
        return open(filename, mode, **kwargs)

    if _type == CompType.GZIP:
        return GzipFile(filename, mode, **kwargs)

    if _type == CompType.BZIP2:
        return BZ2File(filename, mode, **kwargs)

    if _type == CompType.LZMA:
        return LZMAFile(filename, mode, **kwargs)

    raise ValueError("Unknown compression type.")
