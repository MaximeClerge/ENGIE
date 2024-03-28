# -*- coding: utf-8 -*-
"""
Created on Fri Jun  4 11:38:33 2021

@author: GD5264
"""

from quantick.hms2ssm import hms2ssm


class StratBasic:

    def __init__(self, strat_params):

        # unpack strat_params
        self.trade_from_hms = strat_params["trade_from_hms"]
        self.trade_to_hms = strat_params["trade_to_hms"]
        self.way = strat_params["way"]
        self.target_signed_qty = strat_params["target_signed_qty"]
        self.target_price = strat_params["target_price"]
        self.prod_exeks_signed_qty = 0

        # sanity checks
        if not(self.way in ["buy", "sell"]):
            raise ValueError(f"cannot have way = {self.way}")
        if (self.way == "buy") and (self.target_signed_qty < 0):
            raise ValueError(f"cannot have target_signed_qty = {self.target_signed_qty} when way = {self.way}")
        if (self.way == "sell") and (self.target_signed_qty > 0):
            raise ValueError(f"cannot have target_signed_qty = {self.target_signed_qty} when way = {self.way}")

        trade_from_ssm = hms2ssm(self.trade_from_hms, ':')
        trade_to_ssm = hms2ssm(self.trade_to_hms, ':')
        if not(trade_to_ssm > trade_from_ssm):
            raise ValueError(f"cannot have trade_from_hms = {self.trade_from_hms} and trade_to_hms = {self.trade_to_hms}")

    def my_price(self):
        return self.target_price

    def my_qty(self):
        # sanity checks
        if (self.way == "buy") and (self.prod_signed_exeks_qty < 0):
            raise ValueError(f"cannot have prod_signed_exeks_qty = {self.prod_signed_exeks_qty} when way = {self.way}")
        if (self.way == "sell") and (self.target_signed_qty > 0):
            raise ValueError(f"cannot have prod_signed_exeks_qty = {self.prod_signed_exeks_qty} when way = {self.way}")

        remaining_signed_qty = self.target_signed_qty - self.prod_exeks_signed_qty

        # sanity checks
        if ((self.way == "buy") and (remaining_signed_qty < 0) or
            (self.way == "sell") and (remaining_signed_qty > 0)):
            raise ValueError(f"cannot have remaining_signed_qty = {remaining_signed_qty} when way = {self.way}")

        remaining_qty = abs(remaining_signed_qty)

        return remaining_qty
