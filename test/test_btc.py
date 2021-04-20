import pytest
from cli.btc import Client, Account
from network import btc_private_key, http_url

@pytest.fixture()
def client():
    return Client(http_url)

@pytest.fixture()
def account():
    return Account(btc_private_key)

@pytest.fixture()
def map_addr():
    return "2N2YasTUdLbXsafHHmyoKUYcRRicRPgUyNB"

@pytest.fixture()
def address():
    return Account(btc_private_key).address

def test_transfer(client, account, map_addr):
    return client.transfer(account, map_addr, 10)

def test_get_balance(client, address):
    return client.btc_get_balance(address) !=None