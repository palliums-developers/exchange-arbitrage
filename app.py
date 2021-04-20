import time
from network import create_client
from arbitrage import exchange_arbitrage

client = create_client()
while True:
    exchange_arbitrage(client)
    time.sleep(30)
    print("...............")