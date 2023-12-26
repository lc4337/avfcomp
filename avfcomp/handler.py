"""Base compression library which deals with multiple compression formats."""

import bz2
import gzip
import lzma
from io import BufferedIOBase
from typing import Callable, Union

T_CompFile = Union[BufferedIOBase, gzip.GzipFile, bz2.BZ2File, lzma.LZMAFile]


class CompHandler:
    """Compression handlers."""

    PLAIN: Callable[..., BufferedIOBase] = open
    GZIP: Callable[..., gzip.GzipFile] = gzip.open
    BZIP2: Callable[..., bz2.BZ2File] = bz2.open
    LZMA: Callable[..., lzma.LZMAFile] = lzma.open
