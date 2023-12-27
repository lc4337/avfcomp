"""Decompression of an AVF file."""

from io import BytesIO
from typing import List, Callable

from .base import AVFParser
from .handler import T_CompFile, CompHandler


class AVFDecomp(AVFParser):
    """Decompression of an AVF file."""

    @staticmethod
    def zigzag_dec(n: int) -> int:
        """Zigzag transformation decode."""
        return (n >> 1) ^ -(n & 1)

    @staticmethod
    def varint_decompression(data: bytes) -> List[int]:
        """Variable-length integer decompression."""

        res = []
        cur = 0
        len_data = len(data)
        while cur < len_data:
            if (data[cur] >> 7) == 0:  # stands for 1-byte storage
                res.append(data[cur])
                cur += 1

            elif cur + 1 < len_data:  # stands for 2-byte storage
                res.append(((data[cur] & 0x7F) << 8) | data[cur + 1])
                cur += 2

            else:
                raise ValueError("Data corrupted or wrong format.")

        return res

    def __init__(self, handler: Callable[..., T_CompFile] = CompHandler.LZMA):
        super().__init__()
        self.handler = handler

    def decompress(self, data: bytes) -> bytes:
        """Decompression in bytes."""
        data_io = BytesIO(data)
        if self.handler is not CompHandler.PLAIN:
            with self.handler(data_io, "rb") as fin:
                self.read_data(fin)
        else:
            self.read_data(data_io)

        decomp_data = BytesIO()
        self.write_data(decomp_data)
        return decomp_data.getvalue()

    def process_in(self, filename: str):
        """Process the CVF file and parse the data to memory."""
        with self.handler(filename, "rb") as fin:
            self.read_data(fin)

    def read_events(self, fin):
        # Read op codes
        data_len = int.from_bytes(fin.read(3), byteorder="big")
        data = fin.read(data_len)

        num_events = data.index(b"\xff")
        op = list(data[:num_events])

        left_data = self.varint_decompression(data[num_events + 1 :])
        left_events = len(left_data) // 3
        left_event_cur = 0

        timestamps = []
        xpos = []
        ypos = []

        # Read timestamps, xpos, ypos
        for i in range(num_events):
            if op[i] in self.OP_DEC_TABLE:
                op[i] = self.OP_DEC_TABLE[op[i]]
                timestamps.append(left_data[left_event_cur])
                xpos.append(left_data[left_events + left_event_cur])
                ypos.append(left_data[2 * left_events + left_event_cur])
                left_event_cur += 1
            else:
                op[i], ti, xi, yi = self.VEC_DEC_TABLE[op[i]]
                timestamps.append(ti)
                xpos.append(xi)
                ypos.append(yi)

        xpos = list(map(self.zigzag_dec, xpos))
        ypos = list(map(self.zigzag_dec, ypos))

        def get_presum(arr: List[int]) -> List[int]:
            presum_arr = [arr[0]]
            presum = arr[0]
            for i in range(len(arr) - 1):
                presum += arr[i + 1]
                presum_arr.append(presum)
            return presum_arr

        timestamps = get_presum(timestamps)
        xpos = get_presum(xpos)
        ypos = get_presum(ypos)

        self.events = []
        for i in range(num_events):
            event = {
                "type": op[i],
                "gametime": timestamps[i] * 10,
                "xpos": xpos[i],
                "ypos": ypos[i],
            }
            self.events.append(event)

    def read_mines(self, fin):
        cols, rows = self.cols, self.rows
        size = (rows * cols + 7) // 8
        data = fin.read(size)
        self.mines = []
        for i in range(cols):
            for j in range(rows):
                idx = j * cols + i
                byte_idx = idx // 8
                bit_idx = idx % 8
                if (data[byte_idx] >> (7 - bit_idx)) & 1:
                    mine = (j + 1, i + 1)
                    self.mines.append(mine)

    def read_footer(self, fin):
        footer_simp = fin.read()
        self.footer = footer_simp.split(b"\r")
