import pandas as pd
from datetime import *

class Strategy:

  def __init__(self) -> None:
    self.capital: float = 100_000_000
    self.portfolio_value: float = 0

    self.start_date: datetime = datetime(2024, 1, 1)
    self.end_date: datetime = datetime(2024, 3, 30)

    self.expiration_date = [datetime(2024, 1, 19), datetime(2024, 2, 16), datetime(2024, 3, 15)]

    self.options: pd.DataFrame = pd.read_csv("data/cleaned_options_data.csv")
    # self.options["day"] = self.options["ts_recv"].apply(lambda x: x.split("T")[0])

    self.underlying = pd.read_csv("data/underlying_data_hour.csv")
    self.underlying.columns = self.underlying.columns.str.lower()

  def best_call(self, current_date : datetime, expiration_date : datetime):    
    # possible = self.options[self.options['symbol'].apply(lambda x: expiration_date.strftime("%Y%m%d")[2:] + "C" in x)]
    possible = self.options[self.options['symbol'].apply(lambda x: expiration_date.strftime("%Y%m%d")[2:] + "C" in x) & self.options['ts_recv'].apply(lambda x: current_date in x)]
    best_row = possible.loc[possible["ask_px_00"].idxmax()]
    return best_row

  def best_put(self, current_date : datetime, expiration_date : datetime):
    # possible = self.options[self.options['symbol'].apply(lambda x: expiration_date.strftime("%Y%m%d")[2:] + "P" in x)]
    possible = self.options[self.options['symbol'].apply(lambda x: expiration_date.strftime("%Y%m%d")[2:] + "P" in x) & self.options['ts_recv'].apply(lambda x: current_date in x)]
    best_row = possible.loc[possible["ask_px_00"].idxmax()]
    return best_row

  def generate_orders(self) -> pd.DataFrame:
    orders = []
    exp_idx = 0

    for _, prev in self.underlying.iterrows():
      # print(prev)
      expiration_date = self.expiration_date[exp_idx]
      current_date = prev['date']

      if datetime(int(current_date[0:4]), int(current_date[5:7]), int(current_date[8:10])) >= expiration_date:
        exp_idx = min(2, exp_idx+1)

      prev_open = prev['open']
      prev_close = prev['close']
      prev_return = prev_close - prev_open
      action = "B"

      try:
        if prev_return > 0:
          row = self.best_call(current_date, expiration_date)
          order_size = min(1, row["ask_sz_00"])
        else:
          row = self.best_put(current_date, expiration_date)
          order_size = min(1, row["ask_sz_00"])
        
        order = {
            "datetime" : row["ts_recv"],
            "option_symbol" : row["symbol"],
            "action" : action,
            "order_size" : order_size
        }

        print(order)
        orders.append(order)
      except:
        continue
    
    return pd.DataFrame(orders)
