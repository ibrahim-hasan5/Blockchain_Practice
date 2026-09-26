import hashlib
from math import log
from Crypto.Hash import RIPEMD160

BASE58_ALPHABET = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"

def hash256_bytes(data):
    """Returns the SHA-256 hash of the given data."""
    return hashlib.sha256(data).digest()

def hash256(data):
    """Returns the SHA-256 hash of the given data as a hexadecimal string."""
    return hashlib.sha256(data).hexdigest()

def hash160_bytes(s):
    # hash160 returns the RIPEMD-160 hash of the SHA-256 hash of the input data.
    # the output is a 20-byte hash.
    return RIPEMD160.new(hashlib.sha256(s).digest()).digest()

def hash160(s):
    # hash160 returns the RIPEMD-160 hash of the SHA-256 hash of the input data.
    # the output is a 20-byte hash, represented as a hexadecimal string.
    return RIPEMD160.new(hashlib.sha256(s).digest()).hexdigest()

def encode_base58(s):
    # determine how many 0 bytes (b'\x00') s starts with
    count = 0
    for c in s:
        if c == 0:
            count += 1
        else:
            break
    # convert to big endian integer
    num = int.from_bytes(s, 'big')
    prefix = '1' * count
    result = ''
    while num > 0:
        num, mod = divmod(num, 58)
        result = BASE58_ALPHABET[mod] + result
    return prefix + result


def decode_base58(s):
    num = 0

    for c in s:
        num *= 58
        num += BASE58_ALPHABET.index(c)

    combined = num.to_bytes(25, byteorder="big")
    checksum = combined[-4:]

    if hash256_bytes(combined[:-4])[:4] != checksum:
        raise ValueError(f"bad Address {checksum} {hash256_bytes(combined[:-4][:4])}")

    return combined[1:-4]


def bytes_needed(n):
    if n == 0:
        return 1
    return int(log(n, 256)) + 1

def int_to_little_endian(n, length):
    '''Convert an integer to little-endian bytes of a given length.'''
    return n.to_bytes(length, "little")

def little_endian_to_int(b):
    '''Convert little-endian bytes to an integer.'''
    return int.from_bytes(b, "little")

def int_to_big_endian(n, length):
    '''Convert an integer to big-endian bytes of a given length.'''
    return n.to_bytes(length, "big")

def big_endian_to_int(b):
    '''Convert big-endian bytes to an integer.'''
    return int.from_bytes(b, "big")

def encode_varint(i):
    '''Encodes an integer as a varint.'''
    if i < 0xfd:
        return bytes([i])
    elif i < 0x10000:
        return b'\xfd' + int_to_little_endian(i, 2)
    elif i < 0x100000000:
        return b'\xfe' + int_to_little_endian(i, 4)
    elif i < 0x10000000000000000:
        return b'\xff' + int_to_little_endian(i, 8)
    else:
        raise ValueError(f"Integer too large: {i}")

def read_varint(s):
    '''Reads a varint from a stream and returns the integer.'''
    i = s.read(1)[0]
    if i == 0xfd:
        # 0xfd indicates that the next 2 bytes are the integer
        return little_endian_to_int(s.read(2))
    elif i == 0xfe:
        # 0xfe indicates that the next 4 bytes are the integer
        return little_endian_to_int(s.read(4))
    elif i == 0xff:
        # 0xff indicates that the next 8 bytes are the integer
        return little_endian_to_int(s.read(8))
    else:
        return i
