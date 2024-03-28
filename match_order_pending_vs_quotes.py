# -*- coding: utf-8 -*-
"""
Created on Mon Aug 24 09:37:09 2020

@author: GD5264
"""

import numpy as np

from Order import Order
from Exek import Exek


def match_order_pending_vs_quotes(order, quotes):

    """
    Refresh order execution triggered by a quotes update.
    """

    func_name = 'match_order_pending_vs_quotes()'

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

    if (quotes is None):
        # No quotes -> No exectution
        new_order = order
        exeks = []
        return new_order, exeks

    if not(order.status == 'pending'):
        raise ValueError("Status of order must be 'pending'")

    """
    match quotes update
    """

    if (order.side == 'B'):
        exeks = []
        if (type(quotes) is dict):
            S_quotes = []
            if (quotes['ssm'] > (order.act_ssm-ssm_tol)) & ((quotes['ask'] - px_tol) < order.px) & (quotes['ask_qty'] > 0):
                S_quotes = [quotes]
        else:
            keep_p = (quotes['ssm'] > (order.act_ssm-ssm_tol)) & ((quotes['ask'] - px_tol) < order.px) & (quotes['ask_qty'] > 0)
            S_quotes = quotes[keep_p]
        order_prio = order.prio
        order_qty = order.qty
        for S_quote in S_quotes:
            if (S_quote['ask_qty'] <= order_prio):
                order_prio = order_prio - S_quote['ask_qty']
            else:
                exek_qty = min(S_quote['ask_qty']-order_prio, order_qty)
                exek = Exek(ssm=S_quote['ssm'],
                            side='B',
                            px=order.px,
                            qty=exek_qty,
                            signed_qty=side2sign[order.side] * exek_qty,
                            context='match-order-pending-vs-quotes',
                            order=order)
                exeks.append(exek)
                order_prio = 0
                order_qty = order_qty - exek_qty
                if (order_qty == 0):
                    break

    elif (order.side == 'S'):
        exeks = []
        if (type(quotes) is dict):
            B_quotes = []
            if (quotes['ssm'] > (order.act_ssm-ssm_tol)) & ((quotes['bid'] + px_tol) > order.px) & (quotes['bid_qty'] > 0):
                B_quotes = [quotes]
        else:
            keep_p = (quotes['ssm'] > (order.act_ssm-ssm_tol)) & ((quotes['bid'] + px_tol) > order.px) & (quotes['bid_qty'] > 0)
            B_quotes = quotes[keep_p]
        order_prio = order.prio
        order_qty = order.qty
        for B_quote in B_quotes:
            if (B_quote['bid_qty'] <= order_prio):
                order_prio = order_prio - B_quote['bid_qty']
            else:
                exek_qty = min(B_quote['bid_qty']-order_prio, order_qty)
                exek = Exek(ssm=B_quote['ssm'],
                            side='S',
                            px=order.px,
                            qty=exek_qty,
                            signed_qty=side2sign[order.side] * exek_qty,
                            context='match-order-pending-vs-quotes',
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

    quotes = [(1.0,  9, 100, 110,  3),
              (2.0, 10, 110, 120, 10),
              (3.0,  8, 120, 121,  2)]
    dtype = {'names':   ['ssm', 'bid_qty', 'bid', 'ask', 'ask_qty'],
             'formats': [float,    int, float, float,  int]}
    quotes = np.array(quotes, dtype=dtype)

    order = Order(act_ssm=1.0,
                  side='B',
                  px=120,
                  qty=20,
                  prio=1,
                  status='pending')

    new_order, exeks = match_order_pending_vs_quotes(order, quotes)

    print('order:')
    print('------')
    print(order, '\n')
    print('quotes:')
    print('------')
    print(quotes, '\n')
    print('new_order:')
    print('----------')
    print(new_order, '\n')
    print('exeks:')
    print('-----')
    print(exeks, '\n')
