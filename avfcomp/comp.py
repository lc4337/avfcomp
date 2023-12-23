"""Compression of an AVF file."""

import lzma

from .base import AVFParser


class AVFComp(AVFParser):
    """Compression of an AVF file."""

    @staticmethod
    def varint_compression(data):
        """
        Variable-length integer compression.

        Details:
        0 0000000: 1-byte storage,
        1 0000000 00000000: 2-byte storage,
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

    def process_out(self, filename):
        with lzma.open(filename, "wb") as fout:  # use lzma for compression
            self.write_data(fout)

    def write_events(self, fout):
        fout.write(b"\x00\x01")

        op = []
        timestamps = []
        xpos = []
        ypos = []
        # num_events = len(self.events)
        for event in self.events:
            op.append(event["type"])
            timestamps.append(event["gametime"] // 10)
            xpos.append(event["xpos"])
            ypos.append(event["ypos"])

        def get_diff(arr):
            diff_arr = [arr[0]]
            for i in range(len(arr) - 1):
                diff_arr.append(arr[i + 1] - arr[i])
            return diff_arr

        timestamps = get_diff(timestamps)
        xpos = get_diff(xpos)
        ypos = get_diff(ypos)

        zigzag = lambda x: (x << 1) ^ (x >> 31)
        xpos = list(map(zigzag, xpos))
        ypos = list(map(zigzag, ypos))

        data_cc = op + [0] + timestamps + xpos + ypos
        data_cp = self.varint_compression(data_cc)
        data = bytearray(data_cp)
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
