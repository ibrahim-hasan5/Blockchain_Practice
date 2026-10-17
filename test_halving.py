"""
Demonstration of get_block_reward(block_height)
Halving every 10 blocks. Initial reward: 50 UAP Coin.
"""
from Blockchain.Backend.Core.blockchain import Blockchain

blockchain = Blockchain()

print("=" * 45)
print("  Block Reward Halving Schedule (UAP Coin)")
print("=" * 45)
print(f"{'Block Height':<18} {'Halvings':<12} {'Reward (UAP)'}")
print("-" * 45)

# Test key block heights
test_heights = [1, 5, 10, 11, 15, 20, 21, 30, 31, 50, 60, 70, 100]

for height in test_heights:
    halvings = (height - 1) // 10
    reward = blockchain.get_block_reward(height)
    print(f"  Block {height:<12} {halvings:<12} {reward}")

print("-" * 45)
print()

# Show continuous range for first 35 blocks
print("Block-by-block (Height 1 to 35):")
print(f"{'Height':<10} {'Reward'}")
print("-" * 20)
for h in range(1, 36):
    r = blockchain.get_block_reward(h)
    bar = "#" * (r // 2)  # visual bar
    print(f"  {h:<8} {r:<6} {bar}")
