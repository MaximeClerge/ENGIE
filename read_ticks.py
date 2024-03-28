# -*- coding: utf-8 -*-
"""
Created on Fri Feb  9 15:05:24 2024

@author: GD5264
"""

import os
import pandas as pd
import matplotlib.pyplot as plt


script_name = "read_ticks"

plt.close("all")

"""
parameters
"""

ticks_dir = "C:/Users/GD5264/Downloads/"

# underlying
under = "TTF-Hi-Cal-51.6-ICE-ENDEX"

# maturity
matu = "Mar-24"

# date in yyyy-mm-dd format
ymd = "2024-02-08"

"""
file names
"""

trades_fname = f"trades_{under}_{matu}_{ymd}.snappy.parquet"
quotes_fname = f"quotes_10_with-implied_{under}_{matu}_{ymd}.snappy.parquet"

trades_path = os.path.join(ticks_dir, trades_fname)
quotes_path = os.path.join(ticks_dir, quotes_fname)


"""
import trades and best bid-ask quotes
"""

print(script_name + ": read", trades_path)
trades_df = df = pd.read_parquet(trades_path, engine='pyarrow')

print(script_name + ": read", quotes_path)
quotes_df = df = pd.read_parquet(quotes_path, engine='pyarrow')

fig, axes = plt.subplots()
trades_df.plot(ax=axes, x="datetime", y="last", style="ro")
quotes_df.plot(ax=axes, x="datetime", y=["bid", "ask"])
plt.title(f"trades and quotes for ({under}, {matu}) on {ymd}")
plt.grid("on")
plt.legend()
