import time
from .bn import Client as BNClient
from .eth import Client as EClient
from .btc import Client as BClient
from network import *

class Client:

    USDT = "USDT"

    def __init__(self, **kwargs):
        self._cli = BNClient()
        self._borrow = {}
        self._ecli = EClient()
        self._bcli = BClient()

    def get_buy_price(self, currency_code):
        return self._cli.get_buy_price(currency_code)

    def get_sell_price(self, currency_code):
        return self._cli.get_sell_price(currency_code)

    def buy(self, currency_code, amount, price=None, blocking=True):
        '''
        1. usdt减少
        2. currency_code增加
        '''
        if price is None:
            price = self.get_price(currency_code)
        u_amount = amount * price
        self._ecli.transfer(e2v_contract_addr, "vlstusdt", u_amount)
        if currency_code == 'BTC':
            start = self.get_amount(currency_code)
            self._mint_btc_to_addr(btc_addr, amount)
            while True:
                time.sleep(5)
                if self.get_amount(currency_code) != start:
                    return


    def sell(self, currency_code, amount):
        '''
        1.借currency 借款金额增加
        2.卖出currency usdt增加

        '''
        price = self.get_price(currency_code)
        u_amount = amount*price
        self.add_borrow(currency_code, amount)
        self._mint_usdt_to_addr(eth_addr, u_amount)

    def close_buy(self, currency_code, amount=None, price=None):
        pass

    def close_sell(self, currency_code):
        '''
        1.借款减少
        2.存款减少
        '''
        borrow = self.get_borrow_amount(currency_code)
        balance =self.get_amount(currency_code)
        amount = min(borrow, balance)
        self.reduce_borrow(currency_code, amount)
        if currency_code == "BTC":
            self._bcli.transfer(b2v_addr, amount)
        return self.reduce_borrow(currency_code)

    def withdraw(self, currency_code, addr=None, amount=None, blocking=True):
        if addr is None:
            if currency_code == "BTC":
                addr = btc_addr
            elif currency_code == "USDT":
                addr = eth_addr
        if amount is None:
            amount = self.get_amount(currency_code)
        if currency_code == self.USDT:
            e_start = self._ecli.get_balance("vlstusdt")
            self._ecli.transfer(addr, "vlstusdt", amount)
            if blocking:
                while True:
                    e_end = self._ecli.get_balance("vlstusdt")
                    if e_end != e_start:
                        return
                    time.sleep(5)

        if currency_code == "BTC":
            b_start = self._bcli.get_balance()
            self._bcli.transfer(addr, amount)
            if blocking:
                while True:
                    b_end = self._bcli.get_balance()
                    if b_end != b_start:
                        return
                    time.sleep(5)

    def get_borrow_amount(self, currency_code):
        return self._borrow.get(currency_code, 0)

    def add_borrow(self, currency_code, amount):
        amount += self._borrow.get(currency_code, 0)
        self._borrow[currency_code] = amount

    def reduce_borrow(self, currency_code, amount):
        borrow = self.get_borrow_amount(currency_code)
        self._borrow[currency_code] = borrow-amount

    def get_buy_value(self, currency_code, amount):
        return self._cli.get_buy_value(currency_code, amount)

    def get_sell_value(self, currency_code, amount):
        return self._cli.get_sell_value(currency_code, amount)

    def get_price(self, currency_code):
        return self._cli.get_price(currency_code)

    def get_amount(self, currency_code):
        if currency_code == "BTC":
            return self._bcli.get_balance()
        if currency_code == "USDT":
            return self._ecli.get_balance("vlstusdt")

    def get_amount_can_borrow(self, currency_code):
        u_amount = self.get_amount(self.USDT)
        price = self.get_price(currency_code)
        return u_amount / price * 0.5

    def get_amount_can_buy(self, currency_code):
        '''
        该用户可以购买多少指定的currency_code
        '''
        u_amount = self.get_amount("USDT")
        price = self.get_price(currency_code)
        return u_amount / price

    def _mint_btc_to_addr(self, addr, amount):
        from violas_client import Wallet, Client
        from cli.vls import Client as VClient
        amount = int(amount*10**6)
        cli = Client("violas_testnet")
        w = Wallet.new()
        ac = w.new_account()
        cli.mint_coin(ac.address, amount, auth_key_prefix=ac.auth_key_prefix, currency_code="vBTC")
        v_cli = VClient()
        v_cli._ac = ac
        start_balance = self._bcli.get_balance(addr)
        amount = amount / 10**6
        v_cli.to_btc(addr, amount)
        while True:
            end_balance = self._bcli.get_balance(addr)
            if end_balance != start_balance:
                return
            time.sleep(5)

    def _mint_usdt_to_addr(self, addr, amount):
        from violas_client import Wallet, Client
        from cli.vls import Client as VClient
        amount = int(amount*10**6)
        cli = Client("violas_testnet")
        w = Wallet.new()
        ac = w.new_account()
        cli.mint_coin(ac.address, amount, auth_key_prefix=ac.auth_key_prefix, currency_code="vUSDT")
        v_cli = VClient()
        v_cli._ac = ac
        start_balance = self._ecli.get_balance("vlstusdt", addr)
        amount=amount/10**6
        v_cli.to_erc20(addr, amount, "vUSDT")
        while True:
            end_balance = self._ecli.get_balance("vlstusdt", addr)
            if end_balance != start_balance:
                return
            time.sleep(5)






