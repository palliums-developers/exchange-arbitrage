from network import *
from cli.eth import Client
from eth_account import Account
import pytest

to_addr = "0x4d6Bb4ed029B33cF25D0810b029bd8B1A6bcAb7B"


class EAccount:
    def __init__(self, priv_key):
        self.priv_key = priv_key
        ac = Account.from_key(eth_private_key)
        self.addr = ac.address

@pytest.fixture
def cli():
    from cli.eth import Client
    return Client()

@pytest.fixture
def sender():
    from network import eth_private_key
    return EAccount(eth_private_key)

@pytest.fixture
def receiver_addr():
    import web3
    return web3.Web3.toChecksumAddress("0x6f08730da8e7de49a4064d2217c6b68d7e61e727")

@pytest.fixture
def violas_addr():
    return "b14bc3286e4b9b41c86022f2e614d721"

@pytest.fixture
def e2v_addr():
    return e2v_contract_addr

@pytest.fixture
def usdt_addr():
    return usdt_contract_addr

@pytest.fixture
def tokens():
    return ("vlstusdt", )

def test_transfer(cli, sender, receiver_addr, tokens):
    amount = 78
    for token in tokens:
        s_start = cli.get_balance(sender.addr, token)
        r_start = cli.get_balance(receiver_addr, token)
        cli.transfer(sender.priv_key, receiver_addr, token, amount)
        s_end = cli.get_balance(sender.addr, token)
        r_end = cli.get_balance(receiver_addr, token)
        assert s_start - s_end == amount
        assert r_end - r_start == amount




