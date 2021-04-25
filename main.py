import time
from cli.btc import Client as BClient
from cli.vls import Client as VClient
from network import *
from cli.eth import Client as EClient
from cli.bn import Client as BNClient
from arbitrage import Arbitrage
from cli.tbn import Client as TBNClient
from violas_client import Client
from web3 import Web3



vcli = VClient()
vcli.test_repay_borrow("vBTC")
vcli.test_repay_borrow("vUSDT")
vcli.test_clear_balance("vBTC")
vcli.test_clear_balance("vUSDT")

def print_vls(vcli):
    print("viols................")
    print("balance", vcli._cli.get_balances(vls_addr))
    print("lock",vcli._cli.bank_get_lock_amounts(vls_addr))
    print("borrow", vcli._cli.bank_get_borrow_amounts(vls_addr))

def print_bn(bncli: TBNClient):
    print("bn.........................")
    print("btc",bncli.get_amount("BTC"))
    print("usdt", bncli.get_amount("USDT"))
    print("borrow", bncli._borrow)

arbirage = Arbitrage()
print_vls(arbirage._vcli)
print_bn(arbirage._bncli)
arbirage.try_arbitrage("BTC")
print_vls(arbirage._vcli)
print_bn(arbirage._bncli)
