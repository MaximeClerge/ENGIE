# Import distributed modules
import copy
import numpy as np


def hms2ssm(hms, sep=''):

    """
    AIM:
    Convert time expressed in HoursMinutesSeconds (HMS)
    into time expressed in Seconds Since Midnight (SSM)
    There is however 1 exception, if hms is equal to 'close'
    then the returned value is 100000.

    INPUT:
    hms: String or list of strings
    sep: separator

    OUTPUT:
    ssm: Number (i.e Float type or Int type) or list of numbers
    """

    if not(type(hms) is list):
        foo = [hms]
    else:
        foo = copy.deepcopy(hms)

    ssm = len(foo) * [0]

    if not(sep == ''):
        for ii in range(len(foo)):
            foo[ii] = foo[ii].replace(sep, '')

    for ii in range(len(foo)):
        if (foo[ii] == "close"):
            ssm[ii] = 100000.
        elif (len(foo[ii]) == 4):
            hh = foo[ii][0:2]
            mm = foo[ii][2:4]
            ssm[ii] = 3600*int(hh) + 60*int(mm)
        elif (len(foo[ii]) == 6):
            hh = foo[ii][0:2]
            mm = foo[ii][2:4]
            ss = foo[ii][4:6]
            ssm[ii] = 3600*int(hh) + 60*int(mm) + int(ss)
        elif (len(foo[ii]) == 9):
            hh = foo[ii][0:2]
            mm = foo[ii][2:4]
            ss = foo[ii][4:6]
            ms = foo[ii][6:9]
            ssm[ii] = 3600*int(hh) + 60*int(mm) + int(ss) + 1e-3*float(ms)
        elif (len(foo[ii]) == 12):
            hh = foo[ii][0:2]
            mm = foo[ii][2:4]
            ss = foo[ii][4:6]
            mms = foo[ii][6:12]
            ssm[ii] = 3600*int(hh) + 60*int(mm) + int(ss) + 1e-6*float(mms)
        else:
            raise ValueError("hms[" + str(ii) + "]=" + foo[ii] + " has a wrong length (it must be 4, 6, 9 or 12) and is not 'close'")

    if not(type(hms) in [list, np.ndarray]):
        ssm = ssm[0]

    return ssm
