# -*- coding: utf-8 -*-

from io import BytesIO
from io import SEEK_CUR

from .exceptions import InvalidReplayError

class BaseParser:
    def __init__(self, data_buffer, name=None):
        self.name = name
        self.process_buffer(data_buffer)

    def process_buffer(self, data):
        raise NotImplementedError

    def process_out(self, filename):
        raise NotImplementedError

    def __str__(self):
        return "{}({})".format(type(self).__name__, self.name)

    @classmethod
    def from_file(cls, filename):
        with open(filename, "rb") as file:
            return cls(file, name=filename)

    @classmethod
    def from_bytes(cls, data, name=None):
        return cls(BytesIO(data), name=name)

    @staticmethod
    def read_int(binstr):
        res = 0
        for char in binstr:
            res <<= 8
            res += char
        return res


class AVFParser(BaseParser):
    """
    AVFParser class for parsing AVF files.

    Attributes:
        MOUSE_EVENT_TYPES (dict): Dictionary mapping mouse event types to their corresponding names.
        LEVELS (dict): Dictionary mapping level numbers to their corresponding names.
        LEVELS_STAT (list): List of tuples representing the columns, rows, and mines for each level.
        properties (dict): Dictionary to store the properties of the AVF file.
        version (int): Version number of the AVF file.
        is_freesweeper (bool): Flag indicating whether the AVF file is from FreeSweeper.
        prefix (bytes): Bytes representing the prefix of the AVF file.
        level (int): Level of the game.
        cols (int): Number of columns in the game grid.
        rows (int): Number of rows in the game grid.
        num_mines (int): Number of mines in the game.
        mines (list): List of tuples representing the positions of the mines.
        prestamp (bytes): Bytes representing the prestamp of the AVF file.
        ts_info (str): Timestamp information extracted from the AVF file.
        bbbv (str): Version information extracted from the AVF file.
        preevent (bytes): Bytes representing the preevent of the AVF file.
        events (list): List of dictionaries representing the mouse events in the AVF file.
        presuffix (bytes): Bytes representing the presuffix of the AVF file.
        footer (bytes): Bytes representing the footer of the AVF file.
        timeth (int): Game time extracted from the second to last event in the AVF file.
        name (str): Name extracted from the footer of the AVF file.
        version_info (str): Version information extracted from the footer of the AVF file.
    """

    MOUSE_EVENT_TYPES = {
        1: "move",
        3: "lmb_down",
        5: "lmb_up",
        9: "rmb_down",
        17: "rmb_up",
        33: "mmb_down",
        65: "mmb_up",
        145: "rmb_up",
        193: "mmb_up",
        11: "shift_lmb_down",
        21: "lmb_up",
    }

    LEVELS = {
        3: "beginner",
        4: "intermediate",
        5: "expert",
        6: "custom",
    }

    LEVELS_STAT = [
        # (cols, rows, mines)
        (8, 8, 10),
        (16, 16, 40),
        (30, 16, 99),
    ]

    def process_buffer(self, data):
        """
        Process the buffer data and extract information from the AVF file.

        Args:
            data (file-like object): Buffer data containing the AVF file.

        Raises:
            InvalidReplayError: If the level in the AVF file is invalid.

        Returns:
            None
        """
        self.properties = {}
        # version
        self.version = ord(data.read(1))
        self.is_freesweeper = not self.version

        # no idea what these bytes do
        self.prefix = data.read(4)

        self.level = ord(data.read(1))
        try:
            self.properties["level"] = self.LEVELS[self.level]
        except KeyError:
            raise InvalidReplayError(self, message="Invalid level!")

        if 3 <= self.level < 6:
            self.cols, self.rows, self.num_mines = self.LEVELS_STAT[self.level - 3]
        elif self.level == 6:
            self.cols = ord(data.read(1)) + 1
            self.rows = ord(data.read(1)) + 1
            self.num_mines = self.read_int(data.read(2))
            # WxxHxxMxxx

        self.mines = []
        for ii in range(self.num_mines):
            row = ord(data.read(1))
            col = ord(data.read(1))
            self.mines.append((row, col))

        self.prestamp = b""
        while True:
            char = data.read(1)
            if char == b"[":
                break
            self.prestamp += char

        data.seek(-3, SEEK_CUR)
        self.properties["questionmarks"] = ord(data.read(1)) == 17

        # read past opening "["
        data.read(2)

        info = b""
        while True:
            char = data.read(1)
            if char == b"]":
                break
            info += char
        # TODO: make sure this is always correct/add encoding param
        # TODO: split this info into bits and make usable
        self.ts_info = info.decode("cp1252")
        ts_fields = self.ts_info.split("|")
        self.bbbv = ts_fields[-1][1:].split("T")[0]

        self.preevent = data.read(1)
        last = ord(self.preevent)
        while True:
            char = data.read(1)
            cur = ord(char)
            if last == 0 and cur == 1:
                break
            last = cur
            self.preevent += char
        self.preevent = self.preevent[:-2]
        data.seek(-3, SEEK_CUR)

        self.events = []
        self.presuffix = b""
        while True:
            buffer = data.read(8)
            mouse, x1, s2, x2, hun, y1, s1, y2 = tuple(buffer)
            xpos = (x1 << 8) + x2
            ypos = (y1 << 8) + y2
            sec = (s1 << 8) + s2 - 1
            gametime = 1000 * sec + 10 * hun
            
            if sec < 0:
                self.presuffix += buffer
                break

            self.events.append(
                {
                    "type": mouse,
                    "subtype": self.MOUSE_EVENT_TYPES[mouse],
                    "gametime": gametime,
                    "xpos": xpos,
                    "ypos": ypos,
                }
            )

        buffer = data.read(2)
        self.presuffix += buffer
        last2, last1 = buffer
        ref = tuple(b"cs=")
        while True:
            char = data.read(1)
            cur = ord(char)
            if cur == b"":
                raise InvalidReplayError(self)
            self.presuffix += char
            if (last2, last1, cur) == ref:
                break
            last2, last1 = last1, cur

        if self.is_freesweeper:
            for event in self.events:
                ths = ord(data.read(1)) & 0xF
                event["gametime"] += ths

        self.presuffix += data.read(17)

        # no idea what these bytes do
        if self.is_freesweeper:
            while ord(data.read(1)) != 13:
                pass

        footer = data.read()
        footer_fields = footer.split(b"\r")
        footer_meta_info = {}
        footer_positional = []
        for field in footer_fields:
            key, *value = field.split(b":", 2)
            if value:
                (value,) = value
                # TODO: make sure this is always correct/add encoding param
                footer_meta_info[key] = value.decode("cp1252").strip()
            else:
                # TODO: make sure this is always correct/add encoding param
                footer_positional.append(key.decode("cp1252"))

        # section => extract game time from the second to last event
        self.footer = footer
        self.timeth = self.events[-1]["gametime"]
        self.name, self.version_info = footer_positional

    def process_out(self, filename):
        """
        Process the AVF file and write the output to a file.

        Args:
            filename (str): Name of the output file.

        Returns:
            None
        """
        with open(filename, "wb") as fout:
            fout.write(self.version.to_bytes(1))

            fout.write(self.prefix)

            fout.write(self.level.to_bytes(1))
            if self.level == 6:
                fout.write((self.cols - 1).to_bytes(1))
                fout.write((self.rows - 1).to_bytes(1))
                fout.write(self.num_mines.to_bytes(2, "big"))
                # WxxHxxMxxx
                
            for mine in self.mines:
                fout.write(mine[0].to_bytes(1))
                fout.write(mine[1].to_bytes(1))

            fout.write(self.prestamp)

            fout.write(b"[")
            fout.write(self.ts_info.encode("cp1252"))
            fout.write(b"]")

            fout.write(self.preevent)

            for event in self.events:
                mouse = event["type"]
                xpos = event["xpos"]
                ypos = event["ypos"]
                gametime = event["gametime"]
                sec = gametime // 1000 + 1
                hun = (gametime % 1000) // 10

                fout.write(mouse.to_bytes(1))
                fout.write((xpos >> 8).to_bytes(1))
                fout.write((sec & 0xFF).to_bytes(1))
                fout.write((xpos & 0xFF).to_bytes(1))
                fout.write(hun.to_bytes(1))
                fout.write((ypos >> 8).to_bytes(1))
                fout.write((sec >> 8).to_bytes(1))
                fout.write((ypos & 0xFF).to_bytes(1))

            fout.write(self.presuffix)
            
            fout.write(self.footer)

    # def print(self):
    #     """print all attribute of record

    #     print in human readable format for test
    #     """

    #     print("version: ", self.version)
    #     print("is_freesweeper: ", self.is_freesweeper)
    #     print("properties: ", self.properties)
    #     print("cols: ", self.cols)
    #     print("rows: ", self.rows)
    #     print("num_mines: ", self.num_mines)
    #     print("mines: ", self.mines)
    #     print("ts_info: ", self.ts_info)
    #     print("bbbv: ", self.bbbv)
    #     print("events: ", self.events)
    #     print("timeth: ", self.timeth)
    #     print("name: ", self.name)
    #     print("version_info: ", self.version_info)