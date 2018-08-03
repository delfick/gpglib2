# coding:spec

from tests.helpers import data

from gpglib.structures import EncryptedMessage

import itertools
import unittest

def create_decryption_check(msg_type, **options):
    """
        Generate a test function to tests a combination of factors for decryption
        * Size of the message
        * Public Key type
        * Cipher used
    """
    def func(self):
        # Data caches all the keys for get_secret_keys
        keys = data.get_secret_keys()

        # Make the message, get the original
        message = EncryptedMessage(keys)
        original = data.get_original(msg_type)

        # Decrypt the encrypted and compare to the original
        decrypted = message.decrypt(data.get_encrypted(**options))
        self.assertEqual(decrypted, original)

    values = ', '.join("%s=%s" % (k, v) for k, v in sorted(options.items()))
    func.__name__ = "Testing key %s" % values
    func.__test_name__ = func.__name__
    return func

def generate_funcs():
    """
        Use create_decryption_check to generate test functions
        These are used in TestCase class created below
    """
    args = {}

    mdc = (True, False)
    msgs = ('small', 'big')
    keys = ('rsa', 'dsa')
    ciphers = ('cast5', 'aes', 'blowfish', '3des')
    compression = ('zip', 'zlib', 'bzip2', 'none')

    # Make sure we can get secret keys
    data.get_secret_keys()

    # Create a test for each combination of variables
    for do_mdc, key, cipher, compression, msg in itertools.product(mdc, keys, ciphers, compression, msgs):
        tester = create_decryption_check(msg, msg=msg, do_mdc=do_mdc, key=key, cipher=cipher, compression=compression)
        args[tester.__name__] = tester

    return args

# The class that holds all the tests
TestDecryption = type("TestDecryption", (unittest.TestCase, ), generate_funcs())
TestDecryption._is_noy_spec = True
