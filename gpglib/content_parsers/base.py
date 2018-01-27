from gpglib.content_parsers.crypt import Mapped
from gpglib.utils import binary_type, PY3

import itertools

class Parser(object):
    """Base Parser class"""
    def consume(self, tag, message, region, **kwargs):
        """To be implemented by subclasses to do something with the body of the parser"""
        raise NotImplementedError("Don't know about tag type %d" % tag.tag_type)

    def only_implemented(self, received, implemented, message):
        """
            Useful to raise NotImplementedError when we get a value for something that hasn't been implemented
            i.e., self.only_implemented(received, (1, 2, 3), "values 1, 2 and 3")
            Would raise NotImplementedError saying "haven't implemented values 1, 2, and 3" if received is none of those values
        """
        if received not in implemented:
            raise NotImplementedError("%s |:| Sorry, haven't implemented value %s. Have only implemented %s." % (self.name, received, message))

    @property
    def name(self):
        return self.__class__.__name__

    def parse_s2k(self, region, cipher=None, passphrase=None):
        """Get and use string to key specifier for region"""
        # string-to-key specifier'
        # Hash algorithm used by the string-to-key value
        # The salt value used for the hash
        # Count to determine how much data gets hashed
        s2k_specifier, s2k_hash_algo, salt,    raw_count = region.readlist("""
        uint:8,        uint:8,        bytes:8, uint:8""")

        # Make sure passphrase is also a binary type
        # Because we add it to the salt
        if not isinstance(passphrase, binary_type):
            passphrase = passphrase.encode()

        self.only_implemented(s2k_specifier, (3, ), "String to key type 3")

        # Get a hash object we can use
        hasher = Mapped.algorithms.hashes[s2k_hash_algo]

        # The 'count' is the length of the data that gets hashed
        count = (16 + (raw_count & 15)) << ((raw_count >> 4) + 6)

        # The size of the key (in bytes)
        key_size = Mapped.ciphers.key_sizes[cipher]

        # Initialize an infinite stream of salts + passphrases
        combined = salt + passphrase
        if PY3:
            combined = [combined[i:i + 1] for i in range(len(combined))]
        else:
            combined = list(salt + passphrase)
        stream = itertools.cycle(combined)

        # Infinite for loop
        result = []
        for i in itertools.count():
            # Initialize the message, which is at a minimum:
            #   some nulls || salt || passphrase
            message = (b'\x00' * i) + salt + passphrase

            # Fill the rest of the message (up to `count`) with the string `salt + passphrase`
            nxt = list(itertools.islice(stream, count - len(message)))
            message += b''.join(nxt)

            # Now hash the message
            hsh = hasher.new(message).digest()

            # Append the message to the result, until len(result) == count
            size = min(len(hsh), key_size - len(result))
            result.append(hsh[0:size])

            # Break if the result is large enough
            if len(b"".join(result)) >= key_size:
                break

        return b"".join(result)
