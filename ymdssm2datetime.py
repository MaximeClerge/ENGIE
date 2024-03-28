# -*- coding: utf-8 -*-
"""
Created on Tue Aug 18 09:43:34 2020

@author: GD5264
"""

import numpy as np
import pandas as pd


def ymdssm2datetime(ymd, ssm):

    """
    AIM:
    Convert time expressed in datetime
    into time expressed in Year Month Day (YYYY-MM-DD)

    INPUT:
    ymd: string (or list of strings) in yyyy-mm-dd format

    OUTPUT:
    dt: datetime
    """

    if (type(ssm) in [float, np.float64]):
        datetime = pd.to_datetime(ymd, format='%Y-%m-%d').to_pydatetime()
        timedelta = pd.to_timedelta(ssm, unit='s').to_pytimedelta()
        dt = datetime + timedelta
    else:
        dt = [ymdssm2datetime(ymd, ssm[idx]) for idx in range(len(ssm))]

    return dt


if (__name__ == '__main__'):
    ymd = '2023-02-09'
    ssm = 38115.996553
    dt = ymdssm2datetime(ymd, ssm)
    print('ymd =', ymd)
    print('ssm =', ssm)
    print('dt =', dt)

    ssms = [38115.996553, 38356.088676]
    dts = ymdssm2datetime(ymd, ssms)
    print('ssms =', ssms)
    print('dts =', dts)
