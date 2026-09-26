from Blockchain.Backend.Core.script import Script
from Blockchain.Backend.Util.util import (
    hash256_bytes,
    int_to_little_endian,
    bytes_needed,
    decode_base58,
    little_endian_to_int,
    encode_varint,
    hash256,
    read_varint
)

from Blockchain.config import ONE_COIN, ZERO_HASH_BYTES, CURRENT_REWARD

PRIVATE_KEY = (
    "100251472430611582791533626976459854844003248891146606144625396632531193696782"
)
MINER_PUBLIC_ADDRESS = "15EDkKeKEZRtMiASKZoncU2J8WLqjGk5Hz"

class CoinbaseTx:
    def __init__(self, BlockHeight):
        self.BlockHeightInLittleEndian = int_to_little_endian(
            BlockHeight, bytes_needed(BlockHeight)
        )

    def CoinbaseTransaction(self):
        prev_tx = ZERO_HASH_BYTES
        prev_index = 0xFFFFFFFF

        # Create a transaction input for the coinbase transaction
        tx_ins = []
        tx_ins.append(TxIn(prev_tx, prev_index))
        tx_ins[0].script_sig.cmds.append(self.BlockHeightInLittleEndian)

        # Create a transaction output for the miner's reward
        tx_outs = []
        target_amount = CURRENT_REWARD * ONE_COIN  # Convert UAP Coin to Poisha
        miner_public_key = decode_base58(MINER_PUBLIC_ADDRESS)
        target_script = Script.p2pkh_script(miner_public_key)
        tx_outs.append(TxOut(amount=target_amount, script_pubkey=target_script))

        # Create the coinbase transaction
        coinBaseTx = Tx(1, tx_ins, tx_outs, 0)
        coinBaseTx.TxId = coinBaseTx.id()

        return coinBaseTx

class Tx:
    def __init__(self, version, tx_ins, tx_outs, locktime):
        self.version = version
        self.tx_ins = tx_ins
        self.tx_outs = tx_outs
        self.locktime = locktime

    def id(self):
        '''Returns the transaction hash in hex format
        '''
        return (hash256_bytes(self.serialize())[::-1]).hex()

    def serialize(self):
        '''Returns the serialized transaction in bytes format
        The serialization format is as follows:
        - version (4 bytes, little-endian)
        - number of inputs (varint)
        - inputs (variable length)
        - number of outputs (varint)
        - outputs (variable length)
        - locktime (4 bytes, little-endian)

        What is serialized transaction?
        A serialized transaction is a binary representation of a Bitcoin transaction that can be transmitted over the network
        and stored in the blockchain. It contains all the necessary information about the transaction, including the inputs, outputs, and other metadata.
        The serialized transaction is used to create a unique transaction ID (txid) that can be used to reference the transaction in the blockchain.
        The serialization format is defined by the Bitcoin protocol and is used to ensure that transactions are consistent
        across different implementations of the protocol.

        Why is it important to serialize a transaction?
        Serializing a transaction is important because it allows the transaction to be transmitted over the network and stored in the blockchain in a standardized format.
        This ensures that all nodes in the network can understand and validate the transaction, regardless of the implementation of the Bitcoin protocol they are using.
        Additionally, the serialized transaction is used to create a unique transaction ID (txid) that can be used to reference the transaction in the blockchain.
        '''

        result = int_to_little_endian(self.version, 4)
        result += encode_varint(len(self.tx_ins))

        for tx_in in self.tx_ins:
            result += tx_in.serialize()

        result += encode_varint(len(self.tx_outs))

        for tx_out in self.tx_outs:
            result += tx_out.serialize()

        result += int_to_little_endian(self.locktime, 4)
        return result

    def is_coinbase(self):
        '''Returns True if the transaction is a coinbase transaction
        A coinbase transaction is a special type of Bitcoin transaction that is created by miners as a reward for mining a new block.
        It is the first transaction in a block and has no inputs, meaning that it does not spend any existing bitcoins.
        Instead, it creates new bitcoins out of thin air and assigns them to the miner's address as a reward for their work in securing the network.
        The coinbase transaction also includes a special script called the "coinbase script" that contains arbitrary data, such as the block height and extra nonce,
        which can be used to generate unique hashes for the block.
        '''
        return len(self.tx_ins) == 1 and self.tx_ins[0].prev_tx == ZERO_HASH_BYTES and self.tx_ins[0].prev_index == 0xFFFFFFFF
    

    def to_dict(self):
        """
         To Convert Transaction to dict
          1. Convert Transaction Inputs to dict
          2. Convert Transaction Outputs to dict
        """
        '''
        1. Convert Transaction Inputs to dict
         (i) Convert prev_tx Hash in hex from bytes
        (ii) Convert Blockheight in hex which is stored in Script signature
        '''
        for tx_index, tx_in in enumerate(self.tx_ins):
            if self.is_coinbase():
                tx_in.script_sig.cmds[0] = little_endian_to_int(
                    tx_in.script_sig.cmds[0]
                )

            tx_in.prev_tx = tx_in.prev_tx.hex()

            for index, cmd in enumerate(tx_in.script_sig.cmds):
                if isinstance(cmd, bytes):
                    tx_in.script_sig.cmds[index] = cmd.hex()

            tx_in.script_sig = tx_in.script_sig.__dict__
            self.tx_ins[tx_index] = tx_in.__dict__

        '''
         2. Convert Transaction Outputs to dict
          # If there are Numbers we don't need to do anything
          # If values is in bytes, convert it to hex
          # Loop Through all the TxOut Objects and convert them into dict 
        '''
        for index, tx_out in enumerate(self.tx_outs):
            tx_out.script_pubkey.cmds[2] = tx_out.script_pubkey.cmds[2].hex()
            tx_out.script_pubkey = tx_out.script_pubkey.__dict__
            self.tx_outs[index] = tx_out.__dict__

        return self.__dict__
    

