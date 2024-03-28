# -*- coding: utf-8 -*-
"""
Created on Sun Apr 12 16:26:28 2020

@author: GD5264
"""

from quantick.isint import isint
from quantick.ssm2hms import ssm2hms


class Order:

    def __init__(self, act_ssm, side, px, qty, prio, status, context=None):

        if not(isint(prio)):
            raise ValueError('prio must be an int')

        if not(isint(qty)):
            raise ValueError('qty must be an int')

        if not(side in ['B', 'S']):
            raise ValueError('side must be B or S')

        if not(qty > 0):
            raise ValueError('qty must be strictly positive, but qty = ' + str(qty))

        if not(status in ['placing', 'pending']):
            raise ValueError("status is either 'placing' or 'pending'")

        if (status == 'placing') and (prio >= 0):
            raise ValueError('cannot have prio >= 0 when status = placing')

        if (status == 'pending') and (prio < 0):
            raise ValueError('cannot have prio < 0 when status = pending')

        self.act_ssm = act_ssm
        self.act_hms = ssm2hms(act_ssm)
        self.side = side
        self.px = px
        self.qty = qty
        self.prio = prio
        self.status = status
        self.context = context

    def __str__(self):
        self_dict = vars(self)
        out = ''
        for key in self_dict:
            out += key + ': ' + str(self_dict[key]) + '\n'
        return out


if (__name__ == '__main__'):

    order = Order(act_ssm=1.,
                  side='B',
                  px=10.,
                  qty=1,
                  prio=-1,
                  status='placing')

    print(order)
