from io import BytesIO

from js import document, Uint8Array, File, URL
from pyodide.ffi.wrappers import add_event_listener

from avfcomp import AVFComp, AVFDecomp


class PersistentStorage:
    """Persistent storage for the file."""

    def __init__(self) -> None:
        self.file: bytes = b""
        self.filename: str = ""
        self.is_compressed: bool = False


ps = PersistentStorage()


async def upload_file(event):
    ps.file = b""

    file_list = event.target.files
    file = file_list.item(0)
    array_buffer = await file.arrayBuffer()
    file_bytes = array_buffer.to_bytes()
    ps.file = file_bytes
    ps.filename = file.name
    ps.is_compressed = ".cvf" in ps.filename

    output_div = document.querySelector("#output")
    output_div.innerText = ""


def download_file(*args):
    if ps.file == b"":
        output_div = document.querySelector("#output")
        output_div.innerText = "未选择文件"
        return

    file_stream = BytesIO(ps.file)

    js_array = Uint8Array.new(len(ps.file))
    js_array.assign(file_stream.getbuffer())

    file = File.new([js_array], "temp.avf", {type: "octet/stream"})
    url = URL.createObjectURL(file)

    hidden_link = document.createElement("a")
    hidden_link.setAttribute("download", ps.filename)
    hidden_link.setAttribute("href", url)
    hidden_link.click()

    output_div = document.querySelector("#output")
    output_div.innerText = ""


def getcomp(event):
    print("Compressing file ...")
    if ps.file == b"":
        output_div = document.querySelector("#output")
        output_div.innerText = "未选择文件"
        return

    if ps.is_compressed:
        output_div = document.querySelector("#output")
        output_div.innerText = "文件已经被压缩, 请重试"
        return

    cvf = AVFComp()

    original_size = len(ps.file)

    data_io = BytesIO(ps.file)
    cvf.read_data(data_io)
    comp_data = BytesIO()
    with cvf.handler(comp_data, "wb") as fout:
        cvf.write_data(fout)
    cvf_compressed = comp_data.getvalue()

    compressed_size = len(cvf_compressed)

    ps.file = cvf_compressed
    ps.filename = ps.filename.replace(".avf", ".cvf")
    ps.is_compressed = True

    output_div = document.querySelector("#output")
    output_div.innerText = f"压缩完成, 压缩率为: {compressed_size / original_size * 100:.2f}%, 可下载压缩后的文件"

    print("File compressed.")


def getdecomp(event):
    print("Decompressing file ...")
    if ps.file == b"":
        output_div = document.querySelector("#output")
        output_div.innerText = "未选择文件"
        return

    if not ps.is_compressed:
        output_div = document.querySelector("#output")
        output_div.innerText = "文件已经被解压, 请重试"
        return

    cvf = AVFDecomp()
    with cvf.handler(BytesIO(ps.file), "rb") as fin:
        cvf.read_data(fin)
    decomp_data = BytesIO()
    cvf.write_data(decomp_data)
    cvf_decompressed = decomp_data.getvalue()

    ps.file = cvf_decompressed
    ps.filename = ps.filename.replace(".cvf", ".avf")
    ps.is_compressed = False

    output_div = document.querySelector("#output")
    output_div.innerText = "解压完成, 可下载解压后的文件"

    print("File decompressed.")


add_event_listener(document.getElementById("file"), "change", upload_file)

add_event_listener(document.getElementById("download"), "click", download_file)
