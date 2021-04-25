from violas_client import Client
from violas_client.libra_client.account import Account

from network import get_vls_priv_key, vls_addr

cli = Client("violas_testnet")
pri_key = get_vls_priv_key()
ac = Account(bytes.fromhex(pri_key))
# cli.add_currency_to_account(ac, "vUSDT")
cli.mint_coin(ac.address, 10000_000_000, auth_key_prefix=ac.auth_key_prefix, currency_code="vUSDT")
# cli.add_currency_to_account(ac, "vBTC")
# cli.bank_publish(ac)
cli.bank_lock2(ac, 10000_000_000, "vUSDT")