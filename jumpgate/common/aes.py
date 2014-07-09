import base64

from Crypto.Cipher import AES

from jumpgate import config

BLOCK_SIZE = 32
PADDING = '#'


def pad(string):
    return string + (BLOCK_SIZE - len(string) % BLOCK_SIZE) * PADDING


def create_cypher():
    return AES.new(pad(config.CONF['secret_key']))


def encode_aes(string):
    cipher = create_cypher()
    return base64.b64encode(cipher.encrypt(pad(string)))


def decode_aes(encrypted_string):
    cipher = create_cypher()
    return cipher.decrypt(base64.b64decode(encrypted_string)).rstrip(PADDING)
