# coding: spec

from gpglib.structures import Key

import pytest

describe "Consuming rsa keys":
    it "successfully consumes a secret key":
        secret_key = Key(passphrase="password25").parse(pytest.helpers.get_pgp_key("secret", "rsa"))
        # Parent key
        assert 5922803129648873547 in secret_key.key_dict()
        # Sub-key
        assert 6126705363215480599 in secret_key.key_dict()

    it "successfully consumes a public key":
        public_key = Key().parse(pytest.helpers.get_pgp_key("public", "rsa"))
        # Parent key
        assert 5922803129648873547 in public_key.key_dict()
        # Sub-key
        assert 6126705363215480599 in public_key.key_dict()

    it "successfully calls a function to retrieve the passphrase":

        def passphrase_func(message, info):
            return "password25"

        secret_key = Key(passphrase=passphrase_func).parse(
            pytest.helpers.get_pgp_key("secret", "rsa")
        )
        # Parent key
        assert 5922803129648873547 in secret_key.key_dict()
        # Sub-key
        assert 6126705363215480599 in secret_key.key_dict()

describe "Consuming dsa keys":
    it "successfully consumes a secret key":
        secret_key = Key(passphrase="password25").parse(pytest.helpers.get_pgp_key("secret", "dsa"))
        print(secret_key.key_dict().keys())
        # Parent key
        assert 18400890916352345643 in secret_key.key_dict()
        # Sub-key
        assert 14839617247254692497 in secret_key.key_dict()

    it "successfully consumes a public key":
        public_key = Key().parse(pytest.helpers.get_pgp_key("public", "dsa"))
        # Parent key
        assert 18400890916352345643 in public_key.key_dict()
        # Sub-key
        assert 14839617247254692497 in public_key.key_dict()

    it "successfully calls a function to retrieve the passphrase":

        def passphrase_func(message, info):
            return "password25"

        secret_key = Key(passphrase=passphrase_func).parse(
            pytest.helpers.get_pgp_key("secret", "dsa")
        )
        # Parent key
        assert 18400890916352345643 in secret_key.key_dict()
        # Sub-key
        assert 14839617247254692497 in secret_key.key_dict()
