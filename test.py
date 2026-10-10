from Blockchain.Backend.Core.blockchain import Blockchain

if __name__ == '__main__':
    b = Blockchain()
    
    # Case 1: Original blockchain
    print("Case 1: Original blockchain")
    print(f"Blockchain Valid: {b.validate_chain()}")
    print()

    # Modify a block's nonce
    chain = b.read_from_disk()
    if len(chain) > 0:
        chain[-1]["BlockHeader"]["nonce"] += 1
        # Update the chain in database
        b.blockchainDB.update(chain)

    # Case 2: After modifying a block's nonce
    print("Case 2: After modifying a block's nonce")
    print(f"Blockchain Valid: {b.validate_chain()}")
    
    # Restore the chain
    if len(chain) > 0:
        chain[-1]["BlockHeader"]["nonce"] -= 1
        b.blockchainDB.update(chain)
