# -*- coding: utf-8 -*-
"""
Created on Sun Apr 12 16:26:28 2020

@author: GD5264
"""

from isint import isint


class Exek:

    def __init__(self, ssm, side, px, qty, signed_qty, context=None, order=None):

        if not(isint(qty)):
            raise ValueError('qty must be an int')

        if not(qty > 0):
            raise ValueError('qty must be strictly positive')

        if not(isint(signed_qty)):
            raise ValueError('signed_qty must be an int')

        if not(qty == abs(signed_qty)):
            raise ValueError('must have qty=|signd_qty|')

        if not(side in ['B', 'S']):
            raise ValueError('side must be B or S')

        if ((side == 'B') and (signed_qty < 0)):
            raise ValueError('signed_qty must be >0 when side=B')

        if ((side == 'S') and (signed_qty > 0)):
            raise ValueError('signed_qty must be <0 when side=S')

        self.ssm = ssm
        self.side = side
        self.px = px
        self.qty = qty
        self.signed_qty = signed_qty
        self.context = context
        self.order = order

    def __str__(self):
        self_dict = vars(self)
        out = ''
        for key in self_dict:
            out += key + ': ' + str(self_dict[key]) + '\n'
        return out


if (__name__ == '__main__'):
    exek = Exek(ssm=1.,
                side='B',
                px=10.,
                qty=1,
                signed_qty=1)
