"""
Demonstration of validate_coinbase() for all lab test cases.
Mining reward: 50 UAP Coin = 50 * 100_000_000 = 5_000_000_000 Poisha
"""
from Blockchain.Backend.Core.blockchain import Blockchain
from Blockchain.Backend.Core.tx import CoinbaseTx, Tx, TxIn, TxOut
from Blockchain.Backend.Core.script import Script
from Blockchain.Backend.Util.util import decode_base58, int_to_little_endian, bytes_needed
from Blockchain.config import ZERO_HASH_BYTES, CURRENT_REWARD, ONE_COIN

BLOCK_HEIGHT = 1
MINER_ADDRESS = "15EDkKeKEZRtMiASKZoncU2J8WLqjGk5Hz"

blockchain = Blockchain()

def make_coinbase_input(block_height=BLOCK_HEIGHT, prev_tx=ZERO_HASH_BYTES, prev_index=0xFFFFFFFF):
    tx_in = TxIn(prev_tx, prev_index)
    tx_in.script_sig.cmds.append(
        int_to_little_endian(block_height, bytes_needed(block_height))
    )
    return tx_in

def make_output(coins):
    """coins in UAP Coin units (e.g. 50 means 50 UAP Coin)"""
    amount = coins * ONE_COIN
    pubkey_hash = decode_base58(MINER_ADDRESS)
    script = Script.p2pkh_script(pubkey_hash)
    return TxOut(amount=amount, script_pubkey=script)

def run_case(description, tx):
    result = blockchain.validate_coinbase(tx, BLOCK_HEIGHT)
    status = "Valid" if result else "Invalid"
    print(f"  {description}: {status}")
    print()

print("=" * 60)
print("validate_coinbase() Demonstration (Mining reward: 50 UAP Coin)")
print("=" * 60)
print()

# Case 1: One output containing 50 coins → Valid
tx_in = make_coinbase_input()
tx_out = make_output(50)
tx = Tx(1, [tx_in], [tx_out], 0)
run_case("One output containing 50 coins", tx)

# Case 2: Two outputs containing 30 and 20 coins → Valid
tx_in = make_coinbase_input()
tx_out1 = make_output(30)
tx_out2 = make_output(20)
tx = Tx(1, [tx_in], [tx_out1, tx_out2], 0)
run_case("Two outputs containing 30 and 20 coins", tx)

# Case 3: One output containing 60 coins → Invalid (exceeds reward)
tx_in = make_coinbase_input()
tx_out = make_output(60)
tx = Tx(1, [tx_in], [tx_out], 0)
run_case("One output containing 60 coins", tx)

# Case 4: One output containing -5 coins → Invalid (negative amount)
tx_in = make_coinbase_input()
tx_out = make_output(-5) #TxOut(amount=-5 * ONE_COIN, script_pubkey=Script.p2pkh_script(decode_base58(MINER_ADDRESS)))
tx = Tx(1, [tx_in], [tx_out], 0)
run_case("One output containing -5 coins", tx)

# Case 5: Coinbase referencing an ordinary transaction instead of zero hash → Invalid
fake_prev_tx = bytes.fromhex("abcd" * 16)  # 32 bytes, not ZERO_HASH_BYTES
tx_in = make_coinbase_input(prev_tx=fake_prev_tx)
tx_out = make_output(50)
tx = Tx(1, [tx_in], [tx_out], 0)
run_case("Coinbase referencing an ordinary transaction instead of zero hash", tx)
