"""Compression of an AVF file."""

from io import BytesIO
from typing import List, Callable

from .base import AVFParser
from .handler import T_CompFile, CompHandler


class AVFComp(AVFParser):
    """Compression of an AVF file."""

    @staticmethod
    def zigzag_enc(n: int) -> int:
        """Zigzag transformation encode."""
        return (n << 1) ^ (n >> 31)

    @staticmethod
    def varint_compression(data: List[int]) -> bytes:
        """
        Variable-length integer compression.

        Details:
        0 0000000: 1-byte storage,
        1 0000000 00000000: 2-byte storage.
        """

        res = b""
        for cur in data:
            if cur < 0x80:  # 1-byte storage
                res += cur.to_bytes(1, byteorder="big")

            elif cur < 0x8000:
                res += (cur | 0x8000).to_bytes(2, byteorder="big")  # 2-byte storage, high bits

            else:
                raise ValueError("Integer too large.")

        return res

    def __init__(self, handler: Callable[..., T_CompFile] = CompHandler.LZMA):
        super().__init__()
        self.handler = handler

    def compress(self, data: bytes) -> bytes:
        """Compression in bytes."""
        data_io = BytesIO(data)
        self.read_data(data_io)

        comp_data = BytesIO()
        if self.handler is not CompHandler.PLAIN:
            with self.handler(comp_data, "wb") as fout:
                self.write_data(fout)
        else:
            self.write_data(comp_data)
        return comp_data.getvalue()

    def process_out(self, filename: str):
        """write the output to a CVF file."""
        with self.handler(filename, "wb") as fout:
            self.write_data(fout)

    def write_events(self, fout):
        fout.write(b"\x00\x01")

        op: List[int] = []
        timestamps: List[int] = []
        xpos: List[int] = []
        ypos: List[int] = []
        # num_events = len(self.events)
        for event in self.events:
            op.append(event["type"])
            timestamps.append(event["gametime"] // 10)
            xpos.append(event["xpos"])
            ypos.append(event["ypos"])

        def get_diff(arr: List[int]) -> List[int]:
            diff_arr = [arr[0]]
            for i in range(len(arr) - 1):
                diff_arr.append(arr[i + 1] - arr[i])
            return diff_arr

        timestamps = get_diff(timestamps)
        xpos = get_diff(xpos)
        ypos = get_diff(ypos)

        xpos = list(map(self.zigzag_enc, xpos))
        ypos = list(map(self.zigzag_enc, ypos))

        num_events = len(op)
        timestamps_r = []
        xpos_r = []
        ypos_r = []
        for i in range(num_events):
            key = (op[i], timestamps[i], xpos[i], ypos[i])
            enc = self.VEC_ENC_TABLE.get(key)
            if enc is not None:
                op[i] = enc

            else:
                op[i] = self.OP_ENC_TABLE[op[i]]
                timestamps_r.append(timestamps[i])
                xpos_r.append(xpos[i])
                ypos_r.append(ypos[i])

        data_r = timestamps_r + xpos_r + ypos_r
        data = bytes(op) + b"\xff" + self.varint_compression(data_r)
        fout.write(len(data).to_bytes(3, byteorder="big"))
        fout.write(data)

    def write_mines(self, fout):
        size = (self.rows * self.cols + 7) // 8
        data = bytearray(size)
        for mine in self.mines:
            idx = (mine[0] - 1) * self.cols + (mine[1] - 1)
            byte_idx = idx // 8
            bit_idx = idx % 8
            data[byte_idx] |= 1 << (7 - bit_idx)
        fout.write(data)

    def write_footer(self, fout):
        footer_simp = b"\r".join(self.footer)
        fout.write(footer_simp)
