# -*- coding: utf-8 -*-

import lzma

from .base import AVFParser


class AVFComp(AVFParser):
    def process_out(self, filename):
        with lzma.open(filename, "wb") as fout:
            # compression algorithm
            fout.write(b"1")

            # version
            fout.write(self.version.to_bytes(1))

            # prefix
            fout.write(self.prefix)

            # gamemode parameters
            fout.write(self.level.to_bytes(1))
            if self.level == 6:
                fout.write((self.cols - 1).to_bytes(1))
                fout.write((self.rows - 1).to_bytes(1))

            # mines
            self.write_mines(fout)

            # prestamp
            fout.write(self.prestamp)

            # info
            fout.write(b"[")
            fout.write(self.ts_info.encode("cp1252"))
            fout.write(b"]")

            # preevent
            fout.write(self.preevent)
            fout.write(b"\x00\x01")

            # events
            self.write_events(fout)

            # presuffix
            fout.write(self.presuffix)

            # footer
            footer_fields = self.footer.split(b"\r")
            fout.write(b"\r".join(footer_fields[:-1]))

    def write_events(self, fout):
        op = []
        timestamps = []
        xpos = []
        ypos = []
        for event in self.events:
            op.append(event["type"])
            timestamps.append(event["gametime"] // 10)
            xpos.append(event["xpos"])
            ypos.append(event["ypos"])

        def get_diff(arr):
            diff_arr = [arr[0]]
            for i in range(len(arr) - 1):
                diff_arr.append(arr[i+1] - arr[i])
            return diff_arr

        timestamps = get_diff(timestamps)
        xpos = get_diff(xpos)
        ypos = get_diff(ypos)

        
        zigzag = lambda x: (x << 1) ^ (x >> 31)
        min_bytes = lambda x: (x.bit_length() + 7) // 8 if x else 1
        byte_len_timestamps = min_bytes(max(timestamps))
        data = b""
        for i in range(len(op)):
            data += op[i].to_bytes(1)
        # EOF
        data += b"\x00"
        data += byte_len_timestamps.to_bytes(1)
        for i in range(len(op)):
            data += timestamps[i].to_bytes(byte_len_timestamps)
        for i in range(len(op)):
            data += zigzag(xpos[i]).to_bytes(2)
        for i in range(len(op)):
            data += zigzag(ypos[i]).to_bytes(2)
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