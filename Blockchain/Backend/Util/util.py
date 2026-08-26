import hashlib
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