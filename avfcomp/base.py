"""Base parser for AVF files."""

from io import SEEK_CUR
from typing import Dict, List, Tuple

from . import config
from .handler import T_CompFile


class AVFParser:
    """
    AVFParser class for parsing AVF files.

    Attributes:
        MOUSE_EVENT_TYPES (dict): Dictionary mapping mouse event types to their corresponding names.
        LEVELS (dict): Dictionary mapping level numbers to their corresponding names.
        LEVELS_STAT (list): List of tuples representing the columns, rows, and mines for each level.
        version (int): Version number of the AVF file.
        prefix (bytes): Bytes representing the prefix of the AVF file.
        level (int): Level of the game.
        cols (int): Number of columns in the game grid.
        rows (int): Number of rows in the game grid.
        num_mines (int): Number of mines in the game.
        mines (list): List of tuples representing the positions of the mines.
        prestamp (bytes): Bytes representing the prestamp of the AVF file.
        ts_info (bytes): avf info between [] extracted from the AVF file.
        preevent (bytes): Bytes representing the preevent of the AVF file.
        events (list): List of dictionaries representing the mouse events in the AVF file.
        presuffix (bytes): Bytes representing the presuffix of the AVF file.
        footer (bytes): Bytes representing the footer of the AVF file.
    """

    MOUSE_EVENT_TYPES = config.MOUSE_EVENT_TYPES
    LEVELS_STAT = config.LEVELS_STAT
    OP_ENC_TABLE = config.OP_ENC_TABLE
    OP_DEC_TABLE = config.OP_DEC_TABLE
    VEC_ENC_TABLE = config.VEC_ENC_TABLE
    VEC_DEC_TABLE = config.VEC_DEC_TABLE

    def __init__(self):
        """Initializations for variables."""
        self.mines: List[Tuple[int, int]] = []
        self.events: List[Dict[str, int]] = []
        self.footer: List[bytes] = []
        self.version, self.level, self.cols, self.rows, self.num_mines = 0, 0, 0, 0, 0
        self.prefix, self.prestamp, self.ts_info = b"", b"", b""
        self.preevent, self.presuffix = b"", b""

    def process_in(self, filename: str):
        """Process the AVF file and parse the data to memory."""
        with open(filename, "rb") as fin:
            self.read_data(fin)

    def process_out(self, filename: str):
        """Process the AVF file and write the output to a file."""
        with open(filename, "wb") as fout:
            self.write_data(fout)

    def read_data(self, fin: T_CompFile):
        """Process the buffer data and extract information from the AVF file."""
        # version
        self.version = ord(fin.read(1))

        # no idea what these bytes do
        self.prefix = fin.read(4)

        self.level = ord(fin.read(1))

        if 3 <= self.level < 6:
            self.cols, self.rows, self.num_mines = self.LEVELS_STAT[self.level - 3]
        elif self.level == 6:
            self.cols = ord(fin.read(1)) + 1
            self.rows = ord(fin.read(1)) + 1
            self.num_mines = int.from_bytes(fin.read(2), byteorder="big")

        self.read_mines(fin)

        self.prestamp = b""
        while True:
            char = fin.read(1)
            if char == b"[":
                break
            self.prestamp += char

        self.ts_info = b""
        while True:
            char = fin.read(1)
            if char == b"]":
                break
            self.ts_info += char

        # read preevent
        self.preevent = fin.read(1)
        last = ord(self.preevent)
        while True:
            char = fin.read(1)
            cur = ord(char)
            if last <= 1 and cur == 1:
                break
            last = cur
            self.preevent += char
        self.preevent = self.preevent[:-1]

        self.read_events(fin)

        buffer = fin.read(2)
        self.presuffix = buffer
        last2, last1 = buffer
        ref = tuple(b"cs=")
        while True:
            char = fin.read(1)
            cur = ord(char)
            self.presuffix += char
            if (last2, last1, cur) == ref:
                break
            last2, last1 = last1, cur
        self.presuffix += fin.read(17)

        self.read_footer(fin)

    def write_data(self, fout: T_CompFile):
        """Write the data to the output buffer."""
        fout.write(self.version.to_bytes(1, byteorder="big"))

        fout.write(self.prefix)

        fout.write(self.level.to_bytes(1, byteorder="big"))
        if self.level == 6:
            fout.write((self.cols - 1).to_bytes(1, byteorder="big"))
            fout.write((self.rows - 1).to_bytes(1, byteorder="big"))
            fout.write(self.num_mines.to_bytes(2, byteorder="big"))

        self.write_mines(fout)

        fout.write(self.prestamp)

        fout.write(b"[%s]" % self.ts_info)

        fout.write(self.preevent)

        self.write_events(fout)

        fout.write(self.presuffix)

        self.write_footer(fout)

    def read_mines(self, fin: T_CompFile):
        """Write the mines to the input buffer."""
        self.mines = []
        for _ in range(self.num_mines):
            row = ord(fin.read(1))
            col = ord(fin.read(1))
            self.mines.append((row, col))

    def read_events(self, fin: T_CompFile):
        """Write the events to the input buffer."""
        fin.seek(-3, SEEK_CUR)
        self.preevent = self.preevent[:-1]
        self.events = []

        while True:
            buffer = fin.read(8)
            mouse, x1, s2, x2, hun, y1, s1, y2 = tuple(buffer)
            xpos = (x1 << 8) + x2
            ypos = (y1 << 8) + y2
            sec = (s1 << 8) + s2 - 1
            gametime = 1000 * sec + 10 * hun

            if sec < 0:
                fin.seek(-8, SEEK_CUR)
                break

            assert mouse in self.MOUSE_EVENT_TYPES

            self.events.append(
                {
                    "type": mouse,
                    "gametime": gametime,
                    "xpos": xpos,
                    "ypos": ypos,
                }
            )

    def read_footer(self, fin: T_CompFile):
        """Write the footer to the input buffer."""
        footer_raw = fin.read()
        footer_list = footer_raw.split(b"\r")
        skin_v = footer_list[1][footer_list[1].find(b"Skin: ") + 6 :]
        idt = footer_list[2]
        abt_v = footer_list[3][footer_list[3].find(b"Arbiter") + 8 : footer_list[3].find(b"Copyright") - 2]

        self.footer = [skin_v, idt, abt_v]

    def write_mines(self, fout: T_CompFile):
        """Write the mines to the output buffer."""
        for mine in self.mines:
            fout.write(mine[0].to_bytes(1, byteorder="big"))
            fout.write(mine[1].to_bytes(1, byteorder="big"))

    def write_events(self, fout: T_CompFile):
        """Write the events to the output buffer."""
        for event in self.events:
            mouse = event["type"]
            xpos = event["xpos"]
            ypos = event["ypos"]
            gametime = event["gametime"]
            sec = gametime // 1000 + 1
            hun = (gametime % 1000) // 10

            fout.write(mouse.to_bytes(1, byteorder="big"))
            fout.write((xpos >> 8).to_bytes(1, byteorder="big"))
            fout.write((sec & 0xFF).to_bytes(1, byteorder="big"))
            fout.write((xpos & 0xFF).to_bytes(1, byteorder="big"))
            fout.write(hun.to_bytes(1, byteorder="big"))
            fout.write((ypos >> 8).to_bytes(1, byteorder="big"))
            fout.write((sec >> 8).to_bytes(1, byteorder="big"))
            fout.write((ypos & 0xFF).to_bytes(1, byteorder="big"))

    def write_footer(self, fout: T_CompFile):
        """Write the footer to the output buffer."""
        rtime = str(self.events[-1]["gametime"] // 1000).encode("cp1252") + self.ts_info.split(b"|")[-1][-3:]
        rtime_raw = b"RealTime: %s" % rtime
        skin_raw = b"Skin: %s" % self.footer[0]
        idt_raw = self.footer[1]
        abt_raw = b"Minesweeper Arbiter %s. Copyright \xa9 2005-2006 Dmitriy I. Sukhomlynov" % self.footer[2]

        footer_raw = b"\r".join([rtime_raw, skin_raw, idt_raw, abt_raw])
        fout.write(footer_raw)
