from gpglib.content_parsers.crypt import Mapped, crypt_CFB
from gpglib.content_parsers.base import Parser
from gpglib import errors

from Crypto.Hash import SHA
import bitstring

class CompressedParser(Parser):
    """Parse compressed packets"""
    def consume(self, tag, message, region):
        # Get the compression algorithm used
        # And the rest of the message
        algo, rest = region.readlist('uint:8, bytes')

        # Get decompressor and use it to decompress the packet
        decompressor = Mapped.compression.decompression[algo]
        uncompressed = decompressor(rest)

        # Parse the inner packet and return it
        return message.consume(uncompressed)

class SymEncryptedParser(Parser):
    """Parse symmetrically encrypted data packet"""
    def consume(self, tag, message, region, algo, session_key):
        # Get the encryption algorithm used
        cipher, _ = Mapped.algorithms.encryption[algo]

        # Find out the length of the IV
        iv_len = cipher.block_size + 2

        # Read in the encrypted IV
        # The ciphertext is what's left in `region` after the iv
        iv, ciphertext = region.readlist('bytes:%d, bytes' % iv_len)

        # Build the cipher object from the session key and the IV
        decryptor = cipher.new(session_key, cipher.MODE_OPENPGP, iv)

        # Decrypt the ciphertext
        decrypted = decryptor.decrypt(ciphertext)

        # Parse the inner packet and return it
        return message.consume(decrypted)

class LiteralParser(Parser):
    """Extracts various information from the packet but only returns the plaintext"""
    def consume(self, tag, message, region):
        # Is it binary ('b'), text ('t') or utf-8 text ('u')
        # The length of the filename in bytes
        format, filename_length = region.readlist('bytes:1, uint:8')

        # Read in filename
        # Read in the date (can mean anything. ie. creation, modification, or 0)
        filename, date = region.readlist('bytes:%d, uint:32' % filename_length)

        # Add the literal data to the list of decrypted plaintext
        message.add_plaintext(region.read('bytes'))

class UserIdParser(Parser):
    """Parses type-13 packets, which contain information about the user"""
    def consume(self, tag, message, region):
        message.userid = region.read('bytes')

class SymmetricallyEncryptedIntegrityProtectedDataPacketParser(Parser):
    """Parses type-18 packets"""
    def consume(self, tag, message, region, algo, session_key):
        version = region.read('uint:8')
        if version != 1:
            raise errors.PGPException("Expected integrity packet to have version 1")

        encrypted_data = region.read('bytes')

        # Get a cipher object we can use to decrypt the key (and fail if we can't)
        cipherkls, key_size = Mapped.algorithms.encryption[algo]

        block_size = cipherkls.block_size
        segment_size = block_size * 8
        cipher = cipherkls.new(session_key, cipherkls.MODE_CFB, b'\x00' * block_size, segment_size=segment_size)

        decrypted_iv = cipher.decrypt(encrypted_data[:block_size])
        decrypted_data = bytearray()

        offset = block_size
        first_block = cipher.decrypt(encrypted_data[offset:offset + block_size])

        offset += block_size
        iv_check = first_block[:2]
        if iv_check != decrypted_iv[-2:]:
            raise errors.PGPException("There was a mismatch in the integrity check")

        decrypted_data.extend(first_block[2:])

        padding = block_size - (len(encrypted_data) - offset) % block_size
        encrypted_data += b'\x00' * padding

        decrypted_data.extend(cipher.decrypt(encrypted_data[offset:]))
        decrypted_data = decrypted_data[:-padding]

        # We run into trouble here with partial body lengths and the MDC.
        # Let's make pretend.
        mdc_data = bytearray()
        main_data = bytes(decrypted_data)
        if decrypted_data[-22:-20] == b'\xd3\x14':
            # It's there. Hold it back.
            mdc_data = bytes(decrypted_data[-22:])
            main_data = bytes(decrypted_data[:-22])

        message.consume(main_data)
        if mdc_data:
            message.consume(mdc_data)

        if not hasattr(message, "mdc"):
            raise errors.PGPException('Integrity protected message is missing modification detection code.')

        hash_ = SHA.new(decrypted_iv)
        hash_.update(decrypted_iv[-2:])
        hash_.update(decrypted_data[:-20])

        if message.mdc != hash_.digest():
            raise errors.PGPException('Integrity protected message does not match modification detection code.')

class ModificationDetectionCodePacketParser(Parser):
    """Parses type-17 packets"""
    def consume(self, tag, message, region):
        # Just contains a 20 octet sha1 hash
        message.add_mdc(region.read("bytes:20"))

        # Hack to make sure this packet is last
        return dict(mdc_must_be_last=True)
