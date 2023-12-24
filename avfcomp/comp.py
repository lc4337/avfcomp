"""Compression of an AVF file."""

import lzma
from lzma import LZMAFile
from typing import List

from .base import AVFParser


class AVFComp(AVFParser):
    """Compression of an AVF file."""

    @staticmethod
    def zigzag_enc(n: int) -> int:
        """Zigzag transformation encode."""
        return (n << 1) ^ (n >> 31)

    @staticmethod
    def varint_compression(data: List[int]) -> List[int]:
        """
        Variable-length integer compression.

        Details:
        0 0000000: 1-byte storage,
        1 0000000 00000000: 2-byte storage.
        """

        res = []
        cur = 0
        while cur < len(data):
            if data[cur] < 128:  # 1-byte storage
                res.append(data[cur])
                cur += 1

            elif data[cur] < 32768:
                res.append(128 + (data[cur] >> 8))  # 2-byte storage, high bits
                res.append(data[cur] & 0xFF)  # 2-byte storage, low bits
                cur += 1

            else:
                raise ValueError("Integer too large.")

        return res

    def process_out(self, filename: str):
        with lzma.open(filename, "wb") as fout:  # use lzma for compression
            self.write_data(fout)

    def write_events(self, fout: LZMAFile):
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
            if op[i] == 1 and timestamps[i] <= 2 and xpos[i] <= 4 and ypos[i] <= 4:
                op[i] = 5 + self.VEC_ENC_TABLE[(timestamps[i], xpos[i], ypos[i])]
            else:
                op[i] = self.OP_ENC_TABLE[op[i]]
                timestamps_r.append(timestamps[i])
                xpos_r.append(xpos[i])
                ypos_r.append(ypos[i])

        data_cc = timestamps_r + xpos_r + ypos_r
        data_cp = self.varint_compression(data_cc)
        data = bytearray(op + [127] + data_cp)
        fout.write(len(data).to_bytes(3, byteorder="big"))
        fout.write(data)

    def write_mines(self, fout: LZMAFile):
        size = (self.rows * self.cols + 7) // 8
        data = bytearray(size)
        for mine in self.mines:
            idx = (mine[0] - 1) * self.cols + (mine[1] - 1)
            byte_idx = idx // 8
            bit_idx = idx % 8
            data[byte_idx] |= 1 << (7 - bit_idx)
        fout.write(data)

    def write_footer(self, fout: LZMAFile):
        footer_simp = b"\r".join(self.footer)
        fout.write(footer_simp)
