import numpy as np


def ssm2hms(ssm, sep=''):
    """
    AIM:
    Convert time expressed in Seconds Since Midnight (SSM)
    into time expressed in HoursMinutesSeconds (HMS)

    INPUT:
    ssm: Number (i.e Float type or Int type) or list of numbers

    OUTPUT:
    hms: String or list of strings
    """

    if (type(ssm) in [list, np.ndarray]):
        foo = ssm
    else:
        foo = [ssm]

    hms = len(foo) * ['00' + sep + '00' + sep + '00']

    for ii in range(len(foo)):
        if (foo[ii] < 0):
            raise ValueError("ssm cannot be negative")
        if (foo[ii] >= 86400):
            raise ValueError("ssm is too large (maybe using milliseconds instead of seconds ? or use ssm2hmsd() ?)")
        hh = int(foo[ii]) // 3600
        mm = (int(foo[ii]) % 3600) // 60
        ss = foo[ii] - (hh*3600 + mm*60)
        hms[ii] = '%02d'%hh + sep + '%02d'%mm + sep + '%02d'%int(ss)

    if (type(ssm) is list):
        pass
    elif (type(ssm) is np.ndarray):
        hms = np.array(hms)
    else:
        hms = hms[0]

    return hms
