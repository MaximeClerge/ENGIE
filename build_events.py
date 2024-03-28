# -*- coding: utf-8 -*-
"""
Created on Thu Feb 29 13:57:46 2024

@author: GD5264
"""

from hms2ssm import hms2ssm
from issorted import issorted
import numpy as np
from ssm2hms import ssm2hms
from ymdssm2datetime import ymdssm2datetime


def build_events(trades_df,
                 quotes_df,
                 ticks_from_hms,
                 ticks_to_hms,
                 strat_heartbeat_dt,
                 strat_from_hms,
                 strat_to_hms):

    """
    _dt = duration in seconds e.g. 10
    _hms = Hours:Minutes:Seconds string e.g. "09:33:12"
    _ssm = Seconds Since Midnight float e.g. 34392.
    """

    func_name = "build_events()"

    ticks_from_ssm = hms2ssm(ticks_from_hms, ":")
    ticks_to_ssm = hms2ssm(ticks_to_hms, ":")

    # sanity checks on ymd
    trades_ymds = sorted(set(trades_df["ymd"]))
    if not(len(trades_ymds) == 1):
        raise ValueError(f"cannot have multiple trades_df['ymd'] values {trades_ymds}")
    trades_ymd = trades_ymds[0]
    quotes_ymds = sorted(set(quotes_df["ymd"]))
    if not(len(quotes_ymds) == 1):
        raise ValueError(f"cannot have multiple quotes_df['ymd'] values {quotes_ymds}")
    quotes_ymd = quotes_ymds[0]
    if not(trades_ymd == quotes_ymd):
        raise("trades_ymd = {trades_ymd} and quotes_ymd = {quotes_ymd} must be the same")
    ymd = trades_ymd

    # sanity checks on product
    trades_products = sorted(set(trades_df["product"]))
    if not(len(trades_products) == 1):
        raise ValueError(f"cannot have multiple trades_df['product'] values {trades_products}")
    trades_product = trades_products[0]
    quotes_products = sorted(set(quotes_df["product"]))
    if not(len(quotes_products) == 1):
        raise ValueError(f"cannot have multiple quotes_df['product''] values {quotes_products}")
    quotes_product = quotes_products[0]
    if not(trades_product == quotes_product):
        raise("trades_product = {trades_product} and quotes_product = {quotes_product} must be the same")
    product = trades_product

    # cast trades_df to trades_events
    trades_events = []
    for index, trades_row in trades_df.iterrows():
        ssm = trades_row["ssm"]
        if (ssm < ticks_from_ssm) or (ssm > ticks_to_ssm):
            continue
        trades_event = {}
        trades_event["ssm"] = ssm
        trades_event["hms"] = ssm2hms(ssm)
        trades_event["datetime"] = ymdssm2datetime(quotes_ymd, ssm)
        trades_event["type"] = "trades_update"
        trades_event["trades"] = {}
        trades_event["trades"][product] = {}
        trades_event["trades"][product]["last"] = trades_row["last"]
        trades_event["trades"][product]["last_qty"] = trades_row["last_qty"]
        trades_events.append(trades_event)
    print(func_name + f": nb_trade_events = {len(trades_events)}")

    # cast quotes_df to quotes_events
    quotes_events = []
    for index, quotes_row in quotes_df.iterrows():
        ssm = quotes_row["ssm"]
        if (ssm < ticks_from_ssm) or (ssm > ticks_to_ssm):
            continue
        quotes_event = {}
        quotes_event["ssm"] = ssm
        quotes_event["hms"] = ssm2hms(ssm)
        quotes_event["datetime"] = ymdssm2datetime(ymd, ssm)
        quotes_event["type"] = "quotes_update"
        quotes_event["quotes"] = {}
        quotes_event["quotes"][product] = {}
        quotes_event["quotes"][product]["bid_qty"] = quotes_row["bid_qty"]
        quotes_event["quotes"][product]["bid"] = quotes_row["bid"]
        quotes_event["quotes"][product]["ask"] = quotes_row["ask"]
        quotes_event["quotes"][product]["ask_qty"] = quotes_row["ask_qty"]
        quotes_events.append(quotes_event)
    print(func_name + f": nb_quotes_events = {len(quotes_events)}")

    # generate strat events
    strat_from_ssm = hms2ssm(strat_from_hms, ":")
    strat_to_ssm = hms2ssm(strat_to_hms, ":")
    strat_ssms = np.arange(strat_from_ssm, strat_to_ssm + strat_heartbeat_dt, strat_heartbeat_dt) + 1e-6
    strat_events = []
    for ssm in strat_ssms:
        strat_event = {}
        strat_event["hms"] = ymdssm2datetime(ymd, ssm)
        strat_event["ssm"] = ssm
        strat_event["datetime"] = ymdssm2datetime(ymd, ssm)
        strat_event["type"] = "strat_heartbeat"
        strat_events.append(strat_event)
    print(func_name + f": nb_strat_events = {len(strat_events)}")

    # combine events
    events = trades_events + quotes_events + strat_events

    # sort events
    events = sorted(events, key=lambda x: x["datetime"])

    # sanity check
    ssms = [event["ssm"] for event in events]
    if not(issorted(ssms)):
        raise ValueError("internal error on ssms")

    return events


if (__name__ == "__main__"):

    import os
    import pandas as pd
    import time

    script_name = "build_events"

    """
    parameters
    """

    ticks_dir = "C:\\Users\\GD5264\\OneDrive - ENGIE\\Projects\\Mines\\data_ticks"
    events_dir = "C:\\Users\\GD5264\\OneDrive - ENGIE\\Projects\\Mines\\data_events"

    # underlying
    under = "TTF-Hi-Cal-51.6-ICE-ENDEX"

    # maturity
    matu = "Mar-24"

    # date in yyyy-mm-dd format
    ymd = "2024-02-08"

    # ticks observation period
    ticks_from_hms = "08:50:00"
    ticks_to_hms = "17:30:00"

    # strategy heartbeat and active period
    strat_heartbeat_dt = 10
    strat_from_hms = "09:05:00"
    strat_to_hms = "17:00:00"

    """
    input file names
    """

    trades_fname = f"trades_{under}_{matu}_{ymd}.snappy.parquet"
    quotes_fname = f"quotes_10_with-implied_{under}_{matu}_{ymd}.snappy.parquet"

    trades_path = os.path.join(ticks_dir, trades_fname)
    quotes_path = os.path.join(ticks_dir, quotes_fname)

    """
    read trades and quotes
    """

    print(script_name + f": read {trades_path}")
    trades_df = pd.read_parquet(trades_path, engine='pyarrow')
    print(script_name + f": len(trades_df) = {len(trades_df)}")

    print(script_name + f": read {quotes_path}")
    quotes_df = pd.read_parquet(quotes_path, engine='pyarrow')
    print(script_name + f": len(quotes_df) = {len(quotes_df)}")

    """
    cast ticks data and strategy heartbeats into a single events list
    """

    print(script_name + ": building events ...")
    tic = time.time()
    events = build_events(trades_df,
                          quotes_df,
                          ticks_from_hms,
                          ticks_to_hms,
                          strat_heartbeat_dt,
                          strat_from_hms,
                          strat_to_hms)
    toc = time.time()
    print(script_name + ": done in", toc-tic, "sec")
    print(script_name + f": nb_events = {len(events)}")
