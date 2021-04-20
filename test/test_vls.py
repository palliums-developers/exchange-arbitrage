import time
import pytest
from cli.vls import Client as VClient
from cli.btc import Client as BClient
from cli.eth import Client as EClient

from network import *


@pytest.fixture
def vcli():
    return VClient()

@pytest.fixture
def bcli():
    return BClient()

@pytest.fixture
def ecli():
    return EClient()


def test_to_eth(vcli, ecli):
    s_eth = ecli.get_balance(eth_addr, "vlstusdt")
    vcli.to_erc20(eth_addr, 8888, currency_code="vUSDT")
    time.sleep(120)
    e_eth = ecli.get_balance(eth_addr, "vlstusdt")
    assert e_eth > s_eth

def test_to_btc(vcli, bcli):
    s_btc = bcli.get_balance(btc_addr)
    vcli.to_btc(btc_addr, 88)
    time.sleep(240)
    e_btc = bcli.get_balance(btc_addr)
    assert e_btc > s_btc