# -*- coding: utf-8 -*-
"""
Created on Mon Aug 24 09:37:09 2020

@author: GD5264
"""

import numpy as np

from Order import Order
from Exek import Exek


def match_order_placing_vs_quotes(order, quotes):

    """
    Refresh order execution triggered by a quote update.
    """

    func_name = 'match_order_placing_vs_quotes()'

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

    if not(order.qty > 0):
        # Order is not well specified -> No execution & Cancel order
        print(func_name + f": WARNING order.qty = {order.qty} -> order is cancelled")
        new_order = None
        exeks = []
        return new_order, exeks

    if not(order.status == "placing"):
        raise ValueError("Status of order must be 'placing'")

    """
    find most recent quote
    """

    if (type(quotes) is dict):
        quote = quotes
        if not((quote['ssm'] - ssm_tol) < order.act_ssm):
            raise ValueError("quote is not prior to order placing -> order cannot be placed")
    else:
        keep_p = (quotes['ssm'] - ssm_tol) < order.act_ssm
        if not(np.any(keep_p)):
            raise ValueError("no quotes prior to order placing -> order cannot be placed")
        keep_k = np.where(keep_p)[0][-1]
        quote = quotes[keep_k]

    """
    quote sanity check
    """

    if not(quote['ask'] > quote['bid']):
        # Book is crossed -> No exectution & Cancel order
        print(func_name + f": WARNING bid = {quote['bid']} and ask = {quote['ask']} -> order is cancelled")
        new_order = None
        exeks = []
        return new_order, exeks

    """
    match order
    """

    if (order.side == 'B'):

        if (order.px > (quote['ask']-px_tol)):
            exek_qty = min(order.qty, quote['ask_qty'])
            exek_px = quote['ask']
            exek = Exek(ssm=order.act_ssm,
                        side='B',
                        px=exek_px,
                        qty=exek_qty,
                        signed_qty=side2sign[order.side] * exek_qty,
                        context='match-order-placing-vs-quotes',
                        order=order)
            new_order_qty = order.qty - exek_qty
            new_order_prio = exek_qty
        elif (order.px > (quote['bid'] + px_tol)):
            exek = None
            new_order_qty = order.qty
            new_order_prio = 0
        else:
            exek = None
            new_order_qty = order.qty
            new_order_prio = quote['bid_qty']

    elif (order.side == 'S'):

        if (order.px < (quote['bid']+px_tol)):
            exek_qty = min(order.qty, quote['bid_qty'])
            exek_px = quote['bid']
            exek = Exek(ssm=order.act_ssm,
                        side='S',
                        px=exek_px,
                        qty=exek_qty,
                        signed_qty=side2sign[order.side] * exek_qty,
                        context='match-order-placing-vs-quotes',
                        order=order)
            new_order_qty = order.qty - exek_qty
            new_order_prio = exek_qty
        elif (order.px < (quote['ask']-px_tol)):
            exek = None
            new_order_qty = order.qty
            new_order_prio = 0
        else:
            exek = None
            new_order_qty = order.qty
            new_order_prio = quote['ask_qty']

    else:
        raise ValueError(f"cannot have order.side = {order.side}")

    if (new_order_qty > 0):
        new_order = Order(act_ssm=order.act_ssm,
                          side=order.side,
                          px=order.px,
                          qty=new_order_qty,
                          prio=new_order_prio,
                          status='pending',
                          context=order.context)
    else:
        new_order = None

    if (exek is None):
        exeks = []
    else:
        exeks = [exek]

    return new_order, exeks


if (__name__ == '__main__'):

    quotes = [(1.0,   9,  9., 100., 100),
              (2.0, 100, 10.,  11., 110),
              (3.0,   8,  8.,   4.,   4)]

    dtype = [('ssm', float),
             ('bid_qty', int),
             ('bid', float),
             ('ask', float),
             ('ask_qty', int)]

    quotes = np.array(quotes, dtype=dtype)

    order = Order(act_ssm=1.0,
                  side='S',
                  px=9.,
                  qty=105,
                  prio=-1,
                  status='placing')

    new_order, exeks = match_order_placing_vs_quotes(order, quotes)

    print('quotes:')
    print('------')
    print(quotes, '\n')
    print('order:')
    print('------')
    print(order, '\n')
    print('new_order:')
    print('----------')
    print(new_order, '\n')
    print('exeks:')
    print('-----')
    print(exeks, '\n')
