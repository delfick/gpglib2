# coding: spec

from tests.helpers import data

from gpglib.structures import Key

from unittest import TestCase
import nose

describe TestCase, "Consuming rsa keys":
    it "successfully consumes a secret key":
        secret_key = Key(passphrase='password25').parse(data.get_pgp_key('secret', 'rsa'))
        # Parent key
        self.assertIn(5922803129648873547, secret_key.key_dict())
        # Sub-key
        self.assertIn(6126705363215480599, secret_key.key_dict())

    it "successfully consumes a public key":
        public_key = Key().parse(data.get_pgp_key('public', 'rsa'))
        # Parent key
        self.assertIn(5922803129648873547, public_key.key_dict())
        # Sub-key
        self.assertIn(6126705363215480599, public_key.key_dict())

    it "successfully calls a function to retrieve the passphrase":
        def passphrase_func(message, info):
            return 'password25'

        secret_key = Key(passphrase=passphrase_func).parse(data.get_pgp_key('secret', 'rsa'))
        # Parent key
        self.assertIn(5922803129648873547, secret_key.key_dict())
        # Sub-key
        self.assertIn(6126705363215480599, secret_key.key_dict())

describe TestCase, "Consuming dsa keys":
    it "successfully consumes a secret key":
        secret_key = Key(passphrase='password25').parse(data.get_pgp_key('secret', 'dsa'))
        # Parent key
        self.assertIn(7405841044128673154, secret_key.key_dict())
        # Sub-key
        self.assertIn(10470959134280958917, secret_key.key_dict())

    it "successfully consumes a public key":
        public_key = Key().parse(data.get_pgp_key('public', 'dsa'))
        # Parent key
        self.assertIn(7405841044128673154, public_key.key_dict())
        # Sub-key
        self.assertIn(10470959134280958917, public_key.key_dict())

    it "successfully calls a function to retrieve the passphrase":
        def passphrase_func(message, info):
            return 'password25'

        secret_key = Key(passphrase=passphrase_func).parse(data.get_pgp_key('secret', 'dsa'))
        # Parent key
        self.assertIn(7405841044128673154, secret_key.key_dict())
        # Sub-key
        self.assertIn(10470959134280958917, secret_key.key_dict())
