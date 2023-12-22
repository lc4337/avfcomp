"""Decompression of an AVF file."""

import lzma

from .base import AVFParser


class AVFDecomp(AVFParser):
    """Decompression of an AVF file."""

    def process_in(self, filename):
        with lzma.open(filename, "rb") as fin:
            self.read_data(fin)

    def read_events(self, fin):
        op = []
        timestamps = []
        xpos = []
        ypos = []

        # Read op codes
        while True:
            op_code = fin.read(1)
            if op_code == b"\x00":
                break
            op.append(int.from_bytes(op_code, byteorder="big"))

        zigzag_de = lambda x: (x >> 1) ^ -(x & 1)
        num_events = len(op)
        byte_len_dt = int.from_bytes(fin.read(1), byteorder="big")
        for i in range(num_events):
            timestamp = fin.read(byte_len_dt)
            timestamps.append(int.from_bytes(timestamp, byteorder="big"))

        byte_len_dx = int.from_bytes(fin.read(1), byteorder="big")
        for i in range(num_events):
            x = fin.read(byte_len_dx)
            xpos.append(zigzag_de(int.from_bytes(x, byteorder="big")))

        byte_len_dy = int.from_bytes(fin.read(1), byteorder="big")
        for i in range(num_events):
            y = fin.read(byte_len_dy)
            ypos.append(zigzag_de(int.from_bytes(y, byteorder="big")))

        def get_presum(arr):
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
        for i in range(len(op)):
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
