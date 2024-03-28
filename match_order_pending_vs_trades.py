# -*- coding: utf-8 -*-
"""
Created on Mon Aug 24 09:37:09 2020

@author: GD5264
"""

import numpy as np

from Order import Order
from Exek import Exek


def match_order_pending_vs_trades(order, trades):

    """
    Refresh order execution triggered by a trades update.
    """

    func_name = "match_order_pending_vs_trades()"

    ssm_tol = 1e-6
    px_tol = 1e-6
    side2sign = {'B': 1, 'S': -1}

    """
    order sanity check
    """

    if (order is None):
        # No order -> No exectution
        new_order = None
        exeks = []
        return new_order, exeks

    if (trades is None):
        # No trades -> No exectution
        new_order = order
        exeks = []
        return new_order, exeks

    if not(order.status == 'pending'):
        raise ValueError("Status of order must be 'pending'")

    """
    match trades update
    """

    if (order.side == 'B'):
        exeks = []
        if (type(trades) is dict):
            S_trades = []
            if (trades['ssm'] > (order.act_ssm-ssm_tol)) & ((trades['last'] - px_tol) < order.px):
                S_trades = [trades]
        else:
            keep_p = (trades['ssm'] > (order.act_ssm-ssm_tol)) & ((trades['last'] - px_tol) < order.px)
            S_trades = trades[keep_p]
        order_prio = order.prio
        order_qty = order.qty
        for S_trade in S_trades:
            if (S_trade['last_qty'] <= order_prio):
                order_prio = order_prio - S_trade['last_qty']
            else:
                exek_qty = min(S_trade['last_qty']-order_prio, order_qty)
                exek = Exek(ssm=S_trade['ssm'],
                            side='B',
                            px=order.px,
                            qty=exek_qty,
                            signed_qty=side2sign[order.side] * exek_qty,
                            context='match-order-pending-vs-trades',
                            order=order)
                exeks.append(exek)
                order_prio = 0
                order_qty = order_qty - exek_qty
                if (order_qty == 0):
                    break

    elif (order.side == 'S'):
        exeks = []
        if (type(trades) is dict):
            B_trades = []
            if (trades['ssm'] > (order.act_ssm-ssm_tol)) & ((trades['last'] + px_tol) > order.px):
                B_trades = [trades]
        else:
            keep_p = (trades['ssm'] > (order.act_ssm-ssm_tol)) & ((trades['last'] + px_tol) > order.px)
            B_trades = trades[keep_p]
        order_prio = order.prio
        order_qty = order.qty
        for B_trade in B_trades:
            if (B_trade['last_qty'] <= order_prio):
                order_prio = order_prio - B_trade['last_qty']
            else:
                exek_qty = min(B_trade['last_qty']-order_prio, order_qty)
                exek = Exek(ssm=B_trade['ssm'],
                            side='S',
                            px=order.px,
                            qty=exek_qty,
                            signed_qty=side2sign[order.side] * exek_qty,
                            context='match-order-pending-vs-trades',
                            order=order)
                exeks.append(exek)
                order_prio = 0
                order_qty = order_qty - exek_qty
                if (order_qty == 0):
                    break
    else:
        raise ValueError(f"cannot have order.side = {order.side}")

    if (order_qty > 0):
        new_order = Order(act_ssm=order.act_ssm,
                          side=order.side,
                          px=order.px,
                          qty=order_qty,
                          prio=order_prio,
                          status='pending',
                          context=order.context)
    else:
        new_order = None

    return new_order, exeks


if (__name__ == '__main__'):

    trades = [(1.0,  9.0, 100),
              (2.0, 10.0,   6),
              (3.0,  8.0,   4)]
    dtype = {'names': ['ssm', 'last', 'last_qty'],
             'formats': [float, float, int]}
    trades = np.array(trades, dtype=dtype)

    order = Order(act_ssm=1.0,
                  side='S',
                  px=9.,
                  qty=105,
                  prio=1,
                  status='pending')

    new_order, exeks = match_order_pending_vs_trades(order, trades)

    print('order:')
    print('------')
    print(order, '\n')
    print('trades:')
    print('------')
    print(trades, '\n')
    print('new_order:')
    print('----------')
    print(new_order, '\n')
    print('exeks:')
    print('-----')
    print(exeks, '\n')
