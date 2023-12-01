from gpglib.structures import EncryptedMessage, Key

if __name__ == "__main__":
    data = open("tests/data/keys/key.secret.rsa.gpg", "rb").read()
    key = Key(passphrase="password25")
    key.parse(data)
    keys = key.key_dict()
    print(keys)

    data = open("tests/data/encrypted/mdc/rsa/aes/zlib/small.gpg", "rb").read()
    message = EncryptedMessage(keys)
    message.decrypt(data)

    print("Message successfully decrypted data.dump::")
    print(message.plaintext)

    data = open("tests/data/encrypted/mdc/rsa/aes/zlib/big.gpg", "rb").read()
    message = EncryptedMessage(keys)
    message.decrypt(data)

    print("Message successfully decrypted data.big.dump::")
    print(message.plaintext)
