"""Decompression of an AVF file."""

import lzma
from lzma import LZMAFile
from typing import List

from .base import AVFParser


class AVFDecomp(AVFParser):
    """Decompression of an AVF file."""

    @staticmethod
    def zigzag_dec(n: int) -> int:
        """Zigzag transformation decode."""
        return (n >> 1) ^ -(n & 1)

    @staticmethod
    def varint_decompression(data: List[int]) -> List[int]:
        """Variable-length integer decompression."""

        res = []
        cur = 0
        while cur < len(data):
            if data[cur] >> 7 == 0:  # stands for 1-byte storage
                res.append(data[cur])
                cur += 1

            elif cur + 1 < len(data):  # stands for 2-byte storage
                res.append(data[cur + 1] + ((data[cur] & 0x7F) << 8))
                cur += 2

            else:
                raise ValueError("Data corrupted or wrong format.")

        return res

    def process_in(self, filename: str):
        with lzma.open(filename, "rb") as fin:
            self.read_data(fin)

    def read_events(self, fin: LZMAFile):
        # Read op codes
        data_len = int.from_bytes(fin.read(3), byteorder="big")
        data_cp = list(fin.read(data_len))
        data = self.varint_decompression(data_cp)

        num_events = data.index(0)

        op = data[:num_events]
        timestamps = data[num_events + 1 : 2 * num_events + 1]
        xpos = data[2 * num_events + 1 : 3 * num_events + 1]
        ypos = data[3 * num_events + 1 :]

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

    def read_mines(self, fin: LZMAFile):
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

    def read_footer(self, fin: LZMAFile):
        footer_simp = fin.read()
        self.footer = footer_simp.split(b"\r")
