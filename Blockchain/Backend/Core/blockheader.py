from Blockchain.Backend.Util.util import hash256
class BlockHeader:
    def __init__(self, version, prev_block_hash, merkle_root, timestamp, bits, nonce=0):
        self.version = version
        self.prev_block_hash = prev_block_hash
        self.merkle_root = merkle_root
        self.timestamp = timestamp
        self.bits = bits
        self.nonce = nonce
        self.blockHash = ''

    def mine(self, target):
        while (self.blockHash[0:len(target)] != target):
            self.blockHash = hash256(
                (str(self.version) + self.prev_block_hash + self.merkle_root + str(self.timestamp) + str(self.bits) + str(self.nonce)).encode('utf-8'))
            self.nonce += 1
            print(f"Mining Block: Nonce: {self.nonce}, Hash: {self.blockHash}", end="\r", flush=True)
    