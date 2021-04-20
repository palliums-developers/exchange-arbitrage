from .util import Retry
from .bn import Client as BNClient
from .eth import Client as EClient
from .btc import Client as BClient
from network import *

class Client:

    USDT = "USDT"

    def __init__(self, **kwargs):
        self._cli = BNClient()
        self._amounts = kwargs
        self._ecli = EClient()
        self._bcli = BClient()

    def get_buy_price(self, currency_code):
        return self._cli.get_buy_price(currency_code)

    def get_sell_price(self, currency_code):
        return self._cli.get_sell_price(currency_code)

    def buy(self, currency_code, amount, price=None):
        pass
        # if price is None:
        #     price = self.get_price(currency_code)
        # self._reduce_amount(self.USDT, amount*price)
        # self._add_amount(currency_code, amount)

    def sell(self, currency_code, amount):
        pass
        # price = self.get_price(currency_code)
        # self._reduce_amount(currency_code, amount)
        # self._add_amount(self.USDT, amount * price)

    def withdraw(self, currency_code, amount, addr):
        if currency_code == self.USDT:
            self._ecli.transfer(addr, "vlstusdt", amount)
        if currency_code == "BTC":
            self._bcli.transfer(addr, amount)

    def get_buy_value(self, currency_code, amount):
        return self._cli.get_buy_value(currency_code, amount)

    def get_sell_value(self, currency_code, amount):
        return self._cli.get_sell_value(currency_code, amount)

    def get_price(self, currency_code):
        return self._cli.get_price(currency_code)

    def get_amount(self, currency_code):
        if currency_code == "BTC":
            return self._bcli.get_balance(btc_addr)
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





