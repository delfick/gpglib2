# coding:spec

from gpglib.structures import EncryptedMessage

import itertools
import pytest

mdc = (True, False)
msgs = ("small", "big")
keys = ("rsa", "dsa")
ciphers = ("cast5", "aes", "blowfish", "3des")
compression = ("zip", "zlib", "bzip2", "none")

# Create a test for each combination of variables
options = []
for do_mdc, key, cipher, compression, msg in itertools.product(
    mdc, keys, ciphers, compression, msgs
):
    options.append(dict(msg=msg, do_mdc=do_mdc, key=key, cipher=cipher, compression=compression))

describe "Test descryption":

    @pytest.mark.parametrize("options", options)
    it "can decrypt", options:
        # Data caches all the keys for get_secret_keys
        keys = pytest.helpers.get_secret_keys()

        # Make the message, get the original
        message = EncryptedMessage(keys)
        original = pytest.helpers.get_original(options["msg"])

        # Decrypt the encrypted and compare to the original
        decrypted = message.decrypt(pytest.helpers.get_encrypted(**options))
        assert decrypted == original
