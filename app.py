import time
from arbitrage import Arbitrage

arbitrage = Arbitrage()
while True:
    arbitrage.try_arbitrage("BTC")
    time.sleep(30)
    print("...............")