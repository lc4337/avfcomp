# -*- coding: utf-8 -*-

import lzma

from .base import AVFParser


class AVFDecomp(AVFParser):
    VERSION_INFO = "Minesweeper Arbiter 0.52.3. Copyright \xa9 2005-2006 Dmitriy I. Sukhomlynov".encode(
        "cp1252"
    )

    def process_buffer(self, filename):
        with lzma.open(filename, "rb") as fin:
            # Read compression algorithm
            fin.read(1)

            # Read version
            self.version = int.from_bytes(fin.read(1), byteorder="big")

            # Read prefix
            self.prefix = fin.read(4)

            # Read gamemode parameters
            self.level = int.from_bytes(fin.read(1), byteorder="big")
            if self.level == 6:
                self.cols = int.from_bytes(fin.read(1), byteorder="big") + 1
                self.rows = int.from_bytes(fin.read(1), byteorder="big") + 1
            elif 3 <= self.level < 6:
                self.cols, self.rows, self.num_mines = self.LEVELS_STAT[self.level - 3]

            # Read mines
            self.read_mines(fin)
            self.num_mines = len(self.mines)

            # Read prestamp
            self.prestamp = b""
            while True:
                byte = fin.read(1)
                if byte == b"[":
                    break
                self.prestamp += byte

            # Read info
            self.ts_info = b""
            while True:
                byte = fin.read(1)
                if byte == b"]":
                    break
                self.ts_info += byte
            self.ts_info = self.ts_info.decode("cp1252")

            # Read preevent
            self.read_preevent(fin)

            # Read events
            self.read_events(fin)

            # Read presuffix
            self.read_presuffix(fin)

            # Read footer
            self.footer = fin.read() + b"\r" + self.VERSION_INFO

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

    def read_presuffix(self, fin):
        buffer = fin.read(2)
        self.presuffix = buffer
        last2, last1 = buffer
        ref = tuple(b"cs=")
        while True:
            byte = fin.read(1)
            cur = ord(byte)
            self.presuffix += byte
            if (last2, last1, cur) == ref:
                break
            last2, last1 = last1, cur

        self.presuffix += fin.read(17)

    def read_preevent(self, fin):
        self.preevent = b""
        last = fin.read(1)
        while True:
            cur = fin.read(1)
            if last == b"\x00" and cur == b"\x01":
                break
            self.preevent += last
            last = cur
