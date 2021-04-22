import requests
from cryptos import Bitcoin
from cryptos.main import privkey_to_pubkey, privkey_to_address

from cli.util import AmountNotEnough, gen_b2v_data
from network import *
from cli.util import Retry
from network import magicbyte, testnet

class InvalidMethodError(Exception):
    pass

class Account:
    def __init__(self, private_key):
        self.private_key = private_key
        self.public_key = privkey_to_pubkey(private_key)
        self.address = privkey_to_address(self.private_key, magicbyte)

class Client:

    DEFAULT_CONNECT_TIMEOUT_SECS: float = 5.0
    DEFAULT_TIMEOUT_SECS: float = 30.0

    def __init__(self, retry=None):
        self._retry = retry or Retry()
        self._session = requests.session()
        self._method_to_urls = btc_method_to_urls
        self._btc = Bitcoin(testnet=testnet)
        self._timeout = (self.DEFAULT_CONNECT_TIMEOUT_SECS, self.DEFAULT_TIMEOUT_SECS)
        self._ac = Account(get_btc_priv_key())

    def transfer(self, to_address, amount):
        amount = self._from_standard_amount(amount)
        utxos = self.get_utxo(self._ac.address)
        sum, inputs = self.get_inputs(amount, utxos)
        fee = self.estimate_tx_fee(self._ac.address, amount)
        fee = self._from_standard_amount(fee)

        outs = [{
            "address": to_address,
            "value": amount -fee
        }
        ]
        if sum - amount - fee > 0:
            outs.append({
                "address": self._ac.address,
                "value": sum-amount
            })
        tx = self.create_tx(inputs, outs)
        signed_tx = self._btc.signall(tx, self._ac.private_key)
        return self.send_transction(signed_tx)

    def to_violas(self, amount, violas_addr, chain_id):
        amount = self._from_standard_amount(amount)
        fee = self.estimate_fee()
        fee = self._from_standard_amount(fee)
        utxos = self.get_utxo(self._ac.address)
        sum, inputs = self.get_inputs(amount, utxos)
        outs = [{
            "address": b2v_addr,
            "value": amount-fee
        },{
            "script": gen_b2v_data(violas_addr, chain_id),
            "value": 0
        }
        ]
        if sum - amount > 0:
            outs.append({
                "address": self._ac.address,
                "value": sum - amount
            })
        tx = self.create_tx(inputs, outs)
        signed_tx = self._btc.signall(tx, self._ac.private_key)
        return self.send_transction(signed_tx)

    def create_tx(self, inputs, outs):
        return self._btc.mktx(inputs, outs)

    def get_inputs(self, amount, utxos):
        sum = 0
        ret = []
        for utxo in utxos:
            sum += int(utxo.get("value"))
            ret.append({
                "output": f"{utxo.get('txid')}:{utxo.get('vout')}",
                'value':int(utxo.get('value'))
            })
            if sum >= amount:
                return sum, ret
        raise AmountNotEnough(f"Account has {sum} btc, not has {amount} btc")


    def get_transaction(self, txid):
        return self._retry.execute(
            lambda:self.execute("tx", [txid])
        )

    def get_account_info(self, addr):
        return self._retry.execute(
            lambda :self.execute("address", [addr])
        )

    def get_balance(self, addr=None):
        if addr is None:
            addr = self._ac.address
        utxos = self.get_utxo(addr)
        balance = 0
        for utxo in utxos:
            balance += int(utxo.get("value"))
        return self._to_standard_amount(balance)

    def get_utxo(self, addr):
        return self._retry.execute(
            lambda :self.execute("utxo", [addr])
        )

    def send_transction(self, tx):
        return self._retry.execute(
            lambda :self.execute("sendtx", [tx])
        )

    def estimate_fee(self, block_height=1):
        return float(self._retry.execute(
            lambda :self.execute("estimatefee", [block_height]).get("result")
        ))

    def estimate_tx_fee(self, from_addr=None, amount=None, block_height=1):
        if from_addr is None:
            return self.estimate_fee(block_height)
        utxos = self.get_utxo(from_addr)
        _, inputs = self.get_inputs(amount, utxos)
        return ((148 * len(inputs) + 34*2 + 10) // 1000+1)*self.estimate_fee(block_height)

    def execute(self, method, params):
        url = self._method_to_urls.get(method)
        if url is None:
            raise InvalidMethodError(f"{method} is not valid method")
        for param in params:
            url += str(param)
        return self.get(url)

    def get(self, url):
        response = self._session.get(url, timeout=self._timeout)
        response.raise_for_status()
        return response.json()

    def _from_standard_amount(self, amount):
        return int(amount * 10**8)

    def _to_standard_amount(self, amount):
        return amount / 10**8


if __name__ == "__main__":
    pass