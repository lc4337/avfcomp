from typing import Dict, List, Tuple

MOUSE_EVENT_TYPES: Dict[int, str] = {
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

LEVELS_STAT: List[Tuple[int, int, int]] = [
    # (cols, rows, mines)
    (8, 8, 10),
    (16, 16, 40),
    (30, 16, 99),
]

OP_ENC_TABLE: Dict[int, int] = {
    1: 241,
    3: 242,
    5: 243,
    9: 244,
    17: 245,
    33: 246,
    65: 247,
    145: 248,
    193: 249,
    11: 250,
    21: 251,
}

OP_DEC_TABLE: Dict[int, int] = {k: v for v, k in OP_ENC_TABLE.items()}

VEC_ENC_TABLE: Dict[Tuple[int, int, int, int], int] = {
    (1, 0, 2, 0): 0,
    (1, 0, 0, 2): 1,
    (1, 0, 1, 0): 2,
    (1, 0, 0, 0): 3,
    (1, 0, 0, 1): 4,
    (1, 1, 0, 2): 5,
    (1, 1, 2, 0): 6,
    (1, 1, 0, 1): 7,
    (1, 1, 1, 0): 8,
    (1, 1, 0, 0): 9,
    (1, 0, 1, 2): 10,
    (1, 0, 2, 1): 11,
    (1, 0, 1, 1): 12,
    (1, 0, 2, 2): 13,
    (3, 0, 0, 0): 14,
    (5, 0, 0, 0): 15,
    (1, 2, 0, 2): 16,
    (1, 1, 1, 2): 17,
    (1, 1, 2, 2): 18,
    (1, 1, 2, 1): 19,
    (1, 2, 2, 0): 20,
    (1, 1, 1, 1): 21,
    (1, 0, 4, 0): 22,
    (3, 1, 0, 0): 23,
    (5, 1, 0, 0): 24,
    (1, 2, 0, 1): 25,
    (1, 2, 1, 0): 26,
    (17, 0, 0, 0): 27,
    (9, 0, 0, 0): 28,
    (1, 2, 0, 0): 29,
    (1, 0, 3, 0): 30,
    (1, 0, 0, 4): 31,
    (1, 1, 4, 0): 32,
    (1, 0, 0, 3): 33,
    (1, 3, 0, 2): 34,
    (9, 1, 0, 0): 35,
    (1, 1, 0, 4): 36,
    (1, 3, 2, 0): 37,
    (5, 2, 0, 0): 38,
    (1, 0, 6, 0): 39,
    (1, 1, 3, 0): 40,
    (1, 0, 3, 2): 41,
    (3, 2, 0, 0): 42,
    (1, 0, 4, 1): 43,
    (17, 1, 0, 0): 44,
    (1, 1, 0, 3): 45,
    (1, 3, 1, 0): 46,
    (1, 0, 4, 2): 47,
    (1, 3, 0, 1): 48,
    (1, 0, 1, 4): 49,
    (1, 4, 0, 2): 50,
    (5, 3, 0, 0): 51,
    (1, 4, 2, 0): 52,
    (1, 0, 3, 1): 53,
    (5, 4, 0, 0): 54,
    (1, 0, 2, 3): 55,
    (1, 0, 1, 3): 56,
    (5, 5, 0, 0): 57,
    (1, 0, 2, 4): 58,
    (1, 4, 1, 0): 59,
    (1, 3, 0, 0): 60,
    (1, 2, 2, 2): 61,
    (9, 2, 0, 0): 62,
    (1, 1, 3, 2): 63,
    (1, 0, 3, 4): 64,
    (5, 6, 0, 0): 65,
    (1, 4, 0, 1): 66,
    (1, 2, 1, 2): 67,
    (3, 3, 0, 0): 68,
    (1, 1, 4, 2): 69,
    (1, 1, 1, 4): 70,
    (1, 2, 0, 4): 71,
    (1, 1, 4, 1): 72,
    (1, 1, 2, 3): 73,
    (1, 1, 6, 0): 74,
    (1, 5, 0, 2): 75,
    (1, 2, 2, 1): 76,
    (1, 5, 2, 0): 77,
    (1, 1, 3, 1): 78,
    (1, 1, 2, 4): 79,
    (1, 1, 1, 3): 80,
    (1, 2, 1, 1): 81,
    (5, 7, 0, 0): 82,
    (1, 2, 4, 0): 83,
    (1, 5, 1, 0): 84,
    (1, 0, 5, 4): 85,
    (1, 6, 0, 2): 86,
    (1, 5, 0, 1): 87,
    (3, 4, 0, 0): 88,
    (1, 0, 5, 0): 89,
    (1, 2, 0, 3): 90,
    (1, 2, 3, 0): 91,
    (1, 6, 2, 0): 92,
    (1, 4, 0, 0): 93,
    (1, 0, 6, 2): 94,
    (5, 8, 0, 0): 95,
    (1, 0, 5, 2): 96,
    (9, 3, 0, 0): 97,
    (1, 0, 6, 1): 98,
    (1, 0, 8, 0): 99,
    (1, 0, 0, 6): 100,
    (1, 6, 1, 0): 101,
    (1, 1, 0, 6): 102,
    (1, 1, 3, 4): 103,
    (17, 2, 0, 0): 104,
    (1, 1, 5, 0): 105,
    (1, 6, 0, 1): 106,
    (1, 1, 0, 5): 107,
    (1, 0, 4, 3): 108,
    (1, 7, 0, 2): 109,
    (1, 1, 4, 3): 110,
    (1, 5, 0, 0): 111,
    (1, 0, 0, 5): 112,
    (1, 0, 4, 4): 113,
    (1, 2, 6, 0): 114,
    (1, 0, 3, 3): 115,
    (9, 4, 0, 0): 116,
    (1, 7, 2, 0): 117,
    (1, 2, 2, 4): 118,
    (1, 2, 0, 6): 119,
    (1, 7, 1, 0): 120,
    (1, 1, 6, 2): 121,
    (1, 1, 5, 2): 122,
    (1, 1, 4, 4): 123,
    (1, 2, 1, 4): 124,
    (1, 2, 4, 2): 125,
    (1, 1, 6, 1): 126,
    (1, 1, 3, 3): 127,
    (1, 2, 3, 2): 128,
    (3, 5, 0, 0): 129,
    (1, 1, 5, 4): 130,
    (1, 7, 0, 1): 131,
    (1, 2, 2, 3): 132,
    (1, 1, 8, 0): 133,
    (1, 6, 0, 0): 134,
    (1, 2, 5, 0): 135,
    (1, 2, 0, 5): 136,
    (1, 2, 4, 1): 137,
    (1, 1, 2, 5): 138,
    (1, 2, 1, 3): 139,
    (1, 2, 3, 1): 140,
    (5, 9, 0, 0): 141,
    (1, 8, 0, 2): 142,
    (1, 0, 5, 1): 143,
    (1, 0, 1, 6): 144,
    (1, 1, 1, 6): 145,
    (1, 8, 1, 0): 146,
    (1, 8, 2, 0): 147,
    (17, 3, 0, 0): 148,
    (1, 1, 2, 6): 149,
    (1, 1, 1, 5): 150,
    (1, 1, 5, 1): 151,
    (1, 0, 2, 6): 152,
    (1, 0, 1, 5): 153,
    (17, 4, 0, 0): 154,
    (1, 0, 3, 6): 155,
    (1, 0, 2, 5): 156,
    (1, 8, 0, 1): 157,
    (3, 6, 0, 0): 158,
    (1, 7, 0, 0): 159,
    (1, 3, 2, 2): 160,
    (1, 0, 10, 0): 161,
    (1, 2, 3, 4): 162,
    (17, 5, 0, 0): 163,
    (17, 6, 0, 0): 164,
    (1, 0, 8, 1): 165,
    (1, 1, 4, 5): 166,
    (1, 0, 5, 6): 167,
    (1, 0, 6, 3): 168,
    (1, 3, 1, 2): 169,
    (1, 1, 3, 6): 170,
    (1, 0, 8, 2): 171,
    (1, 2, 4, 3): 172,
    (1, 1, 0, 8): 173,
    (1, 2, 8, 0): 174,
    (1, 2, 4, 4): 175,
    (1, 2, 3, 3): 176,
    (1, 0, 7, 0): 177,
    (1, 2, 2, 6): 178,
    (1, 2, 2, 5): 179,
    (9, 5, 0, 0): 180,
    (1, 1, 7, 0): 181,
    (1, 2, 5, 2): 182,
    (1, 9, 0, 2): 183,
    (1, 3, 2, 1): 184,
    (1, 2, 6, 2): 185,
    (1, 0, 7, 4): 186,
    (1, 1, 6, 3): 187,
    (17, 7, 0, 0): 188,
    (1, 2, 1, 6): 189,
    (1, 1, 0, 7): 190,
    (1, 9, 1, 0): 191,
    (1, 0, 5, 3): 192,
    (5, 10, 0, 0): 193,
    (1, 2, 6, 1): 194,
    (1, 1, 5, 3): 195,
    (1, 2, 5, 1): 196,
    (1, 1, 3, 5): 197,
    (1, 0, 7, 2): 198,
    (1, 1, 6, 4): 199,
    (1, 0, 6, 4): 200,
    (1, 2, 1, 5): 201,
    (1, 9, 2, 0): 202,
    (1, 1, 10, 0): 203,
    (1, 3, 1, 1): 204,
    (1, 0, 0, 8): 205,
    (17, 8, 0, 0): 206,
    (1, 8, 0, 0): 207,
    (1, 1, 4, 6): 208,
    (1, 0, 4, 5): 209,
    (1, 9, 0, 1): 210,
    (1, 2, 7, 0): 211,
    (1, 1, 8, 1): 212,
    (3, 7, 0, 0): 213,
    (1, 0, 3, 5): 214,
    (1, 1, 5, 6): 215,
    (1, 2, 0, 7): 216,
    (1, 2, 0, 8): 217,
    (1, 1, 8, 2): 218,
    (1, 2, 5, 4): 219,
    (1, 1, 7, 2): 220,
    (9, 6, 0, 0): 221,
    (1, 2, 4, 5): 222,
    (1, 3, 0, 4): 223,
    (1, 0, 0, 7): 224,
    (1, 2, 3, 6): 225,
    (1, 10, 0, 2): 226,
    (1, 4, 2, 2): 227,
    (1, 2, 3, 5): 228,
    (1, 2, 5, 3): 229,
    (65, 0, 0, 0): 230,
    (1, 2, 6, 3): 231,
    (33, 0, 0, 0): 232,
    (1, 0, 4, 6): 233,
    (1, 1, 1, 8): 234,
    (1, 0, 12, 0): 235,
    (1, 1, 6, 5): 236,
    (1, 2, 6, 4): 237,
    (1, 1, 2, 7): 238,
    (1, 2, 4, 6): 239,
    (1, 1, 7, 1): 240,
}

VEC_DEC_TABLE: Dict[int, Tuple[int, int, int, int]] = {k: v for v, k in VEC_ENC_TABLE.items()}
