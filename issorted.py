# -*- coding: utf-8 -*-
"""
Created on Fri Jun 16 09:25:50 2023

@author: GD5264
"""


def issorted(vals):
    lst = list(vals)
    if (lst == sorted(lst)):
        return True
    else:
        return False
