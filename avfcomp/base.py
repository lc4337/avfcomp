"""Base parser for AVF files."""

from io import SEEK_CUR


class AVFParser:
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
        ts_info (str): avf info between [] extracted from the AVF file.
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

    @staticmethod
    def read_int(binstr):
        """Read an integer from a binary string."""
        res = 0
        for char in binstr:
            res <<= 8
            res += char
        return res

    def __init__(self):
        """Initializations for variables."""
        self.mines = []
        self.events = []
        self.properties = {}
        self.is_freesweeper = False
        self.version, self.level, self.prefix, self.ts_info = None, None, None, None
        self.cols, self.rows, self.num_mines, self.bbbv = None, None, None, None
        self.prestamp, self.preevent, self.presuffix = b"", b"", b""
        self.footer, self.name, self.version_info = None, None, None

    def read_mines(self, fin):
        """Write the mines to the input buffer."""
        for _ in range(self.num_mines):
            row = ord(fin.read(1))
            col = ord(fin.read(1))
            self.mines.append((row, col))

    def read_events(self, fin):
        """Write the events to the input buffer."""
        self.preevent = self.preevent[:-1]
        fin.seek(-3, SEEK_CUR)

        while True:
            buffer = fin.read(8)
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

    def read_data(self, fin):
        """Process the buffer data and extract information from the AVF file."""
        self.properties = {}
        # version
        self.version = ord(fin.read(1))
        self.is_freesweeper = not self.version

        # no idea what these bytes do
        self.prefix = fin.read(4)

        self.level = ord(fin.read(1))
        self.properties["level"] = self.LEVELS[self.level]

        if 3 <= self.level < 6:
            self.cols, self.rows, self.num_mines = self.LEVELS_STAT[self.level - 3]
        elif self.level == 6:
            self.cols = ord(fin.read(1)) + 1
            self.rows = ord(fin.read(1)) + 1
            self.num_mines = self.read_int(fin.read(2))

        self.read_mines(fin)

        while True:
            char = fin.read(1)
            if char == b"[":
                break
            self.prestamp += char

        fin.seek(-3, SEEK_CUR)
        self.properties["questionmarks"] = ord(fin.read(1)) == 17

        # read past opening "["
        fin.read(2)

        info = b""
        while True:
            char = fin.read(1)
            if char == b"]":
                break
            info += char

        # ts info
        self.ts_info = info.decode("cp1252")
        ts_fields = self.ts_info.split("|")
        self.bbbv = ts_fields[-1][1:].split("T")[0]

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
        self.presuffix += buffer
        last2, last1 = buffer
        ref = tuple(b"cs=")
        while True:
            char = fin.read(1)
            cur = ord(char)
            self.presuffix += char
            if (last2, last1, cur) == ref:
                break
            last2, last1 = last1, cur

        if self.is_freesweeper:
            for event in self.events:
                ths = ord(fin.read(1)) & 0xF
                event["gametime"] += ths

        self.presuffix += fin.read(17)

        # no idea what these bytes do
        if self.is_freesweeper:
            while ord(fin.read(1)) != 13:
                pass

        # section => extract game time from the second to last event
        self.footer = fin.read()

    def process_in(self, filename):
        """Process the AVF file and parse the data to memory."""
        with open(filename, "rb") as fin:
            self.read_data(fin)

    def write_mines(self, fout):
        """Write the mines to the output buffer."""
        for mine in self.mines:
            fout.write(mine[0].to_bytes(1, byteorder="big"))
            fout.write(mine[1].to_bytes(1, byteorder="big"))

    def write_events(self, fout):
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

    def write_data(self, fout):
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

        fout.write(b"[")
        fout.write(self.ts_info.encode("cp1252"))
        fout.write(b"]")

        fout.write(self.preevent)

        self.write_events(fout)

        fout.write(self.presuffix)
        fout.write(self.footer)

    def process_out(self, filename):
        """Process the AVF file and write the output to a file."""
        with open(filename, "wb") as fout:
            self.write_data(fout)
