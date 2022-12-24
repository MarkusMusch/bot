import pandas as pd
from datetime import datetime

from src.MarketStructure import MarketStructure
from src.Assets import btc_cont

ms = MarketStructure(btc_cont.ath, btc_cont.prev_low, btc_cont.ath,
                     btc_cont.prev_low)

df = pd.read_csv('./database/SOLBUSD_1h.csv')

for idx, row in df.iterrows():
    ms.next_candle(row)

ms.structure