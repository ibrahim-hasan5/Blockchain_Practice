__path__ = ["D:\\Blockchain Full Stack\\Blockchain"]

VERSION = 1.0

TARGET = "0000"

COIN_NAME = "UAP Coin"
ZERO_HASH = "0" * 64
ZERO_HASH_BYTES = bytes.fromhex(ZERO_HASH)

INITIAL_REWARD = 50 # In Bitcoin Blockchain the initial reward for mining a block was 50 BTC, which halves every 210,000 blocks. 
                    #The current reward is 3.125 BTC, which is 312,500,000 satoshis.
                    # The reward will continue to halve every 210,000 blocks until it reaches zero.

CURRENT_REWARD = INITIAL_REWARD # 50 UAP Coin
ONE_COIN = 100_000_000 # 1 UAP Coin = 100,000,000 Poisha (smallest unit of UAP Coin)