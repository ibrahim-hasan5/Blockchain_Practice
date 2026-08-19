import hashlib

def hash256(data):
    """Returns the SHA-256 hash of the given data."""
    return hashlib.sha256(data).hexdigest()
