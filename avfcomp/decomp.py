# -*- coding: utf-8 -*-

import lzma

from .base import AVFParser
from .exceptions import InvalidReplayError


class AVFDecomp(AVFParser):
    def process_buffer(self, filename):
        with lzma.open(filename, "rb") as fin:
            # Read compression algorithm
            fin.read(1)

            # Read version
            self.version = int.from_bytes(fin.read(1))

            # Read prefix
            self.prefix = fin.read(4)

            # Read gamemode parameters
            self.level = int.from_bytes(fin.read(1))
            if self.level == 6:
                self.cols = int.from_bytes(fin.read(1)) + 1
                self.rows = int.from_bytes(fin.read(1)) + 1
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
            self.preevent = b""
            while True:
                byte = fin.read(1)
                if byte == b"\x00":
                    break
                self.preevent += byte

            # Read events
            self.read_events(fin)

            # Read presuffix
            self.read_presuffix(fin)

            # Read footer
            self.footer = fin.read()

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
            op.append(int.from_bytes(op_code))

        num_events = len(op)
        for i in range(num_events):
            timestamp = fin.read(3)
            timestamps.append(int.from_bytes(timestamp, byteorder='big'))
        for i in range(num_events):
            x = fin.read(2)
            xpos.append(int.from_bytes(x, byteorder='big', signed=True))
        for i in range(num_events):
            y = fin.read(2)
            ypos.append(int.from_bytes(y, byteorder='big', signed=True))

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
                "ypos": ypos[i]
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
            if cur == b"":
                raise InvalidReplayError(self)
            self.presuffix += byte
            if (last2, last1, cur) == ref:
                break
            last2, last1 = last1, cur

        self.presuffix += fin.read(17)
  