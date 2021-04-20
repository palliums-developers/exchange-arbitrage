import time
from cli.btc import Client as BClient
from cli.vls import Client as VClient
from network import *
from cli.eth import Client as EClient
from cli.bn import Client as BNClient
from arbitrage import try_arbitrage
from cli.tbn import Client as TBNClient
from violas_client import Client

bncli = BNClient()
ecli = EClient()
vcli = VClient()
bcli = BClient()
vcli.test_repay_borrow("vBTC")
vcli.test_repay_borrow("vUSDT")
vcli.test_clear_balance("vBTC")
vcli.test_clear_balance("vUSDT")
tbncli = TBNClient()

try_arbitrage(vcli, tbncli, bcli, ecli, "BTC")
