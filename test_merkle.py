"""
Demonstration of calculate_merkle_root(transactions)
Shows how the Merkle tree is built step by step.
"""
from Blockchain.Backend.Core.blockchain import Blockchain
from Blockchain.Backend.Core.tx import CoinbaseTx
from Blockchain.Backend.Util.util import hash256

blockchain = Blockchain()

print("=" * 65)
print("  Merkle Root Calculation Demonstration")
print("=" * 65)

# --- Case 1: Single transaction (only coinbase) ---
print("\nCase 1: Single Transaction (1 coinbase tx)")
print("-" * 65)

tx1 = CoinbaseTx(1).CoinbaseTransaction()
txs = [tx1]

tx_hashes = [tx.id() for tx in txs]
print(f"  Leaf [Tx1 ID]: {tx_hashes[0][:20]}...")
root = blockchain.calculate_merkle_root(txs)
print(f"  Merkle Root  : {root[:20]}...")
print(f"  (Single tx: root == tx hash itself)")

# --- Case 2: Two transactions ---
print("\nCase 2: Two Transactions")
print("-" * 65)

tx1 = CoinbaseTx(2).CoinbaseTransaction()
tx2 = CoinbaseTx(3).CoinbaseTransaction()
txs = [tx1, tx2]

h1 = tx1.id()
h2 = tx2.id()
combined = h1 + h2
parent = hash256(combined.encode('utf-8'))

print(f"  Leaf [Tx1]: {h1[:20]}...")
print(f"  Leaf [Tx2]: {h2[:20]}...")
print(f"               \\       /")
print(f"  Hash(Tx1+Tx2): {parent[:20]}... <- Merkle Root")

root = blockchain.calculate_merkle_root(txs)
print(f"  Calculated  : {root[:20]}...")
print(f"  Match: {root == parent}")

# --- Case 3: Three transactions (odd — last one duplicated) ---
print("\nCase 3: Three Transactions (odd count, last one duplicated)")
print("-" * 65)

tx1 = CoinbaseTx(4).CoinbaseTransaction()
tx2 = CoinbaseTx(5).CoinbaseTransaction()
tx3 = CoinbaseTx(6).CoinbaseTransaction()
txs = [tx1, tx2, tx3]

h1, h2, h3 = tx1.id(), tx2.id(), tx3.id()
h4 = h3  # duplicate last

level2_left  = hash256((h1 + h2).encode('utf-8'))
level2_right = hash256((h3 + h4).encode('utf-8'))  # h3 hashed with itself
root_manual  = hash256((level2_left + level2_right).encode('utf-8'))

print(f"  Leaf [Tx1]: {h1[:16]}...")
print(f"  Leaf [Tx2]: {h2[:16]}...")
print(f"  Leaf [Tx3]: {h3[:16]}...")
print(f"  Leaf [Tx3 COPY]: (odd count, Tx3 duplicated)")
print()
print(f"  Hash(Tx1+Tx2)      : {level2_left[:16]}...")
print(f"  Hash(Tx3+Tx3_copy) : {level2_right[:16]}...")
print(f"  Merkle Root        : {root_manual[:16]}...")

root = blockchain.calculate_merkle_root(txs)
print(f"  Calculated         : {root[:16]}...")
print(f"  Match: {root == root_manual}")

# --- Real block: show merkle root stored in a real block ---
print("\n" + "=" * 65)
print("  Real Block — Merkle Root stored in BlockHeader")
print("=" * 65)
chain = blockchain.read_from_disk()
if chain:
    block = chain[0]
    print(f"  Block Height : {block['Height']}")
    print(f"  Merkle Root  : {block['BlockHeader']['merkle_root']}")
else:
    print("  No blocks in chain yet.")
