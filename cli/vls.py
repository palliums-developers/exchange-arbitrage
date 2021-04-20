import json
from violas_client import Client as VClient
from violas_client.libra_client.account import Account

from network import *
from .util import (
    gen_v2b_data,
    gen_v2e_data
)

class Client:

    USDT = "vUSDT"

    def __init__(self):
        self._cli = VClient.new(url=VLS_RPC_URL)
        self._ac = Account(bytes.fromhex(get_vls_priv_key()))

    def to_btc(self, baddr, amount):
        amount = self._from_standard_amount(amount)
        data = gen_v2b_data(baddr)
        data = json.dumps(data)
        return self._cli.transfer_coin(self._ac, v2b_addr, amount, currency_code="vBTC", data=data)

    def to_erc20(self, eaddr, amount, currency_code):
        amount = self._from_standard_amount(amount)
        data = gen_v2e_data(eaddr)
        data = json.dumps(data)
        return self._cli.transfer_coin(self._ac, v2e_addr, amount, currency_code=currency_code, data=data)

    def buy(self, currency_code, amount):
        amount = self._from_standard_amount(amount)
        amount_in = self._cli.swap_get_swap_input_amount(self.USDT, currency_code, amount)[0]
        self._cli.bank_borrow2(self._ac, amount_in, self.USDT)
        return self._cli.swap(self._ac, self.USDT, currency_code, amount_in)

    def sell(self, currency_code, amount):
        amount = self._from_standard_amount(amount)
        self._cli.bank_borrow2(self._ac, amount, currency_code)
        return self._cli.swap(self._ac, currency_code, self.USDT, amount)

    def repay_borrow(self, currency_code):
        balance = self._cli.get_balance(self._ac.address, currency_code)
        borrows = self._cli.bank_get_borrow_amount(self._ac.address, currency_code)[1]
        amount = min(balance, borrows)
        if amount == 0:
            return
        self._cli.bank_repay_borrow2(self._ac, amount, currency_code)

    def get_balance(self, currency_code):
        return self._cli.get_balance(self._ac.address, currency_code)

    def get_chain_id(self):
        return self._cli.chain_id

    def get_amount_can_buy(self, currency_code):
        u_amount = self._cli.bank_get_max_borrow_amount(self._ac.address, self.USDT)
        amount = self._cli.swap_get_swap_output_amount(self.USDT, currency_code, u_amount)[0]
        return self._to_standard_amount(amount)

    def get_amount_can_borrow(self, currency_code):
        amount = self._cli.bank_get_max_borrow_amount(self._ac.address, currency_code)
        return self._to_standard_amount(amount)

    def get_amount_out(self, currency_in, currency_out, amount_in):
        amount_in = self._from_standard_amount(amount_in)
        amount = self._cli.swap_get_swap_output_amount(currency_in, currency_out, amount_in)[0]
        return self._to_standard_amount(amount)

    def get_amount_in(self, currency_in, currency_out, amount_out):
        amount_out = self._from_standard_amount(amount_out)
        amount = self._cli.swap_get_swap_input_amount(currency_in, currency_out, amount_out)[0]
        return int(amount)

    def get_price(self, currency_code):
        resources = self._cli.swap_get_reserves_resource()
        c_index, u_index = self._cli.swap_get_currency_indexs(currency_code, self.USDT)
        reserve = self._cli.get_reserve(resources, c_index, u_index)
        return reserve.coinb.value / reserve.coina.value

    def get_amount_to_price(self, currency_code, to_price):
        '''
            拉到指定价格需要多少currency_code
            +代表需要买入
            -代表需要卖出
        '''
        index_a, index_b = self._cli.swap_get_currency_indexs(currency_code, self.USDT)
        reserves = self._cli.swap_get_reserves_resource()
        reserve = self._cli.get_reserve(reserves, index_a, index_b)
        c_reserve, u_reserve = reserve.coina.value, reserve.coinb.value
        #价格比市价高， 卖出
        if u_reserve / c_reserve > to_price:
            c_in = self._get_arbitrage_amount_in(c_reserve, u_reserve, to_price, 1)
            return self._to_standard_amount(c_in*(-1))
        #价格比市价低, 买入
        else:
            u_in = self._get_arbitrage_amount_in(u_reserve, c_reserve, 1, to_price)
            amount_out = self._cli.get_output_amount(u_in, u_reserve, c_reserve)
            return self._to_standard_amount(amount_out)

    def _get_arbitrage_amount_in(self, reserve_in, reserve_out, price_in, price_out):
        from sympy import solve
        from sympy.abc import x, y
        results = solve(
            [y - x * reserve_out / (reserve_in + x), (reserve_out - y) / (reserve_in + x) - price_in / price_out])
        for result in results:
            amount_in = result.get(x)
            amount_out = result.get(y)
            if amount_in > 0 and amount_out > 0:
                return amount_in

    def test_repay_borrow(self, currency_code):
        cli = VClient("violas_testnet")
        amount = cli.bank_get_borrow_amount(self._ac.address, currency_code)[1]
        if amount == 0:
            return
        cli.mint_coin(self._ac.address, amount+100, currency_code=currency_code)
        cli.bank_repay_borrow2(self._ac, amount, currency_code)

    def test_clear_balance(self, currency_code):
        balance = self._cli.get_balance(self._ac.address, currency_code)
        if balance == 0:
            return
        self._cli.transfer_coin(self._ac, "000000000000000000000000000000dd", balance, currency_code=currency_code)

    def _to_standard_amount(self, amount):
        return amount / 10**6


    def _from_standard_amount(self, amount):
        return int(amount * 10**6)


