from Blockchain.Backend.Core.blockheader import BlockHeader
from Blockchain.Backend.Core.block import Block
from Blockchain.Backend.Core.Database.database import BlockchainDB
from Blockchain.Backend.Util.util import hash256
from Blockchain.Backend.Core.tx import CoinbaseTx
import time
import json

from Blockchain.config import VERSION, TARGET, ZERO_HASH

class Blockchain:
    def __init__(self):
        # self.chain = []
        self.blockchainDB = BlockchainDB()

        if not self.blockchainDB.BlockchainDBExists():
            print("Blockchain database not found. Creating genesis block...")
            self.create_genesis_block()

    def write_on_disk(self, block):
        self.blockchainDB.write(block)

    def read_from_disk(self):
        return self.blockchainDB.read()

    def get_last_block(self):
        return self.blockchainDB.lastBlock()

    def create_genesis_block(self):
        self.add_block(1, ZERO_HASH)

    def convert_to_json(self):
        self.TxJson = []
        for tx in self.addTransactionsInBlock:
            self.TxJson.append(tx.to_dict())

    def add_block(self, blockHeight, prevBlockHash):

        # Create a new block header
        version = VERSION
        timestamp = int(time.time())
        bits = "ffff0000" # Placeholder for the actual difficulty target

        # transactions = []  # Placeholder for actual transactions
        # Txs = [f"A is sending {blockHeight} coins to B"]  # Placeholder for actual transactions
        # Create a coinbase transaction for the miner
        coinbase_tx = CoinbaseTx(blockHeight).CoinbaseTransaction()
        Txs = [coinbase_tx]

        # merkle_root = hash256(json.dumps(Txs).encode('utf-8'))
        merkle_root = ''

        block_header = BlockHeader(version, prevBlockHash, merkle_root, timestamp, bits)

        block_header.mine(TARGET)

        # Create a new block
        new_block = Block(blockHeight, 1, block_header.__dict__, Txs[0].to_dict()).__dict__

        # Add the new block to the blockchain
        # self.chain.append(new_block)
        # self.convert_to_json()
        self.write_on_disk([new_block])

        print(f"Block {blockHeight} added to the blockchain with hash: {block_header.blockHash}")


    def add_next_block(self):
        last_block = self.get_last_block()
        new_block_height = last_block["Height"] + 1
        new_prev_hash = last_block["BlockHeader"]["blockHash"]
        self.add_block(new_block_height, new_prev_hash)

    def print(self):
        print(json.dumps(self.read_from_disk(), indent=4))

    def validate_chain(self):
        chain = self.read_from_disk()

        # 1. Return False if the blockchain is empty.
        if not chain or len(chain) == 0:
            return False

        previous_hash = ZERO_HASH

        for i, block in enumerate(chain):
            height = block["Height"]
            block_header = block["BlockHeader"]
            stored_hash = block_header["blockHash"]

            # 2. Check that the first block has height 1 and uses ZERO_HASH as its previous hash.
            if i == 0:
                if height != 1 or block_header["prev_block_hash"] != ZERO_HASH:
                    return False
            else:
                # 3. Check that each block has the correct height and previous-block hash.
                if height != i + 1:
                    return False
                if block_header["prev_block_hash"] != previous_hash:
                    return False

            # 4. Recalculate each block's hash and compare it with the stored hash.
            # Important: The existing mining code increments the nonce after calculating the hash.
            # Consider this behavior when recalculating a block's hash.
            recalculated_hash = hash256(
                (str(block_header["version"]) + block_header["prev_block_hash"] + block_header["merkle_root"] + str(block_header["timestamp"]) + str(block_header["bits"]) + str(block_header["nonce"] - 1)).encode('utf-8')
            )

            if recalculated_hash != stored_hash:
                return False

            # 5. Check that each block's hash satisfies the mining target (TARGET).
            if stored_hash[0:len(TARGET)] != TARGET:
                return False

            previous_hash = stored_hash

        return True