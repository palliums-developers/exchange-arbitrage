from violas_client import Client, Wallet
from cli.vls import Client as VClient

cli = Client("violas_testnet")

currency_code = "vBTC"
to_price = 1000
v_cli = VClient()
amount = v_cli.get_amount_to_price(currency_code=currency_code, to_price=to_price)
print(amount)
w = Wallet.new()
ac = w.new_account()
if amount > 0:
    u_amount = v_cli.get_amount_in("vUSDT", currency_code, amount)
    u_amount = int(u_amount*10**6)
    cli.mint_coin(ac.address, u_amount, auth_key_prefix=ac.auth_key_prefix, currency_code="vUSDT")
    cli.add_currency_to_account(ac, currency_code)
    cli.swap(ac, "vUSDT", currency_code, u_amount)
else:
    amount = int(amount * 10 ** 6)
    amount = -1*amount
    cli.mint_coin(ac.address, amount, auth_key_prefix=ac.auth_key_prefix, currency_code=currency_code)
    cli.add_currency_to_account(ac, "vUSDT")
    cli.swap(ac, currency_code, "vUSDT", amount)

index_a, index_b = cli.swap_get_currency_indexs(currency_code, "vUSDT")
reserves = cli.swap_get_reserves_resource()
reserve = cli.get_reserve(reserves, index_a, index_b)
c_reserve, u_reserve = reserve.coina.value, reserve.coinb.value
print(u_reserve, c_reserve, u_reserve/c_reserve)