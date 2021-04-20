import azure
from violas_client import Wallet
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

from testnet import *

def get_vls_priv_key():
    credential = DefaultAzureCredential()
    secret_client = SecretClient(vault_url=f"https://{VAULT_NAME}.vault.azure.net/", credential=credential)
    return secret_client.get_secret(vls_addr).value

def get_btc_priv_key():
    credential = DefaultAzureCredential()
    secret_client = SecretClient(vault_url=f"https://{VAULT_NAME}.vault.azure.net/", credential=credential)
    return secret_client.get_secret(btc_addr).value

def get_eth_pri_key():
    credential = DefaultAzureCredential()
    secret_client = SecretClient(vault_url=f"https://{VAULT_NAME}.vault.azure.net/", credential=credential)
    return secret_client.get_secret(eth_addr).value


def set_pri_key(k, v):
    credential = DefaultAzureCredential()
    secret_client = SecretClient(vault_url=f"https://{VAULT_NAME}.vault.azure.net/", credential=credential)
    return secret_client.set_secret(k, v)

if __name__ == "__main__":
    set_pri_key(btc_addr, "66e29f8cd2a77bd09d4b7f83b164e8674b738697c08176f563bbab4852a3dd83")
    set_pri_key(eth_addr, "8d14e57809310583f206c425067e4def8e7c11bfd36f958e071bbd1a01f1b043")
    set_pri_key(vls_addr, "8ee266e942ff3851038fbab07507a05294956795ef35f847d6190a4136f04362")