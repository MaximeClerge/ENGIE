# -*- coding: utf-8 -*-
"""
Created on Wed Mar  6 11:53:43 2024

@author: GD5264
"""

from datetime import datetime, timedelta
import numpy as np

from match_order_placing_vs_quotes import match_order_placing_vs_quotes
from match_order_pending_vs_quotes import match_order_pending_vs_quotes
from match_order_pending_vs_trades import match_order_pending_vs_trades
from ssm2hms import ssm2hms
from Order import Order


def perform_backtest(strat, product, events, verbose=True):

    func_name = "perform_backtest()"

    # initialize variables
    prod_status = "prod-isnot-tradable_prod-waiting-for-1st-quotes-update"
    prod_buy_order = None
    prod_sell_order = None
    prod_exeks_dfs = []

    for ev, event in enumerate(events):

        # unpack event
        now_ssm = event["ssm"]
        now_hms = event["hms"]
        now_datetime = event["datetime"]

        if (event["type"] == "quotes_update"):
            prod_quote = event["quotes"][product]
            prod_quote["ssm"] = event["ssm"]
            prod_quote["hms"] = event["hms"]
            prod_bid = prod_quote["bid"]
            prod_ask = prod_quote["ask"]

            prod_status = "prod-is-tradable"
            if not(prod_bid < prod_ask):
                if verbose:
                    print(func_name + f": WARNING @ {now_hms}, prod_bid = {prod_bid}, prod_ask = {prod_ask}")
                prod_status = "prod-isnot-tradable_prod-bid-ask-crossed"

        if prod_status.startswith("prod-is-tradable"):

            if (event["type"] == "strat_heartbeat"):

                my_price = strat.my_price()
                my_qty = strat.my_qty()

                # sanity check
                if not(np.isfinite(my_price)):
                    raise ValueError(f"cannot have my_price = {my_price}")
                if not(np.isfinite(my_qty)) or (my_qty < 0):
                    raise ValueError(f"cannot have my_qty = {my_qty}")

                """
                cancel/place order
                """

                if (strat.way == "buy"):

                    place_prod_buy_order_status = None
                    if (my_qty < 1e-6):
                        if (prod_buy_order is None):
                            place_prod_buy_order_status = "prod-buy-order-none"
                        else:
                            place_prod_buy_order_status = "prod-buy-order-cancel"
                            # cancel buy-order
                            prod_buy_order = None
                    elif (prod_buy_order is None):
                        place_prod_buy_order_status = "prod-buy-order-place"
                    elif (abs(my_price - prod_buy_order.px) > 1e-6):
                        place_prod_buy_order_status = "prod-buy-order-cancel-place"
                        # cancel buy-order
                        prod_buy_order = None
                    else:
                        place_prod_buy_order_status = "prod-buy-order-keep"

                    if place_prod_buy_order_status in ("prod-buy-order-place", "prod-buy-order-cancel-place"):
                        # place buy-order
                        prod_buy_order = Order(act_ssm=now_ssm,
                                               side="B",
                                               px=my_price,
                                               qty=my_qty,
                                               prio=-1,
                                               status="placing",
                                               context=event["type"] + " | " + place_prod_buy_order_status)

                elif (strat.way == "sell"):

                    place_prod_sell_order_status = None
                    if (my_qty < 1e-6):
                        if (prod_sell_order is None):
                            place_prod_sell_order_status = "prod-sell-order-none"
                        else:
                            place_prod_sell_order_status = "prod-sell-order-cancel"
                            # cancel sell-order
                            prod_sell_order = None
                    elif (prod_sell_order is None):
                        place_prod_sell_order_status = "prod-sell-order-place"
                    elif (abs(my_price - prod_sell_order.px) > 1e-6):
                        place_prod_sell_order_status = "prod-sell-order-cancel-place"
                        # cancel sell-order
                        prod_sell_order = None
                    else:
                        place_prod_sell_order_status = "prod-sell-order-keep"

                    if place_prod_sell_order_status in ("prod-sell-order-place", "prod-sell-order-cancel-place"):
                        # place sell-order
                        prod_sell_order = Order(act_ssm=now_ssm,
                                                side="S",
                                                px=my_price,
                                                qty=my_qty,
                                                prio=-1,
                                                status="placing",
                                                context=event["type"] + " | " + place_prod_sell_order_status)
                else:
                    raise ValueError(f"cannot have strat.way = {strat.way}")

            """
            match order
            """

            for prod_order_side in ["B", "S"]:

                if (prod_order_side == "B"):
                    prod_order = prod_buy_order
                elif (prod_order_side == "S"):
                    prod_order = prod_sell_order
                else:
                    raise ValueError("cannot have prod_order_side = " + prod_order_side)

                if (prod_order is None):
                    prod_exeks = []
                    continue

                prev_prod_order = prod_order

                prod_exeks_placing = []
                if (prod_order.status == "placing"):
                    prod_order, prod_exeks_placing = match_order_placing_vs_quotes(prod_order, prod_quote)
                    # stop

                prod_exeks_pending = []
                if (event["type"] == "trades_update"):
                    prod_trade = event["trades"][product]
                    prod_trade["ssm"] = event["ssm"]
                    prod_trade["hms"] = event["hms"]
                    prod_order, prod_exeks_pending = match_order_pending_vs_trades(prod_order, prod_trade)
                elif (event["type"] == "quotes_update"):
                    prod_quote = event["quotes"][product]
                    prod_quote["ssm"] = event["ssm"]
                    prod_quote["hms"] = event["hms"]
                    prod_order, prod_exeks_pending = match_order_pending_vs_quotes(prod_order, prod_quote)

                if (prod_order_side == "B"):
                    prod_buy_order = prod_order
                elif (prod_order_side == "S"):
                    prod_sell_order = prod_order

                prod_exeks = prod_exeks_placing + prod_exeks_pending

                if (len(prod_exeks) > 0):
                    if verbose:
                        print(func_name + ": prod_order = " + ssm2hms(prev_prod_order.act_ssm, ":"),
                              prev_prod_order.side,
                              prev_prod_order.qty,
                              prev_prod_order.px,
                              prev_prod_order.context,
                              "-> exeks: ",
                              [(ssm2hms(prod_exek.ssm, ":"), prod_exek.side, prod_exek.qty, prod_exek.px) for prod_exek in prod_exeks])
                    else:
                        pass
                else:
                    # print(func_name + ": prod_order = " + Utils.ssm2hms(prev_prod_order.act_ssm, ":"), prev_prod_order.side, prev_prod_order.qty, prev_prod_order.px)
                    pass

            """
            stack product exeks in a DataFrame
            """

            for prod_exek in prod_exeks:
                prod_exek_hms = ssm2hms(prod_exek.ssm)
                prod_exek_dict = {"datetime": [datetime.strptime(ymd, '%Y-%m-%d') + timedelta(seconds=prod_exek.ssm)],
                                  "ymd": [ymd],
                                  "ssm": [prod_exek.ssm],
                                  "hms": [prod_exek_hms],
                                  "side": [prod_exek.side],
                                  "qty": [prod_exek.qty],
                                  "signed_qty": [prod_exek.signed_qty],
                                  "px": [prod_exek.px],
                                  "context": [prod_exek.context],
                                  "order_context": [prod_exek.order.context]}
                prod_exek_df = pd.DataFrame(prod_exek_dict)
                prod_exeks_dfs.append(prod_exek_df)
                strat.prod_exeks_signed_qty += prod_exek_dict["signed_qty"][0]

    strat.prod_exeks_df = None
    if (len(prod_exeks_dfs) > 0):
        strat.prod_exeks_df = pd.concat(prod_exeks_dfs)
        strat.prod_exeks_df.reset_index(drop=True, inplace=True)


