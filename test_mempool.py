"""
Demonstration of add_to_mempool() and get_pending_transactions()

Test Cases:
  1. Add 3 different txs to mempool → all accepted
  2. Add a duplicate tx → rejected
  3. Mine a block → mempool txs included, then cleared
  4. Check mempool is empty after mining
"""
from Blockchain.Backend.Core.blockchain import Blockchain
from Blockchain.Backend.Core.tx import CoinbaseTx

blockchain = Blockchain()

print("=" * 60)
print("  Mempool Demonstration")
print("=" * 60)

# --- Case 1: Add 3 different transactions ---
print("\nCase 1: Add 3 different transactions to mempool")
print("-" * 60)

tx_a = CoinbaseTx(10).CoinbaseTransaction()
tx_b = CoinbaseTx(20).CoinbaseTransaction()
tx_c = CoinbaseTx(30).CoinbaseTransaction()

r1 = blockchain.add_to_mempool(tx_a)
r2 = blockchain.add_to_mempool(tx_b)
r3 = blockchain.add_to_mempool(tx_c)

print(f"\n  Results: [{r1}, {r2}, {r3}] (all should be True)")

# --- Case 2: Add duplicate tx ---
print("\nCase 2: Add a duplicate transaction (same tx_a again)")
print("-" * 60)

tx_a_duplicate = CoinbaseTx(10).CoinbaseTransaction()  # same block height = same tx id
r_dup = blockchain.add_to_mempool(tx_a_duplicate)
print(f"\n  Duplicate result: {r_dup} (should be False)")

# --- Case 3: Check pending transactions ---
print("\nCase 3: get_pending_transactions()")
print("-" * 60)

pending = blockchain.get_pending_transactions()
print(f"  Pending count : {len(pending)} (should be 3)")
for i, tx in enumerate(pending):
    print(f"  Tx[{i}] ID: {tx.id()[:30]}...")

# --- Case 4: Mine a block → mempool included and cleared ---
print("\nCase 4: Mine next block (mempool txs should be included)")
print("-" * 60)

blockchain.add_next_block()

# --- Case 5: Mempool should be empty now ---
print("\nCase 5: Check mempool after mining")
print("-" * 60)

remaining = blockchain.get_pending_transactions()
print(f"  Mempool size after mining: {len(remaining)} (should be 0)")
print(f"  Mempool is empty: {len(remaining) == 0}")
