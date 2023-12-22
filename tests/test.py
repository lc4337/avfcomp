import hashlib
import sys
import time
from os import listdir, path
work_dir = path.dirname(path.dirname(__file__))
sys.path.insert(0, work_dir)


from avfcomp import AVFComp, AVFDecomp

data_path = path.join(work_dir, "data")
beg_path = path.join(data_path, "avf_beg")
int_path = path.join(data_path, "avf_int")
exp_path = path.join(data_path, "avf_exp")
cvf_path = path.join(data_path, "cvf")
decomp_path = path.join(data_path, "avf_decomp")

def list_files(paths):
    for file in listdir(paths):
        yield file, path.join(paths, file)

def calc_file_hash(file_path):
    with open(file_path, "rb") as fin:
        return hashlib.sha256(fin.read()).hexdigest()

def is_same(file1_path, file2_path):
    file1_hash = calc_file_hash(file1_path)
    file2_hash = calc_file_hash(file2_path)
    return file1_hash == file2_hash

def cost_time(func):
    def fun(*args, **kwargs):
        t = time.perf_counter()
        result = func(*args, **kwargs)
        return (result, time.perf_counter() - t)
    return fun

@cost_time
def get_comp(paths):
    rawsize = 0
    compsize = 0
    for name, file_path in list_files(paths):
        rawsize += path.getsize(file_path)
        cvf = AVFComp.from_file(file_path)
        comp = path.join(cvf_path, name.replace("avf", "cvf"))
        cvf.process_out(comp)
        compsize += path.getsize(comp)
    return (compsize, rawsize)

@cost_time
def get_decomp(paths):
    decompsize = 0
    for name, file_path in list_files(paths):
        cvf = AVFDecomp.from_file(file_path)
        decompsize += path.getsize(file_path)
        decomp = path.join(decomp_path, name.replace("cvf", "avf"))
        cvf.process_out(decomp)
    return decompsize

def test_comp(paths, mode=""):
    size, ctime = get_comp(paths)
    compsize, rawsize = size
    ratio = 100 * (compsize / rawsize)
    speed = (rawsize / ctime) / 1024 / 1024
    print(f"{mode}: {ratio:.2f}% {speed:.2f} MB/s")

def test_decomp(paths):
    size, dtime = get_decomp(paths)
    speed = (size / dtime) / 1024 / 1024
    print(f"{speed:.2f} MB/s")

def check_decomp():
    for name, file_path in list_files(beg_path):
        decomp = path.join(decomp_path, name)
        if not is_same(file_path, decomp):
            print(file_path, decomp)
            raise Exception("CHECK FAILED")
    for name, file_path in list_files(int_path):
        decomp = path.join(decomp_path, name)
        if not is_same(file_path, decomp):
            raise Exception("CHECK FAILED")
    for name, file_path in list_files(exp_path):
        decomp = path.join(decomp_path, name)
        if not is_same(file_path, decomp):
            raise Exception("CHECK FAILED")
    print("ALL FILE CHECK PASSED")

def main():
    print("Test compression: ")
    test_comp(beg_path, "beg")
    test_comp(int_path, "int")
    test_comp(exp_path, "exp")

    print("Test decompression: ")
    test_decomp(cvf_path)
    check_decomp()



if __name__ == "__main__":
    main()

