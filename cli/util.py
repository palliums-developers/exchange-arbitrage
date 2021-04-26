import os
import time
import typing
import dataclasses

class AmountNotEnough(Exception):
    pass

class NetWorkError(Exception):
    pass

class ResponseStatusError(Exception):
    pass

DEFAULT_MAX_RETRIES: int = 3
DEFAULT_RETRY_DELAY: float = 1

@dataclasses.dataclass
class Retry:
    max_retries: int = DEFAULT_MAX_RETRIES
    delay_secs: float = DEFAULT_RETRY_DELAY
    exception: typing.Type[Exception] = NetWorkError

    def execute(self, fn: typing.Callable):  # pyre-ignore
        tries = 0
        while tries < self.max_retries:
            tries += 1
            try:
                return fn()
            except Exception as e:
                if tries < self.max_retries:
                    # simplest backoff strategy: tries * delay
                    time.sleep(self.delay_secs)
                else:
                    raise e

def gen_b2v_data(payee, chain_id):
    if isinstance(payee, bytes):
        payee = payee.hex()
    op_return = "6a"
    l = "3d"
    violas = b"violas".hex()
    version = "0004"
    type = "3000"
    payee = payee
    seq = os.urandom(8).hex()
    module_addr = "1".rjust(32, '0')
    out_amount = "0"*16
    times = "0"*4
    chain_id = str(chain_id).rjust(2, '0')
    return f"{op_return}{l}{violas}{version}{type}{payee}{seq}{module_addr}{out_amount}{times}{chain_id}"

def gen_v2b_data(payee, state="start"):
    if isinstance(payee, bytes):
        payee = payee.hex()
    return {
        "flag": "violas",
        "type": "v2bm",
        "times": 0,
        "to_address": payee,
        "state": state,
    }

def gen_v2e_data(payee, state="start"):
    if isinstance(payee, bytes):
        payee = payee.hex()
    return {
        "flag": "violas",
        "type": "v2em",
        "to_address":payee,
        "state": state,
        "times": 0,
    }




