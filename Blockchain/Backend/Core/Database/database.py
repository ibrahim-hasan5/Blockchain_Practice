import os
import json


class BaseDB:
    def __init__(self):
        self.basepath = "Data"
        self.filepath = "/".join((self.basepath, self.filename))

    def BlockchainDBExists(self):
        return os.path.exists(self.filepath)

    def read(self):
        if not self.BlockchainDBExists():
            print(f"File {self.filepath} not available")
            return False

        with open(self.filepath, "r") as file:
            raw = file.readline()

        if len(raw) > 0:
            data = json.loads(raw)
        else:
            data = []
        return data

    def update(self, data):
        with open(self.filepath,'w+') as f:
            f.write(json.dumps(data))
        return True

    def write(self, item):
        data = self.read()
        if data:
            data = data + item
        else:
            data = item

        with open(self.filepath, "w+") as file:
            file.write(json.dumps(data))


class BlockchainDB(BaseDB):
    def __init__(self):
        self.filename = "uapcoin-blockchain"
        super().__init__()

    def lastBlock(self):
        data = self.read()

        if data:
            return data[-1]


# class AccountDB(BaseDB):
#     def __init__(self):
#         self.filename = "account"
#         super().__init__()


# class NodeDB(BaseDB):
#     def __init__(self):
#         self.filename = "node"
#         super().__init__()