class Block:
    """
    Block is a storage containter that stores transactions
    """

    def __init__(self, Height, Blocksize, BlockHeader, Txs):

        self.Height = Height
        self.Blocksize = Blocksize
        self.BlockHeader = BlockHeader
        self.Txs = Txs
        self.Txcount = len(self.Txs)
        

    