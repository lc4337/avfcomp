"""Test compression and decompression."""

import unittest

import hashlib
import time
import shutil
from os import listdir, path, mkdir
from typing import Iterator, Tuple, Callable, Any

from avfcomp import AVFComp, AVFDecomp

work_dir = path.dirname(path.dirname(__file__))

data_path = path.join(work_dir, "data")
beg_path = path.join(data_path, "avf_beg")
int_path = path.join(data_path, "avf_int")
exp_path = path.join(data_path, "avf_exp")
cvf_path = path.join(data_path, "cvf")
decomp_path = path.join(data_path, "avf_decomp")

# refresh
shutil.rmtree(cvf_path, ignore_errors=True)
shutil.rmtree(decomp_path, ignore_errors=True)
mkdir(cvf_path)
mkdir(decomp_path)


def list_files(paths: str) -> Iterator[Tuple[str, str]]:
    """List all files in a directory."""
    for file in listdir(paths):
        yield file, path.join(paths, file)


def calc_file_hash(file_path):
    """Calculate the hash of a file."""
    with open(file_path, "rb") as fin:
        return hashlib.sha256(fin.read()).hexdigest()


def cost_time(func: Callable) -> Callable[..., Tuple[Any, float]]:
    """Calculate the time cost of a function."""

    def fun(*args, **kwargs) -> Tuple[Any, float]:
        t = time.perf_counter()
        result = func(*args, **kwargs)
        return (result, time.perf_counter() - t)

    return fun


@cost_time
def get_comp(paths: str) -> Tuple[int, int]:
    """Compress all files."""
    rawsize = 0
    compsize = 0
    cvf = AVFComp()
    for name, file_path in list_files(paths):
        rawsize += path.getsize(file_path)
        cvf.process_in(file_path)
        comp = path.join(cvf_path, name.replace("avf", "cvf"))
        cvf.process_out(comp)
        compsize += path.getsize(comp)
    return (compsize, rawsize)


@cost_time
def get_decomp(paths: str) -> int:
    """Decompress all files."""
    decompsize = 0
    cvf = AVFDecomp()
    for name, file_path in list_files(paths):
        cvf.process_in(file_path)
        decompsize += path.getsize(file_path)
        decomp = path.join(decomp_path, name.replace("cvf", "avf"))
        cvf.process_out(decomp)
    return decompsize


def stat_comp(paths: str, mode: str = ""):
    """Get the statistics of compressed files."""
    size, ctime = get_comp(paths)
    compsize, rawsize = size
    ratio = 100 * (compsize / rawsize)
    speed = (rawsize / ctime) / 1024 / 1024
    print(f"{mode}: {ratio:.2f}% {speed:.2f} MB/s")


def stat_decomp(paths: str):
    """Get the statistics of decompressed files."""
    size, dtime = get_decomp(paths)
    speed = (size / dtime) / 1024 / 1024
    print(f"{speed:.2f} MB/s")


class TestCompAndDecomp(unittest.TestCase):
    """Test compression and decompression."""

    def check_decomp(self, paths: str):
        """Check the decompressed files."""
        for name, file_path in list_files(paths):
            decomp = path.join(decomp_path, name)
            self.assertEqual(calc_file_hash(file_path), calc_file_hash(decomp))

    def test_comp_and_decomp(self):
        """Test compression and decompression."""
        print("Test compression: ")
        stat_comp(beg_path, "beg")
        stat_comp(int_path, "int")
        stat_comp(exp_path, "exp")

        print("Test decompression: ")
        stat_decomp(cvf_path)

        self.check_decomp(beg_path)
        self.check_decomp(int_path)
        self.check_decomp(exp_path)


if __name__ == "__main__":
    unittest.main()
