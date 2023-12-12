# -*- coding: utf-8 -*-

import lzma
from io import SEEK_CUR

from .base import AVFParser
from .exceptions import InvalidReplayError


class AVFComp(AVFParser):
    def process_out(self, filename):
        with open(filename, "wb") as fout:
            # compression algorithm
            fout.write(b"1")

            # version
            fout.write(self.version.to_bytes(1))

            # parameters
            self.write_parameters(fout)

            # game start timestamp
            self.write_timestamp(fout)

            # id
            fout.write(self.name.encode("cp1252") + b"\r")

            # verify
            self.write_verification(fout)

            # mines
            self.write_mines(fout)

            # events
            self.write_events(fout)

    def write_events(self, fout):
        data = b""
        for event in self.events:
            data += event["type"].to_bytes(1)
            data += event["gametime"].to_bytes(3)
            data += event["xpos"].to_bytes(2)
            data += event["ypos"].to_bytes(2)

        data = lzma.compress(data)
        fout.write(len(data).to_bytes(4))
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

    def write_parameters(self, fout):
        fout.write(bytes(1))

    def write_timestamp(self, fout):
        fout.write(b"00000000")

    def write_verification(self, fout):
        fout.write(self.prefix)

        fout.write(len(self.prestamp).to_bytes(2))
        fout.write(self.prestamp)

        fout.write(len(self.preevent).to_bytes(2))
        fout.write(self.preevent)

        fout.write(self.presuffix)


