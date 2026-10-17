from Blockchain.Backend.Core.blockheader import BlockHeader
from Blockchain.Backend.Core.block import Block
from Blockchain.Backend.Core.Database.database import BlockchainDB
from Blockchain.Backend.Util.util import hash256, int_to_little_endian, bytes_needed, little_endian_to_int
from Blockchain.Backend.Core.tx import CoinbaseTx
import time
import json

from Blockchain.config import VERSION, TARGET, ZERO_HASH, ZERO_HASH_BYTES, CURRENT_REWARD, ONE_COIN, INITIAL_REWARD, HALVING_INTERVAL

class Blockchain:
    def __init__(self):
        # self.chain = []
        self.blockchainDB = BlockchainDB()

        # In-memory pool of unconfirmed transactions waiting to be mined
        # Structure: { tx_id (hex str) : Tx object }
        self.mempool = {}

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

    def add_to_mempool(self, tx):
        """
        Adds an unconfirmed transaction to the mempool.

        The mempool (memory pool) is a holding area for transactions that have
        been broadcast to the network but not yet included in a mined block.

        Duplicate Check:
            Each transaction has a unique ID (tx.id()). If a transaction with
            the same ID is already in the mempool, it is rejected to prevent
            processing the same transaction twice.

        Args:
            tx: A Tx object to be added to the mempool.

        Returns:
            True  if the transaction was successfully added.
            False if the transaction was already in the mempool (duplicate).
        """
        tx_id = tx.id()

        # Duplicate check: reject if tx is already waiting in the mempool
        if tx_id in self.mempool:
            print(f"[mempool] DUPLICATE: Transaction {tx_id[:20]}... already in mempool. Skipping.")
            return False

        # Add the transaction to the mempool
        self.mempool[tx_id] = tx
        print(f"[mempool] Added: {tx_id[:20]}... | Pending txs: {len(self.mempool)}")
        return True

    def get_pending_transactions(self):
        """
        Returns all unconfirmed transactions currently waiting in the mempool.

        Returns:
            list: A list of Tx objects. Empty list if mempool is empty.
        """
        return list(self.mempool.values())

    def get_block_reward(self, block_height):
        """
        Returns the correct mining reward (in UAP Coin) for a given block height,
        based on a simplified halving schedule.

        How halving works:
        - Blocks 1  - 10  → reward = 50 UAP Coin  (2^0 halvings)
        - Blocks 11 - 20  → reward = 25 UAP Coin  (2^1 halvings)
        - Blocks 21 - 30  → reward = 12 UAP Coin  (2^2 halvings)
        - ...and so on until reward reaches 0.

        Formula:
            halvings = (block_height - 1) // HALVING_INTERVAL
            reward   = INITIAL_REWARD // (2 ** halvings)

        Args:
            block_height (int): The height of the block being mined (starts at 1).

        Returns:
            int: The mining reward in UAP Coin units. Minimum is 0.
        """
        # How many times has the reward halved so far?
        halvings = (block_height - 1) // HALVING_INTERVAL

        # After too many halvings, integer division makes reward reach 0
        # (e.g. 50 // 2^6 = 50 // 64 = 0)
        reward = INITIAL_REWARD >> halvings  # same as INITIAL_REWARD // (2 ** halvings)

        # Minimum reward is 0 (no negative rewards)
        return max(0, reward)

    def calculate_merkle_root(self, transactions):
        """
        Computes the Merkle root from a list of transaction objects.

        How a Merkle Tree works:
        1. Start with the hash (ID) of each transaction as leaf nodes.
        2. Pair up adjacent hashes and hash them together.
        3. If there is an odd number of hashes, duplicate the last one.
        4. Repeat until only one hash remains — that is the Merkle root.

        Example (4 transactions)::

            [TxA]  [TxB]  [TxC]  [TxD]       <- leaf level
                \\    /        \\    /
            [Hash(AB)]    [Hash(CD)]          <- level 2
                    \\        /
                  [Hash(ABCD)]                <- Merkle Root

        Args:
            transactions: list of Tx objects, each having an .id() method
                          that returns the transaction hash as a hex string.

        Returns:
            str: The Merkle root as a hex string.
                 Returns '' if the transaction list is empty.
        """
        # Step 1: Get the transaction ID (hash) for every transaction
        tx_hashes = [tx.id() for tx in transactions]

        if len(tx_hashes) == 0:
            return ''

        # Step 2: Iteratively build the tree until one hash remains
        while len(tx_hashes) > 1:

            # Step 3: If odd number of hashes, duplicate the last one
            if len(tx_hashes) % 2 != 0:
                tx_hashes.append(tx_hashes[-1])

            # Step 4: Hash each pair together to form the next level
            next_level = []
            for i in range(0, len(tx_hashes), 2):
                combined = tx_hashes[i] + tx_hashes[i + 1]
                parent_hash = hash256(combined.encode('utf-8'))
                next_level.append(parent_hash)

            tx_hashes = next_level

        # The single remaining hash is the Merkle root
        return tx_hashes[0]

    def validate_coinbase(self, tx, block_height):
        """
        Validates a coinbase transaction before it can be included in a block.

        Checks:
        1. The transaction has exactly one input.
        2. The input references ZERO_HASH_BYTES and index 0xFFFFFFFF.
        3. The coinbase input's script contains the expected block height
           in little-endian format.
        4. The transaction has at least one output.
        5. Every output amount is positive, and the combined output amount
           equals CURRENT_REWARD * ONE_COIN.
        """
        # Check 1: Exactly one input
        if len(tx.tx_ins) != 1:
            print("[validate_coinbase] FAILED: Transaction must have exactly one input.")
            return False

        tx_in = tx.tx_ins[0]

        # Check 2: Input references ZERO_HASH_BYTES and index 0xFFFFFFFF
        if tx_in.prev_tx != ZERO_HASH_BYTES:
            print("[validate_coinbase] FAILED: Input must reference ZERO_HASH_BYTES.")
            return False
        if tx_in.prev_index != 0xFFFFFFFF:
            print("[validate_coinbase] FAILED: Input index must be 0xFFFFFFFF.")
            return False

        # Check 3: Script contains the expected block height in little-endian format
        expected_height_le = int_to_little_endian(block_height, bytes_needed(block_height))
        if len(tx_in.script_sig.cmds) == 0 or tx_in.script_sig.cmds[0] != expected_height_le:
            print("[validate_coinbase] FAILED: Script does not contain expected block height.")
            return False

        # Check 4: At least one output
        if len(tx.tx_outs) == 0:
            print("[validate_coinbase] FAILED: Transaction must have at least one output.")
            return False

        # Check 5: All output amounts are positive, and total equals CURRENT_REWARD * ONE_COIN
        expected_total = CURRENT_REWARD * ONE_COIN
        total_output = 0
        for tx_out in tx.tx_outs:
            if tx_out.amount <= 0:
                print(f"[validate_coinbase] FAILED: Output amount must be positive (got {tx_out.amount}).")
                return False
            total_output += tx_out.amount

        if total_output != expected_total:
            print(f"[validate_coinbase] FAILED: Total output {total_output} != expected {expected_total}.")
            return False

        return True

    def add_block(self, blockHeight, prevBlockHash):

        # Create a new block header
        version = VERSION
        timestamp = int(time.time())
        bits = "ffff0000" # Placeholder for the actual difficulty target

        # Create a coinbase transaction for the miner
        coinbase_tx = CoinbaseTx(blockHeight).CoinbaseTransaction()

        # Validate the coinbase transaction before mining or writing to disk
        if not self.validate_coinbase(coinbase_tx, blockHeight):
            print(f"[add_block] Block {blockHeight} rejected: invalid coinbase transaction.")
            return False

        # Fetch pending transactions from mempool
        pending_txs = self.get_pending_transactions()

        # Save their IDs now — BEFORE to_dict() mutates the Tx objects
        pending_tx_ids = [tx.id() for tx in pending_txs]

        # Block transactions: coinbase always first, then mempool txs
        Txs = [coinbase_tx] + pending_txs

        # Calculate the real Merkle root from ALL transactions in this block
        merkle_root = self.calculate_merkle_root(Txs)
        print(f"Merkle Root : {merkle_root}")
        print(f"Tx count    : {len(Txs)} (1 coinbase + {len(pending_txs)} from mempool)")

        block_header = BlockHeader(version, prevBlockHash, merkle_root, timestamp, bits)

        block_header.mine(TARGET)

        # Convert ALL transactions to dicts for on-disk storage
        # Note: to_dict() is a destructive call — it modifies the Tx object in place.
        # That is why we saved pending_tx_ids before this step.
        tx_dicts = [tx.to_dict() for tx in Txs]

        # Create a new block storing the full list of transaction dicts
        new_block = Block(blockHeight, 1, block_header.__dict__, tx_dicts).__dict__

        # Persist the block to disk
        self.write_on_disk([new_block])

        # Remove confirmed transactions from the mempool
        for tx_id in pending_tx_ids:
            self.mempool.pop(tx_id, None)

        if pending_tx_ids:
            print(f"[mempool] {len(pending_tx_ids)} tx(s) confirmed and removed from mempool.")

        print(f"Block {blockHeight} added to the blockchain with hash: {block_header.blockHash}")
        return True


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

    def calculate_fee(self, tx):
        """
        Computes the transaction fee for a regular (non-coinbase) transaction.

        Formula:
            fee = sum(input amounts) - sum(output amounts)

        Why inputs > outputs?
            The difference is the miner's fee incentive. Miners pick transactions
            with higher fees to include in their blocks first.

        For coinbase transactions there is nothing being spent, so fee = 0.

        How input amounts are resolved:
            A TxIn only stores (prev_tx_id, prev_index) — it does NOT store the
            coin amount. To find the amount, we look up the referenced output
            from the stored blockchain.

            Lookup key:  tx_in.prev_tx.hex()  (bytes → hex string = TxId)
            Match target: block["Txs"][i]["TxId"]  (stored in blockchain dict)

        Args:
            tx: A Tx object.

        Returns:
            int  : Fee in Poisha (minimum 0). Returns 0 for coinbase transactions.
            None : If a referenced previous transaction is not found in the chain.
        """
        # Coinbase transactions create coins from nothing — no fee
        if tx.is_coinbase():
            return 0

        # ------------------------------------------------------------------
        # Step 1: Build a lookup map of every transaction stored on disk
        #         { TxId (hex str) : tx_dict }
        #
        # We handle two storage formats:
        #   Old format  — block["Txs"] is a single tx dict   (pre-mempool)
        #   New format  — block["Txs"] is a list of tx dicts (post-mempool)
        # ------------------------------------------------------------------
        chain = self.read_from_disk()
        tx_lookup = {}

        for block in chain:
            block_txs = block.get("Txs", [])

            # Normalise: wrap single dict in a list
            if isinstance(block_txs, dict):
                block_txs = [block_txs]

            for tx_dict in block_txs:
                if isinstance(tx_dict, dict) and "TxId" in tx_dict:
                    tx_lookup[tx_dict["TxId"]] = tx_dict

        # ------------------------------------------------------------------
        # Step 2: Sum the value of every input by resolving it from tx_lookup
        # ------------------------------------------------------------------
        total_input = 0

        for tx_in in tx.tx_ins:
            # Convert the raw prev_tx bytes to a hex string to use as lookup key
            prev_tx_id = tx_in.prev_tx.hex()

            if prev_tx_id not in tx_lookup:
                print(f"[calculate_fee] ERROR: Source tx '{prev_tx_id[:20]}...' not found in blockchain.")
                return None

            prev_outputs = tx_lookup[prev_tx_id].get("tx_outs", [])

            if tx_in.prev_index >= len(prev_outputs):
                print(f"[calculate_fee] ERROR: Output index {tx_in.prev_index} out of range "
                      f"(tx has {len(prev_outputs)} output(s)).")
                return None

            total_input += prev_outputs[tx_in.prev_index]["amount"]

        # ------------------------------------------------------------------
        # Step 3: Sum all output amounts directly from the Tx object
        # ------------------------------------------------------------------
        total_output = sum(tx_out.amount for tx_out in tx.tx_outs)

        fee = total_input - total_output

        print(f"[calculate_fee] Input total  : {total_input:>15,} Poisha")
        print(f"[calculate_fee] Output total : {total_output:>15,} Poisha")
        print(f"[calculate_fee] Fee          : {fee:>15,} Poisha  ({fee / ONE_COIN:.8f} UAP Coin)")

        return fee