"""Points configuration for the 2023 SFSGT Season.

Defines the points-by-rank dictionaries for Normal events and Major events.
"""

NORMAL_EVENT_POINTS_BY_RANK = {
    1: 50.0,
    2: 45.0,
    3: 40.0,
    4: 30.0,
    5: 25.0,
    6: 20.0,
    7: 19.5,
    8: 19.0,
    9: 18.5,
    10: 18.0,
    11: 17.5,
    12: 17.0,
    13: 16.5,
    14: 16.0,
    15: 15.5,
    16: 15.0,
    17: 14.5,
    18: 14.0,
    19: 13.5,
    20: 13.0,
    21: 12.5,
    22: 12.0,
    23: 11.5,
    24: 11.0,
    25: 10.5,
    26: 10.0,
    27: 9.5,
    28: 9.0,
    29: 8.5,
    30: 8.0,
    31: 7.5,
    32: 7.0,
    33: 6.5,
    34: 6.0,
    35: 5.5,
    36: 5.0,
    37: 4.5,
    38: 4.0,
    39: 3.5,
    40: 3.0,
    41: 2.5,
    42: 2.0,
    43: 1.5,
    44: 1.0,
    45: 0.5,
}

MAJOR_EVENT_POINTS_BY_RANK = {
    rank: points * 2.0
    for rank, points in NORMAL_EVENT_POINTS_BY_RANK.items()
}
