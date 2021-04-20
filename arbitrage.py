from cli.vls import Client as VClient
from cli.bn import Client as BNClient
from cli.eth import Client as EClient
from cli.btc import Client as BClient
from network import *

MIN_PROFIT = 10

USDT = "USDT"

violas_names = {
    "USDT": "vUSDT",
    "BTC": "vBTC"
}

eth_names = {
    "USDT": "vlstusdt"
}


def name_to_violas(coin):
    return violas_names.get(coin)

def name_to_eth(coin):
    return eth_names.get(coin)

def estimate_eth_gas_fee(eclient:EClient, bnclient:BNClient):
    '''return usdt'''
    amount = eclient.estimate_transaction_fee()
    eth_price = bnclient.get_buy_price("ETH")
    return amount * eth_price

def estimate_btc_gas_fee(bclient: BClient, bnclient: BNClient):
    amount = bclient.estimate_fee()
    btc_price = bnclient.get_buy_price("BTC")
    return amount * btc_price

def estimate_bn2v_gas_fee(bclient, bnclient):
    return 2*estimate_btc_gas_fee(bclient, bnclient)

def estimate_v2bn_gas_fee(eclient, bnclient):
    return 2*estimate_eth_gas_fee(eclient, bnclient)

def check_vmore_bless(vclient:VClient, bnclient:BNClient, eclient: EClient, currency_code, amount):
    v_name = name_to_violas(currency_code)
    '''violas购买currency code需要的usdt'''
    in_usdt = vclient.get_amount_in(name_to_violas(USDT), v_name, amount)

    '''bn卖出currency code给出的usdt'''
    out_usdt = bnclient.get_sell_value(currency_code, amount)
    gas_fee = estimate_v2bn_gas_fee(eclient, bnclient)
    print(f"卖出给予{out_usdt}usdt, 买入需要{in_usdt}usdt, gas_fee:{gas_fee}, amount:{amount}")
    if out_usdt - in_usdt - gas_fee > MIN_PROFIT:
        return True
    return False

def check_vless_bmore(vclient: VClient, bnclient: BNClient, bclient: BClient, currency_code, amount):
    v_name = name_to_violas(currency_code)
    '''violas 卖出currency_code的盈利'''
    out_usdt = vclient.get_amount_out(v_name, name_to_violas(USDT), amount)
    '''bn购买currency_code需要的usdt'''
    in_usdt = bnclient.get_buy_value(currency_code, amount)
    gas_fee = estimate_bn2v_gas_fee(bclient, bnclient)
    print(f"卖出给予{out_usdt}usdt, 买入花费{in_usdt}usdt, gas_fee:{gas_fee}, amount:{amount}")
    if out_usdt - in_usdt - gas_fee > MIN_PROFIT:
        return True
    return False

def try_arbitrage(vclient:VClient, bnclient:BNClient, bclient: BClient, eclient:EClient, currency_code):
    '''可以对冲的最大数量'''
    v_name = name_to_violas(currency_code)
    bn_price = bnclient.get_price(currency_code)
    a_amount = vclient.get_amount_to_price(v_name, bn_price)
    if a_amount < 0:
        '''violas需要卖出currency, bn需要买入'''
        a_amount = -1 * a_amount
        vless_amount = vclient.get_amount_can_borrow(v_name)
        bmore_amount = bnclient.get_amount_can_buy(currency_code)
        max_amount = min(vless_amount, bmore_amount)*0.9
        amount = min(max_amount, a_amount)
        print(f"violas价格高，需要卖出. vless_amount:{vless_amount},bmore_amount:{bmore_amount},max_amount:{max_amount}, a_amount:{a_amount}, amount:{amount}")
        if check_vless_bmore(vclient, bnclient, bclient, currency_code, amount):
            # vclient.sell(v_name, amount)
            bnclient.buy(currency_code, amount)
            print(f"violas 卖出{amount}{v_name}, bn买入{amount}{currency_code}")
            move_bricks_to_violas(vclient, bnclient, bclient, currency_code)
    else:
        vmore_amount = vclient.get_amount_can_buy(v_name)
        bless_amount = bnclient.get_amount_can_borrow(currency_code)
        max_amount = min(vmore_amount, bless_amount)*0.9
        amount = min(max_amount, a_amount)
        print(f"violas价格低，需要买入. vmore_amount:{vmore_amount},bless_amount:{bless_amount},max_amount:{max_amount}, a_amount:{a_amount}, amount:{amount}")
        if check_vmore_bless(vclient, bnclient, eclient, currency_code, amount):
            vclient.buy(v_name, amount)
            bnclient.sell(currency_code, amount)
            print(f"violas买入{amount}{v_name}, bn卖出{amount}{currency_code}")
            move_bricks_to_bn(vclient, bnclient, eclient, currency_code)


def move_bricks_to_violas(vclient: VClient, bnclient: BNClient, bclient:BClient, currency_code):
    from network import vls_addr, bn_usdt_addr
    currency_code = currency_code.upper()
    ''' currency 从bn映射到violas '''
    b_start = bclient.get_balance()
    amount = bnclient.get_amount(currency_code)
    print(amount)
    bnclient.withdraw(currency_code, amount, btc_addr)
    # while True:
    #     b_end = bclient.get_balance()
    #     if b_end > b_start:
    #         break
    #     time.sleep(5)
    chain_id = vclient.get_chain_id()
    bclient.to_violas(amount, vls_addr, chain_id)

    '''usdt从violas映射到币安'''
    amount = vclient.get_balance(name_to_violas(USDT))
    amount = bnclient.get_price(currency_code) * amount
    vclient.to_erc20(bn_usdt_addr, amount, name_to_violas(USDT))

def move_bricks_to_bn(vclient: VClient, bnclient: BNClient, eclient:EClient, currency_code) :
    import time
    from network import vls_addr, bn_btc_addr
    currency_code = currency_code.upper()
    '''currency 从violas映射到币安'''
    v_name = name_to_violas(currency_code)
    amount = vclient.get_balance(v_name)
    if currency_code == "BTC":
        print("to btc", amount)
        vclient.to_btc(bn_btc_addr, amount)

    '''usdt从bn到violas'''
    e_start = eclient.get_balance(name_to_eth(USDT))
    amount = bnclient.get_amount(USDT)
    amount = bnclient.get_price(currency_code) * amount
    bnclient.withdraw(USDT, amount, eth_addr)
    print("withdraw", amount, USDT)
    # while True:
    #     e_end = eclient.get_balance(name_to_eth(USDT))
    #     if e_end > e_start:
    #         break
    #     time.sleep(5)
    print(vls_addr, name_to_eth(USDT), amount)
    eclient.to_violas(vls_addr, name_to_eth(USDT), min(1000, amount))
    print("to violas", amount, name_to_eth(USDT))
