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