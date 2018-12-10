#!/usr/bin/python
# -*- coding: utf-8 -*-

from app.helpers.message import MESSAGE

class BcException(Exception):

    def __init__(self, arg):
        if "have enough funds to send tx. The upfront cost is" in arg:
            self.message = MESSAGE.HANDSHAKE_NOT_ENOUGH_GAS
        elif "insufficient funds for gas * price + value" in arg:
            self.message = MESSAGE.HANDSHAKE_NOT_ENOUGH_GAS
        elif "Error: base fee exceeds gas limit" in arg:
            self.message = MESSAGE.HANDSHAKE_NOT_ENOUGH_GAS
        else:
            self.message = MESSAGE.HANDSHAKE_ERROR_ANYTHING
        self.arg = {arg}


# if __name__ == '__main__':
#     try:
#         raise BcException("Returned error: Error: sender doesn't have enough funds to send tx. The upfront cost is: 300000000000000000 and the sender's account only has: 0 ")    
#         raise BcException("1")    
#     except Exception as ex:
#         print(str(ex.message))
    
