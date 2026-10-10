import sys
sys.path.append("D:/UapCoin")

from Blockchain.Backend.Core.blockchain import Blockchain

if __name__ == "__main__":
    print("Initializing Blockchain...")
    blockchain = Blockchain()

    blockchain.add_next_block()
    blockchain.add_next_block()

    blockchain.print()

        # Case 1: Original blockchain
    print("Case 1: Original blockchain")
    print(f"Blockchain Valid: {blockchain.validate_chain()}")
    print()

    # Modify a block's nonce
    chain = blockchain.read_from_disk()
    if len(chain) > 0:
        chain[-1]["BlockHeader"]["nonce"] += 1
        # Update the chain in database
        blockchain.blockchainDB.update(chain)

    # Case 2: After modifying a block's nonce
    print("Case 2: After modifying a block's nonce")
    print(f"Blockchain Valid: {blockchain.validate_chain()}")
    
    # Restore the chain
    if len(chain) > 0:
        chain[-1]["BlockHeader"]["nonce"] -= 1
        blockchain.blockchainDB.update(chain)