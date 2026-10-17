"""
Demonstration of calculate_fee(tx)

Fee = sum(input amounts) - sum(output amounts)

Test Cases:
  1. Coinbase tx         → fee = 0 (always)
  2. Regular tx, 1% fee  → fee = 50_000_000 Poisha (0.5 UAP Coin)
  3. Regular tx, split   → spend coinbase, send to 2 addresses with fee
  4. Invalid: tx referencing non-existent prev tx → returns None
"""
from Blockchain.Backend.Core.blockchain import Blockchain
from Blockchain.Backend.Core.tx import CoinbaseTx, TxIn, TxOut, Tx
from Blockchain.Backend.Core.script import Script
from Blockchain.Backend.Util.util import decode_base58
from Blockchain.config import ONE_COIN

blockchain = Blockchain()

MINER_ADDRESS = "15EDkKeKEZRtMiASKZoncU2J8WLqjGk5Hz"

def make_output(coins_in_uap, address=MINER_ADDRESS):
    amount = int(coins_in_uap * ONE_COIN)
    pubkey_hash = decode_base58(address)
    script = Script.p2pkh_script(pubkey_hash)
    return TxOut(amount=amount, script_pubkey=script)

# ── Read stored blockchain to get a real coinbase TxId ──────────────────────
chain = blockchain.read_from_disk()

# Handle both old format (single dict) and new format (list of dicts)
block_txs = chain[0]["Txs"]
if isinstance(block_txs, dict):
    coinbase_dict = block_txs          # old: single dict
else:
    coinbase_dict = block_txs[0]       # new: list, first is coinbase

coinbase_txid   = coinbase_dict["TxId"]
coinbase_amount = coinbase_dict["tx_outs"][0]["amount"]   # in Poisha

print("=" * 65)
print("  calculate_fee() Demonstration")
print("=" * 65)
print(f"\n  Reference Coinbase TxId : {coinbase_txid[:30]}...")
print(f"  Coinbase Output Amount  : {coinbase_amount:,} Poisha "
      f"= {coinbase_amount / ONE_COIN} UAP Coin\n")

# ── Case 1: Coinbase transaction → fee always 0 ──────────────────────────────
print("Case 1: Coinbase transaction (fee must be 0)")
print("-" * 65)
coinbase_tx = CoinbaseTx(99).CoinbaseTransaction()
fee1 = blockchain.calculate_fee(coinbase_tx)
print(f"  Result: {fee1} (expected: 0)\n")

# ── Case 2: Regular tx, keeping 1 UAP Coin as fee ────────────────────────────
print("Case 2: Regular tx — spend 50 UAP, send 49 UAP, keep 1 UAP as fee")
print("-" * 65)

fee_coins    = 1                                 # 1 UAP Coin as fee
send_amount  = coinbase_amount - int(fee_coins * ONE_COIN)

# TxIn references the coinbase: prev_tx = bytes.fromhex(coinbase_txid)
tx_in  = TxIn(bytes.fromhex(coinbase_txid), 0)
tx_out = make_output(send_amount / ONE_COIN)     # 49 UAP Coin

regular_tx = Tx(1, [tx_in], [tx_out], 0)
fee2 = blockchain.calculate_fee(regular_tx)
print(f"  Result : {fee2:,} Poisha = {fee2 / ONE_COIN} UAP Coin  (expected: 1.0 UAP)\n")

# ── Case 3: Two outputs, small fee ────────────────────────────────────────────
print("Case 3: Regular tx — 2 outputs (25 UAP + 24.9995 UAP), fee = 0.0005 UAP")
print("-" * 65)

fee_poisha   = int(0.0005 * ONE_COIN)
out_a        = make_output(25)
out_b_amount = coinbase_amount - int(25 * ONE_COIN) - fee_poisha
out_b        = TxOut(amount=out_b_amount, script_pubkey=Script.p2pkh_script(decode_base58(MINER_ADDRESS)))

tx_in2      = TxIn(bytes.fromhex(coinbase_txid), 0)
two_out_tx  = Tx(1, [tx_in2], [out_a, out_b], 0)
fee3        = blockchain.calculate_fee(two_out_tx)
print(f"  Result : {fee3:,} Poisha = {fee3 / ONE_COIN:.8f} UAP Coin  (expected: 0.00050000 UAP)\n")

# ── Case 4: Invalid — references a non-existent transaction ──────────────────
print("Case 4: Invalid tx -- prev_tx not in blockchain -> should return None")
print("-" * 65)
fake_txid   = "ab" * 32                          # 64 hex chars, not real
bad_tx_in   = TxIn(bytes.fromhex(fake_txid), 0)
bad_tx_out  = make_output(10)
bad_tx      = Tx(1, [bad_tx_in], [bad_tx_out], 0)
fee4        = blockchain.calculate_fee(bad_tx)
print(f"  Result : {fee4}  (expected: None)\n")
