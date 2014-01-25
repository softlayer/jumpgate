from Crypto.Cipher import AES
import base64
from jumpgate.config import CONF


BLOCK_SIZE = 32
PADDING = '#'


def pad(string):
    return string + (BLOCK_SIZE - len(string) % BLOCK_SIZE) * PADDING


def create_cypher():
    return AES.new(pad(CONF['secret_key']))


def encode_aes(string):
    cipher = create_cypher()
    return base64.b64encode(cipher.encrypt(pad(string)))


def decode_aes(encrypted_string):
    cipher = create_cypher()
    return cipher.decrypt(base64.b64decode(encrypted_string)).rstrip(PADDING)
