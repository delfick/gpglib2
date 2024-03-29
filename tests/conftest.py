import os

import pytest

from gpglib.structures import Key

this_folder = os.path.dirname(__file__)
data_folder = os.path.join(this_folder, "data")

# Hold any cached values
cached = {}


@pytest.helpers.register
def get_file(name):
    file_path = os.path.join(data_folder, name)
    with open(file_path, "rb") as f:
        return f.read()


@pytest.helpers.register
def get_original(msg):
    return get_file("dump.%s" % msg)


@pytest.helpers.register
def get_encrypted(msg, do_mdc, key, cipher, compression):
    mdc = "mdc" if do_mdc is True else "no_mdc"
    fn = os.path.join("encrypted", mdc, key, cipher, compression, "%s.gpg" % msg)
    return get_file(fn)


@pytest.helpers.register
def get_pgp_key(namespace, algo):
    fn = os.path.join("keys", "key.%s.%s.gpg" % (namespace, algo))
    return get_file(fn)


@pytest.helpers.register
def get_secret_keys():
    """
    Get dictionary of {key_id:key} for all secret keys in the tests/data/keys folder
    Memoized in the cached dictionary
    """
    if "keys" not in cached:
        keys = {}
        key_folder = os.path.join(data_folder, "keys")
        for key_name in os.listdir(key_folder):
            location = os.path.join(key_folder, key_name)
            if os.path.isfile(location) and key_name.endswith("gpg") and "secret" in key_name:
                with open(location, "rb") as k:
                    key = Key(passphrase="password25").parse(k.read())
                    keys.update(key.key_dict())
        cached["keys"] = keys
    return cached["keys"]


# Make sure we can get secret keys
get_secret_keys()
