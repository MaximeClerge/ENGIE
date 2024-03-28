import numpy as np


def isint(x):

    """
    Returns True when x is an integer or a list of integers.
    """

    if (type(x) in [int, np.int32, np.int64]):
        return True

    if (type(x) in [float, bool, str, np.float64, dict]):
        return False

    if (type(x) in [list, tuple]):
        for val in x:
            if not(type(val) in [int, np.int32, np.int64]):
                return False
        return True

    if (x is None):
        return False

    if (x.dtype == int):
        return True

    return False
