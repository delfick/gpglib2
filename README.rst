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

    $ gpg --gen-key --homedir ./gpg
    # Once with RSA encrypt and sign, username Stephen and password "blahandstuff"
    # And again with DSA/Elgamal, username Bobby and password "blahandstuff"

Then find the keyid::

    $ gpg --homedir ./gpg --list-keys
        #     ./gpg/pubring.gpg
        # -----------------
        # pub   2048R/1E42B68C 2012-06-15
        # uid                  Stephen
        # sub   2048R/80C7020A 2012-06-15
    # Here, the key we want is "80C7020A"
    
Then with that keyid export the secret and public keys for both the rsa and dsa keys::

    $ gpg --export 80C7020A > key.public.rsa.gpg
    $ gpg --export-secret-key 80C7020A > key.secret.rsa.gpg

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