if (__name__ == "__main__"):

    import os
    import pandas as pd
    import time

    from build_events import build_events
    from StratBasic import StratBasic

    script_name = "perform_backtest"

    """
    parameters
    """

    ticks_dir = "C:\\Users\\GD5264\\OneDrive - ENGIE\\Projects\\Mines\\data_ticks"

    # underlying
    under = "TTF-Hi-Cal-51.6-ICE-ENDEX"

    # maturity
    matu = "Mar-24"

    # date in yyyy-mm-dd format
    ymd = "2024-02-08"

    # ticks observation period
    ticks_from_hms = "08:50:00"
    ticks_to_hms = "16:31:00"

    # strategy parameters
    strat_params = {}
    strat_params["heartbeat_dt"] = 10
    strat_params["trade_from_hms"] = "08:30:00"
    strat_params["trade_to_hms"] = "16:30:00"
    strat_params["way"] = "sell"
    strat_params["target_signed_qty"] = -40
    strat_params["target_price"] = 28.51

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
                          strat_params["heartbeat_dt"],
                          strat_params["trade_from_hms"],
                          strat_params["trade_to_hms"])
    toc = time.time()
    print(script_name + ": done in", toc-tic, "sec")
    print(script_name + f": nb_events = {len(events)}")

    strat = StratBasic(strat_params)

    product = under + "_" + matu

    perform_backtest(strat,
                     product,
                     events,
                     verbose=True)

    print(script_name + ": ")
    print(strat.prod_exeks_df)
