from setuptools import setup, find_packages
from gpglib import VERSION

# fmt: off

# All the packages except test
packages = [pkg for pkg in find_packages() if not pkg.startswith('tests')]

setup(
      name = "gpglib2"
    , version = VERSION
    , packages = packages

    , python_requires = ">= 3.6"

    , install_requires =
      [ 'pycryptodome==3.6.6'
      , 'bitstring==3.1.5'
      ]

    , extras_require =
      { "tests":
        [ "noseOfYeti==2.0.2"
        , "pytest"
        , "pytest-helpers-namespace==2019.1.8"
        ]
      }

    # metadata for upload to PyPI
    , author = "Stephen Moore"
    , author_email = "delfick755@gmail.com"
    , description = "A python3 compatible fork of gpglib, a Library for decrypting gpg that doesn't shell out to gpg"
    , long_description = open("README.rst").read()
    , license = "LGPLv2"
    , keywords = "gpg decrypt"
    )

# fmt: on
