import time
from cli.vls import Client as VClient
from cli.bn import Client as BNClient
from cli.eth import Client as EClient
from cli.btc import Client as BClient
from cli.tbn import Client as BNTClient
from network import *

class Arbitrage:
    MIN_PROFIT = 10
    USDT = "USDT"
    BTC = "BTC"
    ETH = "ETH"

    violas_names = {
        "USDT": "vUSDT",
        "BTC": "vBTC"
    }
    eth_names = {
        "USDT": "vlstusdt"
    }

    def __init__(self, vcli=None, bcli=None, ecli=None, bncli=None):
        self._vcli = vcli or VClient()
        self._bcli = bcli or BClient()
        self._bncli = bncli or BNTClient()
        self._ecli = ecli or EClient()

    def _name_to_violas(self, coin):
        return self.violas_names.get(coin)

    def _name_to_eth(self, coin):
        return self.eth_names.get(coin)

    def estimate_eth_gas_fee(self):
        '''return usdt'''
        amount = self._ecli.estimate_transaction_fee()
        eth_price = self._bncli.get_buy_price(self.ETH)
        return amount * eth_price

    def estimate_btc_gas_fee(self):
        amount = self._bcli.estimate_tx_fee()
        btc_price = self._bncli.get_buy_price(self.BTC)
        return amount * btc_price

    def estimate_bn2v_gas_fee(self):
        return 2*self.estimate_btc_gas_fee()

    def estimate_v2bn_gas_fee(self):
        return 2*self.estimate_eth_gas_fee()

    def check_vmore_bless(self, currency_code, amount):
        currency_v = self._name_to_violas(currency_code)
        usdt_v = self._name_to_violas(self.USDT)
        '''violas购买currency code需要的usdt'''
        in_usdt = self._vcli.get_amount_in(usdt_v, currency_v, amount)

        '''bn卖出currency code给出的usdt'''
        out_usdt = self._bncli.get_sell_value(currency_code, amount)
        gas_fee = self.estimate_v2bn_gas_fee()
        print(f"卖出给予{out_usdt}usdt, 买入需要{in_usdt}usdt, gas_fee:{gas_fee}, amount:{amount}")
        if out_usdt - in_usdt - gas_fee > self.MIN_PROFIT:
            return True
        return False

    def check_vless_bmore(self, currency_code, amount):
        currency_v = self._name_to_violas(currency_code)
        usdt_v = self._name_to_violas(self.USDT)
        '''violas 卖出currency_code的盈利'''
        out_usdt = self._vcli.get_amount_out(currency_v, usdt_v, amount)
        '''bn购买currency_code需要的usdt'''
        in_usdt = self._bncli.get_buy_value(currency_code, amount)
        gas_fee = self.estimate_bn2v_gas_fee()
        print(f"卖出给予{out_usdt}usdt, 买入花费{in_usdt}usdt, gas_fee:{gas_fee}, amount:{amount}")
        if out_usdt - in_usdt - gas_fee > self.MIN_PROFIT:
            return True
        return False

    def try_arbitrage(self, currency_code):
        '''可以对冲的最大数量'''
        currency_v = self._name_to_violas(currency_code)
        bn_price = self._bncli.get_price(currency_code)
        a_amount = self._vcli.get_amount_to_price(currency_v, bn_price)
        if a_amount < 0:
            '''violas需要卖出currency, bn需要买入'''
            a_amount = -1 * a_amount
            vless_amount = self._vcli.get_amount_can_borrow(currency_v)
            bmore_amount = self._bncli.get_amount_can_buy(currency_code)
            max_amount = min(vless_amount, bmore_amount)*0.9
            amount = min(max_amount, a_amount)
            print(f"violas价格高，需要卖出. vless_amount:{vless_amount},bmore_amount:{bmore_amount},max_amount:{max_amount}, a_amount:{a_amount}, amount:{amount}")
            if self.check_vless_bmore(currency_code, amount):
                self._vcli.sell(currency_v, amount)
                self._bncli.buy(currency_code, amount)
                print(f"violas 卖出{amount}{currency_v}, bn买入{amount}{currency_code}")
                self._v2bn(self.USDT)
                self._bn2v(currency_code)

                self._vcli.close_sell(currency_v)
                self._bncli.close_buy(currency_code)
        else:
            vmore_amount = self._vcli.get_amount_can_buy(currency_v)
            bless_amount = self._bncli.get_amount_can_borrow(currency_code)
            max_amount = min(vmore_amount, bless_amount)*0.9
            amount = min(max_amount, a_amount)
            print(f"violas价格低，需要买入. vmore_amount:{vmore_amount},bless_amount:{bless_amount},max_amount:{max_amount}, a_amount:{a_amount}, amount:{amount}")
            if self.check_vmore_bless(currency_code, amount):
                self._vcli.buy(currency_v, amount)
                self._bncli.sell(currency_code, amount)
                print(f"violas买入{amount}{currency_v}, bn卖出{amount}{currency_code}")
                self._v2bn(currency_code)
                u_amount = self._bncli.get_price(currency_code)*amount
                self._bn2v(self.USDT, u_amount)
                self._vcli.close_buy()
                self._bncli.close_sell(currency_code)

    # def move_bricks_to_violas(self, currency_code):
    #     currency_code = currency_code.upper()
    #     ''' currency 从bn映射到violas '''
    #     b_start = self._bcli.get_balance()
    #     amount = self._bncli.get_amount(currency_code)
    #     self._bncli.withdraw(currency_code, amount, btc_addr)
    #     while True:
    #         b_end = self._bcli.get_balance()
    #         if b_end != b_start:
    #             break
    #         time.sleep(5)
    #     self._b2v(vls_addr)
    #
    #     '''usdt从violas映射到币安'''
    #     amount = self._vcli.get_balance(self._name_to_violas(self.USDT))
    #     self._vcli.to_erc20(bn_usdt_addr, amount, self._name_to_violas(self.USDT))
    #
    # def move_bricks_to_bn(self, currency_code) :
    #     currency_code = currency_code.upper()
    #     '''currency 从violas映射到币安'''
    #     v_name = self._name_to_violas(currency_code)
    #     amount = self._vcli.get_balance(v_name)
    #     if currency_code == "BTC":
    #         self._vcli.to_btc(bn_btc_addr, amount)
    #
    #     '''usdt从bn到violas'''
    #     e_start = self._ecli.get_balance(self._name_to_eth(self.USDT))
    #     amount = self._bncli.get_amount(self.USDT)
    #     self._bncli.withdraw(self.USDT, amount, eth_addr)
    #     print("withdraw", amount, self.USDT)
    #     # while True:
    #     #     e_end = eclient.get_balance(name_to_eth(USDT))
    #     #     if e_end > e_start:
    #     #         break
    #     #     time.sleep(5)
    #     print(vls_addr, self._name_to_eth(self.USDT), amount)
    #     self._ecli.to_violas(vls_addr, self._name_to_eth(self.USDT), amount)
    #     print("to violas", amount, self._name_to_eth(self.USDT))

    def _b2v(self, to_addr=None, amount=None, blocking=True):
        if to_addr is None:
            to_addr = vls_addr
        btc_v = self._name_to_violas(self.BTC)
        if amount is None:
            amount = self._bcli.get_balance()
        v_start = self._vcli.get_balance(btc_v)
        self._bcli.to_violas(amount, to_addr, chain_id=self._vcli.chain_id)
        if blocking:
            while True:
                v_end = self._vcli.get_balance(btc_v)
                if v_start != v_end:
                    break
                time.sleep(5)
        print("b2v", amount)

    def _e2v(self, to_addr=None, amount=None, blocking=True):
        if to_addr is None:
            to_addr = vls_addr
        usdt_e = self._name_to_eth(self.USDT)
        usdt_v = self._name_to_violas(self.USDT)

        if amount is None:
            amount = self._ecli.get_balance(usdt_e)
        else:
            u_amount = self._ecli.get_balance(usdt_e)
            amount = min(u_amount, amount)
        v_start = self._vcli.get_balance(usdt_v)
        self._ecli.to_violas(to_addr, usdt_e, amount)
        if blocking:
            while True:
                v_end = self._vcli.get_balance(usdt_v)
                if v_end != v_start:
                    break
                time.sleep(5)
        print("e2v", amount)


    def _v2b(self, to_addr=None, amount=None, blocking=True):
        if to_addr is None:
            to_addr = btc_addr
        btc_v = self._name_to_violas(self.BTC)
        if amount is None:
            amount = self._vcli.get_balance(btc_v)
        b_start = self._bcli.get_balance()
        self._vcli.to_btc(to_addr,amount)
        if blocking:
            while True:
                time.sleep(5)
                b_end = self._bcli.get_balance()
                if b_end != b_start:
                    break
        print("v2b", amount)

    def _v2e(self, to_addr=None, amount=None, blocking=True):
        if to_addr is None:
            to_addr = eth_addr
        usdt_v = self._name_to_violas(self.USDT)
        usdt_e = self._name_to_eth(self.USDT)
        if amount is None:
            amount = self._vcli.get_balance(usdt_v)
        e_start = self._ecli.get_balance(usdt_e, to_addr)
        self._vcli.to_erc20(to_addr, amount, usdt_v)
        if blocking:
            while True:
                time.sleep(5)
                e_end = self._ecli.get_balance(usdt_e)
                if e_end != e_start:
                    break
        print("v2e", amount)

    def _bn2v(self, currency_code, amount=None, blocking=True):
        if amount is None:
            amount = self._bncli.get_amount(currency_code)
        self._bncli.withdraw(currency_code, amount=amount, blocking=blocking)
        if currency_code == self.BTC:
            self._b2v(blocking=blocking)
        elif currency_code == self.USDT:
            self._e2v(amount=amount, blocking=blocking)

    def _v2bn(self, currency_code, blocking=True):
        if currency_code == self.USDT:
            self._v2e(bn_usdt_addr, blocking=blocking)
        if currency_code == self.BTC:
            self._v2b(bn_btc_addr, blocking=True)