class TxIn:
    ''' Represents a transaction input in a Bitcoin transaction.
    Attributes:
        prev_tx (bytes): The previous transaction hash (32 bytes).
        prev_index (int): The index of the output in the previous transaction.
        script_sig (Script): The script signature for the input.
        sequence (int): The sequence number for the input (default: 0xFFFFFFFF).

    Example:
        TxID : 0x1234567890abcdef1234567890abcdef
        Satoshi -> 0. sent 5 BTC to Einestein
                -> 1. sent 3 BTC to Newton
        
        Now, if Einstein wants to send 2 BTC to Tesla, he will create a new transaction with the following input:
        prev_tx: 0x1234567890abcdef1234567890abcdef (the transaction ID of the previous transaction)
        prev_index: 0 (the index of the output in the previous transaction that Einstein wants to spend)
        script_sig: <Einstein's signature> (the script signature that proves Einstein's ownership of the output)
        sequence: 0xFFFFFFFF (the sequence number for the input)
    '''
    def __init__(self, prev_tx, prev_index, script_sig=None, sequence=0xFFFFFFFF):
        self.prev_tx = prev_tx
        self.prev_index = prev_index

        if script_sig is None:
            self.script_sig = Script()
        else:
            self.script_sig = script_sig

        self.sequence = sequence

    def serialize(self):
        '''Returns the serialized transaction input in bytes format
        The serialization format is as follows:
        - previous transaction hash (32 bytes, little-endian)
        - previous transaction output index (4 bytes, little-endian)
        - script signature length (varint)
        - script signature (variable length)
        - sequence number (4 bytes, little-endian)
        '''
        result = self.prev_tx[::-1]
        result += int_to_little_endian(self.prev_index, 4)
        result += self.script_sig.serialize()
        result += int_to_little_endian(self.sequence, 4)
        return result

class TxOut:
    ''' Represents a transaction output in a Bitcoin transaction.
    Attributes:
        amount (int): The amount to be sent in the output.
        script_pubkey (Script): The script public key for the output.
    Example:
        TxID : 0x1234567890abcdef1234567890abcdef
        Satoshi -> 0. sent 5 BTC to Einestein
                -> 1. sent 3 BTC to Newton
        
        Now, if Einstein wants to send 2 BTC to Tesla, he will create a new transaction with the following output:
        amount: 2 BTC (the amount to be sent in the output)
        script_pubkey: <Tesla's public key hash> (the script public key that specifies the conditions for spending the output)
    '''
    def __init__(self, amount, script_pubkey):
        self.amount = amount
        self.script_pubkey = script_pubkey

    def serialize(self):
        '''Returns the serialized transaction output in bytes format
        The serialization format is as follows:
        - amount (8 bytes, little-endian)
        - script public key length (varint)
        - script public key (variable length)
        '''
        result = int_to_little_endian(self.amount, 8)
        result += self.script_pubkey.serialize()
        return result
