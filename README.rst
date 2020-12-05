GPGLib2
=======

This is a Python3 compatible fork of the gpglib library with support for AES
secret keys and the mdc packet types.

History
-------

Back in 2012 we couldn't find a library for decrypting gpg that didn't shell out
to gpg.

And shelling out to gpg is slow when you do it for many small files.

So, with the help of http://pypi.python.org/pypi/OpenPGP and PyCrypto we created
this, which is more performant than shelling out.

Then in 2017 a friend needed this library for a task, but the library wasn't
compatible with python3. Unfortunately we couldn't get write access back to the
original gpglib, so we have created a fork.

ChangeLog
---------

0.4.0 - 6 December 2020
  * gpglib2 now only supports python3.6 and above
  * Formatting and linting with black and pylama
  * Upgraded dependencies

0.3.1 - 1 September 2018
  * Update pycryptodome for CVE-2018-15560
  * Remove use of a private method in pycryptodome when decrypting session keys

0.3 - 4 August 2018
  * Migrated from pycrypto to pycryptodome

0.2.1 - 7 February 2018
  * performance enhancement

0.2 - 28 Jan 2018
  * Fork and python3 compatibility

Installing
==========

To install, just use pip::

    $ pip install gpglib2

Or download from pypi: http://pypi.python.org/pypi/gpglib2.

Or clone the git repo: https://github.com/delfick/gpglib2.

Making test data
================

This is what I did to get the data in tests/data.

From within tests/data::

    $ gpg --full-gen-key --homedir ./gpg
    # Once with RSA encrypt and sign, username Stephen and password "password25"
    # And again with DSA/Elgamal, username Bobby and password "password25"

Then find the keyid::

    $ gpg --homedir ./gpg --list-keys
      ------------------------------------------------------------------------
      pub   rsa2048 2018-08-03 [SC]
            F93E6E1B45D1C037B42650DE52320610E94B004B
      uid           [ultimate] Stephen <stephen@stephen.com>
      sub   rsa2048 2018-08-03 [E]

      pub   dsa2048 2018-08-03 [SC]
            A02F07AF335D3212FEB29C44FF5D18CBDBE4C62B
      uid           [ultimate] Bobby <bobby@bobby.com>
      sub   elg2048 2018-08-03 [E]

    # Here, the key we want is "F93E6E1B45D1C037B42650DE52320610E94B004B"

Then with that keyid export the secret and public keys for both the rsa and dsa keys::

    $ export KEY=F93E6E1B45D1C037B42650DE52320610E94B004B
    $ gpg --export $KEY > keys/key.public.rsa.gpg
    $ gpg --export-secret-key $KEY > keys/key.secret.rsa.gpg

I then created dump.small and dump.big as random json structures (the big on is from http://json.org/example.html).

Then run ``./tests/data/generate_test_data.sh`` to generate messages in the
``tests/encrypted`` folder. 

Note that this is only necessary if you are editing ``generate_test_data.sh`` to
accommodate different options. If you are doing this then you will also need
to do the same to ``tests/test_decryption.py`` to take the different data into
account.

Tests
=====

Install the pip requirements::

    $ pip install -e ".[tests]"

And then run::

    $ ./test.sh

Currently not much is tested.

Note that if you also do a ``pip install tox`` then you may run the tests with
different python versions by running ``tox``

Docs
====

You can build the docs yourself by going into the docs directory and running
``./build.sh`` and then run ``python3 -m http.server`` and navigate to
``localhost:8000/sphinx/_build/html/``

Generated documentation is also available at: http://gpglib2.readthedocs.org/en/latest/
