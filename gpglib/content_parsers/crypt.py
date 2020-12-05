from gpglib.utils import bytes_to_long, long_to_bytes
from gpglib import errors

from Crypto.Cipher import CAST, AES, Blowfish, DES3, PKCS1_v1_5
from Crypto.PublicKey import RSA, DSA, ElGamal
from Crypto.Hash import SHA, SHA256
from Crypto import Random

import bitstring
import zlib
import bz2

####################
### CFB
####################


def crypt_CFB(region, ciphermod, key, iv):
    """
    Shamelessly stolen from OpenPGP (with some modifications)
    http://pypi.python.org/pypi/OpenPGP
    """
    # Create the cipher
    cipher = ciphermod.new(key, ciphermod.MODE_ECB)

    # Determine how many bytes to process at a time
    shift = ciphermod.block_size

    # Create a bitstring list of ['bytes:8', 'bytes:8', 'bytes:3']
    # Such that the entire remaining region length gets consumed
    region_length = (region.len - region.pos) // 8
    region_datas = ["bytes:%d" % shift] * (region_length // shift)
    leftover = region_length % shift
    if leftover:
        region_datas.append("bytes:%d" % (region_length % shift))

    # Use the cipher to decrypt region
    blocks = []
    for inblock in region.readlist(region_datas):
        mask = cipher.encrypt(iv)
        iv = inblock
        chunk = b"".join([bytes(bytearray((c ^ m,))) for m, c in zip(mask, inblock)])
        blocks.append(chunk)

    return b"".join(blocks)


####################
### MAPPINGS
####################


class Mapping(object):
    """
    Thin class that gives item access to some map of values
    That raises a NotImplementedError if you try to access something not defined on it
    """

    def __init__(self, typ, map):
        self.map = map
        self.type = typ

    def __getitem__(self, key):
        """Complain if key isn't known"""
        if key not in self.map:
            raise NotImplementedError("Haven't implemented %s : %s" % (self.type, key))
        return self.map[key]


class Algorithms(object):
    encryption = Mapping(
        "Symmetric encryption algorithm",
        {
            2: (DES3, 21),  # TripleDES 168 bit key derived from 192
            3: (CAST, 16),  # CAST5 128-bit key
            4: (Blowfish, 16),  # Blowfish 128-bit key
            7: (AES, 16),  # AES 128-bit key
            8: (AES, 24),  # AES with 192-bit key
            9: (AES, 32),  # AES with 256-bit key
        },
    )

    hashes = Mapping("Hash Algorithm", {2: SHA, 8: SHA256})  # SHA-1  # SHA-256

    keys = Mapping(
        "Key algorithm",
        {
            1: RSA,  # Encrypt or Sign
            2: RSA,  # Encrypt Only
            3: RSA,  # Sign Only
            16: ElGamal,  # Encrypt Only
            17: DSA,  # Digital Signature Algorithm
        },
    )


class Compression(object):
    def decompress_zip(compressed):
        """
        To decompress zip, we use zlib with a -15 window size.
        It says to ignore the zlib header
        and that the data is compressed with up to 15 bits of compression.
        """
        return zlib.decompress(compressed, -15)

    decompression = Mapping(
        "Decompressor", {1: decompress_zip, 2: zlib.decompress, 3: bz2.decompress}
    )


class Mapped(object):
    algorithms = Algorithms
    compression = Compression


####################
### PKCS
####################


class PKCS(object):
    @classmethod
    def consume(cls, region, key_algorithm, key):
        """
        Get next mpi values from region as according to key_algorithm
        Decrypt those mpis and then parse them as
        0x2 | random bytes | 0x0 | result

        The result will then be
        algorithm | session_key | checksum

        These values are retrieved from result and returned.
        If, however, mpis don't follow pattern above, then random bytes are used instead
        """
        # Get the mpi values from the region according to key_algorithm
        # And decrypt them with the provided key
        mpis = tuple(mpi.bytes for mpi in Mpi.consume_encryption(region, key_algorithm))

        if isinstance(key, RSA.RsaKey):
            sentinel = Random.new().read(255)
            val = mpis[0]
            if len(val) < 256:
                padding = b"\0" * (256 - len(val))
                val = padding + val
            bts = PKCS1_v1_5.new(key).decrypt(val, sentinel)
            decrypted = bitstring.ConstBitStream(bytes=bts)
        else:
            decrypted = cls.decrypt_elgamal(key, mpis)

        # The size of the key is the amount in decrypted
        # Minus the algorithm at the front and the checksum at the end
        key_size = (decrypted.len - decrypted.pos) / 8 - 1 - 2

        # The algorithm used to encrypt the message is the first byte
        # The session key is the next <key_size> bytes
        # The checksum is the last two bytes
        return decrypted.readlist("uint:8, bytes:%d, uint:16" "" % key_size)

    @classmethod
    def decrypt_elgamal(cls, key, mpis):
        """
        Elgamal is actually deprecated and so there isn't and won't be a
        public PKCS1_v1_5 type cypher for it

        So this method uses the _decrypt method on the key and manually unpads the result
        """
        mpis = list(map(bytes_to_long, mpis))
        bts = long_to_bytes(int(key._decrypt(mpis)))
        padded = bitstring.ConstBitStream(bytes=bts)

        # If decrypted isn't set by the end we raise an exception
        decrypted = None

        # First byte needs to be 02
        if padded.read("bytes:1") == b"\x02":
            # Find the next 00
            pos_before = padded.bytepos
            padded.find("0x00", bytealigned=True)
            pos_after = padded.bytepos

            # The ps section needs to be greater than 8
            if pos_after - pos_before >= 8:
                # Read in the seperator 0 byte
                # Gauranteed to be zero given use of find above
                padded.read("bytes:1")

                # Decrypted value is the rest of the padded value
                decrypted = padded

        if decrypted is None:
            # MPIs weren't valid, use random bytes instead
            decrypted = bitstring.ConstBitStream(bytes=Random.get_random_bytes(19))

        return decrypted


####################
### MPI VALUES
####################


class Mpi(object):
    """Object to hold logic for getting multi precision integers from a region"""

    @classmethod
    def parse(cls, region):
        """Retrieve one MPI value from the region"""
        # Get the length of the MPI to read in
        raw_mpi_length = region.read("uint:16")

        # Read in the MPI bytes and return the resulting bitstream
        mpi_length = (raw_mpi_length + 7) // 8
        return region.read(mpi_length * 8)

    @classmethod
    def retrieve(cls, region, mpis):
        """
        Helper to get multiple mpis from a region
        Allows some nice declarativity below....
        """
        return tuple(cls.parse(region) for mpi in mpis)

    ####################
    ### RFC4880 5.1
    ####################

    @classmethod
    def consume_encryption(cls, region, algorithm):
        """Retrieve necessary MPI values from a public session key"""
        if algorithm is RSA:
            return cls.retrieve(region, ("m**e mod n",))

        elif algorithm is ElGamal:
            return cls.retrieve(region, ("g**k mod p", "m * y**k mod p"))

        else:
            raise errors.PGPException("Unknown mpi algorithm for encryption %d" % algorithm)

    ####################
    ### RFC4880 5.5.2 and 5.5.3
    ####################

    @classmethod
    def consume_public(cls, region, algorithm):
        """Retrieve necessary MPI values from a public key for specified algorithm"""
        if algorithm is RSA:
            return cls.retrieve(region, ("n", "e"))

        elif algorithm is ElGamal:
            return cls.retrieve(region, ("p", "g", "y"))

        elif algorithm is DSA:
            p, q, g, y = cls.retrieve(region, ("p", "q", "g", "y"))

            # Pycryptodome has a weird construct order
            return y, g, p, q

        else:
            raise errors.PGPException("Unknown mpi algorithm for public keys %d" % algorithm)

    @classmethod
    def consume_private(cls, region, algorithm):
        """Retrieve necessary MPI values from a secret key for specified algorithm"""
        if algorithm is RSA:
            return cls.retrieve(region, ("d", "p", "q", "r"))

        elif algorithm is ElGamal:
            return cls.retrieve(region, ("x",))

        elif algorithm is DSA:
            return cls.retrieve(region, ("x",))

        else:
            raise errors.PGPException("Unknown mpi algorithm for secret keys %d" % algorithm)
