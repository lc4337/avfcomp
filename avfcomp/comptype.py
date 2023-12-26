"""Base compression library which deals with multiple compression formats."""

import bz2
import gzip
import lzma
from bz2 import BZ2File
from enum import IntEnum
from gzip import GzipFile
from lzma import LZMAFile
from typing import Union, Literal, Callable
from io import BufferedReader, BufferedWriter


class CompType(IntEnum):
    """Compression type."""

    PLAIN = 0
    GZIP = 1
    BZIP2 = 2
    LZMA = 3


T_CompFile = Union[BufferedReader, BufferedWriter, GzipFile, BZ2File, LZMAFile]
T_CompType = Literal[CompType.PLAIN, CompType.GZIP, CompType.BZIP2, CompType.LZMA]


def get_copen(type: T_CompType) -> Callable[..., T_CompFile]:
    comp_type_mapping = {
        CompType.PLAIN: open,
        CompType.GZIP: gzip.open,
        CompType.BZIP2: bz2.open,
        CompType.LZMA: lzma.open,
    }
    return comp_type_mapping[type]
